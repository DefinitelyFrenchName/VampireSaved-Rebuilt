"""test_doll_hop_table.py — the gate on docs/project/tables/doll_hop.tsv (#6): the newcomers' own rows of the doll-hop
table, as vs2 holds them (tools/doll_hop.py; docs/project/tables/README.md "The doll's hop, vs2's rows"). Every
expectation is anchored on the reference dumps, not on our tables.

  H1 TABLE    the committed table equals the rows read now from vsav2's data view (6 rows: 3 tenants x 2 variants,
              every field and vs2 address), and its header's ROM SHA-1s are the dumps read
  H2 READER   each game has exactly one `movea.l #table,a0`, and its index is loaded from +0x382 (so a row's id is
              the raw id on both games)
  H3 PREMISE  each tenant's vs2 row differs from vsavj's row at the same id (the port changes the table)

CONTROLS ([VSR-22]):
  value-flipped    the committed table with Donovan's variant-0 yv changed: H1 must fail
  index-elsewhere  the index load looked for at +0x383: H2 must fail
  rows-equal       vsavj's data view given vs2's rows at the tenants' ids: H3 must fail
A normal run runs each control and reports it FIRED or DEAD; `--control <name>` runs the gate on the perturbed
input, where it must FAIL.

Usage: python3 tests/test_doll_hop_table.py [--export DIR] [--roms DIR] [--control NAME]
"""
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import runlog  # noqa: E402
from doll_hop import COLUMNS, OUT, PIN, load, measure  # noqa: E402
from test_phase0_tables import read_table  # noqa: E402

CONTROLS = {"value-flipped": {"H1"}, "index-elsewhere": {"H2"}, "rows-equal": {"H3"}}


def committed(perturb=None):
    pin, sha, rows = read_table(OUT)
    out = [dict(zip(COLUMNS, r)) for r in rows[1:]] if rows and rows[0] == COLUMNS else []
    if perturb == "value-flipped" and out:
        out[0] = dict(out[0], yv="8")
    return pin, sha, out


def checks(inp, res, table):
    failed, figures = set(), []
    pin, sha, rows = table
    zips = {os.path.basename(p): h[:12] for p, h in inp["read"] if p.endswith(".zip")}
    head = {os.path.basename(p): h for p, h in sha.items() if p.endswith(".zip")}
    head_ok = pin == PIN and len(zips) == 2 and head == zips
    same = sum(a == b for a, b in zip(rows, res["rows"]))
    figures.append("H1 committed rows %d, measured %d, equal %d; header pin %s, ROM SHA-1s %s" % (
        len(rows), len(res["rows"]), same, pin, "match" if head_ok else "DIFFER"))
    if not res["rows"] or len(rows) != len(res["rows"]) or same != len(rows) or not head_ok:
        failed.add("H1")
    figures.append("H2 " + "; ".join("%s sites %d, indexed from +0x382 %d" % r for r in res["readers"]))
    if len(res["readers"]) != 2 or any(r[1] != 1 or r[2] != 1 for r in res["readers"]):
        failed.add("H2")
    differ = sum(d[1] for d in res["differs"])
    figures.append("H3 tenants %d, vs2's row different from vsavj's %d" % (len(res["differs"]), differ))
    if not res["differs"] or differ != len(res["differs"]):
        failed.add("H3")
    return failed, figures


def run_checks(inp, perturb=None):
    return checks(inp, measure(inp, perturb)[1], committed(perturb))


def main():
    args = sys.argv[1:]
    opts = {}
    for name in ("--export", "--roms", "--control"):
        if name in args:
            i = args.index(name)
            opts[name] = args[i + 1] if i + 1 < len(args) else ""
            args = args[:i] + args[i + 2:]
    control = opts.get("--control")
    export = os.path.realpath(opts.get("--export") or os.path.join(ROOT, "build", "export_" + PIN))
    roms = os.path.realpath(opts.get("--roms") or os.path.join(ROOT, "..", "ROMS"))
    run = runlog.Run("test_doll_hop_table", "control:" + control if control else "normal")
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
        failed, figures = run_checks(inp, control)
    else:
        failed, figures = run_checks(inp)
        for name, want in CONTROLS.items():
            got, _ = run_checks(inp, name)
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
