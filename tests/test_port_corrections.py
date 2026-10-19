"""test_port_corrections.py — the gate on docs/project/port_corrections.tsv and port_corrections_map.tsv (#4): every
part's source is where the table says, in the original at the tables' pin, and every row of the tenants' manifests is
mapped to a part or said not to be one.

  C1 FOUND    each row's `source` (path:line) exists in the export, and its `anchor` (a verbatim fragment) is on that
              line or within two lines of it (a quote's line can wrap)
  C2 FORM     every row has the nine columns, a known tenant, class and status, and (tenant, n) is unique
  C3 COVERED  the map holds every row of the tenants' manifests (TENANT_MANIFESTS) that phase 0's tables carry, once,
              and nothing else; its tenant is the manifest's; its role is known; a `fix` names a part of that
              tenant's catalogue (one or more, comma-separated) and no other role names one
  C4 ANCHORED each map row's anchor is within two lines of its `line`, and that line lies in the row's reach: from the
              start of the nearest comment block above the row's header to the row's last line

CONTROLS ([VSR-22]):
  line-moved      the first row's line moved 200 lines on: C1 must fail
  anchor-altered  the first row's anchor given one character it does not have: C1 must fail
  row-dropped     the map's first row removed: C3 must fail
  part-unknown    the map's first `fix` row pointed at a part its tenant does not have: C3 must fail
  anchor-outside  the map's first row's line moved 200 lines on: C4 must fail
A normal run runs each control and reports it FIRED or DEAD; `--control <name>` runs the gate on the perturbed copy,
where it must FAIL.

Usage: python3 tests/test_port_corrections.py [--export DIR] [--control NAME]
"""
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import runlog  # noqa: E402
from test_phase0_tables import generated, read_table  # noqa: E402

TABLE = os.path.join(ROOT, "docs", "project", "port_corrections.tsv")
MAP = os.path.join(ROOT, "docs", "project", "port_corrections_map.tsv")
TABLES = os.path.join(ROOT, "docs", "project", "tables")
TENANTS = ("donovan", "huitzil", "pyron")
CLASSES = ("reach", "reloc", "crypt-data", "short-table", "dead-row", "engine-diff", "sound", "gfx", "merge", "tool",
           "open", "retracted")
STATUSES = ("fixed", "retracted", "open", "unclear")
ROLES = ("fix", "frame", "unclear")
TENANT_MANIFESTS = {t: (t + ".toml", "moves_%s.toml" % t, "reconciliation_%s.toml" % t) for t in TENANTS}
CONTROLS = {"line-moved": {"C1"}, "anchor-altered": {"C1"}, "row-dropped": {"C3"}, "part-unknown": {"C3"},
            "anchor-outside": {"C4"}}


def rows_of(path):
    out = []
    for line in open(path):
        if line.startswith("#") or line.startswith("tenant\t"):
            continue
        out.append(line.rstrip("\n").split("\t"))
    return out


def perturb(rows, mapped, name):
    rows, mapped = [list(r) for r in rows], [list(r) for r in mapped]
    path, line = rows[0][7].rsplit(":", 1)
    if name == "line-moved":
        rows[0][7] = "%s:%d" % (path, int(line) + 200)
    elif name == "anchor-altered":
        rows[0][8] = rows[0][8] + "~"
    elif name == "row-dropped":
        mapped = mapped[1:]
    elif name == "part-unknown":
        first = next(r for r in mapped if r[4] == "fix")
        first[5] = "999"
    else:
        mapped[0][6] = str(int(mapped[0][6]) + 200)
    return rows, mapped


def reaches(export):
    """Each tenant manifest row phase 0's tables carry, (manifest, kind, row) -> (first line, last line) of its reach:
    from the start of the nearest comment block above its header to its last value's line."""
    lines = defaultdict(list)
    for name in generated(TABLES):
        for r in read_table(os.path.join(TABLES, name))[2]:
            if len(r) < 6 or r[1].startswith("(") or r[2].startswith("(") or not r[5].isdigit():
                continue
            if any(r[0] in names for names in TENANT_MANIFESTS.values()):
                lines[r[:3]].append(int(r[5]))
    out, texts = {}, {}
    for key, ls in lines.items():
        if key[0] not in texts:
            texts[key[0]] = open(os.path.join(export, "build", "manifest", key[0])).read().split("\n")
        text = texts[key[0]]
        head = min(ls)
        while head > 1 and not re.match(r"\s*\[\[?" + re.escape(key[1]) + r"[\].]", text[head - 1]):
            head -= 1
        top = head - 1
        while top > 0 and not text[top - 1].lstrip().startswith("#"):
            top -= 1
        while top > 1 and text[top - 2].lstrip().startswith("#"):
            top -= 1
        out[key] = (top, max(ls))
    return out, texts


def map_checks(rows, mapped, export):
    failed, figures = set(), []
    parts = {(r[0], r[1]) for r in rows if len(r) == 9}
    reach, texts = reaches(export)
    seen = Counter(tuple(r[1:4]) for r in mapped if len(r) == 8)
    bad = [" ".join(r[1:4]) for r in mapped if len(r) != 8 or tuple(r[1:4]) not in reach
           or r[1] not in TENANT_MANIFESTS.get(r[0], ()) or r[4] not in ROLES or (r[4] == "fix") != (r[5] != "-")
           or (r[5] != "-" and any((r[0], n) not in parts for n in r[5].split(","))) or not r[6].isdigit()]
    missing = [k for k in reach if k not in seen]
    dup = [k for k, c in seen.items() if c > 1]
    roles = Counter((r[0], r[4]) for r in mapped if len(r) == 8)
    used = {(r[0], n) for r in mapped if len(r) == 8 and r[4] == "fix" for n in r[5].split(",")}
    figures.append("C3 manifest rows %d, map rows %d, missing %d, duplicate %d, malformed %d%s" % (
        len(reach), len(mapped), len(missing), len(dup), len(bad), (": " + "; ".join(bad[:3])) if bad else ""))
    for t in TENANTS:
        figures.append("C3 %s: fix %d, frame %d, unclear %d; parts mapped %d of %d" % (
            t, roles[(t, "fix")], roles[(t, "frame")], roles[(t, "unclear")], len({p for p in used if p[0] == t}),
            len({p for p in parts if p[0] == t})))
    if bad or missing or dup:
        failed.add("C3")
    lost = []
    for r in mapped:
        if len(r) != 8 or tuple(r[1:4]) not in reach or not r[6].isdigit():
            continue
        top, end = reach[tuple(r[1:4])]
        n, text = int(r[6]), texts[r[1]]
        if not top <= n <= end or not any(r[7] in t for t in text[max(0, n - 3):n + 2]):
            lost.append("%s %s %s: %d" % tuple(r[1:4] + [n]))
    figures.append("C4 anchors outside their row's reach or not at their line %d%s" % (
        len(lost), (": " + "; ".join(lost[:3])) if lost else ""))
    if lost:
        failed.add("C4")
    return failed, figures


def checks(rows, mapped, export):
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
    more, extra = map_checks(rows, mapped, export)
    return failed | more, figures + extra


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
    rows, mapped = rows_of(TABLE), rows_of(MAP)
    print("tables: %s, %s\nexport: %s" % (TABLE, MAP, export))
    fired, dead = [], []
    if control is not None:
        if control not in CONTROLS:
            print("REFUSED: no declared control named %r (declared: %s)" % (control, ", ".join(CONTROLS)))
            run.record("REFUSED", declared=list(CONTROLS))
            sys.exit(3)
        print("MODE: control %s (the gate must FAIL)" % control)
        failed, figures = checks(*perturb(rows, mapped, control), export)
    else:
        failed, figures = checks(rows, mapped, export)
        for name, want in CONTROLS.items():
            got, _ = checks(*perturb(rows, mapped, name), export)
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
