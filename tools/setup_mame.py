"""setup_mame.py — the pinned MAME, built from its recorded source as an instrument (CLAUDE.md [VSR-9]; SPEC.md §5.2;
the `mame-fbneo-instruments` skill, [MFI-21]..[MFI-25], [MFI-31]).

The pin is the original's: its gitlink `emu/mame` at bf92acd2 and the PINNED of its `tools/setup_mame.sh`, commit
27a8d9e85b58058965907d1d8a7a92f8ed039348 (tag mame0288), the MAME version (0.288) of the Homebrew binary that froze
its vanilla oracle logs. Two profiles, each in its own OUT so both binaries exist at once:
  none  the REFERENCE binary, no patch: parity before the patch ([MFI-24]);
  wide  the CPS-2 WIDE v1.2 profile (docs/project/cps2_wide.md), ratified for this repository on 2026-10-19 (SPEC.md
        §0; [VSR-2]): emu/mame-patches/0002-cps2-wide-v1.patch, the original's, applied with patch(1) to the same
        pinned tree, so the two binaries differ by exactly that patch ([MFI-31]).

In OUT (a new directory, or one this tool made for this pin; anything else is refused, SPEC.md §4):
  1. the pinned commit fetched from SOURCE (a git URL or path, upstream by default) into OUT/src.git, a bare
     repository, refused unless the fetched commit is the pin ([MFI-21]: compare the commit, never a tag name);
  2. its tree extracted by `git archive` into OUT/mame: a tree, never a working copy, so nothing can be dirty;
  3. for `wide`, the patch applied with patch(1), never `git apply` ([MFI-25]), and its landing asserted in the
     tree (the marker `cps2wide` in cps2.cpp and the row `vsavjw` in mame.lst);
  4. the CPS-2 subtarget built as the original's setup_mame.sh builds it (MAKE below), the log in OUT/make.log;
  5. the artifact asserted, not the exit code ([MFI-23], [MFI-25]): `-listfull vsavj` known, and `-listfull vsavjw`
     known for `wide`, unknown for `none`; OUT/build.json records the pin, the profile and its patch's SHA-1, the make
     line, the toolchain and the binary's SHA-1, which is printed.
Re-run on an OUT it made for the same pin and profile: when the binary is there with the SHA-1 build.json recorded, it
is NOT rebuilt, only asserted again; otherwise the make resumes. A relink is not byte-reproducible here (R-005: the
code and data sections equal, the UUID and one import stub not), and a binary with a new SHA-1 is a new instrument
that must be proven again, so a changed SHA-1 is printed as `INSTRUMENT MOVED` and the old one kept in build.json.

Python, as the harness is ([VSR-11]); `make` and the emulator are launched processes.

Usage: python3 tools/setup_mame.py <out dir> [--profile none|wide] [--source URL_OR_PATH]
"""
import hashlib
import json
import os
import subprocess
import sys

PINNED = "27a8d9e85b58058965907d1d8a7a92f8ed039348"
TAG = "mame0288"
UPSTREAM = "https://github.com/mamedev/mame.git"
MAKE = ["make", "SUBTARGET=cps2", "SOURCES=src/mame/capcom/cps2.cpp", "NOWERROR=1", "REGENIE=1"]
STAMP = "build.json"
ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PROFILES = {"none": None, "wide": os.path.join("emu", "mame-patches", "0002-cps2-wide-v1.patch")}
MARKERS = ((os.path.join("src", "mame", "capcom", "cps2.cpp"), "cps2wide"),
           (os.path.join("src", "mame", "mame.lst"), "\nvsavjw\n"))


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw).stdout


def tool_version(cmd):
    try:
        return run(cmd).strip().splitlines()[0]
    except (OSError, subprocess.CalledProcessError, IndexError):
        return "absent"


def knows(binary, driver):
    return subprocess.run([binary, "-listfull", driver], capture_output=True).returncode == 0


def main():
    args = sys.argv[1:]
    opts = {"--source": UPSTREAM, "--profile": "none"}
    for name in opts:
        if name in args:
            i = args.index(name)
            opts[name], args = args[i + 1], args[:i] + args[i + 2:]
    source, profile = opts["--source"], opts["--profile"]
    if profile not in PROFILES:
        raise SystemExit("REFUSED: no profile %r (%s)" % (profile, ", ".join(PROFILES)))
    patch = PROFILES[profile] and os.path.join(ROOT, PROFILES[profile])
    patch_sha = patch and hashlib.sha1(open(patch, "rb").read()).hexdigest()
    if len(args) != 1:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    out = os.path.realpath(args[0])
    if any(c.isspace() for c in out):
        raise SystemExit("REFUSED: %r holds a space; MAME's build cannot ([MFI-22])" % out)
    stamp = os.path.join(out, STAMP)
    if os.path.exists(out):
        old = json.load(open(stamp)) if os.path.exists(stamp) else {}
        if (old.get("pin"), old.get("profile", "none"), old.get("patch_sha1")) != (PINNED, profile, patch_sha):
            raise SystemExit("REFUSED: %s exists and is not this tool's build of %s, profile %s" % (
                out, PINNED[:8], profile))
    else:
        os.makedirs(out)
        json.dump({"pin": PINNED, "tag": TAG, "profile": profile, "patch": PROFILES[profile],
                   "patch_sha1": patch_sha}, open(stamp, "w"), indent=1)
    rec = json.load(open(stamp))
    src, tree = os.path.join(out, "src.git"), os.path.join(out, "mame")

    if not os.path.exists(os.path.join(tree, "makefile")):
        if not os.path.exists(src):
            run(["git", "init", "--quiet", "--bare", src])
        run(["git", "-C", src, "fetch", "--quiet", "--depth", "1", source, PINNED])
        got = run(["git", "-C", src, "rev-parse", "FETCH_HEAD^{commit}"]).strip()
        if got != PINNED:
            raise SystemExit("REFUSED: %s gave commit %s, the pin is %s" % (source, got, PINNED))
        os.makedirs(tree, exist_ok=True)
        arc = subprocess.Popen(["git", "-C", src, "archive", "--format=tar", PINNED], stdout=subprocess.PIPE)
        subprocess.run(["tar", "-x", "-C", tree], stdin=arc.stdout, check=True)
        if arc.wait() != 0:
            raise SystemExit("git archive failed")
        rec["source"] = source
        if patch:
            p = subprocess.run(["patch", "-p1", "--forward", "--silent", "-d", tree], stdin=open(patch, "rb"))
            if p.returncode != 0:
                raise SystemExit("FAIL: %s does not apply to the pinned tree" % PROFILES[profile])
    for rel, marker in MARKERS:
        has = marker.encode() in open(os.path.join(tree, rel), "rb").read()
        if has != bool(patch):
            raise SystemExit("FAIL: %s %s the profile's marker %r" % (rel, "lacks" if patch else "carries", marker))
    print("profile %s: %s" % (profile, "patch %s sha1 %s, landed (markers in cps2.cpp and mame.lst)" % (
        PROFILES[profile], patch_sha) if patch else "no patch, no marker in the tree"))
    print("MAME source: %s (tag %s), fetched from %s, extracted at %s" % (PINNED[:8], TAG, rec.get("source"), tree))

    binary = os.path.join(tree, "cps2")
    jobs = os.environ.get("MAME_JOBS") or str(os.cpu_count() or 4)
    make = MAKE + ["-j" + jobs]
    was = rec.get("binary_sha1")
    if was and os.path.exists(binary) and hashlib.sha1(open(binary, "rb").read()).hexdigest() == was:
        print("binary present with its recorded SHA-1: not rebuilt (a relink would move the instrument)")
    else:
        with open(os.path.join(out, "make.log"), "a") as log:
            p = subprocess.run(make, cwd=tree, stdout=log, stderr=subprocess.STDOUT)
        if p.returncode != 0:
            tail = open(os.path.join(out, "make.log")).read().splitlines()[-15:]
            raise SystemExit("make exit %d; make.log ends:\n%s" % (p.returncode, "\n".join(tail)))
    if not os.access(binary, os.X_OK):
        raise SystemExit("FAIL: the build finished and no binary is at %s" % binary)
    if not knows(binary, "vsavj"):
        raise SystemExit("FAIL: the binary does not know vsavj ([MFI-23]: a SOURCES build omits a missing driver)")
    if knows(binary, "vsavjw") != bool(patch):
        raise SystemExit("FAIL: profile %s, and the binary %s vsavjw ([MFI-24], [MFI-25])" % (
            profile, "knows" if not patch else "does not know"))
    sha = hashlib.sha1(open(binary, "rb").read()).hexdigest()
    if was and sha != was:
        print("INSTRUMENT MOVED: the binary was sha1 %s, it is now %s; prove it again before measuring with it" % (
            was, sha))
        rec["previous_sha1"] = rec.get("previous_sha1", []) + [was]
    rec.update({"make": " ".join(make[:-1]), "binary": os.path.relpath(binary, out), "binary_sha1": sha,
                "version": tool_version([binary, "-version"]), "cc": tool_version(["cc", "--version"]),
                "sdl3": tool_version(["pkg-config", "--modversion", "sdl3"]),
                "pkgconf": tool_version(["pkg-config", "--version"])})
    json.dump(rec, open(stamp, "w"), indent=1)
    print("verified: knows vsavj, %s vsavjw" % ("knows" if patch else "does not know"))
    print("binary %s sha1 %s (MAME %s; %s; SDL3 %s)" % (binary, sha, rec["version"], rec["cc"], rec["sdl3"]))


if __name__ == "__main__":
    main()
