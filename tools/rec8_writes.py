"""rec8_writes.py — what the original's merged build writes for `rec8_a`/`rec8_b`, and what the tenants' own rows of
the table `rec8_b` slices hold (#4; docs/project/tables/README.md "What the build wrote for rec8_a and rec8_b").

The original's generator (`tools/gen_donovan_patch.py`, its per-char value rows) writes each `values` row of a
tenant's record at `bank_map.toml`'s vsavj address + id * stride/32, the id being the tenant's on the build's profile
(`cps2-wide-v1` for the merged build), with no variant mirror for an id of 0x10 and up. This reads, statically:
- for each tenant, its record's `rec8_a`/`rec8_b` value, the address that write lands on, and vsavj's data-view
  bytes there;
- the tenant's own row of the table `rec8_b` is a slice of (vsavj 0x0BE3FA, id*0x20, `bank_map.toml`'s note): vsavj's
  row at the id, whether it equals the base-half row at id & 0x0F, and vs2's row for the tenant's source char;
- each game's reader of that table: every `movea.l #table,a0`, and whether the word ten bytes before it loads the
  index from +0x382 (`move.b $382(a6),d0`), the character id.
With `--built DIR` (a merged build's output, `build/proof_merged` of a tools/build_proof.py leg), it also reads that
build's own data view (`verify_data.bin`, beside its `vanilla_data.bin`) and its ops (`patch/patch.json`): the build's
bytes at each write address, how many bytes of the sliced table differ from vanilla, and which ops touch it.
Values are discrete per-character values (CLAUDE.md [VSR-8]). Prints the SHA-1 of every file it read ([VSR-10]).

Usage: python3 tools/rec8_writes.py <export root> <rom dir> [--built DIR]
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_regions import records, sha1  # noqa: E402

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TABLES = os.path.join(ROOT, "docs", "project", "tables")
PROFILE = "cps2-wide-v1"
ROWS = ("rec8_a", "rec8_b")
SLICED = "rec8_b"                  # the table it slices: rows of 0x20 bytes from its vsavj base
SLICED_ROW = 0x20
INDEX_LOAD = bytes.fromhex("102e0382")


def facts(name):
    path = os.path.join(TABLES, name)
    out = {}
    for line in open(path):
        c = line.rstrip("\n").split("\t")
        if not line.startswith("#") and len(c) > 4 and c[0] != "manifest":
            out[(c[0], c[1], c[2], c[3])] = c[4]
    return out, (os.path.relpath(path, ROOT), sha1(open(path, "rb").read()))


def views(export_root, romdir, tmp):
    """{set: (opcode view, data view)} by the original's cps2_decrypt.py, and the SHA-1 of each zip."""
    out, read = {}, []
    for s in ("vsavj", "vsav2"):
        z = os.path.join(romdir, s + ".zip")
        read.append((z, hashlib.sha1(open(z, "rb").read()).hexdigest()))
        op, data = os.path.join(tmp, s + ".op"), os.path.join(tmp, s + ".data")
        subprocess.run([sys.executable, os.path.join(export_root, "tools", "cps2_decrypt.py"), z, op,
                        "--data-out", data], check=True, capture_output=True)
        out[s] = (open(op, "rb").read(), open(data, "rb").read())
    return out, read


def load(export_root, romdir):
    """Everything measure() reads: the records, the fact tables, both games' views, and the SHA-1 of each file."""
    recs, merged_sha = records(export_root)
    table, t_read = facts(os.path.join("facts", "table.tsv"))
    origins, o_read = facts(os.path.join("facts", "origins.tsv"))
    roster, r_read = facts("roster.tsv")
    read = [("tools/build_merged.sh", merged_sha), t_read, o_read, r_read]
    tmp = tempfile.mkdtemp(prefix="rec8_writes.", dir=os.path.join(ROOT, "build", "tmp"))
    try:
        v, z_read = views(export_root, romdir, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    read += z_read
    docs = []
    for tenant, rel in recs:
        raw = open(os.path.join(export_root, rel), "rb").read()
        read.append((rel, sha1(raw)))
        docs.append((tenant, json.loads(raw)))
    return {"docs": docs, "table": table, "origins": origins, "roster": roster, "views": v, "read": read}


def measure(inp, perturb=None):
    """(printed lines, results). results: writes [(tenant, row, same, address, value)], rows [(tenant, aliased, vs2 differs)],
    readers [(set, sites, sites indexed from +0x382)]. `perturb` names a control of tests/test_rec8_writes.py."""
    table, origins, roster = inp["table"], inp["origins"], inp["roster"]
    base = {n: int(table[("bank_map.toml", "table", n, "vsavj")], 16) for n in ROWS}
    stride = {n: int(table[("bank_map.toml", "table", n, "stride")], 16) // 32 for n in ROWS}
    oj = int(origins[("bank_map.toml", "origins", "#1", "vsavj")], 16)
    o2 = int(origins[("bank_map.toml", "origins", "#1", "vsav2")], 16)
    vj, v2 = inp["views"]["vsavj"][1], inp["views"]["vsav2"][1]
    out, res = [], {"writes": [], "rows": [], "readers": []}
    for k, (tenant, doc) in enumerate(inp["docs"]):
        tid = int(roster[("%s.toml" % tenant, "tenant", tenant, "id")], 16)
        for kv in roster.get(("%s.toml" % tenant, "tenant", tenant, "id_by_profile"), "").strip('"').split(","):
            key, _, val = kv.partition("=")
            if key.strip() == PROFILE:
                tid = int(val, 16)
        src = int(doc["char"], 16)
        vals = {r["table"]: r for r in doc["values"]}
        out.append("%s: id %#04x on %s, source char %#04x, variant mirror %s" % (tenant, tid, PROFILE, src,
                                                                                 "yes" if tid < 0x10 else "no"))
        for n in ROWS:
            value = bytes.fromhex(vals[n]["value"])
            if perturb == "value-flipped" and k == 0 and n == ROWS[0]:
                value = bytes([value[0] ^ 1]) + value[1:]
            at = base[n] + tid * stride[n]
            there = vj[at:at + len(value)]
            res["writes"].append((tenant, n, there == value, at, value))
            out.append("  %s: record %s, written at PRG:0x%06X, vsavj there %s: %s" % (
                n, value.hex(), at, there.hex(), "SAME" if there == value else "DIFFERS"))
        own = base[SLICED] + tid * SLICED_ROW
        base_row = (tid & 0x0F) + (1 if perturb == "row-unaliased" and k == 0 else 0)
        alias = base[SLICED] + base_row * SLICED_ROW
        theirs = o2 + base[SLICED] - oj + src * SLICED_ROW
        row = vj[own:own + SLICED_ROW]
        aliased, differs = row == vj[alias:alias + SLICED_ROW], v2[theirs:theirs + SLICED_ROW] != row
        res["rows"].append((tenant, aliased, differs))
        out.append("  own row PRG:0x%06X: vsavj %s; equals vsavj row %#04x: %s" % (
            own, row.hex(), base_row, "yes" if aliased else "no"))
        out.append("  vs2 row PRG:0x%06X: %s; equals vsavj's own row: %s" % (
            theirs, v2[theirs:theirs + SLICED_ROW].hex(), "no" if differs else "yes"))
    load_op = bytes.fromhex("102e0383") if perturb == "index-elsewhere" else INDEX_LOAD
    for s, t in (("vsavj", base[SLICED]), ("vsav2", o2 + base[SLICED] - oj)):
        op = inp["views"][s][0]
        sites = [m.start() for m in re.finditer(re.escape(bytes.fromhex("207c") + t.to_bytes(4, "big")), op)]
        res["readers"].append((s, len(sites), sum(op[a - 10:a - 6] == load_op for a in sites)))
        out.append("reader %s: movea.l #$%X,a0 at %s; index loaded from +0x382 ten bytes before: %s" % (
            s, t, ", ".join("PRG:0x%06X" % a for a in sites) or "none",
            ", ".join("yes" if op[a - 10:a - 6] == load_op else "no" for a in sites) or "-"))
    out.append("rec8 writes equal to vsavj's bytes: %d of %d" % (sum(w[2] for w in res["writes"]), len(res["writes"])))
    return out, res


def built(inp, out_dir):
    """Lines on a merged build's own output: its data view at each write and over the sliced table, and its ops."""
    table = inp["table"]
    paths = {n: os.path.join(out_dir, n) for n in ("vanilla_data.bin", "verify_data.bin", "patch/patch.json")}
    blobs = {n: open(p, "rb").read() for n, p in paths.items()}
    inp["read"] += [(p, sha1(blobs[n])) for n, p in paths.items()]
    van, ver = blobs["vanilla_data.bin"], blobs["verify_data.bin"]
    lines = ["built: vanilla_data.bin equals vsavj's data view: %s" % (
        "yes" if van == inp["views"]["vsavj"][1][:len(van)] else "no")]
    for tenant, n, _, at, value in measure(inp)[1]["writes"]:
        lines.append("built: %s %s at PRG:0x%06X: build %s: %s" % (
            tenant, n, at, ver[at:at + len(value)].hex(), "the record's value" if ver[at:at + len(value)] == value
            else "NOT the record's value"))
    lo = int(table[("bank_map.toml", "table", SLICED, "vsavj")], 16)
    hi = lo + 32 * SLICED_ROW
    ops = json.loads(blobs["patch/patch.json"])["ops"]
    sizes = {"poke32": 4, "poke16": 2, "poke8": 1}

    def span(o):
        a = int(o["addr"], 16)
        return a, a + sizes.get(o["op"], len(bytes.fromhex(o.get("hex", ""))))
    touch = [o for o in ops if "addr" in o and span(o)[0] < hi and span(o)[1] > lo]
    for o in touch:
        a, b = span(o)
        lines.append("built: op %s at PRG:0x%06X +%d: build %s, vanilla %s: %s" % (
            o["op"], a, b - a, ver[a:b].hex(), van[a:b].hex(), "SAME" if ver[a:b] == van[a:b] else "DIFFERS"))
    lines.append("built: ops %d, touching PRG:0x%06X-0x%06X %d; bytes of it differing from vanilla %d" % (
        len(ops), lo, hi, len(touch), sum(ver[a] != van[a] for a in range(lo, hi))))
    return lines


def main():
    args = sys.argv[1:]
    out_dir = None
    if "--built" in args:
        i = args.index("--built")
        out_dir, args = args[i + 1], args[:i] + args[i + 2:]
    if len(args) != 2:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    inp = load(*args)
    for line in measure(inp)[0] + (built(inp, out_dir) if out_dir else []):
        print(line)
    for p, h in inp["read"]:
        print("read %s sha1 %s" % (p, h))


if __name__ == "__main__":
    main()
