"""vet_build.py — the original's merged build with vs2's rows of the five veteran-move tables for the newcomers (#6):
the passing leg of tests/test_vet_moves.py until phase 1 builds.

It is tools/doll_build.py's leg (the original exported at PIN, its audit shimmed, its canonical manifests rendered from
TABLES_DIR, the held values derived from ROMDIR) with other rows appended: docs/project/tables/vet_rows.tsv, each
tenant's row at the table's vsavj base + id * row size. The id is the tenant's on the merged build's profile
(`roster.tsv`), and it must equal the raw id its vs2 row was read at. Rows are written by the WORD, the bytes around a
row kept from vanilla's view:
  - a table read in the DATA view (Zabel's, Morrigan's) by `[[aux_poke]]` `poke16` rows: the stored word, as the 68k
    reads data;
  - a table read in the OPCODE view (Bulleta's, Gallon's, Felicia's: `(d8,PC,Xn)` reads, which CPS-2 decrypts like an
    opcode, [VSR-87]) by `[[code_word]]` rows (`stage = 6`, `addr`, `old_hex` = vanilla's opcode-view word,
    `new_hex`), which the original's generator checks against its vanilla opcode image and emits as a `code` op,
    stored re-encrypted. A `poke` there would write the stored word and the read would see its decryption.
A word holding two tenants' bytes is one row, in the first tenant's manifest. The leg's frozen op count is raised by
exactly the rows appended (doll_build.py's guard).

After the build it reads the build's own views (`verify_op.bin`, `verify_data.bin`, beside `vanilla_op.bin`,
`vanilla_data.bin`): over each table's 32 ids, its view must equal vanilla with the tenants' rows, and in the other view
only the words the rows were written to may differ from vanilla. With `--base <build dir>` (the same build without the
rows, e.g. tools/build_proof.py's), both whole views must differ from that build's in exactly the words written.
Values are discrete per-character values (CLAUDE.md [VSR-8]). Prints the SHA-1 of every file it read ([VSR-10]).

Usage: python3 tools/vet_build.py <original checkout> <pin> <romdir> <tables dir> <run dir> [--base DIR]
       The build's output is <run dir>/leg/build/proof_merged (tests/test_vet_moves.py's <build dir>).
"""
import hashlib
import os
import shutil
import sys
import tempfile

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import runlog  # noqa: E402
from doll_build import finish, prepare, profile_id, sha1_file  # noqa: E402
from rec8_writes import facts, views  # noqa: E402
from vet_rows import COLUMNS, IDS, raw_of  # noqa: E402

SIZE = {"u8": 1, "s16": 2, "s16,s16": 4}


def rows_of(tables):
    """[row dict of vet_rows.tsv's COLUMNS], and its SHA-1."""
    path = os.path.join(tables, "vet_rows.tsv")
    out = []
    for line in open(path):
        c = line.rstrip("\n").split("\t")
        if not line.startswith("#") and c[0] != "move":
            out.append(dict(zip(COLUMNS, c)))
    return out, sha1_file(path)


def plan(tables, vanilla):
    """(tables {base: (view, size, expected 32-id bytes)}, words [(tenant, view, addr, old word, new word, name)]).
    `vanilla` is {"op": opcode view, "data": data view} of vsavj."""
    roster, _ = facts("roster.tsv")
    rows, _ = rows_of(tables)
    spans, owner = {}, {}
    for r in rows:
        tid = profile_id(roster, r["tenant"])
        if tid != int(r["id"], 16):
            raise SystemExit("REFUSED: %s's vs2 row is id %s, its id on the build is %#04x" % (r["tenant"], r["id"], tid))
        base, size, view = int(r["table"][4:], 16), SIZE[r["layout"]], r["view"]
        span = spans.setdefault(base, (view, size, bytearray(vanilla[view][base:base + IDS * size])))[2]
        span[tid * size:(tid + 1) * size] = raw_of(r["value"], size)
        for a in range(base + tid * size, base + (tid + 1) * size):
            owner.setdefault((base, a & ~1), (r["tenant"], r["move"]))
    words = []
    for (base, w), (tenant, move) in sorted(owner.items(), key=lambda kv: (kv[1][0], kv[0])):
        view, _, span = spans[base]
        old, new = vanilla[view][w:w + 2], bytes(span[w - base:w - base + 2])
        if old != new:
            words.append((tenant, view, w, old, new, "vet_%s_%06x" % (move, w)))
    return spans, words


def append(leg, words):
    for tenant in sorted({w[0] for w in words}):
        p = os.path.join(leg, "build", "manifest", "%s.toml" % tenant)
        text = open(p).read()
        for t, view, addr, old, new, name in words:
            if t != tenant:
                continue
            if view == "data":
                text += '\n[[aux_poke]]\nname = "%s"\naddr = %#08x\nop = "poke16"\nval = %#06x\n' % (
                    name, addr, int.from_bytes(new, "big"))
            else:
                text += '\n[[code_word]]\nstage = 6\nname = "%s"\naddr = %#08x\nold_hex = "%s"\nnew_hex = "%s"\n' % (
                    name, addr, old.hex(), new.hex())
        open(p, "w").write(text)


def check(out_dir, spans, words):
    """(lines, ok): the build's views over the tables against the rows and vanilla."""
    names = ("vanilla_op.bin", "vanilla_data.bin", "verify_op.bin", "verify_data.bin")
    img = {n: open(os.path.join(out_dir, n), "rb").read() for n in names}
    lines = ["read %s sha1 %s" % (os.path.join(out_dir, n), hashlib.sha1(img[n]).hexdigest()) for n in names]
    written = {w[2] for w in words}
    ok = bool(words)
    for base, (view, size, want) in sorted(spans.items()):
        other = "data" if view == "op" else "op"
        end = base + IDS * size
        van, got = img["vanilla_%s.bin" % view], img["verify_%s.bin" % view]
        bad = sum(a != b for a, b in zip(got[base:end], want))
        changed = sum(got[i] != van[i] for i in range(base, end))
        o_van, o_got = img["vanilla_%s.bin" % other], img["verify_%s.bin" % other]
        stray = [w for w in range(base, end, 2) if o_got[w:w + 2] != o_van[w:w + 2] and w not in written]
        lines.append("built: table PRG:0x%06X-0x%06X (%s view), bytes differing from vanilla %d, from the expected "
                     "rows %d; %s-view words changed outside the rows written %d" % (
                         base, end, view, changed, bad, other, len(stray)))
        ok = ok and bad == 0 and changed > 0 and not stray
    return lines, ok


def against(base, out_dir, words):
    """(lines, ok): every word of the build's views that differs from the base build's is a word written, and every
    word written differs."""
    lines, ok, written = [], True, {w[2] for w in words}
    for n in ("verify_op.bin", "verify_data.bin"):
        x, y = open(os.path.join(base, n), "rb").read(), open(os.path.join(out_dir, n), "rb").read()
        lines.append("read %s sha1 %s" % (os.path.join(base, n), hashlib.sha1(x).hexdigest()))
        diff = {i & ~1 for i in range(min(len(x), len(y))) if x[i] != y[i]}
        lines.append("against the base: %s words differing %d, of them written %d; words written %d" % (
            n, len(diff), len(diff & written), len(written)))
        ok = ok and len(x) == len(y) and diff == written
    return lines, ok


def main():
    args = sys.argv[1:]
    base = None
    if "--base" in args:
        i = args.index("--base")
        base, args = os.path.realpath(args[i + 1]) if i + 1 < len(args) else "", args[:i] + args[i + 2:]
    if len(args) != 5:
        raise SystemExit(__doc__.strip().splitlines()[-2])
    original, pin, romdir, tables, run = args
    run, romdir, tables = (os.path.realpath(a) for a in (run, romdir, tables))
    if os.path.exists(run):
        raise SystemExit("REFUSED: %s exists (a run owns a fresh directory)" % run)
    rec = runlog.Run("vet_build", "normal")
    leg = prepare(original, pin, romdir, tables, run)
    tmp = tempfile.mkdtemp(prefix="vet_build.", dir=run)
    try:
        v, read = views(leg, romdir, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for p, h in read:
        print("read %s sha1 %s" % (p, h))
    spans, words = plan(tables, {"op": v["vsavj"][0], "data": v["vsavj"][1]})
    print("read %s sha1 %s" % (os.path.join(tables, "vet_rows.tsv"), rows_of(tables)[1]))
    append(leg, words)
    for tenant in sorted({w[0] for w in words}):
        mine = [w for w in words if w[0] == tenant]
        print("append %s.toml: %d [[aux_poke]] poke16 rows, %d [[code_word]] rows: %s" % (
            tenant, sum(w[1] == "data" for w in mine), sum(w[1] == "op" for w in mine),
            " ".join("PRG:0x%06X" % w[2] for w in mine)))
    def built(out):
        lines, ok = check(out, spans, words)
        if base is not None:
            more, ok2 = against(base, out, words)
            lines, ok = lines + more, ok and ok2
        return lines, ok

    ok = finish(leg, romdir, len(words), built)
    rec.record("PASS" if ok else "FAIL", cases=len(words))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
