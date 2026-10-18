"""runlog.py — the run record: one JSON line per gate run, appended under build/runs/ (SPEC.md §6; #3).

A gate calls `record(...)` once, just before it exits, with its own verdict. The line says what ran (the gate, its mode),
on what (HEAD, and whether the tree had changes against it, with a digest of those changes), what it found (the verdict,
the checks that failed, its case count) and what its controls did (declared, fired, dead), and how long it took.
`tools/metrics.py` reads these lines for the dashboard's gate figures. build/ is git-ignored: the log is this host's
record, not the repository's; a figure taken from it is captured into docs/project/metrics/figures.tsv at the close.

Written in Python as the gates are (CLAUDE.md [VSR-11]: the record is a few fields from the gate's own process, and
the gates that write it are Python).
"""
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RUNS = os.path.join(ROOT, "build", "runs")


def tree_state():
    """(HEAD, dirty, digest): digest is the SHA-1 of `git status --porcelain` plus `git diff HEAD`, or "" when clean."""
    def git(*a):
        p = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True, text=True)
        return p.stdout if p.returncode == 0 else ""
    head = git("rev-parse", "HEAD").strip()
    status = git("status", "--porcelain=v1", "--untracked-files=all")
    if not status:
        return head, False, ""
    return head, True, hashlib.sha1((status + git("diff", "HEAD")).encode()).hexdigest()[:12]


class Run:
    """Started when the gate starts; `record` writes the line."""

    def __init__(self, gate, mode="normal"):
        self.gate, self.mode, self.t0 = gate, mode, time.time()
        self.start = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def record(self, verdict, failed=(), cases=None, declared=(), fired=(), dead=(), runs=None):
        head, dirty, digest = tree_state()
        line = {"gate": self.gate, "mode": self.mode, "start": self.start,
                "end": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "duration_s": round(time.time() - self.t0, 2), "head": head, "dirty": dirty, "diff": digest,
                "verdict": verdict, "failed": sorted(failed), "cases": cases, "controls_declared": list(declared),
                "controls_fired": sorted(fired), "controls_dead": sorted(dead)}
        path = os.path.join(runs or RUNS, "runs.jsonl")
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "a") as f:
                f.write(json.dumps(line, sort_keys=True) + "\n")
        except OSError as exc:
            print("RUNLOG: not written (%s)" % exc)
            return None
        print("RUNLOG: %s %s %s, %.1f s" % (self.gate, self.mode, verdict, line["duration_s"]))
        return line


def read(runs=None):
    path = os.path.join(runs or RUNS, "runs.jsonl")
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path):
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out
