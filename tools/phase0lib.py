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
Usage: imported by tools/extract_tables.py and tests/test_phase0_tables.py.
"""
import functools
import hashlib
import json
import os
import re
import sys
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
