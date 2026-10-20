"""raw_id_owners.py — whose code reads each of the raw-id census's left-on-shell tables, and by whose id (#6;
docs/project/tables/README.md "What reaches the left-on-shell tables").

Static, on vsavj's opcode view, for every reading site of a table the census leaves on the shell's row on a build:
  WHOSE ID   the register the site reads `+0x382` through: `a6`, the running object itself (`own`); a register
             loaded by `movea.w $32(aN),aM` within the six instructions before it, the fighter linked to aN
             (`linked to aN`: for a fighter, its opponent; for a projectile or effect, the fighter it is tied to);
             anything else `unresolved`;
  REACHED BY a backward walk from the site: through fall-through to the nearest address something references,
             then to each referencing instruction, up to 7 levels. A reference is a branch, `jsr`/`jmp`, a
             `lea`/`pea` pc-relative operand, an entry of a pc-relative word dispatch table (`jmp`/`jsr
             (d8,PC,Dn.w)`, its count by tools/raw_id_census.py's rule), or a long pointing at it: in the data view
             anywhere below 0x400000, and in the opcode view below CODE_END (tables read pc-relatively are
             decrypted, [VSR-87]). A walk ends at a long in the per-character bank (`bank row`, the character ids
             whose row points there) or in a long table read by `movea.l (d8,PC,Dn.w)` (`type table`, its base
             and the entry, the index being the object's TYPE byte for the two pool walkers), else at `no
             reference`, or at `walk limit` after 7 levels.
The disassembly is linear (capstone, 68000), so a reference from code it mis-decodes is missed: a walk that ends at
`no reference` is unanswered, not unreached. Which fighter spawns a projectile or effect TYPE is not walked (many
spawn sites share a type); tools/raw_id_reach.py's corpus names the fighter whose code ran.

Prints the SHA-1 of every file it read ([VSR-10]). Values are addresses and ids ([VSR-8]).

Usage: python3 tools/raw_id_owners.py <export root> <rom dir> <build dir>
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raw_id_census import BANK, CODE_END, MD, entries  # noqa: E402
from raw_id_reach import sites  # noqa: E402

BRANCH = ("eq", "ne", "cc", "cs", "pl", "mi", "ge", "lt", "gt", "le", "hi", "ls", "vc", "vs")


def disassemble(op):
    """(instructions {addr: insn}, refs {target: {(from, how)}}, prev {next addr: addr it falls from})."""
    ins, refs, prev = {}, collections.defaultdict(set), {}
    a = 0x400
    while a < CODE_END:
        got = list(MD.disasm(op[a:a + 10], a, 1))
        if not got:
            a += 2
            continue
        i = got[0]
        ins[a] = i
        m, s = i.mnemonic, i.op_str
        flow = m in ("bsr.w", "bsr.b", "jsr", "jmp") or m.startswith(("bra", "db")) or (m[:1] == "b" and m[1:3] in BRANCH)
        if flow:
            for t in re.findall(r"\$([0-9a-f]+)(?:\.l)?(?!\()", s):
                refs[int(t, 16)].add((a, m))
        pc = re.search(r"\$([0-9a-f]+)\(pc\)", s)
        if pc and m.startswith(("lea", "pea")):
            refs[int(pc.group(1), 16)].add((a, m))
        jt = re.match(r"\$([0-9a-f]+)\(pc, d\d\.w\)", s)
        if jt and m in ("jmp", "jsr"):
            base = int(jt.group(1), 16)
            for k in range(entries(op, base)):
                o = int.from_bytes(op[base + 2 * k:base + 2 * k + 2], "big", signed=True)
                refs[base + o].add((a, "%s table[%d]" % (m, k)))
        if not (m in ("rts", "rte", "jmp") or m.startswith("bra")):
            prev[a + i.size] = a
        a += i.size
    return ins, refs, prev


def long_tables(op, ins):
    """{base: entries} of the long tables read by `movea.l (d8,PC,Dn.w),An`, entries counted while they point into
    code."""
    out = {}
    for i in ins.values():
        m = re.match(r"\$([0-9a-f]+)\(pc, d\d\.w\), a\d", i.op_str)
        if i.mnemonic == "movea.l" and m:
            b, k = int(m.group(1), 16), 0
            while 0x400 <= int.from_bytes(op[b + 4 * k:b + 4 * k + 4], "big") < CODE_END and op[b + 4 * k + 3] % 2 == 0:
                k += 1
            out[b] = k
    return out


def pointers(op, data, tables):
    """{target: [description]} for the longs that end a walk."""
    out = collections.defaultdict(list)
    for b in range(BANK[0], BANK[1], 4):
        t = int.from_bytes(data[b:b + 4], "big")
        if 0x400 <= t < CODE_END:
            base = BANK[0] + (b - BANK[0]) // 0x80 * 0x80
            out[t].append(("bank", base, (b - base) // 4))
    for base, n in tables.items():
        for k in range(n):
            out[int.from_bytes(op[base + 4 * k:base + 4 * k + 4], "big")].append(("type", base, k))
    return out


def local(op, ins, site):
    """The instructions ending at the site: the linear disassembly's, or, where it does not land on the site (it
    decoded data before it), the longest run of up to 12 words before it that decodes exactly onto it."""
    if site in ins:
        before = sorted(x for x in ins if site - 0x20 <= x < site)
        return [ins[x] for x in before] + [ins[site]]
    for k in range(12, 0, -1):
        run = list(MD.disasm(op[site - 2 * k:site + 10], site - 2 * k))
        addrs = [i.address for i in run]
        if site in addrs:
            return run[:addrs.index(site) + 1]
    return list(MD.disasm(op[site:site + 10], site, 1))


def whose(op, ins, site):
    """The register the site reads +0x382 through, and what it holds."""
    run = local(op, ins, site)
    reg = re.search(r"\$382\((a\d)\)", run[-1].op_str).group(1)
    if reg == "a6":
        return "own (a6)"
    for i in reversed(run[-7:-1]):
        m = re.fullmatch(r"\$32\((a\d)\), " + reg, i.op_str)
        if i.mnemonic == "movea.w" and m:
            return "linked to %s (%s = $32(%s))" % (m.group(1), reg, m.group(1))
    return "unresolved (%s)" % reg


def walk(site, refs, prev, ptrs):
    """The ends of every backward path from the site: [(chain, end)]."""
    ends, seen = [], set()

    def entry(a):
        steps = 0
        while a in prev and a not in refs and a not in ptrs and steps < 200:
            a, steps = prev[a], steps + 1
        return a

    def up(a, chain, depth):
        e = entry(a)
        if depth > 7:
            ends.append((chain, "walk limit (7 levels)"))
            return
        if e in seen:
            return
        seen.add(e)
        chain = chain + ["PRG:0x%06X" % e]
        if e in ptrs:
            for kind, base, k in ptrs[e]:
                ends.append((chain, "bank row: table PRG:0x%06X id 0x%02X" % (base, k) if kind == "bank" else
                             "type table: PRG:0x%06X entry 0x%02X" % (base, k)))
            return
        if e not in refs:
            ends.append((chain, "no reference"))
            return
        for f, how in sorted(refs[e]):
            up(f, chain + ["%s at PRG:0x%06X" % (how, f)], depth + 1)

    up(site, [], 0)
    return ends


def main():
    args = sys.argv[1:]
    if len(args) != 3:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    export, romdir, build = (os.path.realpath(a) for a in args)
    pcs, _, left, read, views = sites(export, romdir, build, views=True)
    op, data = views["vsavj"]
    for p, h in read:
        print("read %s sha1 %s" % (p, h))
    ins, refs, prev = disassemble(op)
    tables = long_tables(op, ins)
    ptrs = pointers(op, data, tables)
    print("instructions %d, referenced addresses %d, long tables read pc-relatively %d" % (len(ins), len(refs),
                                                                                        len(tables)))
    for t in left:
        for site in sorted(a for a, x in pcs["vsavjw"].items() if x == t):
            ends = walk(site, refs, prev, ptrs)
            kinds = sorted({e.split(":")[0] for _, e in ends}) or ["none (the walk only loops back on itself)"]
            print("TABLE %s site PRG:0x%06X: reads the id %s; walk ends: %s" % (t, site, whose(op, ins, site),
                                                                               ", ".join(kinds)))
            rows = collections.defaultdict(lambda: collections.defaultdict(list))
            for chain, end in ends:
                kind, rest = (end.split(": ", 1) + [""])[:2]
                group = re.sub(r" id 0x[0-9A-F]+| entry 0x[0-9A-F]+", "", rest) if kind == "bank row" else rest
                rows[(kind, " <- ".join(chain))][group].append(re.search(r"0x[0-9A-F]+$", rest).group(0)
                                                                if kind == "bank row" else "")
            for (kind, chain), groups in sorted(rows.items()):
                if kind == "bank row":
                    ids = sorted({i for v in groups.values() for i in v})
                    what = "ids %s in tables %s" % (", ".join(ids), ", ".join(sorted(g[6:] for g in groups)))
                else:
                    what = ", ".join(sorted(groups)) or "the walk's last address"
                print("   %s: %s; by %s" % (kind, what, chain))

if __name__ == "__main__":
    main()
