"""export_original.py — a pinned commit of the original, exported read-only into a fresh directory (SPEC.md §0, §3).

Phase 0 reads the original (`DefinitelyFrenchName/VampireSaved`) without ever writing its checkout (the maintainer's
ruling of 2026-10-18: everything above the working directory is read-only). This tool reads ONLY through
`git ls-tree` and `git cat-file --batch` on the checkout, and writes ONLY into OUT_DIR, which must not exist yet (a
run owns its directory, SPEC.md §4). Submodules are skipped and listed; symlinks are recreated as symlinks.

Prints the full commit id, its tree id (the SHA-1 of what was read, [VSR-10]), and the counts.
Usage: python3 tools/export_original.py <original checkout> <commit> <out dir>
"""
import os
import subprocess
import sys


def git(checkout, *args, **kw):
    return subprocess.run(["git", "-C", checkout] + list(args), check=True, capture_output=True, **kw).stdout


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    checkout, commit, out = sys.argv[1:]
    if os.path.exists(out):
        raise SystemExit("refused: %s exists (a run owns a fresh directory)" % out)
    full = git(checkout, "rev-parse", "--verify", commit + "^{commit}").decode().strip()
    tree = git(checkout, "rev-parse", full + "^{tree}").decode().strip()
    entries = []
    for rec in git(checkout, "ls-tree", "-r", "-z", full).split(b"\0"):
        if rec:
            meta, path = rec.split(b"\t", 1)
            mode, kind, sha = meta.decode().split()
            entries.append((mode, kind, sha, path.decode()))
    blobs = [e for e in entries if e[1] == "blob"]
    skipped = [e[3] for e in entries if e[1] != "blob"]
    cat = subprocess.Popen(["git", "-C", checkout, "cat-file", "--batch"], stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    os.makedirs(out)
    total = 0
    for mode, _kind, sha, path in blobs:
        cat.stdin.write((sha + "\n").encode())
        cat.stdin.flush()
        header = cat.stdout.readline().split()
        size = int(header[2])
        data = cat.stdout.read(size)
        cat.stdout.read(1)
        dest = os.path.join(out, path)
        os.makedirs(os.path.dirname(dest) or out, exist_ok=True)
        if mode == "120000":
            os.symlink(data.decode(), dest)
        else:
            with open(dest, "wb") as f:
                f.write(data)
            if mode == "100755":
                os.chmod(dest, 0o755)
        total += size
    cat.stdin.close()
    cat.wait()
    print("commit %s" % full)
    print("tree   %s" % tree)
    print("files  %d (%d bytes)" % (len(blobs), total))
    print("skipped %d non-blob entries%s" % (len(skipped), (": " + ", ".join(skipped)) if skipped else ""))


if __name__ == "__main__":
    main()
