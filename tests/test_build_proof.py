"""test_build_proof.py — the gate on tools/build_proof.py's own logic, without running a build (#4: the build needs
vhunt2, so the proof is phase 1's; SPEC.md §0).

ROM-free. Each check is on synthetic inputs, or on a copy of a file of the export at the tables' pin:
  P1 SAME     compare() finds nothing between two identical build outputs (a zip, a binary, a log)
  P2 DIFFER   compare() reports a zip member that differs, a file that differs and a file only one side has, and
              puts a differing log apart from the verdict
  P3 SHIM     shim_audit() applies to the export's tools/audit_roms.py, for a ROMDIR holding neither vhunt2 set and
              for one holding vhunt2.zip alone: the shimmed module, loaded, requires exactly the vhunt2 sets present
              (set, key and manifest rows) and still requires vsav; and the shim refuses a file it does not apply to
  P4 CONTROL  perturb() changes exactly one value of a rendered donovan.toml: the `val` of the first [[aux_poke]] not
              `only_base_slot` (one the merged build applies), +1

CONTROLS ([VSR-22]):
  blind-compare   compare() replaced by one that finds nothing: P2 must fail
A normal run runs the control and reports it FIRED or DEAD; `--control blind-compare` runs the gate on it, where it
must FAIL.

Usage: python3 tests/test_build_proof.py [--export DIR] [--control NAME]
"""
import importlib.util
import os
import shutil
import sys
import tempfile
import zipfile

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import build_proof  # noqa: E402
import runlog  # noqa: E402
import tomli  # noqa: E402
from test_phase0_tables import read_table  # noqa: E402

TABLES = os.path.join(ROOT, "docs", "project", "tables")
CONTROLS = {"blind-compare": {"P2"}}


def output(base, member=b"member", binary=b"\x00\x01", log="ok\n", extra=False):
    os.makedirs(os.path.join(base, "rompath"))
    with zipfile.ZipFile(os.path.join(base, "rompath", "set.zip"), "w") as z:
        z.writestr("a.bin", member)
    open(os.path.join(base, "prg.bin"), "wb").write(binary)
    open(os.path.join(base, "gen.log"), "w").write(log)
    if extra:
        open(os.path.join(base, "extra.bin"), "wb").write(b"x")


def checks(tmp, export, compare):
    failed, figures = set(), []
    output(os.path.join(tmp, "a"))
    output(os.path.join(tmp, "b"))
    diff, logs, n, members = compare(os.path.join(tmp, "a"), os.path.join(tmp, "b"))
    figures.append("P1 files %d, zip members %d, differing %d, logs differing %d" % (n, members, len(diff), len(logs)))
    if diff or logs or n != 3 or members != 1:
        failed.add("P1")
    output(os.path.join(tmp, "c"), member=b"other", binary=b"\x00\x02", log="elsewhere\n", extra=True)
    diff, logs, n, members = compare(os.path.join(tmp, "a"), os.path.join(tmp, "c"))
    want = {"rompath/set.zip: members a.bin", "prg.bin", "extra.bin (only in rendered)"}
    figures.append("P2 differing %d %s, logs differing %d" % (len(diff), sorted(diff), len(logs)))
    if set(diff) != want or logs != ["gen.log"]:
        failed.add("P2")
    lost, refused = [], True
    for case, present in (("neither", ()), ("vhunt2", ("vhunt2.zip",))):
        roms = os.path.join(tmp, "roms_" + case)
        os.makedirs(roms)
        for z in present:
            open(os.path.join(roms, z), "w").close()
        leg = os.path.join(tmp, "leg_" + case)
        os.makedirs(os.path.join(leg, "tools"))
        shutil.copy(os.path.join(export, "tools", "audit_roms.py"), os.path.join(leg, "tools", "audit_roms.py"))
        _, dropped = build_proof.shim_audit(leg, roms)
        spec = importlib.util.spec_from_file_location("shimmed_" + case, os.path.join(leg, "tools", "audit_roms.py"))
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)
        kept = audit.parse_manifest("".join("%s/m  1  00000000  %s\n" % (z, "0" * 40)
                                            for z in build_proof.VHUNT2_SETS + ("vsav.zip",)))
        want = set(present)
        got = {z for z in audit.REQUIRED_ZIPS if "vhunt2" in z}
        keys = {e[0] for e in audit.HARD_EXPECTATIONS if "vhunt2" in e[0]}
        rows = {k.split("/")[0] for k in kept if k.startswith("vhunt2")}
        if got != want or keys != want or rows != want or set(dropped) != set(build_proof.VHUNT2_SETS) - want:
            lost.append("%s: required %s, keys %s, rows %s" % (case, sorted(got), sorted(keys), sorted(rows)))
        if "vsav.zip/m" not in kept or "vsav.zip" not in audit.REQUIRED_ZIPS:
            lost.append("%s: a vsav requirement went with the shim" % case)
        try:
            build_proof.shim_audit(leg, roms)
            refused = False
        except SystemExit:
            pass
    figures.append("P3 cases 2, vhunt2 requirements not as present %d%s, vsav kept, re-applying refused %s" % (
        len(lost), (": " + lost[0][:80]) if lost else "", refused))
    if lost or not refused:
        failed.add("P3")
    man = os.path.join(leg, "build", "manifest")
    os.makedirs(man)
    shutil.copy(os.path.join(export, "build", "manifest", "donovan.toml"), os.path.join(man, "donovan.toml"))
    before = tomli.loads(open(os.path.join(man, "donovan.toml")).read())
    said = build_proof.perturb(leg)
    after = tomli.loads(open(os.path.join(man, "donovan.toml")).read())
    changed = [(k, i, key) for k in before for i, (x, y) in enumerate(zip(before[k], after[k]))
               if isinstance(before[k], list) for key in x if x[key] != y.get(key)]
    k = next(i for i, r in enumerate(before["aux_poke"]) if not r.get("only_base_slot"))
    first = before["aux_poke"][k]["val"]
    ok = changed == [("aux_poke", k, "val")] and after["aux_poke"][k]["val"] == first + 1
    figures.append("P4 %s; values changed %d %s" % (said, len(changed), changed[:2]))
    if not ok:
        failed.add("P4")
    return failed, figures


def main():
    args = sys.argv[1:]
    export, control = None, None
    if "--export" in args:
        i = args.index("--export")
        export, args = os.path.realpath(args[i + 1]), args[:i] + args[i + 2:]
    if "--control" in args:
        i = args.index("--control")
        control = args[i + 1] if i + 1 < len(args) else ""
    pin = read_table(os.path.join(TABLES, "roster.tsv"))[0]
    export = export or os.path.join(ROOT, "build", "export_" + pin)
    run = runlog.Run("test_build_proof", "control:" + control if control else "normal")
    blind = lambda a, b: ([], [], 3, 1)                                                     # noqa: E731
    os.makedirs(os.path.join(ROOT, "build", "tmp"), exist_ok=True)

    def case(compare):
        tmp = tempfile.mkdtemp(prefix="test_build_proof.", dir=os.path.join(ROOT, "build", "tmp"))
        try:
            return checks(tmp, export, compare)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    fired, dead = [], []
    if control is not None:
        if control not in CONTROLS:
            print("REFUSED: no declared control named %r (declared: %s)" % (control, ", ".join(CONTROLS)))
            run.record("REFUSED", declared=list(CONTROLS))
            sys.exit(3)
        print("MODE: control %s (the gate must FAIL)" % control)
        failed, figures = case(blind)
    else:
        failed, figures = case(build_proof.compare)
        got, _ = case(blind)
        if got == CONTROLS["blind-compare"]:
            print("CONTROL FIRED: blind-compare (failed %s, exactly as declared)" % ",".join(sorted(got)))
            fired.append("blind-compare")
        else:
            print("CONTROL DEAD: blind-compare (failed %s, declared P2)" % (",".join(sorted(got)) or "nothing"))
            dead.append("blind-compare")
            failed.add("control:blind-compare")
    for f in figures:
        print(f)
    print("VERDICT: %s" % ("PASS" if not failed else "FAIL (" + ", ".join(sorted(failed)) + ")"))
    run.record("PASS" if not failed else "FAIL", failed=failed, declared=list(CONTROLS), fired=fired, dead=dead)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
