"""vet_moves.py — the five veteran moves that read the VICTIM's row of a left-on-shell table (#6;
docs/project/tables/README.md "What reaches the left-on-shell tables", "The five veteran moves").

Each of these tables is read by a veteran's move with the opponent's raw id (`movea.w $32(a6),a4; move.b $382(a4)`),
so a newcomer victim gets its shell's row on our build where native vs2 gives it its own. The move is the veteran's
handler of the command id `+0x106` its site is reached under (README); this rig is what shows it, by the site
firing on the move's input:
  bulleta   P1 Bulleta 0x00, ES PURSUIT (8 + two punches, a stock; `+0x102` = 6)   +0x106 0x0A   table PRG:0x02E970
  gallon    P1 Gallon 0x02, WILD CIRCULAR (63214 MK)                               +0x106 0x14   table PRG:0x0331EA
  zabel     P1 Zabel 0x04, HELL DUNK (EX, 623 + LP MP, a stock)                    +0x106 0x0A   table PRG:0x0373CA
  morrigan  P1 Morrigan 0x05, CRYPTIC NEEDLE (EX, 6 HP MP LP 6, a stock)           +0x106 0x0A   table PRG:0x03A60A
  felicia   P1 Felicia 0x07, the HEADSIT (no input: a jump landing on a standing   +0x106 0x10   table PRG:0x0402BA
            opponent)
P2 is Victor 0x03 (the instrument check: every veteran row of the five tables is the same on both games, README) or a
newcomer (0x13, 0x10, 0x11, the ids the doll rig pokes on both games), idle.

A part is `<move>_<victim id>`, run on two legs: native vsav2 from ROMDIR and ours, vsavjw from <build>/rompath
([VSR-82]), both on the WIDE binary (docs/project/instruments.md). Inputs: the doll rig's prologue (the original's
tests/replays/judge/03_down_attack.rpl up to its walk, picks by its id pokes at 1400/1450/1500), the move's lines,
speed level 06 from 2000 and RNG 0000 from 2363 ([VSR-26]); a move that spends a stock has one poked at 2850, and its
use is traced ([VSR-180]). Each leg runs twice on the same inputs: tests/lua/read_tap.lua (non-debug) on both fighters'
`+0x382`, logged at the five sites (on vsav2 their twins, tools/raw_id_reach.py's `sites`) and the defense-read
control; and tests/lua/field_trace.lua for both fighters' state, position and id, P1's `+0x106` and stock. The tap
numbers a frame one lower than the trace (Felicia's headsit: read at the tap's 2897, its state from the trace's 2898);
both legs carry the same offset.

Per part and leg: the site's reads (frame, whose id) and, from the first, P1's position relative to P2 (dx, dy) for
SPAN frames ([VSR-160]); whether the two legs' sequences are identical. The verdict is tests/test_vet_moves.py's.

Prints the SHA-1 of every file it read ([VSR-10]). Values are RAM ids, positions and addresses ([VSR-8]).

Usage: python3 tools/vet_moves.py <export root> <rom dir> <build dir> <out dir> [--bin MAME] [--jobs N]
                                  [--parts bulleta_03,...] [--sides native,ours]
       python3 tools/vet_moves.py --report <out dir>
"""
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raw_id_census import MD  # noqa: E402
from raw_id_reach import RTAP, parse, sites  # noqa: E402
from state_capture import ROLL, load, sha1  # noqa: E402

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MOVES = {
    "bulleta": {"p1": "00", "cmd": 0x0A, "table": "PRG:0x02E970", "stock": True,
                "lines": ("2860-3005 p1=R", "3010-3014 p1=D6", "3050-3052 p1=U12")},
    "gallon": {"p1": "02", "cmd": 0x14, "table": "PRG:0x0331EA",
               "lines": ("2860-2960 p1=R", "2970-2971 p1=R", "2972-2973 p1=DR", "2974-2975 p1=D", "2976-2977 p1=DL",
                         "2978-2980 p1=L5")},
    "zabel": {"p1": "04", "cmd": 0x0A, "table": "PRG:0x0373CA", "stock": True, "pose": 0x0C,
              "lines": ("2860-3005 p1=R", "3010-3012 p1=R", "3013-3015 p1=D", "3016-3019 p1=DR", "3018-3020 p1=12")},
    "morrigan": {"p1": "05", "cmd": 0x0A, "table": "PRG:0x03A60A", "stock": True, "pose": 0x08,
                 "lines": ("2870-2871 p1=R", "2873-2874 p1=3", "2876-2877 p1=2", "2879-2880 p1=1",
                           "2882-2883 p1=R")},
    "felicia": {"p1": "07", "cmd": 0x10, "table": "PRG:0x0402BA",
                "lines": ("2860-2873 p1=R", "2874-2876 p1=UR")},
}
VICTOR = "03"
VICTIMS = (VICTOR, "13", "10", "11")
PARTS = tuple("%s_%s" % (m, v) for m in MOVES for v in VICTIMS)
SIDES = ("native", "ours")
SPAN = 60
STOCK_AT = 2850
FIELDS = ",".join("%x:l:%s_st,%x:w:%s_x,%x:w:%s_y,%x:b:%s_id" % (b + 4, p, b + 0x10, p, b + 0x14, p, b + 0x382, p)
                  for p, b in (("p1", 0xFF8400), ("p2", 0xFF8800))) + ",ff8506:b:p1_cmd,ff8509:b:p1_stock,ff881c:l:p2_node"
FRAMES = 3400


def inputs(export, part):
    move, victim = part.split("_")
    m = MOVES[move]
    base = [line for line in open(os.path.join(export, ROLL["base"])).read().splitlines()
            if not line.startswith(("2860-", "3010-", "5000"))]
    pokes = ["%d:%s:%s" % (f, a, v) for a, v in (("ff8782", m["p1"]), ("ff8b82", victim)) for f in (1400, 1450, 1500)]
    pokes += ["2000-%d:ff8116:06" % (FRAMES - 1), "2363-%d:ff80d4:0000" % (FRAMES - 1)]
    if m.get("stock"):
        pokes.append("%d:ff8509:01" % STOCK_AT)
    return "\n".join(base + list(m["lines"])) + "\n", ";".join(pokes)


def run(export, out, romdir, build, mame, pcs, part, side, kind):
    """One MAME run of a leg: `tap` (the read tap) or `trace` (the field trace), in its own directory."""
    s, rp = ("vsav2", romdir) if side == "native" else ("vsavjw", os.path.join(build, "rompath") + ";" + romdir)
    d = os.path.join(out, "%s.%s.%s" % (part, side, kind))
    os.makedirs(d)
    rpl = os.path.join(d, "inputs.rpl")
    text, pokes = inputs(export, part)
    open(rpl, "w").write(text)
    res = os.path.join(out, "%s_%s.%s.txt" % (kind, part, side))
    env = dict(os.environ, ROMDIR=romdir, MAME_BIN=mame, MAME_SANDBOX=os.path.join(d, "sb"), MAME_ROMPATH=rp,
               REPLAY=rpl, POKES=pokes, FRAMES=str(FRAMES))
    if kind == "tap":
        env.update(RTAP=RTAP, RPCS=",".join("%x" % a for a in sorted(pcs[s])), TRACE_OUT=res, WINDOW="2000,%d" % FRAMES)
        lua = "read_tap.lua"
    else:
        env.update(FIELDS=FIELDS, FIELD_OUT=res, FIELD_FROM="2800", FIELD_TO=str(FRAMES))
        lua = "field_trace.lua"
    with open(os.path.join(d, "mame.log"), "w") as log:
        subprocess.run([os.path.join(export, "tools", "run_mame.sh"), s, "-autoboot_script",
                        os.path.join(export, "tests", "lua", lua)], cwd=d, env=env, stdout=log,
                       stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    subprocess.run(["rm", "-rf", os.path.join(d, "sb")])
    return part, side, kind


def pose_maps(views, pcs):
    """{side: {move: {victim id: {node: pose index}}}} for the moves whose site calls the capture-pose entry: the entry
    is the first absolute `jsr` after the site, on each set; d1 (the move's `pose`) picks the entry's family table
    (read pc-relatively, so in the opcode view), whose row at the victim's id is its pose table: word offsets from
    its base, indexed by the pose (data view). The node a pose index gives on the BUILD is read from the build's own
    tables: this names the index the move used, not whether the build's pose table is right ([VSR-51])."""
    out = {}
    for side, s in (("native", "vsav2"), ("ours", "vsavjw")):
        op, da = views[side]
        out[side] = {}
        for move, m in MOVES.items():
            if "pose" not in m:
                continue
            site = min(pc for pc, t in pcs[s].items() if t == m["table"])
            a, entry = site, None
            for _ in range(40):
                i = next(MD.disasm(op[a:a + 10], a, 1))
                if i.mnemonic == "jsr" and re.fullmatch(r"\$[0-9a-f]+\.l", i.op_str):
                    entry = int(i.op_str[1:-2], 16)
                    break
                a += i.size
            fam = entry + 6 + int.from_bytes(op[entry + 7:entry + 8], "big", signed=True)
            tab = int.from_bytes(op[fam + m["pose"]:fam + m["pose"] + 4], "big")
            out[side][move] = {}
            for v in VICTIMS:
                base = int.from_bytes(da[tab + 4 * int(v, 16):tab + 4 * int(v, 16) + 4], "big")
                nodes = {}
                for k in range(0x100):
                    nodes.setdefault(base + int.from_bytes(da[base + 2 * k:base + 2 * k + 2], "big", signed=True), k)
                out[side][move][v] = {"entry": entry, "table": tab, "base": base, "nodes": nodes}
    return out


def measure(export, romdir, build, out, mame, parts=PARTS, sides=SIDES, jobs=6):
    """Run every (part, side) leg, both runs; returns the run's meta (also written to <out>/vet.json)."""
    pcs, control, _, read, views = sites(export, romdir, build, views=True)
    views = {"native": views["vsav2"], "ours": tuple(open(os.path.join(build, n), "rb").read()
                                                     for n in ("verify_op.bin", "verify_data.bin"))}
    poses = pose_maps(views, pcs)
    read = read + [(mame, sha1(mame)), (os.path.join(build, "rompath", "vsavjw.zip"),
                                        sha1(os.path.join(build, "rompath", "vsavjw.zip"))),
                   (os.path.join(export, ROLL["base"]), sha1(os.path.join(export, ROLL["base"])))]
    for s in pcs:
        pcs[s][control[s]] = "control"
    meta = {"export": export, "parts": list(parts), "sides": list(sides), "read": read, "control": control,
            "pcs": {s: {str(k): v for k, v in d.items()} for s, d in pcs.items()},
            "poses": {side: {move: {v: dict(p, nodes={str(n): k for n, k in p["nodes"].items()})
                                    for v, p in d.items()} for move, d in sd.items()} for side, sd in poses.items()}}
    json.dump(meta, open(os.path.join(out, "vet.json"), "w"), indent=1)
    todo = [(p, s, k) for p in parts for s in sides for k in ("tap", "trace")]
    with ThreadPoolExecutor(jobs) as pool:
        for part, side, kind in pool.map(lambda j: run(export, out, romdir, build, mame, pcs, *j), todo):
            print("ran %s %s %s" % (part, side, kind), flush=True)
    return meta


def legs(out, meta):
    """{(part, side): {site [(tap frame, whose id, id)], ctl, live, rows, done, pose}} from a run's files."""
    pcs = {s: {int(k): v for k, v in d.items()} for s, d in meta["pcs"].items()}
    got = {}
    for part in meta["parts"]:
        table = MOVES[part.split("_")[0]]["table"]
        for side in meta["sides"]:
            s = "vsav2" if side == "native" else "vsavjw"
            reads, writes, end = parse(os.path.join(out, "tap_%s.%s.txt" % (part, side)))
            rows, done = load(os.path.join(out, "trace_%s.%s.txt" % (part, side)))
            site = [(f, who, idr) for f, pc, who, idr, _ in reads if pcs[s].get(pc) == table]
            got[(part, side)] = {"site": site, "ctl": sum(1 for r in reads if r[1] == meta["control"][s]),
                                 "live": end and writes > 0, "rows": rows, "done": done,
                                 "pose": pose(meta, part, side, rows, site[0][0]) if site else None}
    return got


def pose(meta, part, side, rows, f0):
    """The victim's capture pose index on the first trace frame after the read, or None (not a pose move), or -1
    (the victim's node is no pose of its table)."""
    move, victim = part.split("_")
    p = meta["poses"][side].get(move)
    if p is None:
        return None
    return p[victim]["nodes"].get(str(rows.get(f0 + 1, {}).get("p2_node", -1) & 0xFFFFFFFF), -1)


def rel(rows, f0):
    """P1 relative to P2, (dx, dy), from the site's tap frame for SPAN frames."""
    return [(rows[f]["p1_x"] - rows[f]["p2_x"], rows[f]["p1_y"] - rows[f]["p2_y"]) for f in range(f0, f0 + SPAN)
            if f in rows]


def report(out):
    meta = json.load(open(os.path.join(out, "vet.json")))
    for p, h in meta["read"]:
        print("read %s sha1 %s" % (p, h))
    got = legs(out, meta)
    for part in meta["parts"]:
        seqs = {}
        for side in meta["sides"]:
            g = got[(part, side)]
            print("%s %s: tap %s, control reads %d, trace %d frames %s" % (
                part, side, "live" if g["live"] else "DEAD", g["ctl"], len(g["rows"]),
                "complete" if g["done"] else "INCOMPLETE"))
            if not g["site"]:
                print("  site NOT fired")
                continue
            f0, rows = g["site"][0][0], g["rows"]
            r = rows.get(f0 + 1, {})
            print("  site fired %d times, frames %d-%d, ids read %s; trace at %d: P1 st %08X +0x106 %#04x stock %s" % (
                len(g["site"]), f0, g["site"][-1][0], " ".join(sorted({"%s:%02X" % (w, i) for _, w, i in g["site"]})),
                f0 + 1, r.get("p1_st", 0) & 0xFFFFFFFF, r.get("p1_cmd", 0), r.get("p1_stock")))
            seqs[side] = rel(rows, f0)
            k = pose(meta, part, side, rows, f0)
            if k is not None:
                print("  victim's capture pose at %d: index %s (node %08X)" % (
                    f0 + 1, "%#04x" % k if k >= 0 else "NONE", r.get("p2_node", 0) & 0xFFFFFFFF))
            print("  dx,dy from %d: %s" % (f0, " ".join("%d,%d" % xy for xy in seqs[side])))
        if len(seqs) == 2:
            print("  %s: dx,dy sequences %s" % (part, "IDENTICAL" if seqs["native"] == seqs["ours"] else "DIFFER"))


def main():
    args = sys.argv[1:]
    if args[:1] == ["--report"]:
        return report(os.path.realpath(args[1]))
    opts = {"--bin": os.path.join(ROOT, "build", "emu", "mame-wide", "mame", "cps2"), "--jobs": "6",
            "--parts": ",".join(PARTS), "--sides": ",".join(SIDES)}
    for name in list(opts):
        if name in args:
            i = args.index(name)
            opts[name], args = args[i + 1], args[:i] + args[i + 2:]
    if len(args) != 4:
        raise SystemExit(__doc__.strip().splitlines()[-3])
    export, romdir, build, out = (os.path.realpath(a) for a in args)
    if os.path.exists(out):
        raise SystemExit("REFUSED: %s exists (a run owns its directory, SPEC.md §4)" % out)
    os.makedirs(out)
    measure(export, romdir, build, out, os.path.realpath(opts["--bin"]), opts["--parts"].split(","),
            opts["--sides"].split(","), int(opts["--jobs"]))
    report(out)


if __name__ == "__main__":
    main()
