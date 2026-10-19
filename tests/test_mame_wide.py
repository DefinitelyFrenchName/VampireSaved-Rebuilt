"""test_mame_wide.py — the gate on the WIDE-profile MAME (tools/setup_mame.py --profile wide; docs/project/cps2_wide.md,
ratified for this repository 2026-10-19, SPEC.md §0). [VSR-2]'s conditions on a profile, measured: the patched binary
running stock vsavj reproduces the reference binary (the emulator superset invariant), the WIDE set is inert against
the stock set, and the B4 canary proves the 19th tile-address bit reaches the appended banks. A class F gate (SPEC.md
§5.1): it runs the original's own `tests/test_mame_wide.sh`, unchanged, in the export, with this repository's two
binaries and the export's WIDE romsets (the original's `tools/build_wide_romset.py`: `build/wide0/rompath`, the
shippable overlay, and `build/wide_canary/rompath`, group C a copy of group B, never merged into a build).

  W1 IDENTITY  the WIDE build.json names the pin, profile `wide` and this tree's patch's SHA-1; the reference's names
               the pin and profile `none`; each binary's SHA-1 is its build.json's; the WIDE binary knows `vsavjw` and
               the reference does not
  W2 PROFILE   the original's gate prints `PASS: CPS-2 WIDE profile gate (MAME)`; each of its three sections reads
               `ok` on every replay of its corpus (work RAM AND framebuffer), none failed, none skipped

CONTROLS ([VSR-22]):
  ref-as-wide       W1 with the reference binary in the WIDE binary's place: W1 must fail
  canary-unreached  a perturbed copy of the original's gate whose canary run reads the SHIPPABLE overlay (group C
                    zero-filled) instead of the canary set: the sprites relocated into banks 4/5 then fetch zeros,
                    so section 3 must FAIL on the framebuffer ([MFI-39]: "I broke X and something changed")
A normal run runs `ref-as-wide` in-process and `canary-unreached` on one replay (CONTROL_REPLAY), and reports each
FIRED or DEAD; `--control <name>` runs the gate with that control applied, where it must FAIL.

Usage: python3 tests/test_mame_wide.py [--wide DIR] [--ref DIR] [--export DIR] [--roms DIR] [--control NAME]
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import runlog  # noqa: E402
from setup_mame import PINNED, PROFILES, STAMP, knows  # noqa: E402
from test_phase0_tables import read_table  # noqa: E402

CONTROLS = {"ref-as-wide": {"W1"}, "canary-unreached": {"W2"}}
GATE = os.path.join("tests", "test_mame_wide.sh")
PERTURBED = os.path.join("tests", "ctl_canary_unreached_test_mame_wide.sh")
CANARY_LINE = 'go "cw_$rp" "$WIDE_BIN" vsavjw "$CANARY_ROMPATH;$ROMDIR" "$rp" canary'
CONTROL_REPLAY = "02_demitri_vs_cpu"


def binary_of(build):
    rec = json.load(open(os.path.join(build, STAMP)))
    return os.path.join(build, rec.get("binary", "mame/cps2")), rec


def identity(wide_dir, ref_dir, wide_bin=None):
    """(ok, figures) for W1; `wide_bin` replaces the WIDE binary under test (the ref-as-wide control)."""
    patch_sha = hashlib.sha1(open(os.path.join(ROOT, PROFILES["wide"]), "rb").read()).hexdigest()
    figs, ok = [], True
    for label, d, profile, sha_want in (("wide", wide_dir, "wide", patch_sha), ("ref", ref_dir, "none", None)):
        b, rec = binary_of(d)
        if label == "wide" and wide_bin:
            b = wide_bin
        sha = hashlib.sha1(open(b, "rb").read()).hexdigest()
        wide = knows(b, "vsavjw")
        good = (rec.get("pin") == PINNED and rec.get("profile", "none") == profile and rec.get("patch_sha1") == sha_want
                and sha == rec.get("binary_sha1") and wide == (profile == "wide"))
        ok = ok and good
        figs.append("W1 %s: %s sha1 %s; build.json pin %s profile %s patch %s sha1 %s; knows vsavjw %s" % (
            label, b, sha, rec.get("pin", "-")[:8], rec.get("profile", "none"), (rec.get("patch_sha1") or "-")[:8],
            rec.get("binary_sha1"), "yes" if wide else "no"))
    return ok, figs


def sections(text):
    """{section number: (ok rows, failed rows, skipped)} of the original gate's output."""
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^== (\d)\. ", line)
        if m:
            cur = m.group(1)
            out[cur] = [0, 0, "SKIPPED" in line]
        elif cur and line.startswith("  ok: "):
            out[cur][0] += 1
        elif cur and line.startswith("  FAIL: "):
            out[cur][1] += 1
        elif cur and "SKIPPED" in line:
            out[cur][2] = True
    return out


def profile(text, corpus):
    s = sections(text)
    verdict = re.findall(r"^(PASS|FAIL|PARTIAL)\b.*$", text, re.M)
    ok = verdict == ["PASS"] and all(s.get(k, [0, 1, True]) == [corpus, 0, False] for k in "123")
    return ok, ["W2 section %s: ok %d, failed %d, skipped %s" % (k, *s.get(k, [0, 0, True])) for k in "123"] + [
        "W2 original verdict %s, corpus %d" % ("/".join(verdict) or "none", corpus)]


def run_gate(export, script, env, args=()):
    p = subprocess.run(["sh", script] + list(args), cwd=export, env=env, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def perturbed_copy(export):
    text = open(os.path.join(export, GATE)).read()
    if text.count(CANARY_LINE) != 1:
        return None
    path = os.path.join(export, PERTURBED)
    open(path, "w").write(text.replace(CANARY_LINE, CANARY_LINE.replace("$CANARY_ROMPATH", "$WIDE_ROMPATH")))
    return PERTURBED


def main():
    args = sys.argv[1:]
    opts = {}
    for name in ("--wide", "--ref", "--export", "--roms", "--control"):
        if name in args:
            i = args.index(name)
            opts[name] = args[i + 1] if i + 1 < len(args) else ""
            args = args[:i] + args[i + 2:]
    control = opts.get("--control")
    pin = read_table(os.path.join(ROOT, "docs", "project", "tables", "roster.tsv"))[0]
    wide_dir = os.path.realpath(opts.get("--wide") or os.path.join(ROOT, "build", "emu", "mame-wide"))
    ref_dir = os.path.realpath(opts.get("--ref") or os.path.join(ROOT, "build", "emu", "mame-ref"))
    export = os.path.realpath(opts.get("--export") or os.path.join(ROOT, "build", "export_" + pin))
    roms = os.path.realpath(opts.get("--roms") or os.path.join(ROOT, "..", "ROMS"))
    run = runlog.Run("test_mame_wide", "control:" + control if control else "normal")
    print("wide: %s\nref: %s\nexport: %s\nroms: %s" % (wide_dir, ref_dir, export, roms))
    if control is not None and control not in CONTROLS:
        print("REFUSED: no declared control named %r (declared: %s)" % (control, ", ".join(CONTROLS)))
        run.record("REFUSED", declared=list(CONTROLS))
        sys.exit(3)
    if control is not None:
        print("MODE: control %s (the gate must FAIL)" % control)
    failed, figures, fired, dead = set(), [], [], []
    ref_bin = binary_of(ref_dir)[0]

    ok, figs = identity(wide_dir, ref_dir, ref_bin if control == "ref-as-wide" else None)
    figures += figs
    if not ok:
        failed.add("W1")
    if control is None:
        if not identity(wide_dir, ref_dir, ref_bin)[0]:
            print("CONTROL FIRED: ref-as-wide (W1 fails with %s as the WIDE binary)" % ref_bin)
            fired.append("ref-as-wide")
        else:
            print("CONTROL DEAD: ref-as-wide (W1 passed)")
            dead.append("ref-as-wide")
            failed.add("control:ref-as-wide")

    if control != "ref-as-wide":
        env = dict(os.environ, ROMDIR=roms, MAME_WIDE_BIN=binary_of(wide_dir)[0], MAME_REF_BIN=ref_bin)
        for k in ("CPS2_WIDE_CANARY", "WIDE_ROMPATH", "CANARY_ROMPATH", "VIDEO_OUT", "MAME_ROMPATH"):
            env.pop(k, None)
        corpus_text = open(os.path.join(export, GATE)).read()
        corpus = len([t for t in re.search(r'CORPUS="\$\{\*:-([^}]*)\}"', corpus_text).group(1).split()
                      if t != "\\"])    # the default list continues its lines with a backslash
        script = GATE
        if control == "canary-unreached":
            script = perturbed_copy(export)
        if script is None:
            print("REFUSED: the canary line was not found once in %s" % GATE)
            failed.add("W2")
        else:
            code, text = run_gate(export, script, env)
            log = os.path.join(ROOT, "build", "tmp", "test_mame_wide.%s.log" % (control or "normal"))
            os.makedirs(os.path.dirname(log), exist_ok=True)
            open(log, "w").write(text)
            print("original gate: %s exit %d, output in %s" % (script, code, log))
            for line in text.splitlines():
                if line.startswith(("  WIDE binary", "  reference", "  both binaries")):
                    print("  | " + line.strip())
            ok, figs = profile(text, corpus)
            figures += figs
            if not ok:
                failed.add("W2")
        if control is None:
            pscript = perturbed_copy(export)
            ctext = run_gate(export, pscript, env, [CONTROL_REPLAY])[1] if pscript else ""
            s = sections(ctext)
            if s.get("1") == [1, 0, False] and s.get("2") == [1, 0, False] and s.get("3") == [0, 1, False] \
                    and "(framebuffer differs)" in ctext and "(work RAM differs)" not in ctext:
                print("CONTROL FIRED: canary-unreached (%s: sections 1 and 2 ok, section 3 FAIL on the framebuffer "
                      "alone)" % CONTROL_REPLAY)
                fired.append("canary-unreached")
            else:
                print("CONTROL DEAD: canary-unreached (%s: sections %s)" % (CONTROL_REPLAY, s or "none"))
                dead.append("canary-unreached")
                failed.add("control:canary-unreached")
        if os.path.exists(os.path.join(export, PERTURBED)):
            os.remove(os.path.join(export, PERTURBED))
    for f in figures:
        print(f)
    print("VERDICT: %s" % ("PASS" if not failed else "FAIL (" + ", ".join(sorted(failed)) + ")"))
    run.record("PASS" if not failed else "FAIL", failed=failed, cases=2, declared=list(CONTROLS), fired=fired,
               dead=dead)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
