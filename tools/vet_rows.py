"""vet_rows.py — the newcomers' own rows of the five veteran-move tables, read from vs2 (#6; docs/project/tables/README.md
"The five veteran moves").

Each table is read by a veteran's move with the VICTIM's raw id `+0x382` (tools/vet_moves.py): Bulleta's ES pursuit,
Gallon's Wild Circular, Zabel's Hell Dunk, Morrigan's Cryptic Needle and Felicia's headsit. Each table, its vs2 twin,
its row size and the view it is read in are the raw-id census's (docs/project/tables/raw_id_census.tsv, gated against
the dumps by tests/test_raw_id_census.py). The newcomers take vs2's rows ([VSR-40]: a row of a vs2-only character's
own), so this reads each tenant's row from vs2 at the twin + id * row size in the table's view, the id being the
tenant's vs2 char id (`extraction/runs.tsv`), with vsavj's row at the same id beside it.

It also measures the SHAPE the port rests on, per table and on all 32 ids: vsavj's variant half (ids 0x10-0x1F) is a
copy of its base half (so the rows are storage and the newcomers' are the shells', [VSE-10]), and vs2's base half
equals vsavj's (so a veteran victim reads the same row on both games, and Victor is the rig's control).

What a row's fields are (a reading of the code, R-007): Bulleta's, Morrigan's and Felicia's two signed words are the
offset at which a fighter is put from another; Gallon's word is added to her `+0x3A`; Zabel's byte is the victim's
capture POSE index.

Values are discrete per-character values (CLAUDE.md [VSR-8]). Prints the SHA-1 of every file it read ([VSR-10]).
`--write` writes docs/project/tables/vet_rows.tsv; its gate is tests/test_vet_rows_table.py.

Usage: python3 tools/vet_rows.py <export root> <rom dir> [--write]
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doll_hop import runs  # noqa: E402
from extract_regions import sha1  # noqa: E402
from rec8_writes import views  # noqa: E402
from vet_moves import MOVES  # noqa: E402

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TABLES = os.path.join(ROOT, "docs", "project", "tables")
CENSUS = os.path.join(TABLES, "raw_id_census.tsv")
OUT = os.path.join(TABLES, "vet_rows.tsv")
IDS = 32                           # the tables' ids, 0x00-0x1F
LAYOUT = {1: "u8", 2: "s16", 4: "s16,s16"}
COLUMNS = ("move", "table", "view", "layout", "tenant", "id", "value", "vsavj_value", "vs2_row")
PIN = "bf92acd2"


def census():
    """{vsavj table: census row}, and the census's SHA-1."""
    out, cols = {}, None
    for line in open(CENSUS):
        c = line.rstrip("\n").split("\t")
        if line.startswith("#"):
            continue
        if cols is None:
            cols = c
            continue
        out[c[0]] = dict(zip(cols, c))
    return out, (os.path.relpath(CENSUS, ROOT), sha1(open(CENSUS, "rb").read()))


def value(raw):
    """A row as its fields: unsigned hex for a byte, signed decimal words otherwise."""
    if len(raw) == 1:
        return "0x%02X" % raw[0]
    return ",".join(str(int.from_bytes(raw[i:i + 2], "big", signed=True)) for i in range(0, len(raw), 2))


def raw_of(text, size):
    """value() inverted."""
    if size == 1:
        return bytes([int(text, 16)])
    return b"".join(int(v).to_bytes(2, "big", signed=True) for v in text.split(","))


def load(export_root, romdir):
    """Everything measure() reads, and the SHA-1 of each file."""
    cen, c_read = census()
    tenants, r_read = runs()
    os.makedirs(os.path.join(ROOT, "build", "tmp"), exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="vet_rows.", dir=os.path.join(ROOT, "build", "tmp"))
    try:
        v, z_read = views(export_root, romdir, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    tables = []
    for move, m in MOVES.items():
        c = cen.get(m["table"])
        if c is None or c["paired"] != "aligned":
            raise SystemExit("REFUSED: the census has no aligned row for %s's table %s" % (move, m["table"]))
        tables.append((move, int(c["vsavj"][4:], 16), int(c["vsav2"][4:], 16), int(c["row"], 16), c["view"],
                       c["vs2_differs"]))
    return {"tables": tables, "tenants": tenants, "views": v, "read": [c_read, r_read] + z_read}


def measure(inp, perturb=None):
    """(printed lines, results). results: rows [dict of COLUMNS], shape [(move, variant half copies the base half,
    vs2's base half equals vsavj's)], differs [(move, tenant, vs2's row differs, the census's vs2_differs says so)].
    `perturb` names a control of tests/test_vet_rows_table.py that acts on the measurement."""
    out, res = [], {"rows": [], "shape": [], "differs": []}
    for move, bj, b2, size, view, census_differs in inp["tables"]:
        k = 0 if view == "op" else 1
        vj, v2 = bytearray(inp["views"]["vsavj"][k]), inp["views"]["vsav2"][k]
        if perturb == "shape-broken" and move == "zabel":
            vj[bj + 0x1F * size] ^= 1
        if perturb == "census-all-differ":
            census_differs = "dhp"
        rj = [bytes(vj[bj + i * size:bj + (i + 1) * size]) for i in range(IDS)]
        r2 = [v2[b2 + i * size:b2 + (i + 1) * size] for i in range(IDS)]
        copies = rj[16:] == rj[:16]
        same = r2[:16] == rj[:16]
        res["shape"].append((move, copies, same))
        out.append("%s table PRG:0x%06X (vs2 PRG:0x%06X), rows of %d, %s view: vsavj's ids 0x10-0x1F copy 0x00-0x0F: "
                   "%s; vs2's ids 0x00-0x0F equal vsavj's: %s" % (
                       move, bj, b2, size, view, "yes" if copies else "no", "yes" if same else "no"))
        letters = {"donovan": census_differs[0] == "d", "huitzil": census_differs[1] == "h",
                   "pyron": census_differs[2] == "p"}
        for tenant, cid in inp["tenants"]:
            row = {"move": move, "table": "PRG:0x%06X" % bj, "view": view, "layout": LAYOUT[size],
                   "tenant": tenant, "id": "0x%02x" % cid, "value": value(r2[cid]), "vsavj_value": value(rj[cid]),
                   "vs2_row": "PRG:0x%06X" % (b2 + cid * size)}
            res["rows"].append(row)
            res["differs"].append((move, tenant, r2[cid] != rj[cid], letters[tenant]))
            out.append("  %s id %s at vs2 %s: %s (vsavj %s)%s" % (
                tenant, row["id"], row["vs2_row"], row["value"], row["vsavj_value"],
                "" if r2[cid] != rj[cid] else ", the same"))
    return out, res


def render(inp, rows):
    read = ", ".join("%s %s" % (p, h[:12]) for p, h in inp["read"])
    head = ["# vet_rows.tsv — GAMEPLAY: each tenant's own row of the five veteran-move tables, from vs2 (the victim's "
            "row: the offset, word or pose index the veteran's move reads for it).",
            "# GENERATED by tools/vet_rows.py from vsav2 and the original at %s; do not hand-edit before phase 1 "
            "builds from it (docs/project/tables/README.md)." % PIN,
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
