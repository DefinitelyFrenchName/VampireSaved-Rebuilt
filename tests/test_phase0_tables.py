"""test_phase0_tables.py — the gate on phase 0's tables (SPEC.md §3; docs/project/tables/README.md).

Checks every generated table under docs/project/tables/ (the gameplay column's four, the fact column's facts/*.tsv,
the code column's code/*.tsv, the values the census does not count under uncounted/, the manifests' shape in
layout/forms.tsv) against an export of the original at their pin:
  G1 CURRENT  the tables regenerate byte-for-byte from the export (tools/extract_tables.py), and no other generated
              table exists
  G2 PINNED   the export's manifests and generators have the SHA-1s the tables' headers name
  G3 COVERED  per column, the original census's records and the table rows are the same multiset of (manifest, kind,
              key, value) — a census value that is the first line of a TOML value spanning lines matches the whole
              literal it begins, a census value that is a generator value's first line (a lone bracket) or its
              60-character cut matches the whole value it begins, and a held value matches its `HELD:sha1=` cell —
              and (manifest, kind, row, key) is unique across the tables; code/uncounted is not the census's
              (G6 holds it)
  G4 TRUE     every cell equals an independent parse of its manifest at (kind, row, key) (tomli / json), and a TOML
              row's line in the manifest reads `key = value` when the value sits on one line; a code cell has the
              token stream of its generator's value (comments aside: hex stays hex), evaluates equal to it, and its
              line is the assignment's; a one-line value's line is `key = <the cell>` and then only a comment
              (a string may hold a `#`)
  G5 HELD     every value of facts/held.tsv is in its table only as `HELD:sha1=<its SHA-1>`, the SHA-1 is the
              manifest's value's, and no cell anywhere carries a held value in the clear
  G6 COMPLETE the code tables name every public module-level constant (`[A-Z][A-Z0-9_]*`, bound by any assignment
              form) of the census's generators, by an independent AST walk, and code/uncounted holds exactly those
              the census has no record of
  G7 WHOLE    the gameplay, fact and uncounted tables hold every value of every canonical manifest exactly once,
              by an independent walk of each manifest's parse (TOML: every key of every row; JSON: every scalar,
              and every `_` key whole)
  G8 RENDERED tools/render_manifests.py renders every canonical manifest from the tables, and each parses equal to
              the original's (tomli / json, key order included), a held value only as the placeholder of its
              SHA-1; the original's own parser (`_minitoml`, the subset parser on this host) accepts exactly the
              same manifests, and parses each it accepts equal

CONTROLS ([VSR-22], docs/project/must_fire_contract.md), each a perturbed copy built under build/tmp/:
  perturbed-value     the first `true` of variant_selection made `false`: G1, G3, G4, G8 must fail
  dropped-row         the last row of roster removed: G1, G3, G7, G8 must fail (a manifest value is gone too)
  perturbed-manifest  one `only_variant_slot` flipped in a copy of the export's donovan.toml: G1, G2, G3, G4, G8 must fail
  held-leak           the first HELD cell of facts/site_thunk replaced by the manifest's value in the clear: G1, G3,
                      G5 must fail (it renders the same manifest, so G8 passes)
  perturbed-pointer-fact  the first row of facts/json_version_font under the `.` glyph (`/glyphs/./n`, the one key
                      a dotted path could not address) given another glyph row's value: G1, G3, G4, G8 must fail
  perturbed-code      DELTA of code/constants made 0x2751: G1, G3, G4 must fail
  code-hex-as-decimal DELTA of code/constants written 10064, the same number in decimal: G1, G3, G4 must fail
  uncounted-dropped   the last row of code/uncounted removed: G1, G6 must fail
  perturbed-generator DELTA made 0x2751 in a copy of the export's build_gfx_donovan.py: G1, G2, G3, G4 must fail
  note-dropped        the last row of uncounted/note removed: G1, G7, G8 must fail
  perturbed-note      the first `note` of uncounted/note given one more character: G1, G4, G8 must fail
  note-cut-at-hash    the first `notes` value holding a `#` cut there and closed, as a line grammar cutting at the
                      first `#` would read it: G1, G4, G8 must fail
  layout-form-flipped the first `table` form of layout/forms made `array`: G1, G8 must fail
  json-order-swapped  the first JSON dict form with two keys or more given its first two keys swapped: G1, G8
                      must fail
A normal run runs each control and reports it FIRED or DEAD; `--control <name>` makes the perturbed copy the gate's
input and the gate must reach its own FAIL.

The export: `--export DIR`, or build/export_<pin>, made by tools/export_original.py from the original's checkout
($ORIGINAL, default ~/Developer/Vampire_Saved/VampireSaved), which is only read.
Usage: python3 tests/test_phase0_tables.py [--export DIR] [--control NAME]
"""
import filecmp
import glob
import ast
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tokenize
from collections import Counter
from pathlib import Path

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import phase0lib  # noqa: E402
import render_manifests  # noqa: E402
import runlog  # noqa: E402
import tomli  # noqa: E402

TABLES = os.path.join(ROOT, "docs", "project", "tables")
# this run's own scratch, new for every run so concurrent runs never share it ([VSR-143]); made in main()
TMP = None
CONTROLS = {
    "perturbed-value": {"G1", "G3", "G4", "G8"},
    "dropped-row": {"G1", "G3", "G7", "G8"},
    "perturbed-manifest": {"G1", "G2", "G3", "G4", "G8"},
    "held-leak": {"G1", "G3", "G5"},
    "perturbed-pointer-fact": {"G1", "G3", "G4", "G8"},
    "perturbed-code": {"G1", "G3", "G4"},
    "code-hex-as-decimal": {"G1", "G3", "G4"},
    "uncounted-dropped": {"G1", "G6"},
    "perturbed-generator": {"G1", "G2", "G3", "G4"},
    "note-dropped": {"G1", "G7", "G8"},
    "perturbed-note": {"G1", "G4", "G8"},
    "note-cut-at-hash": {"G1", "G4", "G8"},
    "layout-form-flipped": {"G1", "G8"},
    "json-order-swapped": {"G1", "G8"},
}


def generated(tables_dir):
    """Every generated table, relative to tables_dir (held.tsv is hand-written and not one of them; the extraction's
    gameplay tables, generated by tools/extract_regions.py, are tests/test_extraction_tables.py's, doll_hop.tsv,
    generated by tools/doll_hop.py, is tests/test_doll_hop_table.py's, vet_rows.tsv, generated by tools/vet_rows.py,
    is tests/test_vet_rows_table.py's, and raw_id_census.tsv, generated by tools/raw_id_census.py, is
    tests/test_raw_id_census.py's)."""
    out = []
    for p in sorted(glob.glob(os.path.join(tables_dir, "*.tsv")) + glob.glob(os.path.join(tables_dir, "facts", "*.tsv"))
                    + glob.glob(os.path.join(tables_dir, "code", "*.tsv"))
                    + glob.glob(os.path.join(tables_dir, "uncounted", "*.tsv"))
                    + glob.glob(os.path.join(tables_dir, "layout", "*.tsv"))):
        with open(p) as f:
            head = "".join(f.readline() for _ in range(2))
            regions = any("GENERATED by tools/%s" % t in head
                          for t in ("extract_regions.py", "doll_hop.py", "vet_rows.py", "raw_id_census.py"))
        if os.path.basename(p) != "held.tsv" and not regions:
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


def column_of(name):
    for prefix, column in (("facts/", "fact"), ("code/", "code"), ("uncounted/", "uncounted"), ("layout/", "layout")):
        if name.startswith(prefix):
            return column
    return "gameplay"


def manifest_values(path):
    """Every value of one manifest as (kind, row, key) identities, by a walk of its parse written apart from
    phase0lib's. TOML: a top-level scalar is ((top), (top), key); a top-level table is one row of its kind; an array
    of tables is one row per element, named `name`, `name#n` when the name repeats in its kind, `#n` without one.
    JSON: a dict member's row is its parent's pointer and a list element's row is its own, with key `[]`; a `_` key
    is one value whatever it holds."""
    out = []
    if path.endswith(".json"):
        def ptr(parts):
            return "".join("/" + str(x).replace("~", "~0").replace("/", "~1") for x in parts) or "(top)"

        def walk(node, kinds, at):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k.startswith("_") or not isinstance(v, (dict, list)):
                        out.append((".".join(kinds) or "(top)", ptr(at), k))
                    else:
                        walk(v, kinds + [k], at + [k])
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    if isinstance(v, (dict, list)):
                        walk(v, kinds + ["[]"], at + [i])
                    else:
                        out.append((".".join(kinds) or "(top)", ptr(at + [i]), "[]"))
        walk(json.loads(Path(path).read_text()), [], [])
        return out
    doc = tomli.loads(Path(path).read_text())
    for top, v in doc.items():
        if isinstance(v, dict):
            rows = [(v.get("name", "#1"), v)]
        elif isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
            names = Counter(x.get("name") for x in v)
            rows = [(("%s#%d" % (x["name"], i) if names[x["name"]] > 1 else x["name"]) if "name" in x
                     else "#%d" % i, x) for i, x in enumerate(v, 1)]
        else:
            out.append(("(top)", "(top)", top))
            continue
        out += [(top, row, k) for row, x in rows for k in x]
    return out


def code_tokens(text):
    """A Python expression's tokens, comments and line structure aside."""
    skip = (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER)
    return [t.string for t in tokenize.generate_tokens(io.StringIO(text).readline) if t.type not in skip]


def generator_bindings(path):
    """{name: (value source, line)} of every public module-level constant of a generator: each Name a module-level
    assignment stores into (whatever its target's shape), with the matching element of the value. Written apart from
    phase0lib.module_constants, which the extractor uses."""
    text = Path(path).read_text()
    out = {}

    def bind(target, value, line):
        if isinstance(target, ast.Name):
            if re.fullmatch(r"[A-Z][A-Z0-9_]*", target.id):
                out[target.id] = (ast.get_source_segment(text, value) if value is not None else None, line)
        elif isinstance(target, (ast.Tuple, ast.List)):
            elts = value.elts if isinstance(value, (ast.Tuple, ast.List)) else [None] * len(target.elts)
            for t, v in zip(target.elts, elts):
                bind(t, v, line)
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                bind(t, node.value, node.lineno)
        elif isinstance(node, ast.AnnAssign):
            bind(node.target, node.value, node.lineno)
    return out


def code_value(source, names):
    """A generator constant's value: its expression evaluated over the module's other constants (no builtins but
    `range`)."""
    return eval(compile(source, "<cell>", "eval"), {"__builtins__": {"range": range}}, names)


def checks(tables_dir, export):
    failed, figures = set(), []
    names = generated(tables_dir)
    pin, sha, rows = None, {}, []
    for n in names:
        p, s, r = read_table(os.path.join(tables_dir, n))
        pin = pin or p
        sha.update(s)
        rows += [(column_of(n), n) + x for x in r]
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
           if not hashlib.sha1(phase0lib.source_path(export, m).read_bytes()).hexdigest().startswith(h)]
    figures.append("G2 manifests and generators %d, SHA-1 mismatches %s" % (len(sha), bad or "none"))
    if bad:
        failed.add("G2")
    # G3: per column, the census and the rows are the same multiset; ids unique across the tables
    a = phase0lib.load_census(export)
    recs, _ = a.census(Path(export))
    held_sha = set(held.values())
    g3_bad = False
    for column in ("gameplay", "fact", "code"):
        census = Counter()
        for r in recs:
            if r.column != column:
                continue
            v = r.value
            if phase0lib.sha1(v) in held_sha:
                v = "HELD:sha1=" + phase0lib.sha1(v)
            census[(r.file if column == "code" else r.file[len("build/manifest/"):], r.kind, r.key, v)] += 1
        cut = {(m, k, key): v for m, k, key, v in census if column == "code" and (len(v) == 60 or v in "[{(")}
        tabled = Counter()
        for c, t, m, k, _row, key, v, *_ in rows:
            if c == column and t == "code/uncounted.tsv":
                continue
            if c == column and column == "code":
                # the census keeps a generator value's first line, or its first 60 characters; the table keeps it
                if (m, k, key) in cut and v != cut[(m, k, key)] and v.startswith(cut[(m, k, key)]):
                    v = cut[(m, k, key)]
                tabled[(m, k, key, v)] += 1
            elif c == column:
                # the census keeps only the first line, `[`, of a TOML value spanning lines; the table keeps it whole
                if (not m.endswith(".json") and v.startswith("[") and census.get((m, k, key, "["))
                        and not census.get((m, k, key, v))):
                    v = "["
                tabled[(m, k, key, v)] += 1
        only_c, only_t = sum((census - tabled).values()), sum((tabled - census).values())
        figures.append("G3 %-8s census %d, tabled %d, only-in-census %d, only-in-tables %d" % (
            column, sum(census.values()), sum(tabled.values()), only_c, only_t))
        g3_bad = g3_bad or only_c or only_t
    dup = [k for k, c in Counter(r[2:6] for r in rows).items() if c > 1]
    figures.append("G3 duplicate ids %d%s" % (len(dup), (": " + str(dup[0])) if dup else ""))
    if g3_bad or dup:
        failed.add("G3")
    # G4: every cell equals an independent parse, and a one-line value's line says so
    wrong, checked = [], 0
    bindings, values = {}, {}

    def evaluated(pairs):
        """{name: value} of (name, source) pairs in module order; None for a value that does not evaluate."""
        out = {}
        for name, src in pairs:
            try:
                out[name] = code_value(src, out)
            except Exception:                   # whatever the failure: G4 refuses a None
                out[name] = None
        return out
    for c, _t, m, k, row, key, v, line, *_ in rows:
        if v.startswith("HELD:sha1=") or c == "layout":
            continue
        checked += 1
        if c == "code":
            if m not in bindings:
                bindings[m] = generator_bindings(phase0lib.source_path(export, m))
                cells = {r[5]: r[6] for r in rows if r[0] == "code" and r[2] == m}
                values[m] = (evaluated((n, s) for n, (s, _l) in bindings[m].items()),
                             evaluated((n, cells[n]) for n in bindings[m] if n in cells))
            src, at = bindings[m].get(key, (None, None))
            want, mine = values[m][0].get(key), values[m][1].get(key)
            try:
                ok = (src is not None and code_tokens(v) == code_tokens(src) and str(at) == line
                      and mine is not None and mine == want)
            except (SyntaxError, tokenize.TokenError) as exc:
                ok, src = False, "error %r" % exc
            if not ok:
                wrong.append("%s %s table %s generator %r" % (m, key, v[:40], str(src)[:40]))
            continue
        try:
            got = phase0lib.semantic(export, m, k, row, key)
            ok = got == literal(v, m)
            if ok and line != "-":
                text = Path(export, "build", "manifest", m).read_text().splitlines()[int(line) - 1]
                # the cell, then nothing but a comma, blanks and a comment: a string may hold a `#`
                one = re.match(r"^\s*%s\s*=\s*" % re.escape(key), text)
                rest = text[one.end():] if one else ""
                spans = one and phase0lib.partial(rest.split("#")[0].strip().rstrip(","))
                ok = one is not None and (spans or (rest.startswith(v) and
                                                    re.fullmatch(r",?\s*(#.*)?", rest[len(v):]) is not None))
        except (KeyError, IndexError, StopIteration, ValueError, TypeError) as exc:
            ok, got = False, "error %r" % exc
        if not ok:
            wrong.append("%s %s %s.%s table %s manifest %r" % (m, k, row, key, v[:40], str(got)[:40]))
    figures.append("G4 cells checked %d, wrong %d%s" % (checked, len(wrong), (": " + wrong[0]) if wrong else ""))
    if wrong:
        failed.add("G4")
    # G5: held values are only their hashes, and the hash is the manifest's value's
    cells = {(m, k, row, key): v for _c, _t, m, k, row, key, v, *_ in rows}
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
    # G6: the code tables are complete, and code/uncounted is exactly what the census leaves out
    counted = {(r.file, r.key) for r in recs if r.column == "code"}
    every = {("tools/" + g, name) for g in a.GENERATORS if Path(export, "tools", g).exists()
             for name in generator_bindings(Path(export, "tools", g))}
    named = {(m, key) for c, _t, m, _k, _r, key, *_ in rows if c == "code"}
    uncounted = {(m, key) for c, t, m, _k, _r, key, *_ in rows if t == "code/uncounted.tsv"}
    missing, extra, wrong_side = every - named, named - every, uncounted & counted
    short = (every - counted) - uncounted
    figures.append("G6 public constants %d, census-counted %d, uncounted tabled %d, missing %d, unknown %d, "
                   "uncounted but counted %d, uncounted not tabled %d%s" % (
                       len(every), len(counted), len(uncounted), len(missing), len(extra), len(wrong_side),
                       len(short), (": " + str(sorted(missing | extra | wrong_side | short)[0]))
                       if missing or extra or wrong_side or short else ""))
    if missing or extra or wrong_side or short:
        failed.add("G6")
    # G7: the manifest tables are the manifests whole
    walked = Counter((rel[len("build/manifest/"):],) + ident for rel in a.canon(Path(export))
                     for ident in manifest_values(str(Path(export) / rel)))
    held_ids = Counter(r[2:6] for r in rows if r[0] not in ("code", "layout"))
    absent, unknown = walked - held_ids, held_ids - walked
    empty = [rel for rel in a.canon(Path(export)) if not manifest_values(str(Path(export) / rel))]
    figures.append("G7 manifests %d (%d with no value), values %d, in the tables %d, missing %d, unknown %d%s" % (
        len(a.canon(Path(export))), len(empty), sum(walked.values()), sum(held_ids.values()),
        sum(absent.values()), sum(unknown.values()),
        (": " + str(sorted(absent | unknown)[0])) if absent or unknown else ""))
    if absent or unknown:
        failed.add("G7")
    # G8: the manifests rendered from the tables are the originals, as parsed
    out = os.path.join(TMP, "rendered")
    shutil.rmtree(out, ignore_errors=True)
    canon = [rel[len("build/manifest/"):] for rel in a.canon(Path(export))]
    try:
        written = render_manifests.render(tables_dir, out)
        error = None
    except (SystemExit, KeyError, ValueError, IndexError) as exc:
        written, error = [], "renderer failed: %r" % (exc,)
    sub = load_minitoml(export)
    differ, sub_differ = [], []
    for m in canon if not error else []:
        o, r = Path(export, "build", "manifest", m).read_text(), Path(out, m).read_text() if m in written else None
        load = json.loads if m.endswith(".json") else tomli.loads
        why = "not rendered" if r is None else parse_diff(load(o), load(r))
        if why:
            differ.append("%s: %s" % (m, why))
            continue
        if m.endswith(".toml"):
            got = []
            for text in (o, r):
                try:
                    got.append(sub(text))
                except ValueError:
                    got.append(None)
            if (got[0] is None) != (got[1] is None) or (got[0] is not None and parse_diff(got[0], got[1])):
                sub_differ.append(m)
    accepted = sum(1 for m in canon if m.endswith(".toml")) - sum(1 for m in canon if m.endswith(".toml")
                                                                   and refused(sub, export, m))
    figures.append("G8 manifests %d, rendered %d, parse differs %d, _minitoml accepts %d and differs %d%s" % (
        len(canon), len(written), len(differ), accepted, len(sub_differ),
        (": " + (error or (differ + sub_differ)[0])) if error or differ or sub_differ else ""))
    if error or differ or sub_differ or sorted(written) != sorted(canon):
        failed.add("G8")
    return failed, figures


def load_minitoml(export):
    """The original's own `_minitoml` from the export (its subset parser on a host without tomllib)."""
    sys.path.insert(0, os.path.join(export, "tools"))
    try:
        import _minitoml
    finally:
        sys.path.pop(0)
    return _minitoml.loads


def refused(sub, export, m):
    try:
        sub(Path(export, "build", "manifest", m).read_text())
        return False
    except ValueError:
        return True


def parse_diff(o, r, path=""):
    """Where a rendered parse differs from the original's (key order included), or None; a rendered held value
    matches when it is the placeholder of the SHA-1 of the original's literal."""
    if isinstance(r, str) and r.startswith("HELD:sha1="):
        return None if isinstance(o, str) and phase0lib.sha1(json.dumps(o)) == r[len("HELD:sha1="):] else \
            path + " held placeholder of another value"
    if type(o) is not type(r):
        return path + " type"
    if isinstance(o, dict):
        if list(o) != list(r):
            return path + " keys or their order"
        return next((d for d in (parse_diff(o[k], r[k], path + "/" + k) for k in o) if d), None)
    if isinstance(o, list):
        if len(o) != len(r):
            return path + " length"
        return next((d for d in (parse_diff(a, b, "%s/%d" % (path, i)) for i, (a, b) in enumerate(zip(o, r)))
                     if d), None)
    return None if o == r else path + " value"


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
    if name in ("perturbed-code", "code-hex-as-decimal"):
        new = "0x2751" if name == "perturbed-code" else str(0x2750)
        edit("code/constants.tsv", lambda lines: [l.replace("\tDELTA\t0x2750\t", "\tDELTA\t%s\t" % new) for l in lines])
        return tables, export
    if name == "uncounted-dropped":
        edit("code/uncounted.tsv", lambda lines: lines[:-1])
        return tables, export
    if name == "layout-form-flipped":
        edit("layout/forms.tsv", lambda lines: [l.replace("\t(form)\ttable\t", "\t(form)\tarray\t", 1)
                                                if i == next(j for j, x in enumerate(lines) if "\t(form)\ttable\t" in x)
                                                else l for i, l in enumerate(lines)])
        return tables, export
    if name == "json-order-swapped":
        def swap(lines):
            for i, l in enumerate(lines):
                f = l.split("\t")
                if len(f) > 4 and f[4].startswith('{"dict": ') and len(json.loads(f[4])["dict"]) > 1:
                    keys = json.loads(f[4])["dict"]
                    keys[0], keys[1] = keys[1], keys[0]
                    f[4] = json.dumps({"dict": keys})
                    lines[i] = "\t".join(f)
                    return lines
            raise AssertionError("no JSON dict form with two keys")
        edit("layout/forms.tsv", swap)
        return tables, export
    if name == "note-dropped":
        edit("uncounted/note.tsv", lambda lines: lines[:-1])
        return tables, export
    if name in ("perturbed-note", "note-cut-at-hash"):
        table, key = ("uncounted/note.tsv", "note") if name == "perturbed-note" else ("uncounted/notes.tsv", "notes")

        def change(lines):
            i = next(i for i, l in enumerate(lines) if ("\t%s\t\"" % key) in l
                     and (name == "perturbed-note" or "#" in l.split("\t")[4]))
            f = lines[i].split("\t")
            f[4] = f[4][:-1] + "x\"" if name == "perturbed-note" else f[4][:f[4].index("#")] + "\""
            lines[i] = "\t".join(f)
            return lines
        edit(table, change)
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
    if name in ("perturbed-manifest", "perturbed-generator"):
        copy = os.path.join(base, "export")
        for d in ("build/manifest", "tools", "docs"):
            shutil.copytree(os.path.join(export, d), os.path.join(copy, d))
        if name == "perturbed-manifest":
            p, pat, to = os.path.join(copy, "build", "manifest", "donovan.toml"), r"(?m)^(only_variant_slot\s*=\s*)true", r"\1false"
        else:
            p, pat, to = os.path.join(copy, "tools", "build_gfx_donovan.py"), r"(?m)^(DELTA\s*=\s*)0x2750\b", r"\g<1>0x2751"
        text = open(p).read()
        new = re.sub(pat, to, text, count=1)
        assert new != text, "the control's perturbation did not apply"
        open(p, "w").write(new)
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
    global TMP
    os.makedirs(os.path.join(ROOT, "build", "tmp"), exist_ok=True)
    TMP = tempfile.mkdtemp(prefix="test_phase0_tables.", dir=os.path.join(ROOT, "build", "tmp"))
    try:
        gate()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)


def gate():
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
