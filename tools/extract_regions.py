"""extract_regions.py — the original's extraction measurements as tables (#4; SPEC.md §0, the maintainer's direction
"I would table the measurement"; docs/project/tables/README.md).

The original's merged build reads one extraction record per tenant, `regions.json`, from the three directories its
`tools/build_merged.sh` names (D_EX, H_EX, P_EX). Each is what `tools/extract_char.py` measured by diffing vsav2
against its sibling vhunt2: the regions, their vhunt2 twins and shifts, every relocation ref, the code scan, the
dispatch pairs, the per-character bank values. This tool writes them into OUT_DIR:
- under extraction/, one table per section of the record, in the record's own columns, with a leading `tenant`
  column (runs, inputs, shifts, regions, region_lists, refs, variant_sites, pcrel_refs, code_scan, dispatch,
  engine_dispatch, values, auto_tables);
- three gameplay tables (the maintainer's rulings, SPEC.md §0, "Readable gameplay table" and the short values):
  jump_physics.tsv (`jump_params` as named 16.16 fields), cancel_windows.tsv (`byte2d_a` and `byte2d_b`, one row
  per move index) and bank_values.tsv (each tenant's own short bank rows, one row per field). Their rows in
  extraction/values.tsv and extraction/auto_tables.tsv say `TABLE:<name>` instead of the bytes.
Every integer is written in hex (`0x…`, `-0x…`) except `width`, a bit count; an absent key is `-`. The JSON objects'
key order is not carried (it is not data); every list's order and the regions' order are, by row order.

render(tables_dir) is the inverse: it rebuilds each tenant's record from the tables, for the gate
(tests/test_extraction_tables.py). Prints the SHA-1 of every file it read ([VSR-10]), never a byte.

Usage: python3 tools/extract_regions.py <export root> <pin label> <out dir>
"""
import hashlib
import json
import os
import re
import sys
from decimal import Decimal

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FACTS = os.path.join(ROOT, "docs", "project", "tables", "facts")
TENANTS = (("donovan", "D_EX"), ("huitzil", "H_EX"), ("pyron", "P_EX"))
MERGED = "tools/build_merged.sh"
HEX_KEYS = {"src", "orc", "len", "grow", "raw_from", "off", "target", "orc_target", "base_off", "src_target", "delta",
            "value"}
COLUMNS = {
    "runs": ("tenant", "record", "src_set", "oracle_set", "char"),
    "inputs": ("tenant", "file", "sha1"),
    "shifts": ("tenant", "shift", "value"),
    "regions": ("tenant", "region", "src", "orc", "len", "grow", "kind", "shift", "source_only", "pre_classified",
                "raw_from", "sha1"),
    "region_lists": ("tenant", "region", "list", "value"),
    "refs": ("tenant", "region", "off", "width", "target", "orc_target", "shift", "class"),
    "variant_sites": ("tenant", "region", "off", "src", "orc"),
    "pcrel_refs": ("tenant", "region", "kind", "off", "base_off", "target"),
    "code_scan": ("tenant", "off", "width", "target", "how", "class"),
    "dispatch": ("tenant", "table", "src_target", "orc_target"),
    "engine_dispatch": ("tenant", "table", "src_target", "orc_target", "delta"),
    "values": ("tenant", "table", "kind", "ptr", "region", "inside_region", "value"),
    "auto_tables": ("tenant", "table", "verdict", "entry_guess"),
    "jump_physics": ("tenant", "jump", "xv", "xaccel", "yv", "gravity", "vs2_row"),
    "cancel_windows": ("tenant", "move", "special", "ex", "vs2_special", "vs2_ex"),
    "bank_values": ("tenant", "table", "field", "value", "format", "vs2_addr"),
}
GAMEPLAY_TABLES = ("jump_physics", "cancel_windows", "bank_values")
REGION_SCALARS = ("src", "orc", "len", "grow", "kind", "shift", "source_only", "pre_classified", "raw_from", "sha1")
REGION_LISTS = ("dead", "ins", "charid_sites", "table_bytes")       # dead and ins hold [start, end] pairs
REGION_RECORDS = {"refs": "refs", "variant_sites": "variant_sites", "pcrel_refs": "pcrel_refs"}
SECTIONS = ("code_scan", "dispatch", "engine_dispatch", "values", "auto_tables")
JUMPS = ("neutral", "forward", "back")                              # three 0x10 rows of (xv, xaccel, yv, gravity)
JUMP_FIELDS = ("xv", "xaccel", "yv", "gravity")
# The tenant's own short rows, each a field list of (name, format). Not rec8_a or rec8_b: the extractor reads 8 bytes
# at char*8 there, which is a slice of another character's jump_params or pursuit record (bank_map.toml's notes).
BANK_FIELDS = {
    "param32_a": (("fwd_walk_xv", "s16.16"), ("back_walk_xv", "s16.16")),
    "param32_b": (("long0", "s16.16"), ("long1", "s16.16")),
    "word132": (("value", "u16"),),
    "word_pos_a": (("value", "u16"),),
    "word_pos_b": (("value", "u16"),),
    "gap_be23a": (("min_air_dash_height", "u16"),),
    "word_y_off": (("value", "u16"),),
    "word_range": (("value", "u16"),),
    "byte15b": (("value", "u8"),),
}
WIDTH = {"s16.16": 4, "u16": 2, "u8": 1}
GAMEPLAY = {"jump_params": "jump_physics", "byte2d_a": "cancel_windows", "byte2d_b": "cancel_windows",
            **{t: "bank_values" for t in BANK_FIELDS}}
TITLES = {
    "runs": "EXTRACTION: each tenant's record, the sets it diffed and the character id",
    "inputs": "EXTRACTION: the SHA-1 of every source-set member each record read",
    "shifts": "EXTRACTION: the vsav2 -> vhunt2 shift of each shift family",
    "regions": "EXTRACTION: every ported region: vsav2 start, vhunt2 twin, length, growth, kind, shift family, SHA-1",
    "region_lists": "EXTRACTION: each region's offset lists (dead and ins spans, charid_sites, table_bytes), in order",
    "refs": "EXTRACTION: every relocation ref of every region, in the record's order",
    "variant_sites": "EXTRACTION: the bytes where vsav2 and vhunt2 differ inside a region (vsav2, vhunt2 value)",
    "pcrel_refs": "EXTRACTION: the PC-relative table entries found in source-only regions",
    "code_scan": "EXTRACTION: the code scanner's operands outside the regions, in order",
    "dispatch": "EXTRACTION: the per-character dispatch targets, vsav2 and vhunt2",
    "engine_dispatch": "EXTRACTION: the engine dispatch targets that differ by a delta",
    "values": "EXTRACTION: the per-character bank rows (pointers, short values; jump and cancel rows by reference)",
    "auto_tables": "EXTRACTION: the bank gaps the extractor classified, with its entry guess",
    "jump_physics": "GAMEPLAY: each tenant's three jumps from vs2's jump_params row, as 16.16 values",
    "cancel_windows": "GAMEPLAY: each tenant's special- and EX-cancel window per move index, from vs2's byte2d rows",
    "bank_values": "GAMEPLAY: each tenant's own short bank rows from vs2 (walk speeds, pursuit leap, words), by field",
}


def sha1(data):
    return hashlib.sha1(data).hexdigest()


def records(export_root):
    """[(tenant, record path relative to the export)], from build_merged.sh's D_EX/H_EX/P_EX, and its SHA-1."""
    raw = open(os.path.join(export_root, MERGED), "rb").read()
    found = dict(re.findall(r'^([DHP]_EX)="([^"]+)"', raw.decode(), re.M))
    return [(t, found[var] + "/regions.json") for t, var in TENANTS], sha1(raw)


def cell(key, v):
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return ("-0x%x" % -v if v < 0 else "0x%x" % v) if key in HEX_KEYS | {"list"} else str(v)
    assert "\t" not in v and "\n" not in v, v
    return v


def uncell(key, s):
    if s == "-":
        return None
    if s in ("true", "false"):
        return s == "true"
    if key in HEX_KEYS and re.fullmatch(r"-?0x[0-9a-f]+", s):
        return int(s, 16)
    if key == "width":
        return int(s)
    return s


def fixed(word):
    """A signed 16.16 long as its exact decimal (2**16 divides a power of ten, so it terminates)."""
    v = int.from_bytes(word, "big", signed=True)
    return format((Decimal(v) / Decimal(65536)).normalize(), "f")


def unfixed(text):
    v = Decimal(text) * 65536
    assert v == v.to_integral_value(), text
    return int(v).to_bytes(4, "big", signed=True)


def bank():
    """{table: (vs2 address of row 0, entry size)} for the gameplay rows, from bank_map.toml's facts (the original's
    extract_char.py: origins[vsav2] + (vsavj - origins[vsavj]) + char * entry size, stride/32 or span/32 for byte2d),
    and the SHA-1 of the two fact tables read."""
    f, read = {}, []
    for name in ("origins", "table"):
        path = os.path.join(FACTS, name + ".tsv")
        read.append(("docs/project/tables/facts/%s.tsv" % name, sha1(open(path, "rb").read())))
        for line in open(path):
            c = line.rstrip("\n").split("\t")
            if not line.startswith("#") and c[0] == "bank_map.toml":
                f[(c[1], c[2], c[3])] = c[4]
    out = {}
    for t in GAMEPLAY:
        size = int(f[("table", t, "span" if t.startswith("byte2d") else "stride")], 16) // 32
        out[t] = (int(f[("origins", "#1", "vsav2")], 16) + int(f[("table", t, "vsavj")], 16)
                  - int(f[("origins", "#1", "vsavj")], 16), size)
    return out, read


def prg(addr):
    return "PRG:0x%06X" % addr


def jump_rows(tenant, raw, row0):
    rows = []
    for k, jump in enumerate(JUMPS):
        row = {"tenant": tenant, "jump": jump, "vs2_row": prg(row0 + k * 16)}
        for j, f in enumerate(JUMP_FIELDS):
            o = k * 16 + j * 4
            row[f] = fixed(raw[o:o + 4])
        rows.append(row)
    return rows


def bank_rows(tenant, table, raw, addr):
    rows, off = [], 0
    for field, fmt in BANK_FIELDS[table]:
        chunk = raw[off:off + WIDTH[fmt]]
        rows.append({"tenant": tenant, "table": table, "field": field, "format": fmt, "vs2_addr": prg(addr + off),
                     "value": fixed(chunk) if fmt == "s16.16" else str(int.from_bytes(chunk, "big"))})
        off += WIDTH[fmt]
    assert off == len(raw), "%s: %d bytes for %d" % (table, len(raw), off)
    return rows


def unbank(rows):
    return b"".join(unfixed(r["value"]) if r["format"] == "s16.16" else int(r["value"]).to_bytes(WIDTH[r["format"]], "big")
                    for r in rows)


def tables_of(tenant, record_path, doc, rows0):
    """{table: [row dict]} for one tenant's record; rows0 is bank()'s {table: (row-0 address, entry size)}."""
    t = {name: [] for name in COLUMNS}
    at = {name: a + int(doc["char"], 16) * size for name, (a, size) in rows0.items()}
    t["runs"].append({"tenant": tenant, "record": record_path, **{k: doc[k] for k in ("src_set", "oracle_set", "char")}})
    t["inputs"] += [{"tenant": tenant, "file": f, "sha1": h} for f, h in doc["input_sha1s"].items()]
    t["shifts"] += [{"tenant": tenant, "shift": s, "value": v} for s, v in doc["shifts"].items()]
    for name, r in doc["regions"].items():
        t["regions"].append({"tenant": tenant, "region": name, **{k: r.get(k) for k in REGION_SCALARS}})
        for lst in REGION_LISTS:
            for v in r.get(lst, []):
                t["region_lists"].append({"tenant": tenant, "region": name, "list": lst,
                                          "value": ",".join(cell("list", x) for x in v) if isinstance(v, list)
                                          else cell("list", v)})
            if lst in r and not r[lst]:
                t["region_lists"].append({"tenant": tenant, "region": name, "list": lst, "value": "(empty)"})
        for key in REGION_RECORDS:
            if key in r and not r[key]:
                t["region_lists"].append({"tenant": tenant, "region": name, "list": key, "value": "(empty)"})
            t[key] += [{"tenant": tenant, "region": name, **x} for x in r.get(key, [])]
    for sec in SECTIONS:
        for x in doc[sec]:
            row = {"tenant": tenant, **x}
            if sec == "values" and x["table"] in GAMEPLAY:
                raw = bytes.fromhex(x["value"])
                if x["table"] == "jump_params":
                    t["jump_physics"] += jump_rows(tenant, raw, at["jump_params"])
                elif x["table"] == "byte2d_a":
                    t["cancel_windows"] += [{"tenant": tenant, "move": m, "special": b,
                                             "vs2_special": prg(at["byte2d_a"] + m)} for m, b in enumerate(raw)]
                elif x["table"] == "byte2d_b":
                    ex = {r["move"]: r for r in t["cancel_windows"] if r["tenant"] == tenant}
                    assert len(ex) == len(raw), "byte2d_b before byte2d_a, or of another length"
                    for m, b in enumerate(raw):
                        ex[m].update(ex=b, vs2_ex=prg(at["byte2d_b"] + m))
                else:
                    t["bank_values"] += bank_rows(tenant, x["table"], raw, at[x["table"]])
                row["value"] = "TABLE:" + GAMEPLAY[x["table"]]
            elif sec == "auto_tables" and x["table"] in BANK_FIELDS:
                t["bank_values"] += bank_rows(tenant, x["table"], bytes.fromhex(x["entry_guess"]), at[x["table"]])
                row["entry_guess"] = "TABLE:bank_values"
            t[sec].append(row)
    return t


def gameplay_cell(key, v):
    if key in ("move", "special", "ex"):
        return str(v)
    return v


def write(out, pin, tables, read):
    for name, rows in tables.items():
        sub = "" if name in GAMEPLAY_TABLES else "extraction"
        path = os.path.join(out, sub, name + ".tsv")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("# %s.tsv — %s.\n" % (name, TITLES[name]))
            f.write("# GENERATED by tools/extract_regions.py from the original at %s; do not hand-edit before "
                    "phase 1 builds from it (docs/project/tables/README.md).\n" % pin)
            f.write("# read: %s\n" % ", ".join("%s %s" % (p, h[:12]) for p, h in read))
            f.write("\t".join(COLUMNS[name]) + "\n")
            for row in rows:
                if sub:
                    f.write("\t".join(cell(k, row.get(k)) for k in COLUMNS[name]) + "\n")
                else:
                    f.write("\t".join(gameplay_cell(k, row[k]) for k in COLUMNS[name]) + "\n")


def read_rows(path):
    """(read header pairs, [row dict]) of one generated table."""
    read, rows, cols = [], [], None
    for line in open(path):
        line = line.rstrip("\n")
        if line.startswith("# read:"):
            parts = [p.split() for p in line[len("# read:"):].split(",")]
            read = [(p[0], p[1]) for p in parts if p]
        elif line.startswith("#"):
            continue
        elif cols is None:
            cols = line.split("\t")
        else:
            rows.append(dict(zip(cols, line.split("\t"))))
    return read, rows


def render(tables_dir):
    """{tenant: record} rebuilt from the tables (the inverse of tables_of)."""
    t = {}
    for name in COLUMNS:
        sub = "" if name in GAMEPLAY_TABLES else "extraction"
        t[name] = read_rows(os.path.join(tables_dir, sub, name + ".tsv"))[1]
    docs = {}
    for run in t["runs"]:
        docs[run["tenant"]] = {"src_set": run["src_set"], "oracle_set": run["oracle_set"], "char": run["char"],
                               "input_sha1s": {}, "shifts": {}, "regions": {},
                               **{sec: [] for sec in SECTIONS}}
    for r in t["inputs"]:
        docs[r["tenant"]]["input_sha1s"][r["file"]] = r["sha1"]
    for r in t["shifts"]:
        docs[r["tenant"]]["shifts"][r["shift"]] = uncell("value", r["value"])
    for r in t["regions"]:
        reg = {k: uncell(k, r[k]) for k in REGION_SCALARS if r[k] != "-"}
        docs[r["tenant"]]["regions"][r["region"]] = reg
    for r in t["region_lists"]:
        reg = docs[r["tenant"]]["regions"][r["region"]]
        lst = reg.setdefault(r["list"], [])
        if r["value"] != "(empty)":
            vals = [int(v, 16) for v in r["value"].split(",")]
            lst.append(vals if r["list"] in ("dead", "ins") else vals[0])
    for key in REGION_RECORDS:
        for r in t[key]:
            reg = docs[r["tenant"]]["regions"][r["region"]]
            reg.setdefault(key, []).append({k: uncell(k, v) for k, v in r.items()
                                            if k not in ("tenant", "region") and v != "-"})
    for sec in SECTIONS:
        for r in t[sec]:
            docs[r["tenant"]][sec].append({k: uncell(k if k != "value" else "-", v) for k, v in r.items()
                                           if k != "tenant" and v != "-"})
    for tenant, doc in docs.items():
        for x in doc["values"]:
            if x.get("value") == "TABLE:jump_physics":
                raw = b"".join(unfixed(row[f]) for jump in JUMPS for row in t["jump_physics"]
                               if row["tenant"] == tenant and row["jump"] == jump for f in JUMP_FIELDS)
                x["value"] = raw.hex()
            elif x.get("value") == "TABLE:cancel_windows":
                col = "special" if x["table"] == "byte2d_a" else "ex"
                rows = sorted((int(r["move"]), int(r[col])) for r in t["cancel_windows"] if r["tenant"] == tenant)
                x["value"] = bytes(b for _, b in rows).hex()
            elif x.get("value") == "TABLE:bank_values":
                x["value"] = unbank(r for r in t["bank_values"]
                                    if (r["tenant"], r["table"]) == (tenant, x["table"])).hex()
        for x in doc["auto_tables"]:
            if x.get("entry_guess") == "TABLE:bank_values":
                x["entry_guess"] = unbank(r for r in t["bank_values"]
                                          if (r["tenant"], r["table"]) == (tenant, x["table"])).hex()
    return docs


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    export_root, pin, out = sys.argv[1:]
    recs, merged_sha = records(export_root)
    rows0, read = bank()
    read, tables = [(MERGED, merged_sha)] + read, {name: [] for name in COLUMNS}
    for tenant, rel in recs:
        raw = open(os.path.join(export_root, rel), "rb").read()
        read.append((rel, sha1(raw)))
        for name, rows in tables_of(tenant, rel, json.loads(raw), rows0).items():
            tables[name] += rows
    write(out, pin, tables, read)
    for name, rows in tables.items():
        print("%-16s %6d rows" % (name, len(rows)))
    for p, h in read:
        print("read %s sha1 %s" % (p, h))


if __name__ == "__main__":
    main()
