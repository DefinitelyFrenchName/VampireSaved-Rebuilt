"""doll_build.py — the original's merged build with vs2's doll-hop rows for the newcomers (#6): the passing leg of
tests/test_doll_hop.py until phase 1 builds.

It is tools/build_proof.py's rendered leg plus one step. The original is exported at PIN, its audit shimmed, its
canonical manifests deleted and rendered from TABLES_DIR, and the held values derived from ROMDIR. Then each tenant's
rows of docs/project/tables/doll_hop.tsv are appended to its rendered manifest as `[[aux_poke]]` rows (`poke32`, no slot
flag, so the original's generator applies them on every profile). Each lands at the table's vsavj base
(`facts/table.tsv`, `rec8_b`) + id*0x20 + variant*0x10 + 4 per field. The id is the tenant's on the merged build's
profile (`roster.tsv`), and it must equal the raw id its vs2 row was read at. The original's `tools/build_merged.sh`
then builds it. Its guard on the op count reads the 3-tenant count frozen in the leg's `tests/test_tenant_loop.sh`
(848 at the pin); that count is raised by exactly the rows appended, so the guard stays exact.

After the build it reads the build's own data view (`verify_data.bin`, beside `vanilla_data.bin`): each tenant's row
must equal the table's values, and every other byte of the table must equal vanilla.
Values are discrete per-character values (CLAUDE.md [VSR-8]). Prints the SHA-1 of every file it read ([VSR-10]).

Usage: python3 tools/doll_build.py <original checkout> <pin> <romdir> <tables dir> <run dir>
       The build's output is <run dir>/leg/build/proof_merged (tests/test_doll_hop.py's <build dir>).
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import phase0lib  # noqa: E402
import render_manifests  # noqa: E402
import runlog  # noqa: E402
from build_proof import OUT, build, shim_audit  # noqa: E402
from doll_hop import FIELDS, ROW, TABLE, VARIANT  # noqa: E402
from extract_regions import unfixed  # noqa: E402
from rec8_writes import PROFILE, facts  # noqa: E402

TABLE_ROWS = 32                    # the table's ids: 0x00-0x1F, rows of 0x20
FROZEN_OPS = 848                   # the 3-tenant op count the leg's tests/test_tenant_loop.sh freezes at the pin


def rows_of(tables):
    """{tenant: [(id, variant, [field values])]} from doll_hop.tsv, and its SHA-1."""
    path = os.path.join(tables, "doll_hop.tsv")
    out = {}
    for line in open(path):
        c = line.rstrip("\n").split("\t")
        if line.startswith("#") or c[0] == "tenant":
            continue
        out.setdefault(c[0], []).append((int(c[1], 16), int(c[2]), c[3:3 + len(FIELDS)]))
    return out, sha1_file(path)


def sha1_file(path):
    return hashlib.sha1(open(path, "rb").read()).hexdigest()


def profile_id(roster, tenant):
    tid = int(roster[("%s.toml" % tenant, "tenant", tenant, "id")], 16)
    for kv in roster.get(("%s.toml" % tenant, "tenant", tenant, "id_by_profile"), "").strip('"').split(","):
        key, _, val = kv.partition("=")
        if key.strip() == PROFILE:
            tid = int(val, 16)
    return tid


def pokes(tables):
    """{tenant: [(name, addr, val)]}: the `poke32` rows, and the table's vsavj base."""
    table, _ = facts(os.path.join("facts", "table.tsv"))
    roster, _ = facts("roster.tsv")
    base = int(table[("bank_map.toml", "table", TABLE, "vsavj")], 16)
    rows, _ = rows_of(tables)
    out = {}
    for tenant, rs in rows.items():
        tid = profile_id(roster, tenant)
        for cid, var, vals in rs:
            if cid != tid:
                raise SystemExit("REFUSED: %s's vs2 row is id %#04x, its id on %s is %#04x" % (
                    tenant, cid, PROFILE, tid))
            for k, (f, v) in enumerate(zip(FIELDS, vals)):
                addr = base + tid * ROW + var * VARIANT + 4 * k
                val = int.from_bytes(unfixed(v), "big")
                out.setdefault(tenant, []).append(("doll_hop_%s_v%d" % (f, var), addr, val))
    return out, base


def append(leg, rows):
    for tenant, rs in rows.items():
        p = os.path.join(leg, "build", "manifest", "%s.toml" % tenant)
        text = open(p).read()
        text += "".join('\n[[aux_poke]]\nname = "%s"\naddr = %#08x\nop = "poke32"\nval = %#010x\n' % r for r in rs)
        open(p, "w").write(text)


def shim_ops(leg, added):
    """The leg's frozen 3-tenant op count, raised by the rows appended; returns (old, new)."""
    p = os.path.join(leg, "tests", "test_tenant_loop.sh")
    text = open(p).read()
    old = 'check_n "3 tenants" "$WORK/three" %d ' % FROZEN_OPS
    if text.count(old) != 1:
        raise SystemExit("REFUSED: %s does not freeze the 3-tenant count at %d" % (p, FROZEN_OPS))
    open(p, "w").write(text.replace(old, 'check_n "3 tenants" "$WORK/three" %d ' % (FROZEN_OPS + added)))
    return FROZEN_OPS, FROZEN_OPS + added


def check(out_dir, rows, base):
    """(lines, ok): the build's data view over the table against the rows and vanilla."""
    van = open(os.path.join(out_dir, "vanilla_data.bin"), "rb").read()
    ver = open(os.path.join(out_dir, "verify_data.bin"), "rb").read()
    want = bytearray(van[base:base + TABLE_ROWS * ROW])
    for rs in rows.values():
        for _, addr, val in rs:
            want[addr - base:addr - base + 4] = val.to_bytes(4, "big")
    got = ver[base:base + TABLE_ROWS * ROW]
    lines = ["read %s sha1 %s" % (os.path.join(out_dir, n), hashlib.sha1(b).hexdigest())
             for n, b in (("vanilla_data.bin", van), ("verify_data.bin", ver))]
    changed = sum(got[i] != van[base + i] for i in range(len(got)))
    lines.append("built: table PRG:0x%06X-0x%06X, bytes differing from vanilla %d, from the expected rows %d" % (
        base, base + len(got), changed, sum(a != b for a, b in zip(got, want))))
    return lines, got == bytes(want) and changed > 0


def main():
    args = sys.argv[1:]
    if len(args) != 5:
        raise SystemExit(__doc__.strip().splitlines()[-2])
    original, pin, romdir, tables, run = args
    run, romdir, tables = (os.path.realpath(a) for a in (run, romdir, tables))
    if os.path.exists(run):
        raise SystemExit("REFUSED: %s exists (a run owns a fresh directory)" % run)
    rec = runlog.Run("doll_build", "normal")
    os.makedirs(run)
    leg = os.path.join(run, "leg")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "export_original.py"), original, pin, leg],
                       capture_output=True, text=True, check=True)
    print("export %s" % " ".join(l.strip() for l in p.stdout.splitlines()[:2]))
    sha, absent = shim_audit(leg, romdir)
    print("shim   tools/audit_roms.py sha1 %s; vhunt2 sets dropped (not in ROMDIR): %s" % (
        sha, ", ".join(absent) or "none"))
    a = phase0lib.load_census(leg)
    canon = [rel[len("build/manifest/"):] for rel in a.canon(Path(leg))]
    for m in canon:
        os.remove(os.path.join(leg, "build", "manifest", m))
    held_json = os.path.join(run, "held_values.json")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "gen_held.py"), leg, romdir,
                        os.path.join(run, "held"), held_json], capture_output=True, text=True)
    if p.returncode:
        raise SystemExit("REFUSED: the held values could not be derived:\n" + p.stdout + p.stderr)
    written = render_manifests.render(tables, os.path.join(leg, "build", "manifest"), json.load(open(held_json)))
    if sorted(written) != sorted(canon):
        raise SystemExit("REFUSED: rendered %d manifests, the census names %d" % (len(written), len(canon)))
    print("render %d canonical manifests deleted and rendered from %s" % (len(canon), tables))
    rows, base = pokes(tables)
    print("read %s sha1 %s" % (os.path.join(tables, "doll_hop.tsv"), rows_of(tables)[1]))
    append(leg, rows)
    for tenant, rs in rows.items():
        print("append %s.toml: %d [[aux_poke]] poke32 rows, PRG:0x%06X-0x%06X" % (
            tenant, len(rs), rs[0][1], rs[-1][1] + 4))
    added = sum(len(r) for r in rows.values())
    print("shim   tests/test_tenant_loop.sh 3-tenant op count %d -> %d" % shim_ops(leg, added))
    code, secs, last = build(leg, romdir)
    print("build  exit %d in %.0f s; last line: %s" % (code, secs, last))
    ok = code == 0
    if ok:
        lines, ok = check(os.path.join(leg, OUT), rows, base)
        for line in lines:
            print(line)
        print("read %s sha1 %s" % (os.path.join(leg, OUT, "rompath", "vsavjw.zip"),
                                   sha1_file(os.path.join(leg, OUT, "rompath", "vsavjw.zip"))))
    print("VERDICT: %s" % ("PASS" if ok else "FAIL"))
    rec.record("PASS" if ok else "FAIL", cases=sum(len(r) for r in rows.values()))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
