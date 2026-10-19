"""build_proof.py — phase 0's build proof: the original's build, run on its own manifests and on the manifests rendered
from the tables, produces the same output byte for byte (SPEC.md §3).

In RUN_DIR (which must not exist; a run owns its directory, SPEC.md §4):
  1. two exports of the original at PIN (tools/export_original.py), `pristine/` and `rendered/`;
  2. in BOTH, the same shim of the copy of `tools/audit_roms.py`: vhunt2 dropped from its required sets, its key
     checks and its manifest rows, every other member still checked (the maintainer's ruling of 2026-10-18,
     SPEC.md §0; vhunt2 is not in ROMDIR by the ruling that dropped it);
  3. in `rendered/`, the canonical manifests deleted and rendered from TABLES_DIR (tools/render_manifests.py), the
     five held values derived from ROMDIR (tools/gen_held.py), so nothing of the original's manifests survives;
  4. the original's `tools/build_merged.sh` in each leg (ROMDIR read only; TMPDIR inside the leg);
  5. every file each build wrote compared byte for byte (a zip member by member, since a zip's timestamps are its
     container's): the verdict is on every non-log file; logs are reported apart, as they name their own paths.

THE CONTROL ([VSR-22]): `--control perturbed-render` changes one rendered value (the first `val` of an
`[[aux_poke]]` in donovan.toml, +1) after rendering, so the builds MUST differ and the proof must FAIL.

Usage: python3 tools/build_proof.py <original checkout> <pin> <romdir> <tables dir> <run dir> [--control NAME]
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import phase0lib  # noqa: E402
import render_manifests  # noqa: E402
import runlog  # noqa: E402

CONTROLS = ("perturbed-render",)
OUT = "build/proof_merged"            # the build's output, relative to each leg


def shim_audit(leg):
    """The ruled vhunt2 shim, applied to one leg's copy of tools/audit_roms.py; returns the SHA-1 after it."""
    p = os.path.join(leg, "tools", "audit_roms.py")
    text = open(p).read()
    edits = [
        ('    ("vhunt2.zip", "vhunt2.key", 0x61306B20),\n    ("vhunt2r1.zip", "vhunt2.key", 0x61306B20),\n', ""),
        ('REQUIRED_ZIPS = ["qsound_hle.zip", "vhunt2.zip", "vhunt2r1.zip", "vsav.zip",',
         'REQUIRED_ZIPS = ["qsound_hle.zip", "vsav.zip",'),
        ("        inv[path] = (int(size), int(crc, 16), sha)",
         '        if not path.startswith("vhunt2"):\n            inv[path] = (int(size), int(crc, 16), sha)'),
    ]
    for old, new in edits:
        if text.count(old) != 1:
            raise SystemExit("REFUSED: the audit shim does not apply to %s (%r)" % (p, old[:40]))
        text = text.replace(old, new)
    open(p, "w").write(text)
    return hashlib.sha1(text.encode()).hexdigest()


def perturb(leg):
    p = os.path.join(leg, "build", "manifest", "donovan.toml")
    text = open(p).read()
    m = re.search(r"(?ms)^\[\[aux_poke\]\].*?^val = (0x[0-9A-Fa-f]+|\d+)$", text)
    new = text[:m.start(1)] + "%#06x" % (int(m.group(1), 0) + 1) + text[m.end(1):]
    open(p, "w").write(new)
    return "donovan.toml [[aux_poke]] val %s -> %#06x" % (m.group(1), int(m.group(1), 0) + 1)


def build(leg, romdir):
    tmp = os.path.join(leg, "build", "tmp")
    os.makedirs(tmp, exist_ok=True)
    env = dict(os.environ, ROMDIR=romdir, TMPDIR=tmp)
    t = time.time()
    p = subprocess.run(["sh", "tools/build_merged.sh", OUT], cwd=leg, env=env, capture_output=True, text=True)
    open(os.path.join(leg, "build", "proof_merged.stdout"), "w").write(p.stdout + p.stderr)
    last = (p.stdout + p.stderr).strip().splitlines()[-1:] or [""]
    return p.returncode, time.time() - t, last[0]


def files(base):
    out = {}
    for d, _subdirs, names in os.walk(base):
        for n in names:
            path = os.path.join(d, n)
            out[os.path.relpath(path, base)] = path
    return out


def members(path):
    with zipfile.ZipFile(path) as z:
        return {i.filename: hashlib.sha1(z.read(i.filename)).hexdigest() for i in z.infolist()}


def compare(a, b):
    """(differing non-log files, differing logs, files compared, zip members compared)."""
    fa, fb = files(a), files(b)
    diff, logs, n_members = [], [], 0
    for rel in sorted(set(fa) | set(fb)):
        is_log = rel.endswith(".log")
        if rel not in fa or rel not in fb:
            (logs if is_log else diff).append(rel + " (only in %s)" % ("pristine" if rel in fa else "rendered"))
            continue
        if rel.endswith(".zip"):
            ma, mb = members(fa[rel]), members(fb[rel])
            n_members += len(ma)
            bad = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
            if bad:
                diff.append("%s: members %s" % (rel, ", ".join(bad[:4])))
            continue
        if open(fa[rel], "rb").read() != open(fb[rel], "rb").read():
            (logs if is_log else diff).append(rel)
    return diff, logs, len(set(fa) | set(fb)), n_members


def main():
    args = sys.argv[1:]
    control = None
    if "--control" in args:
        i = args.index("--control")
        control = args[i + 1] if i + 1 < len(args) else ""
        args = args[:i] + args[i + 2:]
        if control not in CONTROLS:
            raise SystemExit("REFUSED: no declared control %r (declared: %s)" % (control, ", ".join(CONTROLS)))
    if len(args) != 5:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    original, pin, romdir, tables, run = args
    run = os.path.realpath(run)
    if os.path.exists(run):
        raise SystemExit("REFUSED: %s exists (a run owns a fresh directory)" % run)
    rec = runlog.Run("build_proof", "control:" + control if control else "normal")
    os.makedirs(run)
    legs = {name: os.path.join(run, name) for name in ("pristine", "rendered")}
    for name, leg in legs.items():
        p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "export_original.py"), original, pin, leg],
                           capture_output=True, text=True, check=True)
        print("export %-8s %s" % (name, " ".join(l.strip() for l in p.stdout.splitlines()[:2])))
        print("shim   %-8s tools/audit_roms.py sha1 %s" % (name, shim_audit(leg)))
    leg = legs["rendered"]
    a = phase0lib.load_census(leg)
    canon = [rel[len("build/manifest/"):] for rel in a.canon(Path(leg))]
    for m in canon:
        os.remove(os.path.join(leg, "build", "manifest", m))
    held_json = os.path.join(run, "held_values.json")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "gen_held.py"), leg, romdir,
                        os.path.join(run, "held"), held_json], capture_output=True, text=True)
    print("\n".join("held   " + l for l in p.stdout.splitlines() if "derived" in l or "wrote" in l))
    if p.returncode:
        raise SystemExit("REFUSED: the held values could not be derived:\n" + p.stdout + p.stderr)
    written = render_manifests.render(tables, os.path.join(leg, "build", "manifest"), json.load(open(held_json)))
    if sorted(written) != sorted(canon):
        raise SystemExit("REFUSED: rendered %d manifests, the census names %d" % (len(written), len(canon)))
    print("render %d canonical manifests deleted and rendered from %s" % (len(canon), tables))
    if control:
        print("MODE: control %s (%s; the proof must FAIL)" % (control, perturb(leg)))
    results = {}
    for name, lg in legs.items():
        code, secs, last = build(lg, romdir)
        results[name] = code
        print("build  %-8s exit %d in %.0f s; last line: %s" % (name, code, secs, last))
    failed = [n for n, c in results.items() if c]
    diff, logs, n_files, n_members = ([], [], 0, 0) if failed else compare(
        os.path.join(legs["pristine"], OUT), os.path.join(legs["rendered"], OUT))
    print("compare %d files (%d zip members); differing non-log files %d, differing logs %d" % (
        n_files, n_members, len(diff), len(logs)))
    for d in diff[:10]:
        print("  DIFFERS: " + d)
    for d in logs[:10]:
        print("  log differs: " + d)
    ok = not failed and not diff and n_files > 0
    print("VERDICT: %s" % ("PASS" if ok else "FAIL (%s)" % ("build failed: " + ", ".join(failed) if failed
                                                          else "%d files differ" % len(diff))))
    rec.record("PASS" if ok else "FAIL", cases=n_files, declared=list(CONTROLS))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
