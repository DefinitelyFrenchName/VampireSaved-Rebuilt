"""gen_held.py — the five values held out of the tables, derived from the reference dumps (docs/project/tables/facts/
held.tsv; SPEC.md §0, the hex ruling).

A held value is a `thunk_hex` that carries whole vanilla or vs2 code or tables, so the tables carry only its SHA-1.
This tool derives each from the decrypted opcode images of vsavj and vsav2 and refuses unless every derived literal
has the SHA-1 held.tsv names for it:
- index_window_018468 and hitclass_map_extend (Huitzil and Pyron): the original's own generators
  (tools/gen_index_window_thunk.py, tools/gen_hitclass_map_thunk.py), run from the export;
- throw_arc_tables and beam_list_type6: rebuilt here from their source spans, each edit named (R-003; the
  original carries them as written, with the reasoning in huitzil.toml's comment blocks above the two rows).
Only addresses, lengths and the authored instructions are in this file; every copied byte is read from the dumps.

Writes OUT_JSON: {sha1: literal} for tools/render_manifests.py --held. Prints the SHA-1 of every dump and image it
read ([VSR-10]) and of every literal it derived, never a byte.

Usage: python3 tools/gen_held.py <export root> <romdir> <scratch dir> <out json>
       (the scratch dir must not exist; the opcode images are written there)
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import phase0lib  # noqa: E402


def sha1(data):
    return hashlib.sha1(data).hexdigest()


def word(img, addr):
    return int.from_bytes(img[addr:addr + 2], "big")


def throw_arc_tables(vs2):
    """vs2's physics-row installer tail (PRG:0x0275E4-0x027622), with its two `(d16,PC)` table operands made
    absolute-long placeholders the build substitutes (data_subst `qqqqqqqq` = map1, `pppppppp` = table2): the
    opcode's source EA goes from mode 7/reg 2 to mode 7/reg 1, and the 2-byte displacement becomes the 4-byte
    placeholder."""
    out = ""
    for lo, hi, ph in ((0x0275E4, 0x0275EC, "qqqqqqqq"), (0x0275F0, 0x0275FA, "pppppppp")):
        op = word(vs2, hi)
        assert op & 0x3F == 0x3A, "PRG:0x%06X: source EA is not (d16,PC)" % hi
        out += vs2[lo:hi].hex() + "%04x" % (op & ~0x3F | 0x39) + ph
    return out + vs2[0x0275FE:0x027622].hex()


def beam_list_type6(vs2, vj):
    """The list-type-6 takeover body, 0xFE bytes, in five parts:
    +0x00 authored: is A0 inside the placed anim region [aaaaaaaa, bbbbbbbb)? (region_subst placeholders) else +0x4A;
    +0x10 vs2's composite-list handler PRG:0x01A1FC-0x01A236, its three A5 scratch slots moved from vs2's
          -$4A80/-$4A88/-$4A84 (a live vsavj buffer) to -$7F00/-$7EF8/-$7EFC, and its `bsr.w` to vs2's child
          dispatcher (PRG:0x0199DC) retargeted to the local one at +0x5C;
    +0x4A vanilla's own type-6 head (PRG:0x01B6AA: move.w/cmp.w), its `bcs.w` rejoined by absolute jumps;
    +0x5C authored child dispatcher: word 4 -> the copied drawer at +0x6E, anything else -> vanilla's drawer
          at $1AFAE ("list already in A0");
    +0x6E vanilla's drawer PRG:0x01B61A-0x01B6AA, with its bank word $2000 -> $1000 and its code bias
          $3800 -> $7A00 (vsavj's $3800 plus vs2's $4200)."""
    body = bytearray.fromhex("b1fc" "aaaaaaaa" "6542" "b1fc" "bbbbbbbb" "643a")       # cmpa.l/bcs.b; cmpa.l/bcc.b
    handler = bytearray(vs2[0x01A1FC:0x01A236])
    for at, old, new in ((0x02, 0xB580, 0x8100), (0x06, 0xB578, 0x8108), (0x0A, 0xB57C, 0x8104),
                         (0x28, 0xB578, 0x8108), (0x30, 0xB57C, 0x8104), (0x34, 0xB580, 0x8100)):
        assert word(handler, at) == old, "vs2 handler +0x%02X is not -$%04X(a5)" % (at, 0x10000 - old)
        handler[at:at + 2] = new.to_bytes(2, "big")
    assert (word(handler, 0x22) == 0x6100 and
            0x01A21E + 2 + int.from_bytes(handler[0x24:0x26], "big", signed=True) == 0x0199DC), "vs2 bsr.w moved"
    handler[0x24:0x26] = (0x5C - (0x32 + 2)).to_bytes(2, "big")
    body += handler
    site = 0x01B6AA
    assert word(vj, site + 4) == 0x6500, "vanilla's type-6 head is not move.w/cmp.w/bcs.w"
    taken = site + 6 + int.from_bytes(vj[site + 6:site + 8], "big", signed=True)
    body += vj[site:site + 4] + bytes.fromhex("6506")                                   # move.w; cmp.w; bcs.b +0x56
    body += bytes.fromhex("4ef9") + (site + 8).to_bytes(4, "big")                      # jmp: not taken
    body += bytes.fromhex("4ef9") + taken.to_bytes(4, "big")                           # jmp: taken
    body += bytes.fromhex("0c500004" "6606" "5448" "60000008" "4ef90001afae")          # cmpi.w #4,(a0); bne.b;
    #                                                         addq.w #2,a0; bra.w +0x6E; jmp $1AFAE.l
    drawer = bytearray(vj[0x01B61A:0x01B6AA])
    for at, old, new in ((0x3C, 0x2000, 0x1000), (0x7E, 0x3800, 0x7A00)):
        assert word(drawer, at) == old, "vanilla drawer +0x%02X is not $%04X" % (at, old)
        drawer[at:at + 2] = new.to_bytes(2, "big")
    body += drawer
    assert len(body) == 0xFE, "beam body is 0x%X bytes" % len(body)
    return body.hex()


def main():
    if len(sys.argv) != 5:
        raise SystemExit(__doc__.strip().splitlines()[-2])
    export, romdir, scratch, out = sys.argv[1:]
    os.makedirs(scratch)
    tools = os.path.join(export, "tools")
    for z in ("vsavj.zip", "vsav2.zip"):
        print("read %s sha1 %s" % (z, sha1(open(os.path.join(romdir, z), "rb").read())))
    img = {}
    for name in ("vsavj", "vsav2"):
        op = os.path.join(scratch, name + "_op.bin")
        subprocess.run([sys.executable, os.path.join(tools, "cps2_decrypt.py"), os.path.join(romdir, name + ".zip"),
                        op, "--data-out", os.path.join(scratch, name + "_data.bin")], check=True, capture_output=True)
        img[name] = open(op, "rb").read()
        print("image %s opcodes sha1 %s" % (name, sha1(img[name])))
    ops = [os.path.join(scratch, "vsavj_op.bin"), os.path.join(scratch, "vsav2_op.bin")]
    run = lambda tool, *extra: subprocess.run([sys.executable, os.path.join(tools, tool)] + ops + list(extra),  # noqa
                                              check=True, capture_output=True, text=True).stdout
    derived = {
        "index_window_018468": run("gen_index_window_thunk.py", "--quiet").strip(),
        "hitclass_map_extend": next(l for l in run("gen_hitclass_map_thunk.py").splitlines()
                                    if l and not l.startswith("#")).strip(),
        "throw_arc_tables": throw_arc_tables(img["vsav2"]),
        "beam_list_type6": beam_list_type6(img["vsav2"], img["vsavj"]),
    }
    held, bad, literals = phase0lib.read_held(), [], {}
    for (manifest, _kind, row, _key), want in sorted(held.items()):
        literal = json.dumps(derived[row])
        got = sha1(literal.encode())
        print("%-24s %-14s derived sha1 %s %s" % (row, manifest, got, "ok" if got == want else "WANT " + want))
        if got != want:
            bad.append(row)
        literals[got] = literal
    if bad:
        raise SystemExit("REFUSED: %d derived values do not have their held SHA-1: %s" % (len(bad), bad))
    json.dump(literals, open(out, "w"), indent=1)
    print("wrote %s: %d held values, every one its held SHA-1" % (out, len(literals)))


if __name__ == "__main__":
    main()
