"""phase0lib.py — what phase 0's extractor and gate share (SPEC.md §3; docs/project/tables/README.md).

The acceptance of phase 0 is defined by the ORIGINAL's rule-5 census (`tools/audit_rule5.py` in an export of the pinned
commit): its records are the values to carry. The census records no row identity and no line, so this module aligns
each record with the manifest row it came from:
- TOML: a text pass with the census's own line grammar (its HDR_RE/KV_RE, imported) yields every key line in order
  with its kind, the kind's ordinal in the file, and its line; the census emits its records in the same order, so a
  greedy in-order match on (kind, key, value) is exact. The row's name comes from an independent parse (tomli).
- JSON: the census's own walk, repeated with the concrete position kept as a JSON Pointer (RFC 6901).

Each aligned value becomes one table row of the shared schema (SCHEMA). Two departures from the census's literal:
- a TOML value spanning lines (the census keeps its first line, `[`) is carried whole, from the parse;
- a value listed in docs/project/tables/facts/held.tsv (SPEC.md §0: runs that hold a whole vanilla or vs2 routine
  or table) is carried as `HELD:sha1=<SHA-1 of the census's value>`, never in the clear.
The code column (the generators' module-level constants) is read by an AST walk instead (code_rows): the census's
record names the constant, the source gives its whole value, as written.
Usage: imported by tools/extract_tables.py and tests/test_phase0_tables.py.
"""
import ast
import functools
import hashlib
import io
import json
import os
import re
import sys
import tokenize
from collections import Counter
from pathlib import Path

import tomli

SCHEMA = ("manifest", "kind", "row", "key", "value", "line", "prov_kind", "prov_refs")
PROV_WORDS = ("measured", "ruled", "derived", "testimony", "maintainer")
REFS = re.compile(r"\b14z-\d+[a-z]?\b|#\d+\b|\b20\d\d-\d\d-\d\d\b")
HELD_FILE = os.environ.get("PHASE0_HELD") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "project", "tables",
                         "facts", "held.tsv")

# The four subject tables of the gameplay column, and which records each holds.
VARIANT_KEYS = {"only_variant_slot", "only_base_slot", "unless_composed", "roster_subst"}
ROSTER_PAIRS = {("tenant", "id"), ("tenant", "id_by_profile"), ("port", "dst_slot"), ("port", "mirror_variant")}


def subject(rec):
    """The table a record belongs to, as a path under docs/project/tables/ without its extension."""
    if rec.column == "fact":
        if rec.file.endswith(".json"):
            stem = rec.file[len("build/manifest/"):-len(".json")]
            return "facts/json_" + re.sub(r"[^A-Za-z0-9]+", "_", stem)
        return "facts/" + ("top" if rec.kind == "(top)" else rec.kind)
    if rec.file.endswith(".json") or rec.key == "layout":
        return "select_wheel"
    if (rec.kind, rec.key) in ROSTER_PAIRS:
        return "roster"
    if (rec.kind, rec.key) == ("aux_poke", "val"):
        return "hit_class_mask"
    if rec.key in VARIANT_KEYS:
        return "variant_selection"
    raise ValueError("no subject table for %s [[%s]].%s" % (rec.file, rec.kind, rec.key))


def load_census(export_root):
    """The original's census module, imported from the export (read, never written)."""
    sys.path.insert(0, str(Path(export_root) / "tools"))
    import audit_rule5
    sys.path.pop(0)
    return audit_rule5


def sha1(text):
    return hashlib.sha1(text.encode()).hexdigest()


def read_held(path=HELD_FILE):
    """{(manifest, kind, row, key): sha1} of the values held out of the tables."""
    held = {}
    if os.path.exists(path):
        for line in open(path):
            if line.startswith("#") or line.startswith("manifest\t") or not line.strip():
                continue
            f = line.rstrip("\n").split("\t")
            held[(f[0], f[1], f[2], f[3])] = f[5]
    return held


def toml_key_lines(a, text):
    """Every key line of a manifest, in order: (kind, ordinal, key, raw value, line number)."""
    out, kind, ordinals, ordinal = [], "(top)", {}, 0
    for n, raw in enumerate(text.splitlines(), 1):
        if raw.strip().startswith("#"):
            continue
        m = a.HDR_RE.match(raw.split("#")[0].rstrip())
        if m:
            kind = m.group(2)
            ordinals[kind] = ordinals.get(kind, 0) + 1
            ordinal = ordinals[kind]
            continue
        m = a.KV_RE.match(raw.split("#")[0].rstrip())
        if m:
            out.append((kind, ordinal, m.group(1), m.group(2).strip().rstrip(","), n))
    return out


def toml_rows(doc, kind):
    if kind == "(top)":
        return [doc]
    node = doc.get(kind, {})
    return node if isinstance(node, list) else [node]


def toml_row_name(doc, kind, ordinal):
    rows = toml_rows(doc, kind)
    if kind == "(top)":
        return "(top)"
    row = rows[ordinal - 1] if 0 < ordinal <= len(rows) else {}
    return row.get("name") if isinstance(row, dict) else None


def toml_locator(doc, entry):
    """A TOML row's id: its name; `name#n` when the name repeats within its kind; `#n` when it has none."""
    kind, ordinal = entry[0], entry[1]
    name = toml_row_name(doc, kind, ordinal)
    if name is None:
        return "#%d" % ordinal
    if kind != "(top)" and sum(1 for r in toml_rows(doc, kind) if isinstance(r, dict) and r.get("name") == name) > 1:
        return "%s#%d" % (name, ordinal)
    return name


def pointer(parts):
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in parts) or "(top)"


def unpointer(ptr):
    if ptr == "(top)":
        return []
    return [p.replace("~1", "/").replace("~0", "~") for p in ptr.split("/")[1:]]


def json_paths(doc):
    """The census's JSON walk with the position kept: (census kind, key, row pointer, json value) in order. A dict
    member's row is its parent's pointer; a list element's row is its own pointer and its key `[]`."""
    out = []

    def walk(node, path, where):
        if isinstance(node, dict):
            for k, v in node.items():
                if not k.startswith("_"):
                    walk(v, path + [str(k)], where + [k])
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + ["[]"], where + [i])
        else:
            kind = ".".join(path[:-1]) or "(top)"
            key = path[-1] if path else "(top)"
            row = pointer(where if key == "[]" else where[:-1])
            out.append((kind, key, row, json.dumps(node)))
    walk(doc, [], [])
    return out


def prov_fields(prov):
    low = prov.lower()
    kind = next((w for w in PROV_WORDS if re.search(r"\b%s\b" % w, low)), "none")
    refs = []
    for r in REFS.findall(prov):
        if r not in refs:
            refs.append(r)
    return kind, "; ".join(refs) or "-"


def toml_literal(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, list):
        return "[" + ", ".join(toml_literal(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join("%s = %s" % (k, toml_literal(x)) for k, x in v.items()) + "}"
    return str(v)


def partial(raw):
    """A census value that is only the first line of a TOML value spanning lines."""
    return (raw.startswith("[") and not raw.endswith("]")) or raw.startswith('"""') or raw.startswith("'''")


@functools.lru_cache(maxsize=None)
def parsed(path):
    text = Path(path).read_text()
    return json.loads(text) if path.endswith(".json") else tomli.loads(text)


def aligned_rows(export_root, column):
    """(table rows by subject, the census records, the files read with their SHA-1) for one census column."""
    root = Path(export_root)
    a = load_census(root)
    recs, problems = a.census(root)
    if problems:
        raise SystemExit("the original's census reports problems: %s" % problems[:3])
    held = read_held()
    wanted = [r for r in recs if r.column == column]
    by_file = {}
    for r in wanted:
        by_file.setdefault(r.file, []).append(r)
    tables, read = {}, {}
    for rel, frecs in by_file.items():
        data = (root / rel).read_bytes()
        read[rel] = hashlib.sha1(data).hexdigest()
        text = data.decode("utf-8", errors="replace")
        if rel.endswith(".json"):
            # the same layout as toml_key_lines: (kind, locator, key, value, line); the locator is a JSON Pointer
            entries = [(k, row, key, v, "-") for k, key, row, v in json_paths(json.loads(text))]
            locate = lambda e: e[1]                                     # noqa: E731
        else:
            doc = parsed(str(root / rel))
            entries = toml_key_lines(a, text)
            locate = functools.partial(toml_locator, doc)
        pos = 0
        for r in frecs:
            while pos < len(entries) and (entries[pos][0], entries[pos][2], entries[pos][3]) != (r.kind, r.key, r.value):
                pos += 1
            if pos == len(entries):
                raise SystemExit("unaligned census record: %s [[%s]].%s = %s" % (rel, r.kind, r.key, r.value))
            e = entries[pos]
            pos += 1
            pk, refs = prov_fields(r.prov)
            manifest = rel[len("build/manifest/"):]
            row = locate(e)
            value = r.value
            if not rel.endswith(".json") and partial(value):
                value = toml_literal(semantic(export_root, manifest, r.kind, row, r.key))
            if (manifest, r.kind, row, r.key) in held:
                value = "HELD:sha1=" + sha1(r.value)
            tables.setdefault(subject(r), []).append(
                (manifest, r.kind, row, r.key, value, str(e[4]), pk, refs))
    return tables, wanted, read


def source_path(export_root, manifest):
    """Where a table's `manifest` cell lives in the export: a generator (`tools/<name>.py`, the code column) or a
    manifest under build/manifest/."""
    if manifest.startswith("tools/"):
        return Path(export_root) / manifest
    return Path(export_root) / "build" / "manifest" / manifest


def public_name(name):
    return re.match(r"^[A-Z][A-Z0-9_]*$", name) is not None


def module_constants(text):
    """Every PUBLIC module-level constant of a generator, by an AST walk, in order: (name, value node, line). A public
    name is the census's grammar, `[A-Z][A-Z0-9_]*`; `NAME = v` and `A, B = a, b` both bind constants, but the
    census's line grammar sees only the first."""
    out = []
    for n in ast.parse(text).body:
        if not isinstance(n, ast.Assign) or len(n.targets) != 1:
            continue
        t = n.targets[0]
        if isinstance(t, ast.Name) and public_name(t.id):
            out.append((t.id, n.value, n.lineno))
        elif isinstance(t, ast.Tuple) and any(isinstance(e, ast.Name) and public_name(e.id) for e in t.elts):
            if not (isinstance(n.value, ast.Tuple) and len(n.value.elts) == len(t.elts)):
                raise SystemExit("line %d: a tuple of constants not bound element by element" % n.lineno)
            out += [(e.id, v, n.lineno) for e, v in zip(t.elts, n.value.elts) if public_name(e.id)]
    return out


def as_written(segment):
    """A value's source text on one line: its comments dropped, each line stripped, the lines joined by one space
    (none after an opening bracket or before a closing one). A one-line value is its text unchanged."""
    lines = segment.splitlines()
    for tok in tokenize.generate_tokens(io.StringIO(segment).readline):
        if tok.type == tokenize.COMMENT:
            row, col = tok.start
            lines[row - 1] = lines[row - 1][:col]
    parts = [ln.strip() for ln in lines if ln.strip()]
    out = parts[0]
    for p in parts[1:]:
        out += ("" if out[-1] in "([{" or p[0] in ")]}" else " ") + p
    return out


def trailing_comment(text, lineno):
    """The comment that ends a source line, without its `#` and leading blanks (the census's provenance for a
    generator constant); empty when there is none."""
    line = text.splitlines()[lineno - 1]
    for tok in tokenize.generate_tokens(io.StringIO(line + "\n").readline):
        if tok.type == tokenize.COMMENT:
            return tok.string[1:].lstrip()
    return ""


def code_rows(export_root):
    """The code column: (rows by table, the census records, the files read with their SHA-1). code/constants holds
    every constant the census counts; code/uncounted every other public module-level constant of the same
    generators (the census's line grammar takes one name, so `A, B = a, b` escapes it)."""
    root = Path(export_root)
    a = load_census(root)
    recs, problems = a.census(root)
    if problems:
        raise SystemExit("the original's census reports problems: %s" % problems[:3])
    wanted = [r for r in recs if r.column == "code"]
    counted = Counter((r.file, r.key) for r in wanted)
    by_key = {(r.file, r.key): r for r in wanted}
    tables, read = {}, {}
    for gen in a.GENERATORS:
        rel = "tools/" + gen
        p = root / rel
        if not p.exists():
            continue
        data = p.read_bytes()
        read[rel] = hashlib.sha1(data).hexdigest()
        text = data.decode()
        for name, node, line in module_constants(text):
            value = as_written(ast.get_source_segment(text, node))
            r = by_key.get((rel, name))
            pk, refs = prov_fields(r.prov if r else trailing_comment(text, line))
            table = "code/constants" if r else "code/uncounted"
            tables.setdefault(table, []).append((rel, "(module)", "(module)", name, value, str(line), pk, refs))
    found = Counter((m, key) for rows in tables.values() for m, _k, _r, key, *_ in rows)
    if counted - found:
        raise SystemExit("census records with no module constant: %s" % sorted(counted - found)[:3])
    return tables, wanted, read


def toml_as_written(line, want):
    """A one-line TOML value's literal as its line writes it, without the trailing comment: the line's census grammar
    cuts at the first `#`, which a string may hold (a note citing `#120`), so the literal is the shortest cut of the
    line at a `#` (or the whole line) that parses to the value."""
    rest = line.split("=", 1)[1]
    for cut in [i for i, ch in enumerate(rest) if ch == "#"] + [len(rest)]:
        try:
            if tomli.loads("v = " + rest[:cut])["v"] == want:
                return rest[:cut].strip()
        except tomli.TOMLDecodeError:
            pass
    raise SystemExit("no literal on line %r parses to %r" % (line[:60], want))


def uncounted_rows(export_root, counted):
    """Every manifest value the census does not count, as table rows by subject: a TOML key of its IGNORE_KEYS
    (`uncounted/<key>`), and a JSON `_` key, whose value is carried whole (`uncounted/json_underscore`). `counted` is
    the set of (manifest, kind, row, key) the gameplay and fact tables already hold. The census attributes nothing to
    a value it does not count, so prov is `none`/`-`."""
    root = Path(export_root)
    a = load_census(root)
    tables, read = {}, {}
    for rel in a.canon(root):
        data = (root / rel).read_bytes()
        read[rel] = hashlib.sha1(data).hexdigest()
        text = data.decode("utf-8", errors="replace")
        manifest = rel[len("build/manifest/"):]
        if rel.endswith(".json"):
            def walk(node, path, where):
                if isinstance(node, dict):
                    for k, v in node.items():
                        if k.startswith("_"):
                            tables.setdefault("uncounted/json_underscore", []).append(
                                (manifest, ".".join(path) or "(top)", pointer(where), k, json.dumps(v), "-", "none",
                                 "-"))
                        else:
                            walk(v, path + [str(k)], where + [k])
                elif isinstance(node, list):
                    for i, v in enumerate(node):
                        walk(v, path + ["[]"], where + [i])
            walk(json.loads(text), [], [])
            continue
        doc = parsed(str(root / rel))
        for e in toml_key_lines(a, text):
            kind, ordinal, key, raw, line = e
            row = toml_locator(doc, e)
            if (manifest, kind, row, key) in counted:
                continue
            if key not in a.IGNORE_KEYS:
                raise SystemExit("%s line %d: [[%s]].%s is neither counted nor ignored by the census" % (
                    rel, line, kind, key))
            want = semantic(export_root, manifest, kind, row, key)
            value = toml_literal(want) if partial(raw) else toml_as_written(text.splitlines()[line - 1], want)
            tables.setdefault("uncounted/" + key, []).append(
                (manifest, kind, row, key, value, str(line), "none", "-"))
    return tables, read


def layout_rows(export_root):
    """What the value tables do not say about a manifest's shape, as rows of `layout/forms` (key `(form)`):
    - one per canonical manifest: kind and row `(file)`, value `toml` or `json` (so a manifest with no value, comments
      only, is still named and its SHA-1 pinned in the header);
    - one per TOML kind: row `(kind)`, value `table` (`[x]`) or `array` (`[[x]]`), line its first header;
    - one per JSON container: row its pointer, value `{"dict": [its keys in order]}` or `{"list": its length}` (JSON
      consumers iterate in order, so the order is carried)."""
    root = Path(export_root)
    a = load_census(root)
    rows, read = [], {}
    for rel in a.canon(root):
        data = (root / rel).read_bytes()
        read[rel] = hashlib.sha1(data).hexdigest()
        manifest = rel[len("build/manifest/"):]
        fmt = "json" if rel.endswith(".json") else "toml"
        rows.append((manifest, "(file)", "(file)", "(form)", fmt, "-", "none", "-"))
        text = data.decode("utf-8", errors="replace")
        if fmt == "json":
            def walk(node, path, where):
                if isinstance(node, dict):
                    form = {"dict": list(node)}
                elif isinstance(node, list):
                    form = {"list": len(node)}
                else:
                    return
                rows.append((manifest, ".".join(path) or "(top)", pointer(where), "(form)", json.dumps(form), "-",
                             "none", "-"))
                for k, v in (node.items() if isinstance(node, dict) else enumerate(node)):
                    if not (isinstance(k, str) and k.startswith("_")):
                        walk(v, path + ([str(k)] if isinstance(node, dict) else ["[]"]), where + [k])
            walk(json.loads(text), [], [])
            continue
        doc, first = parsed(str(root / rel)), {}
        for n, raw in enumerate(text.splitlines(), 1):
            m = a.HDR_RE.match(raw.split("#")[0].rstrip())
            if m and not raw.strip().startswith("#"):
                first.setdefault(m.group(2), (n, "array" if m.group(1) == "[[" else "table"))
        for kind, (line, form) in first.items():
            node = doc.get(kind)
            if not ((form == "array" and isinstance(node, list)) or (form == "table" and isinstance(node, dict))):
                raise SystemExit("%s: [%s] header form %s does not match its parse" % (rel, kind, form))
            rows.append((manifest, kind, "(kind)", "(form)", form, str(line), "none", "-"))
    return {"layout/forms": rows}, read


def semantic(export_root, manifest, kind, row, key):
    """The value at (kind, row, key) by an independent parse (tomli / json), as a Python value."""
    path = str(Path(export_root) / "build" / "manifest" / manifest)
    doc = parsed(path)
    if manifest.endswith(".json"):
        node = doc
        for part in unpointer(row):
            node = node[int(part)] if isinstance(node, list) else node[part]
        return node if key == "[]" else node[key]
    rows = toml_rows(doc, kind)
    if kind == "(top)":
        target = doc
    elif "#" in row and row.rsplit("#", 1)[1].isdigit():
        target = rows[int(row.rsplit("#", 1)[1]) - 1]
    else:
        target = next(r for r in rows if r.get("name") == row)
    return target[key]
