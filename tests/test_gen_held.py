"""test_gen_held.py — the gate on the five held values' derivation (tools/gen_held.py; docs/project/tables/README.md).

Needs the reference dumps (ROMDIR, read only) and an export of the original at the tables' pin.
  H1 DERIVED  tools/gen_held.py exits 0 and writes one literal per distinct held SHA-1
  H2 HELD     every literal it wrote has, by an independent SHA-1 here, the SHA-1 facts/held.tsv names for each
              held row, and every held row is covered
  H3 WHOLE    the 30 manifests rendered with those literals parse equal to the original's (tomli / json, key order
              included), with no held placeholder left

CONTROLS ([VSR-22]):
  wrong-held-sha     a copy of held.tsv with throw_arc_tables' SHA-1 changed: gen_held must refuse, H1, H2, H3 fail
  placeholder-left   the render made without the derived literals: H3 must fail
A normal run runs each control and reports it FIRED or DEAD; `--control <name>` makes the perturbed input the gate's
and the gate must reach its own FAIL.

Usage: python3 tests/test_gen_held.py [--romdir DIR] [--export DIR] [--control NAME]
       (ROMDIR default: ../ROMS beside this repository; export default: build/export_<pin>)
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import phase0lib  # noqa: E402
import render_manifests  # noqa: E402
import runlog  # noqa: E402
import tomli  # noqa: E402
from test_phase0_tables import parse_diff, read_table  # noqa: E402

TABLES = os.path.join(ROOT, "docs", "project", "tables")
HELD = os.path.join(TABLES, "facts", "held.tsv")
CONTROLS = {"wrong-held-sha": {"H1", "H2", "H3"}, "placeholder-left": {"H3"}}


def checks(tmp, export, romdir, held_file, use_literals=True):
    failed, figures = set(), []
    out = os.path.join(tmp, "held_values.json")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "gen_held.py"), export, romdir,
                        os.path.join(tmp, "scratch"), out], capture_output=True, text=True,
                       env=dict(os.environ, PHASE0_HELD=held_file))
    held = phase0lib.read_held(HELD)
    literals = json.load(open(out)) if p.returncode == 0 and os.path.exists(out) else {}
    figures.append("H1 gen_held exit %d, literals %d, distinct held SHA-1s %d%s" % (
        p.returncode, len(literals), len(set(held.values())),
        "" if p.returncode == 0 else ": " + (p.stdout + p.stderr).strip().splitlines()[-1]))
    if p.returncode or len(literals) != len(set(held.values())):
        failed.add("H1")
    mine = {hashlib.sha1(lit.encode()).hexdigest(): lit for lit in literals.values()}
    keyed_wrong = sum(1 for k, lit in literals.items() if hashlib.sha1(lit.encode()).hexdigest() != k)
    uncovered = [".".join(i[1:]) for i, h in held.items() if h not in mine]
    figures.append("H2 held rows %d, covered %d, literals keyed by another SHA-1 %d%s" % (
        len(held), len(held) - len(uncovered), keyed_wrong, (": " + uncovered[0]) if uncovered else ""))
    if uncovered or keyed_wrong or not literals:
        failed.add("H2")
    rendered = os.path.join(tmp, "rendered")
    render_manifests.render(TABLES, rendered, mine if use_literals else {})
    differ, placeholders = [], 0
    a = phase0lib.load_census(export)
    for rel in a.canon(Path(export)):
        m = rel[len("build/manifest/"):]
        o, r = Path(export, rel).read_text(), Path(rendered, m).read_text()
        placeholders += r.count("HELD:sha1=")
        load = json.loads if m.endswith(".json") else tomli.loads
        why = parse_diff(load(o), load(r))
        if why:
            differ.append("%s: %s" % (m, why))
    figures.append("H3 manifests %d, parse differs %d, placeholders left %d%s" % (
        len(a.canon(Path(export))), len(differ), placeholders, (": " + differ[0]) if differ else ""))
    if differ or placeholders:
        failed.add("H3")
    return failed, figures


def perturbed_held(tmp):
    """A copy of held.tsv with throw_arc_tables' SHA-1 changed (its last hex digit turned)."""
    path = os.path.join(tmp, "held.tsv")
    lines = open(HELD).readlines()
    for i, line in enumerate(lines):
        f = line.split("\t")
        if len(f) > 5 and f[2] == "throw_arc_tables":
            f[5] = f[5][:-1] + ("0" if f[5][-1] != "0" else "1")
            lines[i] = "\t".join(f)
    open(path, "w").writelines(lines)
    return path


def run_case(name, export, romdir):
    tmp = tempfile.mkdtemp(prefix="test_gen_held.", dir=os.path.join(ROOT, "build", "tmp"))
    try:
        if name == "wrong-held-sha":
            return checks(tmp, export, romdir, perturbed_held(tmp))
        return checks(tmp, export, romdir, HELD, use_literals=(name != "placeholder-left"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    args = sys.argv[1:]
    opts = {}
    for flag in ("--romdir", "--export", "--control"):
        if flag in args:
            i = args.index(flag)
            opts[flag] = args[i + 1] if i + 1 < len(args) else ""
            args = args[:i] + args[i + 2:]
    romdir = os.path.realpath(opts.get("--romdir") or os.path.join(ROOT, "..", "ROMS"))
    pin = read_table(os.path.join(TABLES, "roster.tsv"))[0]
    export = os.path.realpath(opts.get("--export") or os.path.join(ROOT, "build", "export_" + pin))
    os.makedirs(os.path.join(ROOT, "build", "tmp"), exist_ok=True)
    control = opts.get("--control")
    run = runlog.Run("test_gen_held", "control:" + control if control else "normal")
    print("romdir: %s\nexport: %s" % (romdir, export))
    fired, dead = [], []
    if control is not None:
        if control not in CONTROLS:
            print("REFUSED: no declared control named %r (declared: %s)" % (control, ", ".join(CONTROLS)))
            run.record("REFUSED", declared=list(CONTROLS))
            sys.exit(3)
        print("MODE: control %s (the perturbed input is the gate's; the gate must FAIL)" % control)
        failed, figures = run_case(control, export, romdir)
    else:
        failed, figures = run_case("normal", export, romdir)
        for name, want in CONTROLS.items():
            got, _ = run_case(name, export, romdir)
            if got == want:
                print("CONTROL FIRED: %s (failed %s, exactly as declared)" % (name, ",".join(sorted(got))))
                fired.append(name)
            else:
                print("CONTROL DEAD: %s (failed %s, declared %s)" % (name, ",".join(sorted(got)) or "nothing",
                                                                     ",".join(sorted(want))))
                dead.append(name)
                failed.add("control:" + name)
    for f in figures:
        print(f)
    print("VERDICT: %s" % ("PASS" if not failed else "FAIL (" + ", ".join(sorted(failed)) + ")"))
    run.record("PASS" if not failed else "FAIL", failed=failed, declared=list(CONTROLS), fired=fired, dead=dead)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
