"""test_phase0_gameplay.py — the gate on phase 0's gameplay tables (SPEC.md §3; docs/project/tables/README.md).

Checks the four tables under docs/project/tables/ (variant_selection, roster, select_wheel, hit_class_mask) against an
export of the original at their pin:
  G1 CURRENT     the tables regenerate byte-for-byte from the export (tools/extract_gameplay_tables.py)
  G2 PINNED      the export's manifests have the SHA-1s the tables' headers name
  G3 COVERED     every record of the original's census `gameplay` column is one table row, and every row is one record
                 (the multisets of (manifest, kind, key, value) are equal; (manifest, kind, row, key) is unique)
  G4 TRUE        every cell equals an independent parse of its manifest at (kind, row, key) (tomli / json), and a TOML
                 row's line in the manifest reads `key = value`

CONTROLS ([VSR-22], docs/project/must_fire_contract.md), each a perturbed copy built under build/tmp/:
  perturbed-value     one table cell changed (the first `true` of variant_selection made `false`): G1, G3 (the value
                      multiset moves) and G4 must fail
  dropped-row         one table row removed (the last row of roster): G1 and G3 must fail
  perturbed-manifest  one gameplay value flipped in a copy of the export's donovan.toml: G1, G2, G3 and G4 must fail
A normal run runs each control and reports it FIRED or DEAD; `--control <name>` makes the perturbed copy the gate's
input and the gate must reach its own FAIL.

The export: `--export DIR`, or build/export_<pin>, made by tools/export_original.py from the original's checkout
($ORIGINAL, default ~/Developer/Vampire_Saved/VampireSaved), which is only read.
Usage: python3 tests/test_phase0_gameplay.py [--export DIR] [--control NAME]
"""
import filecmp
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import phase0lib  # noqa: E402
import tomli  # noqa: E402

TABLES = os.path.join(ROOT, "docs", "project", "tables")
NAMES = ("variant_selection", "roster", "select_wheel", "hit_class_mask")
TMP = os.path.join(ROOT, "build", "tmp", "test_phase0_gameplay")
CONTROLS = {
    "perturbed-value": {"G1", "G3", "G4"},
    "dropped-row": {"G1", "G3"},
    "perturbed-manifest": {"G1", "G2", "G3", "G4"},
}


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
    pin, sha, rows = None, {}, []
    for n in NAMES:
        p, s, r = read_table(os.path.join(tables_dir, n + ".tsv"))
        pin, sha, rows = pin or p, s or sha, rows + [(n,) + x for x in r]
    figures.append("rows %d in %d tables, pin %s" % (len(rows), len(NAMES), pin))
    # G1: regenerate and compare
    regen = os.path.join(TMP, "regen")
    shutil.rmtree(regen, ignore_errors=True)
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "extract_gameplay_tables.py"), export, pin, regen],
                       capture_output=True, text=True)
    same = p.returncode == 0 and all(filecmp.cmp(os.path.join(regen, n + ".tsv"), os.path.join(tables_dir, n + ".tsv"),
                                                 shallow=False) for n in NAMES)
    figures.append("G1 regenerated equal: %s%s" % (same, "" if p.returncode == 0 else " (" + p.stdout.strip()[-200:]
                                                   + p.stderr.strip()[-200:] + ")"))
    if not same:
        failed.add("G1")
    # G2: the export is the content the headers name
    import hashlib
    bad = [m for m, h in sha.items()
           if not hashlib.sha1(open(os.path.join(export, "build", "manifest", m), "rb").read()).hexdigest()
           .startswith(h)]
    figures.append("G2 manifests %d, SHA-1 mismatches %s" % (len(sha), bad or "none"))
    if bad:
        failed.add("G2")
    # G3: the census column and the rows are the same multiset, and rows are unique
    a = phase0lib.load_census(export)
    from pathlib import Path
    recs, _ = a.census(Path(export))
    census = Counter((os.path.basename(r.file), r.kind, r.key, r.value) for r in recs if r.column == "gameplay")
    tabled = Counter((m, k, key, v) for _n, m, k, _row, key, v, *_ in rows)
    dup = [k for k, c in Counter((r[1], r[2], r[3], r[4]) for r in rows).items() if c > 1]
    figures.append("G3 census gameplay %d, tabled %d, only-in-census %d, only-in-tables %d, duplicate ids %d" % (
        sum(census.values()), sum(tabled.values()), sum((census - tabled).values()), sum((tabled - census).values()),
        len(dup)))
    if census != tabled or dup:
        failed.add("G3")
    # G4: every cell equals an independent parse, and its line says so
    wrong = []
    for _n, m, k, row, key, v, line, *_ in rows:
        try:
            parsed = phase0lib.semantic_value(export, m, k, row, key)
            ok = literal(parsed, m) == literal(v, m)
            if ok and line != "-":
                text = open(os.path.join(export, "build", "manifest", m)).read().splitlines()[int(line) - 1]
                ok = re.match(r"^\s*%s\s*=\s*%s\s*(#.*)?$" % (re.escape(key), re.escape(v)), text) is not None
        except (KeyError, IndexError, StopIteration, ValueError) as exc:
            ok, parsed = False, "error %r" % exc
        if not ok:
            wrong.append("%s %s %s.%s table %s manifest %s" % (m, k, row, key, v, parsed))
    figures.append("G4 cells checked %d, wrong %d%s" % (len(rows), len(wrong), (": " + wrong[0]) if wrong else ""))
    if wrong:
        failed.add("G4")
    return failed, figures


def perturbed(name, export):
    """The control's perturbation, written once: (tables dir, export) with one thing changed, under build/tmp/."""
    base = os.path.join(TMP, "control_" + name)
    shutil.rmtree(base, ignore_errors=True)
    tables = os.path.join(base, "tables")
    os.makedirs(tables)
    for n in NAMES:
        shutil.copy(os.path.join(TABLES, n + ".tsv"), tables)
    if name == "perturbed-value":
        p = os.path.join(tables, "variant_selection.tsv")
        lines = open(p).readlines()
        i = next(i for i, l in enumerate(lines) if "\ttrue\t" in l)
        lines[i] = lines[i].replace("\ttrue\t", "\tfalse\t", 1)
        open(p, "w").writelines(lines)
        return tables, export
    if name == "dropped-row":
        p = os.path.join(tables, "roster.tsv")
        lines = open(p).readlines()
        open(p, "w").writelines(lines[:-1])
        return tables, export
    if name == "perturbed-manifest":
        copy = os.path.join(base, "export")
        os.makedirs(os.path.join(copy, "build"))
        shutil.copytree(os.path.join(export, "build", "manifest"), os.path.join(copy, "build", "manifest"))
        shutil.copytree(os.path.join(export, "tools"), os.path.join(copy, "tools"))
        for extra in ("docs",):
            shutil.copytree(os.path.join(export, extra), os.path.join(copy, extra))
        p = os.path.join(copy, "build", "manifest", "donovan.toml")
        text = open(p).read()
        text = re.sub(r"(?m)^(only_variant_slot\s*=\s*)true", r"\1false", text, count=1)
        open(p, "w").write(text)
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
            sys.exit(3)
        print("MODE: control %s (the perturbed copy is the gate's input; the gate must FAIL)" % name)
        failed, figures = checks(*perturbed(name, export))
    else:
        failed, figures = checks(TABLES, export)
        for name in CONTROLS:
            got, _ = checks(*perturbed(name, export))
            if got == CONTROLS[name]:
                print("CONTROL FIRED: %s (failed %s, exactly as declared)" % (name, ",".join(sorted(got))))
            else:
                print("CONTROL DEAD: %s (failed %s, declared %s)" % (name, ",".join(sorted(got)) or "nothing",
                                                                     ",".join(sorted(CONTROLS[name]))))
                failed.add("control:" + name)
    for f in figures:
        print(f)
    print("VERDICT: %s%s" % ("PASS" if not failed else "FAIL", "" if not failed else " (" + ", ".join(sorted(failed))
                                                                + ")"))
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
