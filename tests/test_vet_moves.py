"""test_vet_moves.py — the gate on the five veteran moves that read the VICTIM's row of a left-on-shell table (#6):
against each newcomer, each move places its fighters on a build exactly as on native vs2, and against Victor it is
unchanged (docs/project/tables/README.md "The five veteran moves").

The rig is tools/vet_moves.py, unchanged: P1 Bulleta (ES pursuit), Gallon (Wild Circular), Zabel (Hell Dunk), Morrigan
(Cryptic Needle) or Felicia (the headsit) against P2 Victor 0x03 and each newcomer (0x13, 0x10, 0x11, by the same id
pokes on both games), speed level and RNG pinned ([VSR-26]); native vsav2 from the rom dir against the build's vsavjw
from <build>/rompath, both on the WIDE MAME. Each leg runs the read tap at the moves' sites and the field trace.

  K1 FIRED    on every leg: the tap live and the trace complete; the move's site read P2's id and only the part's id;
              P1's `+0x106` is the move's command id within two trace frames of the read; a move that spends a stock
              spent the one poked ([VSR-180]); for the two moves that set the victim's capture pose (Zabel, Morrigan),
              the victim's node after the read is a pose of its own pose table. A part failing it is VOID, never
              judged ([VSR-194])
  K2 CONTROL  every move against Victor: P1's (dx, dy) to P2, frame by frame from the site's read for SPAN frames,
              and the victim's capture pose index, identical on both legs. Every veteran row of the five tables is
              the same on both games, so this checks the instrument, the rig and the pokes ([VSR-177])
  K3 PORT     every move against each newcomer: the same, identical on both legs (vs2's rows on the build)
The read frames are reported, not asserted ([VSR-179]). Zabel's row is a POSE index, which no position can show
([VSR-178]): the pose is what judges it. The pose index on the build is read through the build's own pose tables, so
it says which pose the move asked for, not whether the build's pose table is right ([VSR-51]).

CONTROLS ([VSR-22]), on the recorded legs, after the real verdict:
  victor-moved     ours' bulleta_03 trace with P1's x raised by 1 px five frames after the read: K2 must fail
  newcomer-moved   ours' felicia_13 trace, the same change: K3 must fail
  site-missing     native's zabel_11 site reads removed: K1 must fail
  victor-pose      ours' zabel_03 capture pose index raised by 1: K2 must fail
A normal run applies each control and reports it FIRED or DEAD; `--control <name>` runs the gate on the perturbed
legs, where it must FAIL. A control is judged on the checks it declares: on a build where K3 already fails (the
original's), `newcomer-moved` cannot be told from the defect, and says so.

Usage: python3 tests/test_vet_moves.py <build dir> <out dir> [--export DIR] [--roms DIR] [--bin MAME] [--jobs N]
                                       [--control NAME]
       <build dir> holds rompath/vsavjw.zip (a merged build's output); <out dir> must not exist (a run owns it).
"""
import copy
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import runlog  # noqa: E402
from vet_moves import MOVES, PARTS, SIDES, SPAN, STOCK_AT, VICTOR, legs, measure, rel  # noqa: E402

PIN = "bf92acd2"
CONTROLS = {"victor-moved": {"K2"}, "newcomer-moved": {"K3"}, "site-missing": {"K1"}, "victor-pose": {"K2"}}


def perturb(got, name):
    """A copy of the legs with the control's change."""
    got = copy.deepcopy(got)
    if name in ("victor-moved", "newcomer-moved"):
        g = got[("bulleta_" + VICTOR if name == "victor-moved" else "felicia_13", "ours")]
        if g["site"]:
            f = g["site"][0][0] + 5
            if f in g["rows"]:
                g["rows"][f]["p1_x"] += 1
    elif name == "site-missing":
        got[("zabel_11", "native")]["site"] = []
    elif name == "victor-pose":
        g = got[("zabel_" + VICTOR, "ours")]
        if g["pose"] is not None:
            g["pose"] += 1
    return got


def fired(part, side, g):
    """The reasons a leg did not produce the move's event (empty: it did)."""
    move, victim = part.split("_")
    m, bad = MOVES[move], []
    if not g["live"]:
        bad.append("%s tap dead (no END or no write to +0x382)" % side)
    if not g["done"]:
        bad.append("%s trace not complete" % side)
    if not g["site"]:
        return bad + ["%s site never read" % side]
    ids = {(who, i) for _, who, i in g["site"]}
    if ids != {("P2", int(victim, 16))}:
        bad.append("%s site read %s" % (side, " ".join("%s:%02X" % x for x in sorted(ids))))
    f0, rows = g["site"][0][0], g["rows"]
    if not any(rows.get(f, {}).get("p1_cmd") == m["cmd"] for f in range(f0, f0 + 3)):
        bad.append("%s +0x106 not %#04x by %d" % (side, m["cmd"], f0 + 2))
    if m.get("stock") and not (rows.get(STOCK_AT + 1, {}).get("p1_stock") == 1 and rows.get(f0 + 1, {}).get("p1_stock") == 0):
        bad.append("%s the stock poked at %d not spent by %d" % (side, STOCK_AT, f0 + 1))
    if "pose" in m and (g["pose"] is None or g["pose"] < 0):
        bad.append("%s the victim's node is no pose of its table" % side)
    return bad


def judge(got):
    """(failed checks, printed figures, per-part lines)."""
    failed, figures, lines = set(), [], []
    void, control, port = [], [], []
    for part in PARTS:
        bad = [b for side in SIDES for b in fired(part, side, got[(part, side)])]
        if bad:
            void.append(part)
            lines.append("  %s VOID: %s" % (part, "; ".join(bad)))
            continue
        seq = {side: rel(got[(part, side)]["rows"], got[(part, side)]["site"][0][0]) for side in SIDES}
        pos = len(seq["native"]) == SPAN and seq["native"] == seq["ours"]
        poses = [got[(part, side)]["pose"] for side in SIDES]
        same = pos and poses[0] == poses[1]
        first = [n for n, (a, b) in enumerate(zip(seq["native"], seq["ours"])) if a != b]
        lines.append("  %s read @%d/%d: positions %s%s%s" % (
            part, got[(part, "native")]["site"][0][0], got[(part, "ours")]["site"][0][0],
            "IDENTICAL" if pos else "DIFFER", "" if pos or not first else
            " (first at +%d: native %d,%d ours %d,%d)" % ((first[0],) + seq["native"][first[0]] + seq["ours"][first[0]]),
            "" if poses[0] is None else "; capture pose native %#04x ours %#04x %s" % (
                poses[0], poses[1], "IDENTICAL" if poses[0] == poses[1] else "DIFFER")))
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
    run = runlog.Run("test_vet_moves", "control:" + control if control else "normal")
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
    meta = measure(export, roms, build, out, mame, jobs=int(opts["--jobs"]))
    for p, h in meta["read"]:
        print("read %s sha1 %s" % (p, h))
    got = legs(out, meta)
    on, dead = [], []
    if control is not None:
        print("MODE: control %s (the gate must FAIL)" % control)
        failed, figures, lines = judge(perturb(got, control))
    else:
        failed, figures, lines = judge(got)
        for name, want in CONTROLS.items():
            res = judge(perturb(got, name))[0]
            if want & failed:
                print("CONTROL UNJUDGEABLE: %s (its checks %s already fail on the real legs)" % (
                    name, ",".join(sorted(want))))
            elif want <= res and not (res - failed - want):
                print("CONTROL FIRED: %s (failed %s, as declared)" % (name, ",".join(sorted(want))))
                on.append(name)
            else:
                print("CONTROL DEAD: %s (failed %s, declared %s)" % (name, ",".join(sorted(res - failed)) or "nothing",
                                                                     ",".join(sorted(want))))
                dead.append(name)
                failed.add("control:" + name)
    for line in lines:
        print(line)
    for f in figures:
        print(f)
    print("VERDICT: %s" % ("PASS" if not failed else "FAIL (" + ", ".join(sorted(failed)) + ")"))
    run.record("PASS" if not failed else "FAIL", failed=failed, cases=len(PARTS), declared=list(CONTROLS),
               fired=on, dead=dead)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
