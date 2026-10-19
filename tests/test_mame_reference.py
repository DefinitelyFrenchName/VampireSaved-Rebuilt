"""test_mame_reference.py — the gate on the reference MAME (tools/setup_mame.py): the binary this repository built from
the pinned source is the instrument that froze the original's vanilla oracle logs ([VSR-9]; [MFI-24]: parity before
any profile patch). Its subject is an emulator as an instrument, a class F gate (SPEC.md §5.1), so it runs the
original's own `tests/test_mame_parity.sh`, unchanged, in the export, with this binary as its source build
(SPEC.md §5.2).

  M1 IDENTITY  build.json names the pin and profile `none` (absent before R-005's profiles), the binary's SHA-1 is the one build.json recorded, and the binary does not
               know `vsavjw` (no profile)
  M2 PARITY    the original's gate prints `PASS: MAME parity.`; every frozen row it ran (its section 1, the vsavj
               logs, and 1b, the reference binary's frozen logs) reads `ok`, as many as its section headers count,
               none of them zero; every replay of its A/B sections (2, vsavj, and 3, vsav2: replays frozen nowhere,
               run on this binary and on the reference binary) reads `ok  identical`, none skipped; and its in-gate
               control printed `CONTROL FIRED: wrong-hash`. (R-005: the original's header says every replay is
               frozen; at bf92acd2 eight `118_*` replays are not, and run in section 2.)

CONTROLS ([VSR-22]):
  other-binary  M1 run on the Homebrew reference binary instead of ours: M1 must fail (its SHA-1 is not build.json's)
  wrong-hash    the original gate's own mode (`CONTROL=wrong-hash`: every frozen reference hash with one digit
                changed): M2 must fail
A normal run runs `other-binary` in-process and reports it FIRED or DEAD, and reads `wrong-hash`'s in-gate FIRED line;
`--control <name>` runs the gate with that control applied, where it must FAIL.

Usage: python3 tests/test_mame_reference.py [--build DIR] [--export DIR] [--roms DIR] [--ref BIN] [--jobs N]
                                            [--control NAME]
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import runlog  # noqa: E402
from setup_mame import PINNED, STAMP, knows  # noqa: E402
from test_phase0_tables import read_table  # noqa: E402

CONTROLS = {"other-binary": {"M1"}, "wrong-hash": {"M2"}}
GATE = os.path.join("tests", "test_mame_parity.sh")


def identity(build, binary):
    """(ok, figure) for M1 on `binary` against the build record in `build`."""
    rec = json.load(open(os.path.join(build, STAMP)))
    sha = hashlib.sha1(open(binary, "rb").read()).hexdigest()
    wide = knows(binary, "vsavjw")
    ok = (rec.get("pin") == PINNED and rec.get("profile", "none") == "none" and sha == rec.get("binary_sha1")
          and not wide)
    return ok, "M1 %s sha1 %s, build.json pin %s sha1 %s, knows vsavjw %s" % (
        binary, sha, rec.get("pin", "-")[:8], rec.get("binary_sha1"), "yes" if wide else "no")


def parity(text):
    """(ok, figures) for M2 on the original gate's output."""
    heads = [int(n) for n in re.findall(r"^== 1b?\. .*\((\d+) replays", text, re.M)]
    ab_heads = [int(n) for n in re.findall(r"^== [23]\. .*\((\d+) replays", text, re.M)]
    oks = len(re.findall(r"^  \S+ +ok  [0-9a-f]{40}$", text, re.M))
    ab_oks = len(re.findall(r"^  \S+ +ok  identical$", text, re.M))
    fails = len(re.findall(r"^  \S+ +(FAIL|RUN-FAIL|NONDETERMINISTIC)", text, re.M))
    skipped = len(re.findall(r"^  SKIPPED", text, re.M))
    verdict = re.findall(r"^(PASS|FAIL|PARTIAL)\b.*$", text, re.M)
    fired = bool(re.search(r"^CONTROL FIRED: wrong-hash", text, re.M))
    ok = (verdict == ["PASS"] and len(heads) == 2 and all(heads) and oks == sum(heads) and len(ab_heads) == 2
          and ab_oks == sum(ab_heads) and not fails and not skipped and fired)
    return ok, ["M2 sections 1/1b replays %s, rows ok %d; A/B sections 2/3 replays %s, identical %d; "
                "rows failed %d, sections skipped %d" % (
                    "/".join(map(str, heads)) or "-", oks, "/".join(map(str, ab_heads)) or "-", ab_oks, fails,
                    skipped),
        "M2 original verdict %s, in-gate CONTROL FIRED: wrong-hash %s" % (
            "/".join(verdict) or "none", "yes" if fired else "no")]


def main():
    args = sys.argv[1:]
    opts = {}
    for name in ("--build", "--export", "--roms", "--ref", "--jobs", "--control"):
        if name in args:
            i = args.index(name)
            opts[name] = args[i + 1] if i + 1 < len(args) else ""
            args = args[:i] + args[i + 2:]
    control = opts.get("--control")
    pin = read_table(os.path.join(ROOT, "docs", "project", "tables", "roster.tsv"))[0]
    build = os.path.realpath(opts.get("--build") or os.path.join(ROOT, "build", "emu", "mame-ref"))
    export = os.path.realpath(opts.get("--export") or os.path.join(ROOT, "build", "export_" + pin))
    roms = os.path.realpath(opts.get("--roms") or os.path.join(ROOT, "..", "ROMS"))
    ref = opts.get("--ref") or shutil.which("mame") or ""
    binary = os.path.join(build, json.load(open(os.path.join(build, STAMP))).get("binary", "mame/cps2"))
    run = runlog.Run("test_mame_reference", "control:" + control if control else "normal")
    print("build: %s\nexport: %s\nroms: %s\nreference: %s" % (build, export, roms, ref or "none"))
    if control is not None and control not in CONTROLS:
        print("REFUSED: no declared control named %r (declared: %s)" % (control, ", ".join(CONTROLS)))
        run.record("REFUSED", declared=list(CONTROLS))
        sys.exit(3)
    if control is not None:
        print("MODE: control %s (the gate must FAIL)" % control)
    failed, figures, fired, dead = set(), [], [], []

    ok, fig = identity(build, ref if control == "other-binary" else binary)
    figures.append(fig)
    if not ok:
        failed.add("M1")
    if control is None:
        if ref and not identity(build, ref)[0]:
            print("CONTROL FIRED: other-binary (M1 fails on %s)" % ref)
            fired.append("other-binary")
        else:
            print("CONTROL DEAD: other-binary (%s)" % ("no reference binary" if not ref else "M1 passed on it"))
            dead.append("other-binary")
            failed.add("control:other-binary")

    if control != "other-binary":
        env = dict(os.environ, ROMDIR=roms, MAME_SRC_BIN=binary, MAME_REF_BIN=ref,
                   PARITY_JOBS=opts.get("--jobs") or str(max(1, (os.cpu_count() or 2) // 2)))
        env.pop("CONTROL", None)
        if control == "wrong-hash":
            env["CONTROL"] = "wrong-hash"
        p = subprocess.run(["sh", GATE], cwd=export, env=env, capture_output=True, text=True)
        text = p.stdout + p.stderr
        log = os.path.join(ROOT, "build", "tmp", "test_mame_reference.%s.log" % (control or "normal"))
        os.makedirs(os.path.dirname(log), exist_ok=True)
        open(log, "w").write(text)
        print("original gate: %s exit %d, output in %s" % (GATE, p.returncode, log))
        for line in text.splitlines():
            if line.startswith(("  under test", "               sha1", "  reference", "  unpatched", "CONTROL ")):
                print("  | " + line.strip())
        ok, figs = parity(text)
        figures += figs
        if not ok:
            failed.add("M2")
        if control is None:
            (fired if re.search(r"^CONTROL FIRED: wrong-hash", text, re.M) else dead).append("wrong-hash")
    for f in figures:
        print(f)
    print("VERDICT: %s" % ("PASS" if not failed else "FAIL (" + ", ".join(sorted(failed)) + ")"))
    run.record("PASS" if not failed else "FAIL", failed=failed, cases=2, declared=list(CONTROLS), fired=fired,
               dead=dead)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
