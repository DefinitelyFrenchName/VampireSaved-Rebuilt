"""test_phase0_tables.py — the gate on phase 0's tables (SPEC.md §3; docs/project/tables/README.md).

Checks every generated table under docs/project/tables/ (the gameplay column's four, the fact column's facts/*.tsv)
against an export of the original at their pin:
  G1 CURRENT  the tables regenerate byte-for-byte from the export (tools/extract_tables.py), and no other generated
              table exists
  G2 PINNED   the export's manifests have the SHA-1s the tables' headers name
  G3 COVERED  per column, the original census's records and the table rows are the same multiset of (manifest, kind,
              key, value) — a census value that is the first line of a TOML value spanning lines matches the whole
              literal it begins, and a held value matches its `HELD:sha1=` cell — and (manifest, kind, row, key) is
              unique across the tables
  G4 TRUE     every cell equals an independent parse of its manifest at (kind, row, key) (tomli / json), and a TOML
              row's line in the manifest reads `key = value` when the value sits on one line
  G5 HELD     every value of facts/held.tsv is in its table only as `HELD:sha1=<its SHA-1>`, the SHA-1 is the
              manifest's value's, and no cell anywhere carries a held value in the clear

CONTROLS ([VSR-22], docs/project/must_fire_contract.md), each a perturbed copy built under build/tmp/:
  perturbed-value     the first `true` of variant_selection made `false`: G1, G3, G4 must fail
  dropped-row         the last row of roster removed: G1, G3 must fail
  perturbed-manifest  one `only_variant_slot` flipped in a copy of the export's donovan.toml: G1, G2, G3, G4 must fail
  held-leak           the first HELD cell of facts/site_thunk replaced by the manifest's value in the clear: G1, G3,
                      G5 must fail
  perturbed-pointer-fact  the first row of facts/json_version_font under the `.` glyph (`/glyphs/./n`, the one key
                      a dotted path could not address) given another glyph row's value: G1, G3, G4 must fail
A normal run runs each control and reports it FIRED or DEAD; `--control <name>` makes the perturbed copy the gate's
input and the gate must reach its own FAIL.

The export: `--export DIR`, or build/export_<pin>, made by tools/export_original.py from the original's checkout
($ORIGINAL, default ~/Developer/Vampire_Saved/VampireSaved), which is only read.
Usage: python3 tests/test_phase0_tables.py [--export DIR] [--control NAME]
"""
import filecmp
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import phase0lib  # noqa: E402
import runlog  # noqa: E402
import tomli  # noqa: E402

TABLES = os.path.join(ROOT, "docs", "project", "tables")
TMP = os.path.join(ROOT, "build", "tmp", "test_phase0_tables")
CONTROLS = {
    "perturbed-value": {"G1", "G3", "G4"},
    "dropped-row": {"G1", "G3"},
    "perturbed-manifest": {"G1", "G2", "G3", "G4"},
    "held-leak": {"G1", "G3", "G5"},
    "perturbed-pointer-fact": {"G1", "G3", "G4"},
}


def generated(tables_dir):
    """Every generated table, relative to tables_dir (held.tsv is hand-written and not one of them)."""
    out = []
    for p in sorted(glob.glob(os.path.join(tables_dir, "*.tsv")) + glob.glob(os.path.join(tables_dir, "facts",
                                                                                           "*.tsv"))):
        if os.path.basename(p) != "held.tsv":
            out.append(os.path.relpath(p, tables_dir))
    return out


def read_table(path):
    pin, sha, rows = None, {}, []
    for line in open(path):
        line = line.rstrip("\n")
        if line.startswith("# GENERATED"):
            pin = re.search(r"original at (\S+);", line).group(1)
        elif line.startswith("# read:"):
            for part in line[len("# read:"):].split(","):
                name, h = part.split()
                sha[name] = h
        elif not line.startswith("#") and not line.startswith("manifest\t"):
            rows.append(tuple(line.split("\t")))
    return pin, sha, rows


def literal(v, manifest):
    """A table cell parsed as what it is: a TOML literal, or a JSON value for a JSON manifest."""
    if manifest.endswith(".json"):
        return json.loads(v)
    return tomli.loads("v = " + v)["v"]


def checks(tables_dir, export):
    failed, figures = set(), []
    names = generated(tables_dir)
    pin, sha, rows = None, {}, []
    for n in names:
        p, s, r = read_table(os.path.join(tables_dir, n))
        pin = pin or p
        sha.update(s)
        column = "fact" if n.startswith("facts/") else "gameplay"
        rows += [(column,) + x for x in r]
    held = phase0lib.read_held(os.path.join(tables_dir, "facts", "held.tsv"))
    figures.append("rows %d in %d tables, pin %s, held %d" % (len(rows), len(names), pin, len(held)))
    # G1: regenerate and compare, both ways
    regen = os.path.join(TMP, "regen")
    shutil.rmtree(regen, ignore_errors=True)
    os.makedirs(os.path.join(regen, "facts"))
    shutil.copy(os.path.join(tables_dir, "facts", "held.tsv"), os.path.join(regen, "facts", "held.tsv"))
    env = dict(os.environ, PHASE0_HELD=os.path.join(tables_dir, "facts", "held.tsv"))
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "extract_tables.py"), export, pin, regen],
                       capture_output=True, text=True, env=env)
    regen_names = generated(regen)
    differ = [n for n in names if n not in regen_names or not filecmp.cmp(os.path.join(regen, n),
                                                                          os.path.join(tables_dir, n), shallow=False)]
    extra = [n for n in regen_names if n not in names]
    figures.append("G1 regenerated %d tables, differing %d%s, missing %d%s" % (
        len(regen_names), len(differ), (" (" + ", ".join(differ[:3]) + ")") if differ else "", len(extra),
        "" if p.returncode == 0 else "; extractor failed: " + (p.stdout + p.stderr).strip()[-200:]))
    if p.returncode or differ or extra:
        failed.add("G1")
    # G2: the export is the content the headers name
    bad = [m for m, h in sha.items()
           if not hashlib.sha1(open(os.path.join(export, "build", "manifest", m), "rb").read()).hexdigest()
           .startswith(h)]
    figures.append("G2 manifests %d, SHA-1 mismatches %s" % (len(sha), bad or "none"))
    if bad:
        failed.add("G2")
    # G3: per column, the census and the rows are the same multiset; ids unique across the tables
    a = phase0lib.load_census(export)
    recs, _ = a.census(Path(export))
    held_sha = set(held.values())
    g3_bad = False
    for column in ("gameplay", "fact"):
        census = Counter()
        for r in recs:
            if r.column != column:
                continue
            v = r.value
            if phase0lib.sha1(v) in held_sha:
                v = "HELD:sha1=" + phase0lib.sha1(v)
            census[(r.file[len("build/manifest/"):], r.kind, r.key, v)] += 1
        tabled = Counter()
        for c, m, k, _row, key, v, *_ in rows:
            if c == column:
                # the census keeps only the first line, `[`, of a TOML value spanning lines; the table keeps it whole
                if (not m.endswith(".json") and v.startswith("[") and census.get((m, k, key, "["))
                        and not census.get((m, k, key, v))):
                    v = "["
                tabled[(m, k, key, v)] += 1
        only_c, only_t = sum((census - tabled).values()), sum((tabled - census).values())
        figures.append("G3 %-8s census %d, tabled %d, only-in-census %d, only-in-tables %d" % (
            column, sum(census.values()), sum(tabled.values()), only_c, only_t))
        g3_bad = g3_bad or only_c or only_t
    dup = [k for k, c in Counter(r[1:5] for r in rows).items() if c > 1]
    figures.append("G3 duplicate ids %d%s" % (len(dup), (": " + str(dup[0])) if dup else ""))
    if g3_bad or dup:
        failed.add("G3")
    # G4: every cell equals an independent parse, and a one-line value's line says so
    wrong, checked = [], 0
    for _c, m, k, row, key, v, line, *_ in rows:
        if v.startswith("HELD:sha1="):
            continue
        checked += 1
        try:
            got = phase0lib.semantic(export, m, k, row, key)
            ok = got == literal(v, m)
            if ok and line != "-":
                text = Path(export, "build", "manifest", m).read_text().splitlines()[int(line) - 1]
                one = re.match(r"^\s*%s\s*=\s*(.*?)\s*(#.*)?$" % re.escape(key), text.split("#")[0] + "#")
                spans = one and phase0lib.partial(one.group(1).rstrip(","))
                ok = one is not None and (spans or one.group(1).rstrip(",").strip() == v)
        except (KeyError, IndexError, StopIteration, ValueError, TypeError) as exc:
            ok, got = False, "error %r" % exc
        if not ok:
            wrong.append("%s %s %s.%s table %s manifest %r" % (m, k, row, key, v[:40], str(got)[:40]))
    figures.append("G4 cells checked %d, wrong %d%s" % (checked, len(wrong), (": " + wrong[0]) if wrong else ""))
    if wrong:
        failed.add("G4")
    # G5: held values are only their hashes, and the hash is the manifest's value's
    cells = {(m, k, row, key): v for _c, m, k, row, key, v, *_ in rows}
    leaks, mism = [], []
    for ident, h in held.items():
        if cells.get(ident) != "HELD:sha1=" + h:
            mism.append("%s cell is %s" % (".".join(ident[1:]), str(cells.get(ident))[:30]))
        else:
            src = Path(export, "build", "manifest", ident[0]).read_text()
            if not any(phase0lib.sha1(m.group(1)) == h for m in re.finditer(r'(?m)^\s*%s\s*=\s*("[^"]*")' %
                                                                            re.escape(ident[3]), src)):
                mism.append("%s: no manifest value has SHA-1 %s" % (".".join(ident[1:]), h[:12]))
    for ident, v in cells.items():
        if not v.startswith("HELD:") and phase0lib.sha1(v) in set(held.values()):
            leaks.append(".".join(ident))
    figures.append("G5 held %d, cells not their hash %d, values in the clear %d%s" % (
        len(held), len(mism), len(leaks), (": " + (mism + leaks)[0]) if mism or leaks else ""))
    if mism or leaks:
        failed.add("G5")
    return failed, figures


def perturbed(name, export):
    """The control's perturbation, written once: (tables dir, export) with one thing changed, under build/tmp/."""
    base = os.path.join(TMP, "control_" + name)
    shutil.rmtree(base, ignore_errors=True)
    tables = os.path.join(base, "tables")
    shutil.copytree(TABLES, tables, ignore=shutil.ignore_patterns("*.md"))

    def edit(rel, fn):
        p = os.path.join(tables, rel)
        lines = open(p).readlines()
        open(p, "w").writelines(fn(lines))

    if name == "perturbed-value":
        def flip(lines):
            i = next(i for i, l in enumerate(lines) if "\ttrue\t" in l)
            lines[i] = lines[i].replace("\ttrue\t", "\tfalse\t", 1)
            return lines
        edit("variant_selection.tsv", flip)
        return tables, export
    if name == "perturbed-pointer-fact":
        def swap(lines):
            i = next(i for i, l in enumerate(lines) if "\t/glyphs/./" in l)
            f = lines[i].split("\t")
            f[4] = json.dumps("#####") if f[4] != json.dumps("#####") else json.dumps(".....")
            lines[i] = "\t".join(f)
            return lines
        edit("facts/json_version_font.tsv", swap)
        return tables, export
    if name == "dropped-row":
        edit("roster.tsv", lambda lines: lines[:-1])
        return tables, export
    if name == "held-leak":
        def leak(lines):
            i = next(i for i, l in enumerate(lines) if "\tHELD:sha1=" in l)
            f = lines[i].split("\t")
            text = Path(export, "build", "manifest", f[0]).read_text()
            f[4] = next(m.group(1) for m in re.finditer(r'(?m)^\s*thunk_hex\s*=\s*("[^"]*")', text)
                        if "HELD:sha1=" + phase0lib.sha1(m.group(1)) == f[4])
            lines[i] = "\t".join(f)
            return lines
        edit("facts/site_thunk.tsv", leak)
        return tables, export
    if name == "perturbed-manifest":
        copy = os.path.join(base, "export")
        for d in ("build/manifest", "tools", "docs"):
            shutil.copytree(os.path.join(export, d), os.path.join(copy, d))
        p = os.path.join(copy, "build", "manifest", "donovan.toml")
        text = open(p).read()
        open(p, "w").write(re.sub(r"(?m)^(only_variant_slot\s*=\s*)true", r"\1false", text, count=1))
        return tables, copy
    raise KeyError(name)


def ensure_export(pin):
    path = os.path.join(ROOT, "build", "export_" + pin)
    if not os.path.isdir(path):
        original = os.environ.get("ORIGINAL", os.path.expanduser("~/Developer/Vampire_Saved/VampireSaved"))
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "export_original.py"), original, pin, path],
                       check=True)
    return path


def main():
    args = sys.argv[1:]
    run, fired, dead = runlog.Run("test_phase0_tables", ("control:" + args[args.index("--control") + 1])
                                  if "--control" in args[:-1] else "normal"), [], []
    export = None
    if args[:1] == ["--export"]:
        export, args = os.path.realpath(args[1]), args[2:]
    pin = read_table(os.path.join(TABLES, "roster.tsv"))[0]
    export = export or ensure_export(pin)
    print("tables: %s\nexport: %s" % (TABLES, export))
    if args[:1] == ["--control"]:
        name = args[1] if len(args) > 1 else ""
        if name not in CONTROLS:
            print("REFUSED: no declared control named %r (declared: %s)" % (name, ", ".join(CONTROLS)))
            run.record("REFUSED", declared=list(CONTROLS))
            sys.exit(3)
        print("MODE: control %s (the perturbed copy is the gate's input; the gate must FAIL)" % name)
        failed, figures = checks(*perturbed(name, export))
    else:
        failed, figures = checks(TABLES, export)
        for name in CONTROLS:
            got, _ = checks(*perturbed(name, export))
            if got == CONTROLS[name]:
                print("CONTROL FIRED: %s (failed %s, exactly as declared)" % (name, ",".join(sorted(got))))
                fired.append(name)
            else:
                dead.append(name)
                print("CONTROL DEAD: %s (failed %s, declared %s)" % (name, ",".join(sorted(got)) or "nothing",
                                                                     ",".join(sorted(CONTROLS[name]))))
                failed.add("control:" + name)
    for f in figures:
        print(f)
    print("VERDICT: %s%s" % ("PASS" if not failed else "FAIL", "" if not failed else " (" + ", ".join(sorted(failed))
                                                                + ")"))
    rows = re.match(r"rows (\d+)", figures[0]) if figures else None
    run.record("PASS" if not failed else "FAIL", failed=failed, cases=int(rows.group(1)) if rows else None,
               declared=list(CONTROLS), fired=fired, dead=dead)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
