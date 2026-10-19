"""state_capture.py — #4's capture (SPEC.md §0, ruled R-004 "(c) then (a)"): which move enters the fighter state
`+0x04` = 0x02100600 (the handler at vsavj PRG:0x026670, whose substate 0 reads the table at vsavj PRG:0x0BE3FA by the
raw id `+0x382`) for each newcomer, on native vs2 and on the original's merged build, and how the two legs move while
in it ([VSR-43]: captures before conclusions; docs/project/tables/README.md "What the build wrote for rec8_a and
rec8_b").

The rigs are the original's own (its tools/name_moves.py, tests/replays/naming/<rig>.rpl/.json), two kinds:
  naming  P1 the tenant performs named moves, P2 Demitri idle: the six parts holding a pursuit event ("... off
          throw"), every other move in them captured too. The legs are the original's tests/audit_pursuit_flag.sh
          `leg`: native vsav2 as written; ours with the native select lines replaced by the merged wheel's real
          cursor path (CURSOR, the original's [VSP-123] paths); the rig's pokes plus level 6 from frame 2000;
  victim  P1 Victor attacks P2 the tenant (hits, knockdowns, throw; blocks; for Donovan air hits), the parts the
          original's tests/audit_victim_parity.sh runs, the way it runs them: both picks by the REAL cursor route on
          each game's own decoded wheel (its tools/select_wheel.py and select_paths.py; the rig's id pokes dropped,
          its #147), one P2 HP pin 10 frames before each event, level 8 from frame 2000;
RNG 0000 from 2363 on both kinds.
  roll    the TECH ROLL, the original's tests/audit_tech_roll.sh rig (tests/replays/judge/03_down_attack.rpl: P1
          Bulleta 0x01 sweeps P2, picks by the gate's id pokes at 1400/1450/1500) with P2 holding a direction + LP
          through the knockdown landing (3058-3088, the gate's `roll` line, `L1`, and the other direction `R1`); P2
          Victor 0x03 (the gate's legacy control) and each tenant (0x13, 0x10, 0x11, the ids the original's gates poke
          on both games); traced 3020-3250 as the gate does, on both legs.
A third kind, `corpus`, is a census rather than a rig: every replay of the original's
tests/replays/ (no gate's pokes, so a KO a gate forces by an HP poke may not happen), a vs2 replay (`*_vsav2`,
`*_vs2_*`) on vsav2, every other on our build, run to its last scripted frame + 200; its report lists every stretch
any fighter spends in a `0x0210xxxx` state (the routine the STATE belongs to), with the states before it. Native is set vsav2 from ROMDIR; ours is set vsavjw from <build>/rompath;ROMDIR
([VSR-82]: the set name follows the rompath). Both run on the WIDE binary (proven to run stock sets as the reference
does, docs/project/instruments.md), through the original's tools/run_mame.sh and tests/lua/field_trace.lua. BOTH
players are traced (blocks RAM:$FF8400 and $FF8800, the same on both games, atlas/ram.md there), so the veteran on the
other side is a positive control: a state any fighter can enter shows on him too.

Per event (its frame to frame+gap), per player: every distinct `+0x04` long, in order, with its first frame; whether
the STATE was entered, for how many frames, the player's id (`+0x382`) and `+0x0A` there, and its x/y on entering, at
the extremes and on leaving; and whether the two legs' trajectories in the STATE are identical.
Prints the SHA-1 of every rig, of the WIDE binary and of the build's vsavjw.zip ([VSR-10]). Values are RAM states and
positions, no ROM bytes ([VSR-8]).

Usage: python3 tools/state_capture.py <export root> <rom dir> <build dir> <out dir> [--bin MAME] [--jobs N]
                                       [--rigs naming,victim]
       python3 tools/state_capture.py --report <out dir>
"""
import hashlib
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
STATE = 0x02100600
RIGS = {"naming": ("donovan_4", "donovan_7", "huitzil_3", "huitzil_4", "pyron_3", "pyron_4"),
        "victim": ("donovan_victim_1", "donovan_victim_2", "donovan_victim_3", "huitzil_victim_1", "huitzil_victim_2",
                   "pyron_victim_1", "pyron_victim_2"),
        "roll": tuple("roll_%s_%s" % (d, i) for d in ("L1", "R1") for i in ("03", "13", "10", "11")),
        "corpus": ()}           # filled from the export's tests/replays/ at run time
ROLL = {"base": os.path.join("tests", "replays", "judge", "03_down_attack.rpl"), "p1": "01", "hold": "3058-3088",
        "from": 3020, "to": 3250, "frames": 3300}
ROUTINE = 0x0210
CURSOR = {"donovan": "D D DR DR", "huitzil": "D D D", "pyron": "D D D D"}
CELL = {"donovan": "13", "huitzil": "10", "pyron": "11"}      # the original's victim gate's ids on the merged build
VICTOR = "03"
PLAYERS = (("p1", 0xFF8400, 0xFF8782), ("p2", 0xFF8800, 0xFF8B82))
FIELDS = ",".join("%x:l:%s_st,%x:w:%s_x,%x:w:%s_y,%x:b:%s_v0a,%x:b:%s_id" % (
    b + 4, p, b + 0x10, p, b + 0x14, p, b + 0x0A, p, i, p) for p, b, i in PLAYERS) + ",ff8850:w:p2hp"
NATIVE_P1 = ("1100-", "1160-", "1220-", "1280-")


def sha1(path):
    return hashlib.sha1(open(path, "rb").read()).hexdigest()


def cursor(rpl, path):
    """The original's `cursor` (tests/audit_pursuit_flag.sh): P1's merged-wheel moves from 1100, 60 frames apart,
    inserted before P2's first move line; the native P1 move lines dropped."""
    out, done = [], False
    for line in open(rpl).read().splitlines():
        if line.startswith("1104-1106 p2=R") and not done:
            out += ["%d-%d p1=%s" % (1100 + 60 * i, 1102 + 60 * i, m) for i, m in enumerate(path.split())]
            done = True
        if line.startswith(NATIVE_P1) and " p1=" in line:
            continue
        out.append(line)
    return "\n".join(out) + "\n"


def routes(export, romdir, build, out):
    """{(side, player, cell): path} on each game's own decoded wheel (the original's victim gate's `route`)."""
    tools = os.path.join(export, "tools")
    v2_op, v2_da = os.path.join(out, "v2_op.bin"), os.path.join(out, "v2_da.bin")
    subprocess.run([sys.executable, os.path.join(tools, "cps2_decrypt.py"), os.path.join(romdir, "vsav2.zip"), v2_op,
                    "--data-out", v2_da], check=True, capture_output=True)
    wheels = {"native": (v2_da, "vsav2"), "ours": (os.path.join(build, "verify_data.bin"), "vsavj")}
    got = {}
    for side, (view, s) in wheels.items():
        w = os.path.join(out, "wheel_%s.json" % side)
        subprocess.run([sys.executable, os.path.join(tools, "select_wheel.py"), view, "--set", s, "--json", w],
                       check=True, capture_output=True, cwd=export)
        for player, cells in ((1, (VICTOR,)), (2, tuple(CELL.values()))):
            for c in cells:
                r = subprocess.run([sys.executable, os.path.join(tools, "select_paths.py"), w, "--cell", c,
                                    "--player", str(player)], check=True, capture_output=True, text=True, cwd=export)
                got[(side, player, c)] = r.stdout.strip().split(": ", 1)[-1]
    for p in (v2_op, v2_da):
        os.remove(p)
    return got


def victim_inputs(export, rig, rpl, p1, p2):
    """The original victim gate's `leg_rpl` and `leg_pokes` (level pinned): the rig's prologue replaced by the two
    real routes; the six id pokes and the cadence HP pins dropped, one HP pin 10 frames before each event."""
    sys.path.insert(0, os.path.join(export, "tools"))
    import name_moves as nm
    src = open(rpl).read()
    assert src.count(nm.REPLAY17_PROLOGUE) == 1, "the rig does not carry replay 17's prologue verbatim"
    text = src.replace(nm.REPLAY17_PROLOGUE, nm.prologue_for(p1.split(), p2.split()))
    ids = [p for p in rig["pokes"] if p.split(":")[1] in ("ff8782", "ff8b82")]
    hp = [p for p in rig["pokes"] if p.split(":")[1] == "ff8850"]
    assert len(ids) == 6, "expected the six early-window id pokes, found %d" % len(ids)
    rest = [p for p in rig["pokes"] if p not in ids and p not in hp]
    return text, rest + ["%d:ff8850:01200120" % (e["frame"] - 10) for e in rig["events"]] + [
        "2000-%d:ff8116:08" % (rig["frames"] - 1)]


def corpus_leg(export, romdir, build, out, mame, name):
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
    trace = os.path.join(d, "trace.txt")
    env = dict(os.environ, ROMDIR=romdir, MAME_BIN=mame, MAME_SANDBOX=os.path.join(d, "sb"), MAME_ROMPATH=rp,
               REPLAY=rpl, FIELDS=FIELDS, FIELD_OUT=trace, FRAMES=str(last + 200))
    env.pop("POKES", None)
    with open(os.path.join(d, "mame.log"), "w") as log:
        subprocess.run([os.path.join(export, "tools", "run_mame.sh"), s, "-autoboot_script",
                        os.path.join(export, "tests", "lua", "field_trace.lua")], cwd=d, env=env, stdout=log,
                       stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    subprocess.run(["rm", "-rf", os.path.join(d, "sb")])
    return name, s, trace


def corpus_report(out, names):
    """Every stretch any fighter spends in routine 0x10 (`+0x04` high word 0x0210), per replay."""
    incomplete, stretches = [], []
    for name in names:
        rows, done = load(os.path.join(out, "corpus", name, "trace.txt"))
        if not done:
            incomplete.append(name)
        for p, _, _ in PLAYERS:
            prev, run = [], None
            for f in sorted(rows):
                r = rows[f]
                st = r[p + "_st"] & 0xFFFFFFFF
                if st >> 16 == ROUTINE:
                    if run is None:
                        run = {"from": f, "states": [], "id": r[p + "_id"], "v0a": r[p + "_v0a"], "before": prev[-3:],
                               "xy": []}
                    if not run["states"] or run["states"][-1] != st:
                        run["states"].append(st)
                    run["xy"].append((r[p + "_x"], r[p + "_y"]))
                else:
                    if run is not None:
                        run["to"] = f
                        stretches.append((name, p, run))
                        run = None
                    if not prev or prev[-1] != st:
                        prev.append(st)
            if run is not None:
                run["to"] = max(rows) + 1
                stretches.append((name, p, run))
    print("corpus: %d replays, %d traced to their FIELDSUMMARY; incomplete: %s" % (
        len(names), len(names) - len(incomplete), " ".join(incomplete) or "none"))
    for name, p, run in stretches:
        print("%s %s: frames %d-%d, id %#04x, +0x0A %#04x, states %s, after %s; y %d..%d" % (
            name, p.upper(), run["from"], run["to"] - 1, run["id"], run["v0a"],
            " ".join("%08X" % s for s in run["states"]), " ".join("%08X" % s for s in run["before"]),
            min(y for _, y in run["xy"]), max(y for _, y in run["xy"])))
    print("stretches in routine 0x10: %d; in the STATE %08X: %d" % (
        len(stretches), STATE, sum(STATE in r["states"] for _, _, r in stretches)))


def rig_of(export, part):
    if part.startswith("roll_"):
        _, hold, p2 = part.split("_")
        return {"tenant": "roll", "frames": ROLL["frames"], "events": [
            {"name": "P2 %s rolls (%s held %s)" % (p2, hold, ROLL["hold"]), "frame": ROLL["from"],
             "gap": ROLL["to"] - ROLL["from"]}]}
    return json.load(open(os.path.join(export, "tests", "replays", "naming", part + ".json")))


def roll_leg(export, romdir, build, out, mame, part, side):
    _, hold, p2 = part.split("_")
    d = os.path.join(out, "%s.%s" % (part, side))
    os.makedirs(d)
    rpl = os.path.join(d, "%s.%s.rpl" % (part, side))
    open(rpl, "w").write(open(os.path.join(export, ROLL["base"])).read() + "%s p2=%s\n" % (ROLL["hold"], hold))
    pokes = ";".join("%d:%s:%s" % (f, a, v) for a, v in (("ff8782", ROLL["p1"]), ("ff8b82", p2))
                     for f in (1400, 1450, 1500))
    s, rp = ("vsav2", romdir) if side == "native" else ("vsavjw", os.path.join(build, "rompath") + ";" + romdir)
    trace = os.path.join(out, "tr_%s.%s.txt" % (part, side))
    env = dict(os.environ, ROMDIR=romdir, MAME_BIN=mame, MAME_SANDBOX=os.path.join(d, "sb"), MAME_ROMPATH=rp,
               REPLAY=rpl, POKES=pokes, FIELDS=FIELDS, FIELD_OUT=trace, FIELD_FROM=str(ROLL["from"]),
               FIELD_TO=str(ROLL["to"]), FRAMES=str(ROLL["frames"]))
    with open(os.path.join(d, "mame.log"), "w") as log:
        subprocess.run([os.path.join(export, "tools", "run_mame.sh"), s, "-autoboot_script",
                        os.path.join(export, "tests", "lua", "field_trace.lua")], cwd=d, env=env, stdout=log,
                       stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    subprocess.run(["rm", "-rf", os.path.join(d, "sb")])
    return part, side, trace


def leg(export, romdir, build, out, mame, route, part, side):
    if part.startswith("roll_"):
        return roll_leg(export, romdir, build, out, mame, part, side)
    rig = json.load(open(os.path.join(export, "tests", "replays", "naming", part + ".json")))
    fr = rig["frames"]
    d = os.path.join(out, "%s.%s" % (part, side))
    os.makedirs(d)
    rpl = os.path.join(export, "tests", "replays", "naming", part + ".rpl")
    s, rp = ("vsav2", romdir) if side == "native" else ("vsavjw", os.path.join(build, "rompath") + ";" + romdir)
    tenant = rig["tenant"].replace("_victim", "")
    if "_victim" in part:
        text, pokes = victim_inputs(export, rig, rpl, route[(side, 1, VICTOR)], route[(side, 2, CELL[tenant])])
    else:
        text = open(rpl).read() if side == "native" else cursor(rpl, CURSOR[tenant])
        pokes = rig["pokes"] + ["2000-%d:ff8116:06" % (fr - 1)]
    pokes = ";".join(pokes + ["2363-%d:ff80d4:0000" % (fr - 1)])
    rpl = os.path.join(d, "%s.%s.rpl" % (part, side))
    open(rpl, "w").write(text)
    trace = os.path.join(out, "tr_%s.%s.txt" % (part, side))
    env = dict(os.environ, ROMDIR=romdir, MAME_BIN=mame, MAME_SANDBOX=os.path.join(d, "sb"), MAME_ROMPATH=rp,
               REPLAY=rpl, POKES=pokes, FIELDS=FIELDS, FIELD_OUT=trace, FIELD_FROM="2300", FIELD_TO=str(fr),
               FRAMES=str(fr))
    with open(os.path.join(d, "mame.log"), "w") as log:
        subprocess.run([os.path.join(export, "tools", "run_mame.sh"), s, "-autoboot_script",
                        os.path.join(export, "tests", "lua", "field_trace.lua")], cwd=d, env=env, stdout=log,
                       stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    subprocess.run(["rm", "-rf", os.path.join(d, "sb")])
    return part, side, trace


def load(trace):
    rows, done = {}, False
    for line in open(trace):
        s = line.split()
        if s and s[0] == "F":
            rows[int(s[1])] = {k: int(v) for k, v in (kv.split("=") for kv in s[2:])}
        elif "FIELDSUMMARY" in line:
            done = True
    return rows, done


def event_rows(rows, f0, gap, p="p1"):
    """For player `p`: (distinct +0x04 longs in order with first frame, the STATE's figures or None)."""
    seen, inside = [], []
    for f in range(f0, f0 + gap):
        r = rows.get(f)
        if r is None:
            continue
        st = r[p + "_st"] & 0xFFFFFFFF
        if not seen or seen[-1][1] != st:
            seen.append((f, st))
        if st == STATE:
            inside.append((f, {k[len(p) + 1:]: v for k, v in r.items() if k.startswith(p + "_")}))
    info = None
    if inside:
        ys = [r["y"] for _, r in inside]
        info = {"frames": len(inside), "first": inside[0][0], "id": inside[0][1]["id"], "v0a": inside[0][1]["v0a"],
                "enter": (inside[0][1]["x"], inside[0][1]["y"]), "min_y": min(ys), "max_y": max(ys),
                "leave": (inside[-1][1]["x"], inside[-1][1]["y"]), "xy": [(r["x"], r["y"]) for _, r in inside]}
    return seen, info


def report(out):
    meta = json.load(open(os.path.join(out, "capture.json")))
    for p, h in meta["read"]:
        print("read %s sha1 %s" % (p, h))
    if meta.get("corpus"):
        return corpus_report(out, meta["corpus"])
    summary = []
    for part in meta["parts"]:
        rig = rig_of(meta["export"], part)
        legs = {}
        for side in ("native", "ours"):
            rows, done = load(os.path.join(out, "tr_%s.%s.txt" % (part, side)))
            legs[side] = rows
            print("%s %s: %d frames traced, %s" % (part, side, len(rows), "complete" if done else "INCOMPLETE"))
        for ev in rig["events"]:
            if ev.get("movement") or ev["gap"] <= 0:
                continue
            for p, _, _ in PLAYERS:
                res = {side: event_rows(legs[side], ev["frame"], ev["gap"], p) for side in legs}
                hit = {side: res[side][1] for side in res}
                if not any(hit.values()):
                    continue
                print("\n%s @%d %s — %s" % (part, ev["frame"], ev["name"], p.upper()))
                for side in ("native", "ours"):
                    seen, info = res[side]
                    print("  %-6s states: %s" % (side, " ".join("%08X@+%d" % (st, f - ev["frame"]) for f, st in seen)))
                    if info:
                        print("  %-6s in STATE: %d frames from +%d, id %#04x, +0x0A %#04x; x,y enter %s, y min %d max"
                              " %d, leave %s" % (side, info["frames"], info["first"] - ev["frame"], info["id"],
                                                 info["v0a"], info["enter"], info["min_y"], info["max_y"],
                                                 info["leave"]))
                same = bool(hit["native"] and hit["ours"] and hit["native"]["xy"] == hit["ours"]["xy"])
                dy = ([b[1] - a[1] for a, b in zip(hit["native"]["xy"], hit["ours"]["xy"])]
                      if all(hit.values()) else [])
                print("  trajectory in STATE: %s" % ("IDENTICAL" if same else "DIFFERS (ours y - native y, by frame: %s)"
                                                     % dy if dy else "entered on one leg only"))
                summary.append((part, ev["name"], p, "%#04x" % (hit["native"] or hit["ours"])["id"],
                                bool(hit["native"]), bool(hit["ours"]), same))
    print("\nSUMMARY (part, event, player, id, STATE on native, on ours, trajectory identical)")
    for row in summary:
        print("  %s | %s | %s | %s | %s | %s | %s" % row)
    print("events entering the STATE: %d" % len(summary))


def main():
    args = sys.argv[1:]
    if args[:1] == ["--report"]:
        return report(os.path.realpath(args[1]))
    opts = {"--bin": os.path.join(ROOT, "build", "emu", "mame-wide", "mame", "cps2"), "--jobs": "6",
            "--rigs": "naming,victim"}
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
    kinds = opts["--rigs"].split(",")
    corpus = (sorted(f[:-4] for f in os.listdir(os.path.join(export, "tests", "replays")) if f.endswith(".rpl"))
              if "corpus" in kinds else [])
    if corpus and len(kinds) > 1:
        raise SystemExit("REFUSED: --rigs corpus runs alone")
    parts = tuple(p for k in kinds for p in RIGS[k])
    read = [(mame, sha1(mame)), (os.path.join(build, "rompath", "vsavjw.zip"),
                                 sha1(os.path.join(build, "rompath", "vsavjw.zip")))]
    for z in ("vsav2.zip", "vsavj.zip", "vsav.zip"):
        read.append((os.path.join(romdir, z), sha1(os.path.join(romdir, z))))
    if any(p.startswith("roll_") for p in parts):
        read.append((os.path.join(export, ROLL["base"]), sha1(os.path.join(export, ROLL["base"]))))
    for part in (p for p in parts if not p.startswith("roll_")):
        for x in ("rpl", "json"):
            p = os.path.join(export, "tests", "replays", "naming", "%s.%s" % (part, x))
            read.append((p, sha1(p)))
    route = routes(export, romdir, build, out) if any("_victim" in p for p in parts) else {}
    for k, v in sorted(route.items()):
        print("route %s P%d cell %s: %s" % (k + (v,)))
    for name in corpus:
        p = os.path.join(export, "tests", "replays", name + ".rpl")
        read.append((p, sha1(p)))
    json.dump({"export": export, "romdir": romdir, "build": build, "bin": mame, "parts": parts, "read": read,
               "corpus": corpus,
               "routes": ["%s P%d %s: %s" % (k + (v,)) for k, v in sorted(route.items())]},
              open(os.path.join(out, "capture.json"), "w"), indent=1)
    if corpus:
        with ThreadPoolExecutor(int(opts["--jobs"])) as pool:
            for name, s, trace in pool.map(lambda n: corpus_leg(export, romdir, build, out, mame, n), corpus):
                print("ran %s on %s -> %s" % (name, s, trace), flush=True)
        return report(out)
    jobs = [(part, side) for part in parts for side in ("native", "ours")]
    with ThreadPoolExecutor(int(opts["--jobs"])) as pool:
        for part, side, trace in pool.map(lambda j: leg(export, romdir, build, out, mame, route, *j), jobs):
            print("ran %s %s -> %s" % (part, side, trace), flush=True)
    report(out)


if __name__ == "__main__":
    main()
