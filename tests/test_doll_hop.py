"""test_doll_hop.py — the gate on the newcomers' doll hop (#6): after Anakaris's Royal Judgement, each newcomer's doll
hops on a build exactly as on native vs2, and Victor's is unchanged (docs/project/tables/README.md "The doll's hop";
the rows: docs/project/tables/doll_hop.tsv, ruled 2026-10-20, `SPEC.md` §0).

The rig is tools/state_capture.py's `doll`, unchanged: P1 Anakaris 0x06 lands Royal Judgement, P2 holds U or UR through
the doll (8 parts: Victor 0x03 and each newcomer, 0x13, 0x10, 0x11, by the same id pokes on both games), speed level
and RNG pinned ([VSR-26]); native vsav2 from the rom dir against the build's vsavjw from <build>/rompath, both on the
WIDE MAME. A hop is a stretch of sequence 6 of routine 0x10 (state_capture's `hops`).

  K1 TRACED   every leg traced to its FIELDSUMMARY, at least one hop on it, and P2's id (+0x382) in the state is the
              part's id; a part failing it is VOID, never judged ([VSR-180], [VSR-194])
  K2 CONTROL  Victor's hops, U and UR: the ordered per-frame (dx, dy) of every hop identical on both legs. Victor's
              row is vsavj's on both games, so this checks the instrument, the rig and the pokes ([VSR-177])
  K3 PORT     each newcomer's hops, U and UR: identical on both legs (vs2's rows on the build)
Start frames are reported, not asserted ([VSR-179]); Victor's identical start frames say the legs run in step.

CONTROLS ([VSR-22]), on the recorded traces, after the real verdict:
  victor-moved     ours' Victor U trace with its sixth frame in the state raised by 1 px: K2 must fail
  newcomer-moved   ours' Donovan U trace, the same change: K3 must fail
  hop-missing      native's Pyron UR trace with the state removed: K1 must fail
A normal run applies each control and reports it FIRED or DEAD; `--control <name>` runs the gate on the perturbed
traces, where it must FAIL. A control is judged on the checks it declares: on a build where K3 already fails (the
original's), `newcomer-moved` cannot be told from the defect, and says so.

Usage: python3 tests/test_doll_hop.py <build dir> <out dir> [--export DIR] [--roms DIR] [--bin MAME] [--jobs N]
                                     [--control NAME]
       <build dir> holds rompath/vsavjw.zip (a merged build's output); <out dir> must not exist (a run owns it).
"""
import copy
import os
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import runlog  # noqa: E402
from state_capture import RIGS, STATE, VICTOR, hops, load, roll_leg, sha1  # noqa: E402

PIN = "bf92acd2"
PARTS = RIGS["doll"]
CONTROLS = {"victor-moved": {"K2"}, "newcomer-moved": {"K3"}, "hop-missing": {"K1"}}


def perturb(legs, name):
    """A copy of the traces with the control's change: {(part, side): (rows, done)}."""
    legs = copy.deepcopy(legs)
    if name in ("victor-moved", "newcomer-moved"):
        rows = legs[("doll_U_03" if name == "victor-moved" else "doll_U_13", "ours")][0]
        inside = [f for f in sorted(rows) if (rows[f]["p2_st"] & 0xFFFFFF00) == STATE]
        rows[inside[min(5, len(inside) - 1)]]["p2_y"] += 1
    elif name == "hop-missing":
        for r in legs[("doll_UR_11", "native")][0].values():
            if (r["p2_st"] & 0xFFFFFF00) == STATE:
                r["p2_st"] = 0x02000000
    return legs


def judge(legs):
    """(failed checks, printed figures, per-part lines)."""
    failed, figures, lines = set(), [], []
    void, control, port = [], [], []
    for part in PARTS:
        want = int(part.split("_")[2], 16)
        got, bad = {}, []
        for side in ("native", "ours"):
            rows, done = legs[(part, side)]
            h = hops(rows)
            ids = {rows[f]["p2_id"] for f in rows if (rows[f]["p2_st"] & 0xFFFFFF00) == STATE}
            if not done:
                bad.append("%s not traced to its FIELDSUMMARY" % side)
            if not h:
                bad.append("%s no hop" % side)
            if ids != {want}:
                bad.append("%s P2 id in the state %s" % (side, ",".join("%#04x" % i for i in sorted(ids)) or "none"))
            got[side] = h
            for n, (f, path) in enumerate(h):
                lines.append("  %s %-6s hop %d @%d: %d frames, airborne %d, peak dy %d, end dx %d" % (
                    part, side, n + 1, f, len(path), sum(dy > 0 for _, dy in path), max(dy for _, dy in path),
                    path[-1][0]))
        if bad:
            void.append(part)
            lines.append("  %s VOID: %s" % (part, "; ".join(bad)))
            continue
        same = [p for _, p in got["native"]] == [p for _, p in got["ours"]]
        lines.append("  %s hops native %d, ours %d: %s" % (part, len(got["native"]), len(got["ours"]),
                                                          "IDENTICAL" if same else "DIFFER"))
        (control if part.endswith("_" + VICTOR) else port).append((part, same))
    figures.append("K1 parts %d, void %d%s" % (len(PARTS), len(void), (": " + " ".join(void)) if void else ""))
    if void:
        failed.add("K1")
    figures.append("K2 Victor parts judged %d, identical %d" % (len(control), sum(s for _, s in control)))
    if not control or not all(s for _, s in control):         # a void part is K1's, never judged here
        failed.add("K2")
    figures.append("K3 newcomer parts judged %d, identical %d%s" % (
        len(port), sum(s for _, s in port), "".join(" %s=%s" % (p, "same" if s else "DIFFERS") for p, s in port)))
    if not port or not all(s for _, s in port):
        failed.add("K3")
    return failed, figures, lines


def main():
    args = sys.argv[1:]
    opts = {"--export": os.path.join(ROOT, "build", "export_" + PIN), "--roms": os.path.join(ROOT, "..", "ROMS"),
            "--bin": os.path.join(ROOT, "build", "emu", "mame-wide", "mame", "cps2"), "--jobs": "6", "--control": None}
    for name in list(opts):
        if name in args:
            i = args.index(name)
            opts[name], args = (args[i + 1] if i + 1 < len(args) else ""), args[:i] + args[i + 2:]
    if len(args) != 2:
        raise SystemExit(__doc__.strip().splitlines()[-2].strip())
    control = opts["--control"]
    build, out = (os.path.realpath(a) for a in args)
    export, roms, mame = (os.path.realpath(opts[k]) for k in ("--export", "--roms", "--bin"))
    run = runlog.Run("test_doll_hop", "control:" + control if control else "normal")
    if control is not None and control not in CONTROLS:
        print("REFUSED: no declared control named %r (declared: %s)" % (control, ", ".join(CONTROLS)))
        run.record("REFUSED", declared=list(CONTROLS))
        sys.exit(3)
    zip_ = os.path.join(build, "rompath", "vsavjw.zip")
    if not os.path.isfile(zip_):
        print("REFUSED: %s does not exist; a run measures only the build it names ([VSR-132])" % zip_)
        run.record("REFUSED")
        sys.exit(3)
    if os.path.exists(out):
        print("REFUSED: %s exists (a run owns its directory, SPEC.md §4)" % out)
        run.record("REFUSED")
        sys.exit(3)
    os.makedirs(out)
    for p in (mame, zip_, os.path.join(roms, "vsav2.zip"), os.path.join(roms, "vsavj.zip")):
        print("read %s sha1 %s" % (p, sha1(p)))
    jobs = [(part, side) for part in PARTS for side in ("native", "ours")]
    with ThreadPoolExecutor(int(opts["--jobs"])) as pool:
        traces = dict(((part, side), trace) for part, side, trace in
                      pool.map(lambda j: roll_leg(export, roms, build, out, mame, *j), jobs))
    legs = {k: load(t) for k, t in traces.items()}
    fired, dead = [], []
    if control is not None:
        print("MODE: control %s (the gate must FAIL)" % control)
        failed, figures, lines = judge(perturb(legs, control))
    else:
        failed, figures, lines = judge(legs)
        for name, want in CONTROLS.items():
            got = judge(perturb(legs, name))[0]
            if want & failed:
                print("CONTROL UNJUDGEABLE: %s (its checks %s already fail on the real traces)" % (
                    name, ",".join(sorted(want))))
            elif want <= got and not (got - failed - want):
                print("CONTROL FIRED: %s (failed %s, as declared)" % (name, ",".join(sorted(want))))
                fired.append(name)
            else:
                print("CONTROL DEAD: %s (failed %s, declared %s)" % (name, ",".join(sorted(got - failed)) or "nothing",
                                                                     ",".join(sorted(want))))
                dead.append(name)
                failed.add("control:" + name)
    for line in lines:
        print(line)
    for f in figures:
        print(f)
    print("VERDICT: %s" % ("PASS" if not failed else "FAIL (" + ", ".join(sorted(failed)) + ")"))
    run.record("PASS" if not failed else "FAIL", failed=failed, cases=len(PARTS), declared=list(CONTROLS),
               fired=fired, dead=dead)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
