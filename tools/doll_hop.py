"""doll_hop.py — the newcomers' own rows of the doll-hop table, read from vs2 (#6; docs/project/tables/README.md "The
doll's hop, vs2's rows").

The table at vsavj `PRG:0x0BE3FA` (vs2 `PRG:0x0D8598`) is each character's hop as a paper doll after Anakaris's Royal
Judgement (R-005, measured): row id*0x20, two variants of 0x10 picked by `+0x0A`, each four signed 16.16 longs
(xv, xaccel, yv, yaccel; the original's *"four longs (xv, xacc, yv, yacc) x 2 variants per char"*). Both games index
it by the raw id `+0x382`. The newcomers take vs2's rows (ruled 2026-10-20, `SPEC.md` §0), so this reads them from
vs2's data view at vs2's table + id*0x20 + variant*0x10, the id being the tenant's vs2 char id
(`extraction/runs.tsv`). The vs2 table address is computed from the original's facts (`facts/origins.tsv`,
`facts/table.tsv`: `rec8_b`'s vsavj base, which is this table) and confirmed against each game's code: one
`movea.l #table,a0`, its index loaded from +0x382 ten bytes before.

Values are discrete per-character values (CLAUDE.md [VSR-8]). Prints the SHA-1 of every file it read ([VSR-10]).
`--write` writes docs/project/tables/doll_hop.tsv; its gate is tests/test_doll_hop_table.py.

Usage: python3 tools/doll_hop.py <export root> <rom dir> [--write]
"""
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_regions import fixed, sha1  # noqa: E402
from rec8_writes import INDEX_LOAD, facts, views  # noqa: E402

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TABLES = os.path.join(ROOT, "docs", "project", "tables")
OUT = os.path.join(TABLES, "doll_hop.tsv")
TABLE = "rec8_b"                   # the original's name for the table's slice in bank_map.toml
ROW, VARIANT = 0x20, 0x10
FIELDS = ("xv", "xaccel", "yv", "yaccel")
COLUMNS = ("tenant", "id", "variant") + FIELDS + ("vs2_row",)
PIN = "bf92acd2"


def runs():
    path = os.path.join(TABLES, "extraction", "runs.tsv")
    out = []
    for line in open(path):
        c = line.rstrip("\n").split("\t")
        if not line.startswith("#") and c[0] != "tenant":
            out.append((c[0], int(c[4], 16)))
    return out, (os.path.relpath(path, ROOT), sha1(open(path, "rb").read()))


def load(export_root, romdir):
    """Everything measure() reads, and the SHA-1 of each file."""
    table, t_read = facts(os.path.join("facts", "table.tsv"))
    origins, o_read = facts(os.path.join("facts", "origins.tsv"))
    tenants, r_read = runs()
    os.makedirs(os.path.join(ROOT, "build", "tmp"), exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="doll_hop.", dir=os.path.join(ROOT, "build", "tmp"))
    try:
        v, z_read = views(export_root, romdir, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return {"table": table, "origins": origins, "tenants": tenants, "views": v,
            "read": [t_read, o_read, r_read] + z_read}


def measure(inp, perturb=None):
    """(printed lines, results). results: rows [dict of COLUMNS], readers [(set, sites, indexed from +0x382)],
    differs [(tenant, vs2's row differs from vsavj's at the id)]. `perturb` names a control of
    tests/test_doll_hop_table.py that acts on the measurement."""
    base_j = int(inp["table"][("bank_map.toml", "table", TABLE, "vsavj")], 16)
    oj = int(inp["origins"][("bank_map.toml", "origins", "#1", "vsavj")], 16)
    o2 = int(inp["origins"][("bank_map.toml", "origins", "#1", "vsav2")], 16)
    base_2 = o2 + base_j - oj
    vj, v2 = inp["views"]["vsavj"][1], inp["views"]["vsav2"][1]
    if perturb == "rows-equal":
        vj = bytearray(vj)
        for _, cid in inp["tenants"]:
            vj[base_j + cid * ROW:base_j + (cid + 1) * ROW] = v2[base_2 + cid * ROW:base_2 + (cid + 1) * ROW]
    out, res = [], {"rows": [], "readers": [], "differs": []}
    load_op = bytes.fromhex("102e0383") if perturb == "index-elsewhere" else INDEX_LOAD
    for s, t in (("vsavj", base_j), ("vsav2", base_2)):
        op = inp["views"][s][0]
        sites = [m.start() for m in re.finditer(re.escape(bytes.fromhex("207c") + t.to_bytes(4, "big")), op)]
        res["readers"].append((s, len(sites), sum(op[a - 10:a - 6] == load_op for a in sites)))
        out.append("reader %s: movea.l #$%X,a0 at %s; index loaded from +0x382 ten bytes before: %s" % (
            s, t, ", ".join("PRG:0x%06X" % a for a in sites) or "none",
            ", ".join("yes" if op[a - 10:a - 6] == load_op else "no" for a in sites) or "-"))
    for tenant, cid in inp["tenants"]:
        res["differs"].append((tenant, v2[base_2 + cid * ROW:base_2 + (cid + 1) * ROW]
                               != vj[base_j + cid * ROW:base_j + (cid + 1) * ROW]))
        for var in (0, 1):
            at = base_2 + cid * ROW + var * VARIANT
            row = {"tenant": tenant, "id": "0x%02x" % cid, "variant": str(var), "vs2_row": "PRG:0x%06X" % at}
            for k, f in enumerate(FIELDS):
                row[f] = fixed(v2[at + 4 * k:at + 4 * k + 4])
            res["rows"].append(row)
            out.append("%s id %s variant %d at vs2 PRG:0x%06X: %s" % (
                tenant, row["id"], var, at, ", ".join("%s %s" % (f, row[f]) for f in FIELDS)))
        out.append("%s: vs2's row differs from vsavj's row at PRG:0x%06X: %s" % (
            tenant, base_j + cid * ROW, "yes" if res["differs"][-1][1] else "no"))
    return out, res


def render(inp, rows):
    read = ", ".join("%s %s" % (p, h[:12]) for p, h in inp["read"])
    head = ["# doll_hop.tsv — GAMEPLAY: each tenant's own two rows of the doll-hop table, from vs2, as 16.16 values.",
            "# GENERATED by tools/doll_hop.py from vsav2 and the original at %s; do not hand-edit before phase 1 builds "
            "from it (docs/project/tables/README.md)." % PIN,
            "# read: " + read,
            "\t".join(COLUMNS)]
    return "\n".join(head + ["\t".join(r[c] for c in COLUMNS) for r in rows]) + "\n"


def main():
    args = sys.argv[1:]
    write = "--write" in args
    args = [a for a in args if a != "--write"]
    if len(args) != 2:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    inp = load(*args)
    lines, res = measure(inp)
    for line in lines:
        print(line)
    for p, h in inp["read"]:
        print("read %s sha1 %s" % (p, h))
    if write:
        with open(OUT, "w") as f:
            f.write(render(inp, res["rows"]))
        print("wrote %s (%d rows)" % (os.path.relpath(OUT, ROOT), len(res["rows"])))


if __name__ == "__main__":
    main()
