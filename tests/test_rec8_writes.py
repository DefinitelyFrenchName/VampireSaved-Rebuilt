"""test_rec8_writes.py — the gate on tools/rec8_writes.py (#4): what the original's merged build writes for
`rec8_a`/`rec8_b`, and the tenants' own rows of the table `rec8_b` slices (docs/project/tables/README.md "What the
build wrote for rec8_a and rec8_b"). Every expectation is anchored on the reference dumps, not on our tables.

  R1 NO-OP    each tenant's `rec8_a`/`rec8_b` record value equals vsavj's data-view bytes where the original's
              generator writes it (6 writes)
  R2 COPIES   each tenant's own row of the table at vsavj 0x0BE3FA equals its base-half row in vsavj, and vs2's row
              for the tenant differs from it
  R3 READER   each game has exactly one `movea.l #table,a0`, and its index is loaded from +0x382

CONTROLS ([VSR-22]):
  value-flipped    the first record's rec8_a value with one bit flipped: R1 must fail
  row-unaliased    the first tenant compared against the next base-half row: R2 must fail
  index-elsewhere  the index load looked for at +0x383: R3 must fail
A normal run runs each control and reports it FIRED or DEAD; `--control <name>` runs the gate on the perturbed
measure, where it must FAIL.

Usage: python3 tests/test_rec8_writes.py [--export DIR] [--roms DIR] [--control NAME]
"""
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import runlog  # noqa: E402
from rec8_writes import load, measure  # noqa: E402
from test_phase0_tables import read_table  # noqa: E402

CONTROLS = {"value-flipped": {"R1"}, "row-unaliased": {"R2"}, "index-elsewhere": {"R3"}}


def checks(res):
    failed, figures = set(), []
    same = sum(w[2] for w in res["writes"])
    figures.append("R1 writes %d, equal to vsavj's bytes %d" % (len(res["writes"]), same))
    if not res["writes"] or same != len(res["writes"]):
        failed.add("R1")
    copies = sum(r[1] for r in res["rows"])
    differ = sum(r[2] for r in res["rows"])
    figures.append("R2 tenants %d, own row a base-half copy %d, vs2's row different %d" % (
        len(res["rows"]), copies, differ))
    if not res["rows"] or copies != len(res["rows"]) or differ != len(res["rows"]):
        failed.add("R2")
    figures.append("R3 " + "; ".join("%s sites %d, indexed from +0x382 %d" % r for r in res["readers"]))
    if any(r[1] != 1 or r[2] != 1 for r in res["readers"]) or len(res["readers"]) != 2:
        failed.add("R3")
    return failed, figures


def main():
    args = sys.argv[1:]
    opts = {}
    for name in ("--export", "--roms", "--control"):
        if name in args:
            i = args.index(name)
            opts[name] = args[i + 1] if i + 1 < len(args) else ""
            args = args[:i] + args[i + 2:]
    control = opts.get("--control")
    pin = read_table(os.path.join(ROOT, "docs", "project", "tables", "roster.tsv"))[0]
    export = os.path.realpath(opts.get("--export") or os.path.join(ROOT, "build", "export_" + pin))
    roms = os.path.realpath(opts.get("--roms") or os.path.join(ROOT, "..", "ROMS"))
    run = runlog.Run("test_rec8_writes", "control:" + control if control else "normal")
    print("export: %s\nroms: %s" % (export, roms))
    fired, dead = [], []
    if control is not None and control not in CONTROLS:
        print("REFUSED: no declared control named %r (declared: %s)" % (control, ", ".join(CONTROLS)))
        run.record("REFUSED", declared=list(CONTROLS))
        sys.exit(3)
    inp = load(export, roms)
    for p, h in inp["read"]:
        print("read %s sha1 %s" % (p, h))
    if control is not None:
        print("MODE: control %s (the gate must FAIL)" % control)
        failed, figures = checks(measure(inp, control)[1])
    else:
        failed, figures = checks(measure(inp)[1])
        for name, want in CONTROLS.items():
            got, _ = checks(measure(inp, name)[1])
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
    run.record("PASS" if not failed else "FAIL", failed=failed, cases=6, declared=list(CONTROLS), fired=fired,
               dead=dead)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
