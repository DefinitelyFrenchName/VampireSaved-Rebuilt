"""setup_mame.py — the pinned MAME, built from its recorded source as the reference instrument (CLAUDE.md [VSR-9];
SPEC.md §5.2; the `mame-fbneo-instruments` skill, [MFI-21]..[MFI-25]).

The pin is the original's: its gitlink `emu/mame` at bf92acd2 and the PINNED of its `tools/setup_mame.sh`, commit
27a8d9e85b58058965907d1d8a7a92f8ed039348 (tag mame0288), the MAME version (0.288) of the Homebrew binary that froze
its vanilla oracle logs. This builds the REFERENCE binary only, with no profile patch: parity before the patch
([MFI-24]); a WIDE profile is built only once the maintainer ratifies it for this repository ([VSR-2]).

In OUT (a new directory, or one this tool made for this pin; anything else is refused, SPEC.md §4):
  1. the pinned commit fetched from SOURCE (a git URL or path, upstream by default) into OUT/src.git, a bare
     repository, refused unless the fetched commit is the pin ([MFI-21]: compare the commit, never a tag name);
  2. its tree extracted by `git archive` into OUT/mame: a tree, never a working copy, so nothing can be dirty;
  3. the CPS-2 subtarget built as the original's setup_mame.sh builds it (MAKE below), the log in OUT/make.log;
  4. the artifact asserted, not the exit code ([MFI-23], [MFI-25]): `-listfull vsavj` known, `-listfull vsavjw`
     unknown; OUT/build.json records the pin, the make line, the toolchain and the binary's SHA-1, which is printed.
Re-run on an OUT it made, it resumes the make and asserts again.

Python, as the harness is ([VSR-11]); `make` and the emulator are launched processes.

Usage: python3 tools/setup_mame.py <out dir> [--source URL_OR_PATH]
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
    source = UPSTREAM
    if "--source" in args:
        i = args.index("--source")
        source, args = args[i + 1], args[:i] + args[i + 2:]
    if len(args) != 1:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    out = os.path.realpath(args[0])
    if any(c.isspace() for c in out):
        raise SystemExit("REFUSED: %r holds a space; MAME's build cannot ([MFI-22])" % out)
    stamp = os.path.join(out, STAMP)
    if os.path.exists(out):
        mine = os.path.exists(stamp) and json.load(open(stamp)).get("pin") == PINNED
        if not mine:
            raise SystemExit("REFUSED: %s exists and is not this tool's build of %s" % (out, PINNED[:8]))
    else:
        os.makedirs(out)
        json.dump({"pin": PINNED, "tag": TAG}, open(stamp, "w"), indent=1)
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
    print("MAME source: %s (tag %s), fetched from %s, extracted at %s" % (PINNED[:8], TAG, rec.get("source"), tree))

    jobs = os.environ.get("MAME_JOBS") or str(os.cpu_count() or 4)
    make = MAKE + ["-j" + jobs]
    with open(os.path.join(out, "make.log"), "a") as log:
        p = subprocess.run(make, cwd=tree, stdout=log, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        tail = open(os.path.join(out, "make.log")).read().splitlines()[-15:]
        raise SystemExit("make exit %d; make.log ends:\n%s" % (p.returncode, "\n".join(tail)))

    binary = os.path.join(tree, "cps2")
    if not os.access(binary, os.X_OK):
        raise SystemExit("FAIL: the build finished and no binary is at %s" % binary)
    if not knows(binary, "vsavj"):
        raise SystemExit("FAIL: the binary does not know vsavj ([MFI-23]: a SOURCES build omits a missing driver)")
    if knows(binary, "vsavjw"):
        raise SystemExit("FAIL: the binary knows vsavjw: not a reference build ([MFI-24])")
    sha = hashlib.sha1(open(binary, "rb").read()).hexdigest()
    rec.update({"make": " ".join(make[:-1]), "binary": os.path.relpath(binary, out), "binary_sha1": sha,
                "version": tool_version([binary, "-version"]), "cc": tool_version(["cc", "--version"]),
                "sdl3": tool_version(["pkg-config", "--modversion", "sdl3"]),
                "pkgconf": tool_version(["pkg-config", "--version"])})
    json.dump(rec, open(stamp, "w"), indent=1)
    print("verified: knows vsavj, does not know vsavjw")
    print("binary %s sha1 %s (MAME %s; %s; SDL3 %s)" % (binary, sha, rec["version"], rec["cc"], rec["sdl3"]))


if __name__ == "__main__":
    main()
