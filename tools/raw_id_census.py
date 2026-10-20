"""raw_id_census.py — every table the engine reads by the raw character id `+0x382`, with the newcomers' rows in
vsavj, in vs2 and on a build (#6; docs/project/tables/README.md "The raw-id census").

Why: in the original's build a newcomer (Donovan 0x13, Huitzil/Phobos 0x10, Pyron 0x11) reads whatever vsavj holds at
its id where nothing was ported, and the doll-hop table at `PRG:0x0BE3FA` was found that way, by accident (R-005). By
the ground rule (CLAUDE.md [VSR-40]) a character-specific row is vs2's. A missing row produces no symptom to steer
toward, so the list is made by enumerating ([VSR-186]); the doll table, measured in play (R-005, R-006), is the
anchor the static reading must reproduce ([VSR-187]).

How, on each game's opcode view (the original's cps2_decrypt.py):
  1. SITES: every `move.b`/`move.w $382(An),Dn` at an even offset below 0x400000;
  2. ACCESS: from each site, capstone's 68000 disassembly forward (at most 14 instructions, stopping at a branch),
     following the id register through register copies and its scaling (`add.w Dn,Dn`, `lsl`/`asl #k`, `mulu #k`),
     to the first indexed access by it: `(pc|An, Dn.w)` or `adda.w Dn,An`. The table base is the access's own
     pc-relative address, or the An base loaded by `lea`/`movea.l` before it plus the access's displacement; the
     row size is the scaling. A site whose id reaches no indexed access (a compare, a call argument) is counted,
     not tabled;
  3. PAIRING: a vsavj table and its vs2 twin. Inside the per-character bank (`PRG:0x0BCE7A`-`0x0BF700`) by the
     bank's one shift (`facts/origins.tsv`), elsewhere by aligning the two games' ordered site lists by shape
     (instruction text with every `$` value masked, and the row size): two official builds of one engine read their
     tables in the same order ([VSR-38], [VSR-78]: pair through the code, never by a byte pattern). Where the
     alignment names another twin for a bank table, both are reported;
  4. KIND: `code-dispatch` (a pc-relative word table followed by `jmp`/`jsr` through it: its entry count is its
     smallest positive target offset / 2, [VSR-94]), `code-value` (any other table below `PRG:0x0BC000`, in code:
     its extent is not measured), `pointer` (rows of 4 whose 32 vsavj entries are all even and below 0x400000),
     `value` (the rest);
  5. VIEW: a `(d8,PC,Xn)` read is a program-space fetch, which CPS-2 decrypts like an opcode, so its table is read
     in the opcode view; any other read is a data fetch and its table is read in the data view ([VSR-87]);
  6. ROWS: per newcomer, vs2's row at the id against vsavj's (`vs2_differs`), and whether vsavj's row at the id
     equals its base-half row at id & 0x0F (`shell`). For a pointer table vs2's row always differs (the two
     address spaces differ), so only the target's content could say more; that is not read here. `vs2_own`: vs2's
     row at the id differs from vs2's own row at id & 0x0F, so vs2 gives the newcomer a row of its own; it compares
     within one game, so it holds for pointer and code tables too.
With `--built DIR` (a merged build's output: `verify_data.bin`, `verify_op.bin`), each newcomer row on that build:
`vs2` (equal to vs2's row), `vanilla` (unchanged from vsavj), `rewritten` (neither), and whether the build changed
the reading site's code (its first 16 bytes).

Values are addresses, sizes and flags (CLAUDE.md [VSR-8]). Prints the SHA-1 of every file it read ([VSR-10]).
`--write` writes docs/project/tables/raw_id_census.tsv (the dumps' facts only); its gate is
tests/test_raw_id_census.py.

Usage: python3 tools/raw_id_census.py <export root> <rom dir> [--built DIR] [--write]
"""
import collections
import difflib
import hashlib
import os
import re
import shutil
import sys
import tempfile

import capstone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_regions import sha1  # noqa: E402
from rec8_writes import facts, views  # noqa: E402

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "docs", "project", "tables", "raw_id_census.tsv")
PIN = "bf92acd2"
BANK = (0x0BCE7A, 0x0BF700)
CODE_END = 0x0BC000
TENANTS = (("donovan", 0x13), ("huitzil", 0x10), ("pyron", 0x11))
COLUMNS = ("vsavj", "row", "view", "vsav2", "paired", "kind", "entries_vsavj", "entries_vsav2", "sites", "vs2_differs",
           "shell", "vs2_own")
MD = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000)
MD.detail = False


def imm(x):
    x = x.lstrip("#")
    return int(x[1:], 16) if x.startswith("$") else int(x, 0)


def id_loads(op, perturb=None):
    disp = b"\x03\x83" if perturb == "blind-scan" else b"\x03\x82"
    return [a for a in range(0, min(len(op), 0x400000) - 4, 2)
            if (int.from_bytes(op[a:a + 2], "big") & 0xF1F8) in (0x1028, 0x3028) and op[a + 2:a + 4] == disp]


def follow(op, a):
    """The indexed access an id load reaches: {site, row, base, shape, dispatch} or None."""
    ins = list(MD.disasm(op[a:a + 96], a))[:14]
    if not ins:
        return None
    regs, row, abase, text, view = {ins[0].op_str.split(",")[-1].strip()}, 1, {}, [], 1
    for k, i in enumerate(ins):
        m, ops = i.mnemonic, [x.strip() for x in i.op_str.split(",")]
        text.append("%s %s" % (m, i.op_str))
        if (k and m.startswith(("move.", "movea.")) and len(ops) == 2 and ops[0] in regs
                and re.fullmatch(r"d\d", ops[1])):
            regs.add(ops[1])
        if m.startswith("add.") and len(ops) == 2 and ops[0] == ops[1] and ops[1] in regs:
            row *= 2
        if re.fullmatch(r"(lsl|asl)\.[bwl]", m) and len(ops) == 2 and ops[1] in regs and ops[0].startswith("#"):
            row <<= imm(ops[0])
        if m.startswith("mulu") and ops[-1] in regs and ops[0].startswith("#"):
            row *= imm(ops[0])
        if m.startswith(("lea", "movea.l")) and len(ops) == 2 and re.fullmatch(r"a\d", ops[1]):
            mm = re.fullmatch(r"#?\$([0-9a-f]+)(?:\.[wl])?(?:\(pc\))?", ops[0])
            if mm:
                abase[ops[1]] = int(mm.group(1), 16)
        idx = re.search(r"(?:\$([0-9a-f]+))?\((pc|a\d),\s*(d\d)\.[wl]", i.op_str)
        base = None
        if k and idx and idx.group(3) in regs:
            d = int(idx.group(1), 16) if idx.group(1) else 0
            if idx.group(2) == "pc":
                base, view = d, 0
            elif idx.group(2) in abase:
                base = abase[idx.group(2)] + (d - 0x10000 if d >= 0x8000 else d)
            else:
                return {"site": a, "row": row, "base": None, "shape": "", "dispatch": False}
        elif k and m.startswith("adda") and ops[0] in regs:
            if ops[1] not in abase:
                return {"site": a, "row": row, "base": None, "shape": "", "dispatch": False}
            base = abase[ops[1]]
        if base is not None:
            nxt = ins[k + 1] if k + 1 < len(ins) else None
            dispatch = bool(nxt and nxt.mnemonic.startswith(("jmp", "jsr")) and "(pc," in nxt.op_str
                            and "$%x(" % base in nxt.op_str)
            return {"site": a, "row": row, "base": base, "dispatch": dispatch, "view": view,
                    "shape": re.sub(r"\$[0-9a-f]+", "$X", " ; ".join(text)) + "|%d" % row}
        if k and m.startswith(("rts", "rte", "jmp", "jsr", "bra", "bsr", "b", "db")) and m not in (
                "btst", "bset", "bclr", "bchg"):
            return None
    return None


def entries(op, base):
    """A word dispatch table's entry count: the entries before its smallest positive target offset, read only while
    still inside the table ([VSR-94])."""
    k, limit = 0, 0x10000
    while 2 * k < limit and k < 0x100:
        o = int.from_bytes(op[base + 2 * k:base + 2 * k + 2], "big", signed=True)
        if o > 0:
            limit = min(limit, o)
        k += 1
    return k


def load(export_root, romdir, built=None):
    t_rows, t_read = facts(os.path.join("facts", "origins.tsv"))
    os.makedirs(os.path.join(ROOT, "build", "tmp"), exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="raw_id_census.", dir=os.path.join(ROOT, "build", "tmp"))
    try:
        v, z_read = views(export_root, romdir, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    inp = {"origins": t_rows, "views": v, "read": [t_read] + z_read, "built": None}
    if built:
        blobs = {n: open(os.path.join(built, n), "rb").read() for n in ("verify_data.bin", "verify_op.bin")}
        inp["built"] = blobs
        inp["read"] += [(os.path.join(built, n), hashlib.sha1(b).hexdigest()) for n, b in blobs.items()]
    return inp


def measure(inp, perturb=None):
    """(lines, results): results tables [dict of COLUMNS], counts, built [(table, tenant, class, site patched)],
    twins {vsavj site: its vs2 twin site, by the alignment}."""
    oj = int(inp["origins"][("bank_map.toml", "origins", "#1", "vsavj")], 16)
    o2 = int(inp["origins"][("bank_map.toml", "origins", "#1", "vsav2")], 16)
    if perturb == "shift-off":
        o2 += 0x80
    sites, n_loads = {}, {}
    for g in ("vsavj", "vsav2"):
        op = inp["views"][g][0]
        loads = id_loads(op, perturb)
        n_loads[g] = len(loads)
        sites[g] = [f for f in (follow(op, a) for a in loads) if f]
    seq = {g: [s for s in sites[g] if s["base"] is not None] for g in sites}
    twin = {}
    sm = difflib.SequenceMatcher(None, [s["shape"] for s in seq["vsavj"]], [s["shape"] for s in seq["vsav2"]],
                                 autojunk=False)
    for tag, i1, i2, j1, _ in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                twin[seq["vsavj"][i1 + k]["site"]] = seq["vsav2"][j1 + k]
    tables = collections.defaultdict(list)
    for s in seq["vsavj"]:
        tables[(s["base"], s["row"], s["view"])].append(s)
    vj, v2 = inp["views"]["vsavj"], inp["views"]["vsav2"]
    rows, unpaired, out, built = [], [], [], []
    for (b, r, w), ss in sorted(tables.items()):
        got = sorted({twin[s["site"]]["base"] for s in ss if s["site"] in twin})
        if BANK[0] <= b < BANK[1]:
            b2 = b + o2 - oj
            paired = "bank" if got in ([], [b2]) else "bank; alignment says " + ",".join("PRG:0x%06X" % x for x in got)
        elif len(got) == 1:
            b2, paired = got[0], "aligned"
        else:
            unpaired.append((b, r, ss))
            continue
        dispatch = any(s["dispatch"] for s in ss)
        if b < CODE_END:
            kind = "code-dispatch" if dispatch else "code-value"
        elif r == 4 and all(int.from_bytes(vj[w][b + 4 * k:b + 4 * k + 4], "big") % 2 == 0
                            and int.from_bytes(vj[w][b + 4 * k:b + 4 * k + 4], "big") < 0x400000 for k in range(32)):
            kind = "pointer"
        else:
            kind = "value"
        ent = (str(entries(vj[0], b)), str(entries(v2[0], b2))) if kind == "code-dispatch" else ("-", "-")
        differs, shell, own = [], [], []
        for name, i in TENANTS:
            J, V = vj[w][b + i * r:b + (i + 1) * r], v2[w][b2 + i * r:b2 + (i + 1) * r]
            S = vj[w][b + (i & 15) * r:b + ((i & 15) + 1) * r]
            differs.append(name[0] if J != V else "-")
            shell.append(name[0] if J == S else "-")
            own.append(name[0] if V != v2[w][b2 + (i & 15) * r:b2 + ((i & 15) + 1) * r] else "-")
            if inp["built"]:
                B = inp["built"]["verify_op.bin" if w == 0 else "verify_data.bin"][b + i * r:b + (i + 1) * r]
                cls = "vs2" if B == V else ("vanilla" if B == J else "rewritten")
                patched = any(inp["built"]["verify_op.bin"][s["site"]:s["site"] + 16] != vj[0][s["site"]:s["site"] + 16]
                              for s in ss)
                built.append(("PRG:0x%06X" % b, name, cls, patched))
        rows.append({"vsavj": "PRG:0x%06X" % b, "row": "0x%X" % r, "view": "op" if w == 0 else "data",
                     "vsav2": "PRG:0x%06X" % b2, "paired": paired,
                     "kind": kind, "entries_vsavj": ent[0], "entries_vsav2": ent[1],
                     "sites": " ".join("PRG:0x%06X" % s["site"] for s in ss), "vs2_differs": "".join(differs),
                     "shell": "".join(shell), "vs2_own": "".join(own)})
    counts = {"loads_vsavj": n_loads["vsavj"], "loads_vsav2": n_loads["vsav2"],
              "indexed_vsavj": sum(1 for s in sites["vsavj"]), "tables": len(rows), "unpaired": len(unpaired),
              "no_base": sum(1 for s in sites["vsavj"] if s["base"] is None)}
    out.append("id loads: vsavj %(loads_vsavj)d, vsav2 %(loads_vsav2)d; vsavj loads reaching an indexed access "
               "%(indexed_vsavj)d (no resolvable base %(no_base)d); tables paired %(tables)d, unpaired "
               "%(unpaired)d" % counts)
    for b, r, ss in unpaired:
        out.append("UNPAIRED PRG:0x%06X row 0x%X, sites %s" % (b, r, " ".join("PRG:0x%06X" % s["site"] for s in ss)))
    for row in rows:
        out.append("\t".join(row[c] for c in COLUMNS))
    port = [(row, name) for row in rows for name, _ in TENANTS if name[0] in row["shell"] and name[0] in row["vs2_own"]]
    by_kind = collections.Counter(row["kind"] for row, _ in port)
    out.append("to port (vsavj's row a shell copy, vs2's its own): rows %d in tables %d; %s" % (
        len(port), len({row["vsavj"] for row, _ in port}), ", ".join("%s %d" % kv for kv in sorted(by_kind.items()))))
    for t, name, cls, patched in built:
        out.append("built %s %s: %s%s" % (t, name, cls, ", reading site patched" if patched else ""))
    if built:
        c = collections.Counter(x[2] for x in built)
        out.append("built: rows %d, vs2 %d, vanilla %d, rewritten %d" % (len(built), c["vs2"], c["vanilla"],
                                                                         c["rewritten"]))
        cls = {(t, name): x for t, name, x, _ in built}
        left = [(row, name) for row, name in port if cls[(row["vsavj"], name)] == "vanilla"]
        for row, name in left:
            out.append("built: left on vanilla's shell row: %s (%s, row 0x%s) %s" % (
                row["vsavj"], row["kind"], row["row"][2:], name))
        out.append("built: rows to port %d, left on vanilla's shell row %d in tables %d; %s" % (
            len(port), len(left), len({row["vsavj"] for row, _ in left}),
            ", ".join("%s %d" % kv for kv in sorted(collections.Counter(row["kind"] for row, _ in left).items()))))
    return out, {"tables": rows, "counts": counts, "built": built,
                 "twins": {s: t["site"] for s, t in twin.items()}}


def render(inp, rows):
    read = ", ".join("%s %s" % (p, h[:12]) for p, h in inp["read"] if not p.endswith(".bin"))
    head = ["# raw_id_census.tsv — FACTS: every table vsavj reads by the raw character id +0x382, its vs2 twin, and "
            "the newcomers' rows in both games.",
            "# GENERATED by tools/raw_id_census.py from vsavj, vsav2 and the original at %s; do not hand-edit "
            "(docs/project/tables/README.md)." % PIN,
            "# read: " + read,
            "\t".join(COLUMNS)]
    return "\n".join(head + ["\t".join(r[c] for c in COLUMNS) for r in rows]) + "\n"


def main():
    args = sys.argv[1:]
    built = None
    if "--built" in args:
        i = args.index("--built")
        built, args = args[i + 1], args[:i] + args[i + 2:]
    write = "--write" in args
    args = [a for a in args if a != "--write"]
    if len(args) != 2:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    inp = load(args[0], args[1], built)
    lines, res = measure(inp)
    for line in lines:
        print(line)
    for p, h in inp["read"]:
        print("read %s sha1 %s" % (p, h))
    if write:
        with open(OUT, "w") as f:
            f.write(render(inp, res["tables"]))
        print("wrote %s (%d rows)" % (os.path.relpath(OUT, ROOT), len(res["tables"])))


if __name__ == "__main__":
    main()
