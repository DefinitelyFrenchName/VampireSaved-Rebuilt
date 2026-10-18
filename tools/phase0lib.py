"""phase0lib.py — what phase 0's extractor and census share (SPEC.md §3; docs/project/tables/README.md).

The acceptance of phase 0 is defined by the ORIGINAL's rule-5 census (`tools/audit_rule5.py` in an export of the pinned
commit): its records are the values to carry. The census records no row identity and no line, so this module aligns
each record with the manifest row it came from:
- TOML: a text pass with the census's own line grammar (its HDR_RE/KV_RE, imported) yields every key line in order
  with its kind, the kind's ordinal in the file, and its line; the census emits its records in the same order, so a
  greedy in-order match on (kind, key, value) is exact. The row's name comes from an independent parse (tomli).
- JSON: the census's own walk, repeated with list indices kept, so each record gets its concrete path.

Each aligned value becomes one table row of the shared schema (SCHEMA). Usage: imported by
tools/extract_gameplay_tables.py and tests/test_phase0_gameplay.py.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import tomli

SCHEMA = ("manifest", "kind", "row", "key", "value", "line", "prov_kind", "prov_refs")
PROV_WORDS = ("measured", "ruled", "derived", "testimony", "maintainer")
REFS = re.compile(r"\b14z-\d+[a-z]?\b|#\d+\b|\b20\d\d-\d\d-\d\d\b")

# The four subject tables of the gameplay column, and which records each holds.
VARIANT_KEYS = {"only_variant_slot", "only_base_slot", "unless_composed", "roster_subst"}
ROSTER_PAIRS = {("tenant", "id"), ("tenant", "id_by_profile"), ("port", "dst_slot"), ("port", "mirror_variant")}


def subject(rec):
    """The subject table a gameplay record belongs to (its file stem under docs/project/tables/)."""
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


def toml_row_name(doc, kind, ordinal):
    node = doc
    for part in kind.split("."):
        node = node.get(part, {}) if isinstance(node, dict) else {}
    rows = node if isinstance(node, list) else [node]
    row = rows[ordinal - 1] if 0 < ordinal <= len(rows) else {}
    return row.get("name") if isinstance(row, dict) else None


def json_paths(doc):
    """The census's JSON walk with indices kept: (census kind, key, concrete parent path, json value) in order."""
    out = []

    def walk(node, path, concrete):
        if isinstance(node, dict):
            for k, v in node.items():
                if not k.startswith("_"):
                    walk(v, path + [str(k)], concrete + [str(k)])
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + ["[]"], concrete[:-1] + ["%s[%d]" % (concrete[-1], i)] if concrete else ["[%d]" % i])
        else:
            out.append((".".join(path[:-1]) or "(top)", path[-1] if path else "(top)",
                        ".".join(concrete[:-1]) or "(top)", json.dumps(node)))
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


def aligned_rows(export_root, column="gameplay"):
    """(table rows by subject, the census records, the files read with their SHA-1) for one census column."""
    root = Path(export_root)
    a = load_census(root)
    recs, problems = a.census(root)
    if problems:
        raise SystemExit("the original's census reports problems: %s" % problems[:3])
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
            # the same layout as toml_key_lines: (kind, locator, key, value, line); the locator is the concrete path
            entries = [(k, row, key, v, "-") for k, key, row, v in json_paths(json.loads(text))]
            locate = lambda e: e[1]                                     # noqa: E731
        else:
            doc = tomli.loads(text)
            entries = toml_key_lines(a, text)
            locate = lambda e: toml_row_name(doc, e[0], e[1]) or "#%d" % e[1]   # noqa: E731
        pos = 0
        for r in frecs:
            while pos < len(entries) and (entries[pos][0], entries[pos][2], entries[pos][3]) != (r.kind, r.key, r.value):
                pos += 1
            if pos == len(entries):
                raise SystemExit("unaligned census record: %s [[%s]].%s = %s" % (rel, r.kind, r.key, r.value))
            e = entries[pos]
            pos += 1
            pk, refs = prov_fields(r.prov)
            row = (Path(rel).name, r.kind, locate(e), r.key, r.value, str(e[4]), pk, refs)
            tables.setdefault(subject(r), []).append(row)
    return tables, wanted, read


def semantic_value(export_root, manifest, kind, row, key):
    """The value at (kind, row, key) by an independent parse, as the table writes it: the TOML literal or the
    JSON dump. Used by the gate to check a table cell against the manifest without the text pass."""
    path = Path(export_root) / "build" / "manifest" / manifest
    if manifest.endswith(".json"):
        node = json.loads(path.read_text())
        for part in re.findall(r"[^.\[\]]+|\[\d+\]", row) if row != "(top)" else []:
            node = node[int(part[1:-1])] if part.startswith("[") else node[part]
        return json.dumps(node[key])
    doc = tomli.loads(path.read_text())
    node = doc
    for part in kind.split("."):
        node = node[part]
    rows = node if isinstance(node, list) else [node]
    if row.startswith("#"):
        target = rows[int(row[1:]) - 1]
    else:
        target = next(r for r in rows if r.get("name") == row)
    return toml_literal(target[key])


def toml_literal(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return json.dumps(v)
    return str(v)
