"""test_raw_id_census.py — the gate on docs/project/tables/raw_id_census.tsv (#6): every table vsavj reads by the raw
character id, its vs2 twin and the newcomers' rows (tools/raw_id_census.py; docs/project/tables/README.md "The raw-id
census"). Every expectation is anchored on the reference dumps, and the anchor row on a measurement in play.

  C1 TABLE    the committed inventory equals the one read now from vsavj and vsav2 (every row, every column), and
              its header names the dumps read
  C2 ANCHOR   the doll-hop table is in it as measured in play (R-005, R-006): vsavj PRG:0x0BE3FA, rows of 0x20 read
              in the data view, twin vs2 PRG:0x0D8598 paired by the bank's shift, and for all three newcomers vs2's
              row differing, vsavj's row a shell copy and vs2's row its own ([VSR-187]: the static reading is
              licensed by reproducing the one table measured both ways)
  C3 SCAN     each game's id loads are found (both counts above zero) and every vsavj table the scan reaches is
              either paired or listed as unpaired

CONTROLS ([VSR-22]):
  table-edited  the committed inventory with the anchor's `shell` changed: C1 and C2 must fail
  blind-scan    the id loads looked for at +0x383: C1, C2 and C3 must fail
  shift-off     the bank's vs2 shift off by 0x80: C1 and C2 must fail
A normal run runs each control and reports it FIRED or DEAD; `--control <name>` runs the gate on the perturbed
input, where it must FAIL.

Usage: python3 tests/test_raw_id_census.py [--export DIR] [--roms DIR] [--control NAME]
"""
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import runlog  # noqa: E402
from raw_id_census import COLUMNS, OUT, PIN, load, measure  # noqa: E402
from test_phase0_tables import read_table  # noqa: E402

CONTROLS = {"table-edited": {"C1", "C2"}, "blind-scan": {"C1", "C2", "C3"}, "shift-off": {"C1", "C2"}}
ANCHOR = {"vsavj": "PRG:0x0BE3FA", "row": "0x20", "view": "data", "vsav2": "PRG:0x0D8598", "paired": "bank",
          "kind": "value", "vs2_differs": "dhp", "shell": "dhp", "vs2_own": "dhp"}


def committed(perturb=None):
    pin, sha, rows = read_table(OUT)
    out = [dict(zip(COLUMNS, r)) for r in rows[1:]] if rows and rows[0] == COLUMNS else []
    if perturb == "table-edited":
        out = [dict(r, shell="---") if r["vsavj"] == ANCHOR["vsavj"] else r for r in out]
    return pin, sha, out


def checks(inp, res, table, anchor_in):
    failed, figures = set(), []
    pin, sha, rows = table
    zips = {os.path.basename(p): h[:12] for p, h in inp["read"] if p.endswith(".zip")}
    head = {os.path.basename(p): h for p, h in sha.items() if p.endswith(".zip")}
    same = sum(a == b for a, b in zip(rows, res["tables"]))
    head_ok = pin == PIN and len(zips) == 2 and head == zips
    figures.append("C1 committed rows %d, measured %d, equal %d; header pin %s, ROM SHA-1s %s" % (
        len(rows), len(res["tables"]), same, pin, "match" if head_ok else "DIFFER"))
    if not res["tables"] or len(rows) != len(res["tables"]) or same != len(rows) or not head_ok:
        failed.add("C1")
    got = [r for r in anchor_in if r["vsavj"] == ANCHOR["vsavj"] and r["row"] == ANCHOR["row"]]
    ok = len(got) == 1 and all(got[0][k] == v for k, v in ANCHOR.items())
    figures.append("C2 anchor %s rows of %s: %s" % (ANCHOR["vsavj"], ANCHOR["row"], (
        ", ".join("%s %s" % (k, got[0][k]) for k in ANCHOR if k not in ("vsavj", "row"))) if got else "ABSENT"))
    if not ok:
        failed.add("C2")
    c = res["counts"]
    figures.append("C3 id loads vsavj %d, vsav2 %d; vsavj loads reaching an indexed access %d, no base %d; tables "
                   "paired %d, unpaired %d" % (c["loads_vsavj"], c["loads_vsav2"], c["indexed_vsavj"], c["no_base"],
                                               c["tables"], c["unpaired"]))
    if not c["loads_vsavj"] or not c["loads_vsav2"] or not c["tables"]:
        failed.add("C3")
    return failed, figures


def run_checks(inp, perturb=None):
    res = measure(inp, perturb if perturb in ("blind-scan", "shift-off") else None)[1]
    table = committed(perturb)
    # C2 reads the committed inventory under table-edited, the measured one otherwise
    return checks(inp, res, table, table[2] if perturb == "table-edited" else res["tables"])


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
    run = runlog.Run("test_raw_id_census", "control:" + control if control else "normal")
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
    run.record("PASS" if not failed else "FAIL", failed=failed, cases=len(committed()[2]), declared=list(CONTROLS),
               fired=fired, dead=dead)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
