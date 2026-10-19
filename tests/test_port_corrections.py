"""test_port_corrections.py — the gate on docs/project/port_corrections.tsv (#4): every part's source is where the
table says, in the original at the tables' pin.

  C1 FOUND    each row's `source` (path:line) exists in the export, and its `anchor` (a verbatim fragment) is on that
              line or within two lines of it (a quote's line can wrap)
  C2 FORM     every row has the nine columns, a known tenant, class and status, and (tenant, n) is unique

CONTROLS ([VSR-22]):
  line-moved      the first row's line moved 200 lines on: C1 must fail
  anchor-altered  the first row's anchor given one character it does not have: C1 must fail
A normal run runs each control and reports it FIRED or DEAD; `--control <name>` runs the gate on the perturbed copy,
where it must FAIL.

Usage: python3 tests/test_port_corrections.py [--export DIR] [--control NAME]
"""
import os
import sys
from collections import Counter

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import runlog  # noqa: E402
from test_phase0_tables import read_table  # noqa: E402

TABLE = os.path.join(ROOT, "docs", "project", "port_corrections.tsv")
TENANTS = ("donovan", "huitzil", "pyron")
CLASSES = ("reach", "reloc", "crypt-data", "short-table", "dead-row", "engine-diff", "sound", "gfx", "merge", "tool",
           "open", "retracted")
STATUSES = ("fixed", "retracted", "open", "unclear")
CONTROLS = {"line-moved": {"C1"}, "anchor-altered": {"C1"}}


def rows_of(path):
    out = []
    for line in open(path):
        if line.startswith("#") or line.startswith("tenant\t"):
            continue
        out.append(line.rstrip("\n").split("\t"))
    return out


def perturb(rows, name):
    rows = [list(r) for r in rows]
    path, line = rows[0][7].rsplit(":", 1)
    if name == "line-moved":
        rows[0][7] = "%s:%d" % (path, int(line) + 200)
    else:
        rows[0][8] = rows[0][8] + "~"
    return rows


def checks(rows, export):
    failed, figures = set(), []
    lost, cache = [], {}
    for r in rows:
        if len(r) != 9:
            continue
        path, line = r[7].rsplit(":", 1)
        full = os.path.join(export, path)
        if full not in cache:
            cache[full] = open(full, errors="replace").read().splitlines() if os.path.exists(full) else None
        text = cache[full]
        n = int(line)
        near = text[max(0, n - 3):n + 2] if text else []
        if not any(r[8] in t for t in near):
            lost.append("%s %s: %s" % (r[0], r[1], r[7]))
    figures.append("C1 rows %d, sources %d, anchors not at their line %d%s" % (
        len(rows), len(cache), len(lost), (": " + "; ".join(lost[:3])) if lost else ""))
    if lost:
        failed.add("C1")
    bad = [" ".join(r[:2]) for r in rows if len(r) != 9 or r[0] not in TENANTS or r[2] not in CLASSES
           or r[6] not in STATUSES]
    dup = [k for k, c in Counter(tuple(r[:2]) for r in rows).items() if c > 1]
    per = Counter(r[0] for r in rows)
    figures.append("C2 per tenant %s, by status %s, malformed %d, duplicate ids %d" % (
        dict(sorted(per.items())), dict(sorted(Counter(r[6] for r in rows if len(r) == 9).items())), len(bad),
        len(dup)))
    if bad or dup:
        failed.add("C2")
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
    pin = read_table(os.path.join(ROOT, "docs", "project", "tables", "roster.tsv"))[0]
    export = export or os.path.join(ROOT, "build", "export_" + pin)
    run = runlog.Run("test_port_corrections", "control:" + control if control else "normal")
    rows = rows_of(TABLE)
    print("table: %s\nexport: %s" % (TABLE, export))
    fired, dead = [], []
    if control is not None:
        if control not in CONTROLS:
            print("REFUSED: no declared control named %r (declared: %s)" % (control, ", ".join(CONTROLS)))
            run.record("REFUSED", declared=list(CONTROLS))
            sys.exit(3)
        print("MODE: control %s (the gate must FAIL)" % control)
        failed, figures = checks(perturb(rows, control), export)
    else:
        failed, figures = checks(rows, export)
        for name, want in CONTROLS.items():
            got, _ = checks(perturb(rows, name), export)
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
    run.record("PASS" if not failed else "FAIL", failed=failed, cases=len(rows), declared=list(CONTROLS),
               fired=fired, dead=dead)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
