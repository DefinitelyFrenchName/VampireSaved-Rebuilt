"""test_vet_rows_table.py — the gate on docs/project/tables/vet_rows.tsv (#6): the newcomers' own rows of the five
veteran-move tables, as vs2 holds them (tools/vet_rows.py; docs/project/tables/README.md "The five veteran moves").
Every expectation is anchored on the reference dumps, or on the raw-id census that tests/test_raw_id_census.py gates
against them, never on our build.

  V1 TABLE    the committed table equals the rows read now from vsav2 (15 rows: 5 tables x 3 tenants, every value
              and vs2 address), and its header's ROM SHA-1s are the dumps read
  V2 SHAPE    for each table, on all 32 ids: vsavj's ids 0x10-0x1F are a copy of its ids 0x00-0x0F, and vs2's ids
              0x00-0x0F equal vsavj's (the rows are storage; a veteran victim reads the same row on both games)
  V3 PREMISE  each tenant's vs2 row differs from vsavj's exactly where the census's `vs2_differs` says it does

CONTROLS ([VSR-22]):
  value-flipped  the committed table with Felicia's Pyron row changed: V1 must fail
  shape-broken   vsavj's data view with Zabel's id 0x1F row changed: V2 must fail
  census-all-differ  the census read as saying all three of Gallon's rows differ (`dhp`): V3 must fail
A normal run runs each control and reports it FIRED or DEAD; `--control <name>` runs the gate on the perturbed
input, where it must FAIL.

Usage: python3 tests/test_vet_rows_table.py [--export DIR] [--roms DIR] [--control NAME]
"""
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import runlog  # noqa: E402
from test_phase0_tables import read_table  # noqa: E402
from vet_rows import COLUMNS, OUT, PIN, load, measure  # noqa: E402

CONTROLS = {"value-flipped": {"V1"}, "shape-broken": {"V2"}, "census-all-differ": {"V3"}}


def committed(perturb=None):
    pin, sha, rows = read_table(OUT)
    out = [dict(zip(COLUMNS, r)) for r in rows[1:]] if rows and list(rows[0]) == list(COLUMNS) else []
    if perturb == "value-flipped":
        out = [dict(r, value="-3,98") if (r["move"], r["tenant"]) == ("felicia", "pyron") else r for r in out]
    return pin, sha, out


def checks(inp, res, table):
    failed, figures = set(), []
    pin, sha, rows = table
    zips = {os.path.basename(p): h[:12] for p, h in inp["read"] if p.endswith(".zip")}
    head = {os.path.basename(p): h for p, h in sha.items() if p.endswith(".zip")}
    head_ok = pin == PIN and len(zips) == 2 and head == zips
    same = sum(a == b for a, b in zip(rows, res["rows"]))
    figures.append("V1 committed rows %d, measured %d, equal %d; header pin %s, ROM SHA-1s %s" % (
        len(rows), len(res["rows"]), same, pin, "match" if head_ok else "DIFFER"))
    if not res["rows"] or len(rows) != len(res["rows"]) or same != len(rows) or not head_ok:
        failed.add("V1")
    figures.append("V2 tables %d, variant half a copy %d, vs2's base half equal %d" % (
        len(res["shape"]), sum(s[1] for s in res["shape"]), sum(s[2] for s in res["shape"])))
    if not res["shape"] or not all(s[1] and s[2] for s in res["shape"]):
        failed.add("V2")
    agree = sum(d[2] == d[3] for d in res["differs"])
    figures.append("V3 rows %d, vs2's differing from vsavj's %d, agreeing with the census %d%s" % (
        len(res["differs"]), sum(d[2] for d in res["differs"]), agree,
        "".join(" %s_%s=same" % d[:2] for d in res["differs"] if not d[2])))
    if not res["differs"] or agree != len(res["differs"]) or not any(d[2] for d in res["differs"]):
        failed.add("V3")
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
    run = runlog.Run("test_vet_rows_table", "control:" + control if control else "normal")
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
    run.record("PASS" if not failed else "FAIL", failed=failed, cases=15, declared=list(CONTROLS), fired=fired,
               dead=dead)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
