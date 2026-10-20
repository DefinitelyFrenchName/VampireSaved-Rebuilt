"""raw_id_reach.py — which of the raw-id census's left-on-shell tables the game reaches in play, and with whose id
(#6; docs/project/tables/README.md "The raw-id census", "What reaches the left-on-shell tables").

The census (tools/raw_id_census.py) is static: a row it lists is one a newcomer reads IF it reaches the reading code.
This answers the first half of "if" over a corpus: every replay of the original's tests/replays/ (the 97 top-level
ones, the corpus tools/state_capture.py runs), a vs2 replay (`*_vsav2`, `*_vs2_*`) on vsav2, every other on the
original's merged build, run to its last scripted frame + 200, with no gate's pokes.

The instrument is the original's tests/lua/read_tap.lua (non-debug, so frame counting stays replay-exact): a read
tap on both fighters' `+0x382` (RAM:$FF8782, RAM:$FF8B82, the same on both games), logged only when the reading
instruction (CURPC) is one of the left-on-shell tables' reading sites, or on vsav2 their twins (the census's site
alignment). Writes to the two fields are always logged, so the tap's own liveness and the two fighters' ids at
any frame come from the same log. A read names the fighter whose id was read; for a table the census reads by the
opponent's id (`movea.w $32(a6)`), the OTHER fighter is the one whose code ran.

Controls ([VSR-22]), each in every run:
  control-site  the defense curve's id read, vsavj PRG:0x018C10 (`move.b $382(a1),d0`, the original's
                tests/audit_defense_row_reads.sh), and on vsav2 its twin found by its own 12 bytes (unique): it runs on every
                hit, so a corpus where it never fires has a dead filter (CURPC not the instruction's address)
  writes        the select's writes to `+0x382`: a replay whose log has none never picked, or ran blind
A run is VOID when either control fails on its set.

Not seen: a read of `+0x382` from any other block (an object's copy of the id), and anything the corpus does not
play. Absence here is the weakest evidence ([VSR-52]); a table this does not reach is unanswered, not dead.

Prints the SHA-1 of every file it read ([VSR-10]). Values are RAM ids and addresses ([VSR-8]).

Usage: python3 tools/raw_id_reach.py <export root> <rom dir> <build dir> <out dir> [--bin MAME] [--jobs N]
       python3 tools/raw_id_reach.py --report <out dir>
"""
import collections
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raw_id_census import TENANTS, load, measure  # noqa: E402
from state_capture import sha1  # noqa: E402

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CONTROL = 0x018C10
RTAP = "ff8782,2;ff8b82,2"
PLAYER = {0xFF8782: "P1", 0xFF8B82: "P2"}
NEWCOMER = {cid: name for name, cid in TENANTS}


def sites(export, romdir, build, views=False):
    """{set: {pc: table}} for the left-on-shell tables, plus each set's control PC; and what the census read (and,
    with `views`, the two games' (opcode, data) views)."""
    inp = load(export, romdir, build)
    _, res = measure(inp)
    left = sorted({t for t, name, cls, _ in res["built"] if cls == "vanilla"
                   for row in res["tables"] if row["vsavj"] == t
                   and name[0] in row["shell"] and name[0] in row["vs2_own"]})
    out = {"vsavjw": {}, "vsav2": {}}
    for row in res["tables"]:
        if row["vsavj"] in left:
            for s in row["sites"].split():
                a = int(s[6:], 16)
                out["vsavjw"][a] = row["vsavj"]
                if a in res["twins"]:
                    out["vsav2"][res["twins"][a]] = row["vsavj"]
    opj, op2 = inp["views"]["vsavj"][0], inp["views"]["vsav2"][0]
    key = opj[CONTROL:CONTROL + 12]       # the read and the two instructions after it; the bytes before differ
    found = [m.start() for m in re.finditer(re.escape(key), op2[:0x100000])]
    control = {"vsavjw": CONTROL, "vsav2": found[0] if len(found) == 1 else None}
    return (out, control, left, inp["read"]) + ((inp["views"],) if views else ())


def run(export, romdir, build, out, mame, name, pcs):
    rpl = os.path.join(export, "tests", "replays", name + ".rpl")
    native = name.endswith("_vsav2") or "_vs2_" in name
    s, rp = ("vsav2", romdir) if native else ("vsavjw", os.path.join(build, "rompath") + ";" + romdir)
    last = 0
    for line in open(rpl):
        t = line.split("#")[0].split()
        if t and t[0][0].isdigit():
            last = max(last, int(t[0].split("-")[-1]))
    d = os.path.join(out, "corpus", name)
    os.makedirs(d)
    tap = os.path.join(d, "tap.txt")
    env = dict(os.environ, ROMDIR=romdir, MAME_BIN=mame, MAME_SANDBOX=os.path.join(d, "sb"), MAME_ROMPATH=rp,
               REPLAY=rpl, RTAP=RTAP, RPCS=",".join("%x" % a for a in sorted(pcs[s])), TRACE_OUT=tap,
               FRAMES=str(last + 200))
    env.pop("POKES", None)
    with open(os.path.join(d, "mame.log"), "w") as log:
        subprocess.run([os.path.join(export, "tools", "run_mame.sh"), s, "-autoboot_script",
                        os.path.join(export, "tests", "lua", "read_tap.lua")], cwd=d, env=env, stdout=log,
                       stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    subprocess.run(["rm", "-rf", os.path.join(d, "sb")])
    return name, s


def lane(data, mask):
    shift = (mask & -mask).bit_length() - 1
    return (data & mask) >> shift, shift


def parse(path):
    """(reads [(frame, pc, player, id read, the other player's id)], writes, END seen)."""
    ids, reads, writes, end = {"P1": None, "P2": None}, [], 0, False
    if not os.path.exists(path):
        return reads, writes, end
    for line in open(path):
        p = line.split()
        if p[0] == "END":
            end = True
        if p[0] not in ("R", "W"):
            continue
        frame, pc, off, data, mask = int(p[1]), int(p[3], 16), int(p[5], 16), int(p[7], 16), int(p[9], 16)
        word = off & ~1
        who = PLAYER.get(word)
        if who is None:
            continue
        val, shift = lane(data, mask)
        high = (val >> 8) & 0xFF if mask & 0xFF00 and mask & 0xFF else (val if shift == 8 else None)
        if p[0] == "W":
            writes += 1
            if high is not None:
                ids[who] = high
        elif high is not None:
            other = ids["P2" if who == "P1" else "P1"]
            reads.append((frame, pc, who, high, other))
    return reads, writes, end


def report(out):
    meta = json.load(open(os.path.join(out, "reach.json")))
    pcs = {s: {int(k): v for k, v in d.items()} for s, d in meta["pcs"].items()}
    control = meta["control"]
    for p, h in meta["read"]:
        print("read %s sha1 %s" % (p, h))
    seen = collections.defaultdict(list)
    ctl = collections.Counter()
    blind, incomplete = [], []
    for name, s in meta["ran"]:
        reads, writes, end = parse(os.path.join(out, "corpus", name, "tap.txt"))
        if not end:
            incomplete.append(name)
        if not writes:
            blind.append(name)
        by = collections.defaultdict(list)
        for r in reads:
            if r[1] == control[s]:
                ctl[s] += 1
            elif r[1] in pcs[s]:
                by[(pcs[s][r[1]], r[1], r[2], r[3], r[4])].append(r[0])
        for (t, pc, who, idr, other), frames in sorted(by.items()):
            seen[t].append((name, s, pc, who, idr, other, len(frames), min(frames), max(frames)))
    print("corpus: %d replays, %d complete (END line), incomplete: %s; no write to +0x382: %s" % (
        len(meta["ran"]), len(meta["ran"]) - len(incomplete), " ".join(incomplete) or "none", " ".join(blind) or "none"))
    void = []
    for s in ("vsavjw", "vsav2"):
        if any(x == s for _, x in meta["ran"]):
            print("CONTROL control-site %s PC %s: %d reads" % (s, "%06X" % control[s] if control[s] else "NOT FOUND",
                                                               ctl[s]))
            if not ctl[s]:
                void.append(s)
    print("CONTROL writes: %s" % ("every replay wrote +0x382" if not blind else "%d replays did not" % len(blind)))
    for t in meta["left"]:
        rows = seen.get(t, [])
        ids = sorted({r[4] for r in rows})
        newc = sorted({NEWCOMER[i] for i in ids if i in NEWCOMER})
        print("TABLE %s: %s" % (t, "reached in %d replays, ids read %s%s" % (
            len({r[0] for r in rows}), " ".join("%02X" % i for i in ids),
            "; NEWCOMER read: " + ", ".join(newc) if newc else "") if rows else "not reached"))
        for name, s, pc, who, idr, other, n, f0, f1 in rows:
            print("   %s on %s: PC %06X read %s's id %02X (other fighter %s), %d reads, frames %d-%d" % (
                name, s, pc, who, idr, "%02X" % other if other is not None else "?", n, f0, f1))
    print("VERDICT: %s" % ("VOID (control-site dead on %s)" % ", ".join(void) if void else
                           "MEASURED (%d of %d tables reached)" % (sum(1 for t in meta["left"] if seen.get(t)),
                                                                  len(meta["left"]))))


def main():
    args = sys.argv[1:]
    if args[:1] == ["--report"]:
        return report(os.path.realpath(args[1]))
    opts = {"--bin": os.path.join(ROOT, "build", "emu", "mame-wide", "mame", "cps2"), "--jobs": "6"}
    for name in list(opts):
        if name in args:
            i = args.index(name)
            opts[name], args = args[i + 1], args[:i] + args[i + 2:]
    if len(args) != 4:
        raise SystemExit(__doc__.strip().splitlines()[-2])
    export, romdir, build, out = (os.path.realpath(a) for a in args)
    if os.path.exists(out):
        raise SystemExit("REFUSED: %s exists (a run owns its directory, SPEC.md §4)" % out)
    os.makedirs(out)
    mame = os.path.realpath(opts["--bin"])
    pcs, control, left, read = sites(export, romdir, build)
    for s in pcs:
        pcs[s][control[s]] = "control"
    corpus = sorted(f[:-4] for f in os.listdir(os.path.join(export, "tests", "replays")) if f.endswith(".rpl"))
    read = read + [(mame, sha1(mame)), (os.path.join(build, "rompath", "vsavjw.zip"),
                                        sha1(os.path.join(build, "rompath", "vsavjw.zip")))]
    for name in corpus:
        p = os.path.join(export, "tests", "replays", name + ".rpl")
        read.append((p, sha1(p)))
    print("left-on-shell tables: %d; sites watched: vsavjw %d, vsav2 %d; control PC vsavjw %06X, vsav2 %s" % (
        len(left), len(pcs["vsavjw"]) - 1, len(pcs["vsav2"]) - 1, control["vsavjw"],
        "%06X" % control["vsav2"] if control["vsav2"] else "NOT FOUND"))
    ran = []
    with ThreadPoolExecutor(int(opts["--jobs"])) as pool:
        for name, s in pool.map(lambda n: run(export, romdir, build, out, mame, n, pcs), corpus):
            print("ran %s on %s" % (name, s), flush=True)
            ran.append((name, s))
    json.dump({"export": export, "romdir": romdir, "build": build, "bin": mame, "read": read, "left": left,
               "control": control, "ran": ran,
               "pcs": {s: {str(k): v for k, v in d.items() if v != "control"} for s, d in pcs.items()}},
              open(os.path.join(out, "reach.json"), "w"), indent=1)
    report(out)


if __name__ == "__main__":
    main()
