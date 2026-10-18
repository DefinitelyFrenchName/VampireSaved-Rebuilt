"""classify_tests.py — #120 spec draft (14z-205): every script under tests/ classed by how the rebuild can reuse it.

Reads, never writes the tree: docs/project/gate_index.md (GENERATED: kind, tier, needs, the gate's own header sentence),
tests/gate_index.tsv (family), tests/ci_emulator.tsv (lane, scope, cadence) and each script's code lines (comments
dropped). Usage: python3 tools/classify_tests.py <the original's checkout> <out.tsv>.

CLASSES (the spec's § "The tests the rebuild can use"):
  E1  acceptance, as is      an emulator gate whose subject is a built artifact's behaviour, reading the build only
                             through its rompath (or none): it runs unchanged against the rebuild's romset
  E2  acceptance, adapted    an emulator gate that also reads this pipeline's internals (patch.json, placements.json,
                             prg/, verify_*.bin, gen/, a manifest): its verdict applies, its inputs need an adapter
  F   game fact              a gate whose subject is pristine vsavj/vsav2/vhunt2 or the emulators as instruments (no
                             build, no manifest): reusable unchanged, it locks facts the rebuild's docs inherit
  P   pipeline-internal      a static gate on this pipeline's manifests, generators or ops: not reusable; the facts it
                             locks are what the rebuild must carry as documented tables
  T   tooling and process    runner, docs, rule-checker, close and agent tooling gates: a specification for the rebuild's
                             own tooling (port the idea and its controls, not the script)
  M   MiSTer (phase 2)       the Verilator/MiSTer lane: reused when the rebuild reaches the core
  R   releases (phase 2)     release packaging, the applier, launchers and release binaries: reused with phase 2
A ROM-free gate (ci_portable) with no build and no manifest tests this repo's tools: T, not F.
The class is a SCRIPT'S reading of the code, to be confirmed gate by gate when each is ported.
"""
import re, sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2])

rows = {}
for line in (ROOT / "docs/project/gate_index.md").read_text().splitlines():
    m = re.match(r"^\| `tests/([^`]+)\.sh` \| ([^|]*) \| ([^|]*) \| ([^|]*) \| (.*) \| ([^|]*) \|$", line)
    if m:
        g, kind, tier, needs, locks, since = (x.strip() for x in m.groups())
        rows[g] = {"kind": kind, "tier": tier, "needs": needs, "locks": locks, "since": since}
fam = {}
for line in (ROOT / "tests/gate_index.tsv").read_text().splitlines():
    if line and not line.startswith("#"):
        f = line.split("\t")
        fam[f[0].replace("tests/", "").replace(".sh", "")] = f[1]
reg = {}
for line in (ROOT / "tests/ci_emulator.tsv").read_text().splitlines():
    if line and not line.startswith("#"):
        f = line.split("\t")
        reg[f[0]] = {"lane": f[1], "scope": f[2], "cadence": f[3] if len(f) > 3 else ""}

INTERNAL = re.compile(r"(\$\{?BUILD\}?|\$\{?MERGED\}?|\$\{?OUTBASE\}?|build/[A-Za-z0-9_]+)/(patch|prg|placements|verify_|gen/|out/|manifest)")
MANIFEST = re.compile(r"build/manifest/|tools/gen_donovan_patch|tools/build_donovan|tools/build_merged|tools/extract_char|tools/reconcile_batch|tools/patch_prg")
BUILDREF = re.compile(r"\$\{?BUILD|\$\{?MERGED|build/m3b_merged|build/don_m|build/hui|build/pyron|build/m5_|rompath")
PROCESS_FAM = {"runner", "docs"}

def code(g):
    p = ROOT / "tests" / (g + ".sh")
    return "\n".join(l for l in p.read_text(errors="replace").splitlines() if not l.lstrip().startswith("#"))

import hashlib, subprocess
head = subprocess.run(["git", "rev-parse", "--short=8", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
dirty = subprocess.run(["git", "status", "--porcelain", "--", "tests/"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
h = hashlib.sha1()
for sp in sorted((ROOT / "tests").glob("*.sh")):
    h.update(sp.name.encode()); h.update(sp.read_bytes())
with out.open("w") as o:
    idx = {n: hashlib.sha1((ROOT / n).read_bytes()).hexdigest()[:12] for n in ("docs/project/gate_index.md", "tests/gate_index.tsv", "tests/ci_emulator.tsv")}
    o.write("# read from the working tree at HEAD %s%s; the %d top-level tests/*.sh scripts' contents hash to %s (sha1 over name+bytes, sorted); index inputs: %s\n" % (
        head, " plus uncommitted changes under tests/" if dirty else " (tests/ clean)", len(list((ROOT / "tests").glob("*.sh"))), h.hexdigest()[:16],
        ", ".join("%s %s" % (n, v) for n, v in idx.items())))
    o.write("gate\tfamily\tkind\ttier\tlane\tscope\tneeds\tclass\twhy\tcovers\n")
    for p in sorted((ROOT / "tests").glob("*.sh")):
        g = p.stem
        r = rows.get(g, {"kind": "?", "tier": "?", "needs": "?", "locks": "?"})
        c = code(g)
        e = reg.get(g)
        family = fam.get(g, "?")
        if e and e["lane"] == "mister":
            cls, why = "M", "the Verilator/MiSTer lane"
        elif re.search(r"release|applier|package|launcher|readme_recording", g):
            cls, why = "R", "release packaging, the applier or the release binaries"
        elif family in PROCESS_FAM or g.startswith("run_") or "rulecheck" in g or "rule_checker" in g or "close" in g:
            cls, why = "T", "family %s: this project's tooling or process" % family
        elif e:
            hits = sorted(set(m.group(2).rstrip("/_") for m in INTERNAL.finditer(c)))
            man = bool(MANIFEST.search(c))
            if hits or man:
                cls, why = "E2", "reads " + ", ".join(hits + (["the manifests or generator"] if man else []))
            elif BUILDREF.search(c):
                cls, why = "E1", "the build only through its rompath"
            else:
                cls, why = "F", "no build: pristine sets or the emulators as instruments"
        else:
            if MANIFEST.search(c) or INTERNAL.search(c):
                cls, why = "P", "static, on the manifests, generator or a build's internals"
            elif BUILDREF.search(c):
                cls, why = "E1", "static, on a built romset's bytes"
            elif r["tier"] == "ci_portable":
                cls, why = "T", "ROM-free, no build: a test of this repo's tools"
            else:
                cls, why = "F", "static, no build and no manifest"
        o.write("\t".join([g, family, r["kind"], r["tier"], e["lane"] if e else "-", e["scope"] if e else "-",
                           r["needs"], cls, why, r["locks"].replace("\t", " ")[:300]]) + "\n")
print("wrote", out)
