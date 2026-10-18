---
name: cps2-hardware
description: Hard rules about the CPS-2 board itself, for any CPS-2 game on any emulator - ROM file byte order vs 68k logical order, the encryption window and the opcode/data views, gfx simm interleave and tile addressing, the OBJ sprite-list format (the terminator bit, both ORAM pages, the CPS-2 Turbo promote), QSound packing laws, and the CPS-2 WIDE extended profile as a platform artifact. Load before reading, decrypting, dumping or extending any CPS-2 ROM image. Game-independent; the emulators' behaviour is the cps2-emulation skill, MiSTer is mister-cps2-wide-core.
---

# CPS-2 hardware (level 1, game-independent)

**Anchors in Vampire Saved Rebuilt.** Rules whose anchor is in `docs/game/` or
`docs/platform/` resolve once those are imported; rules anchored in the original's
`docs/project/`, `HANDOFF.md` or `STATE.md` point at the original
(`DefinitelyFrenchName/VampireSaved` at `6dee2be7`) until this repository re-homes them.
The lock (the original's `tools/checkskills.py`) is to be rebuilt; until then nothing
checks the anchors. Session keys (`14z-N`) and issue numbers (`#N`) cited in a rule are
the original's.

Agent-facing rules, IDs `[CPH-NN]`, each ANCHORED `**[CPH-NN]**` at the
paragraph of `docs/platform/gotchas.md` or `docs/project/cps2_wide.md` it
distils, and locked in the original by its skill lock (`tools/checkskills.py`):
lock both ways, no game/character/build names in this file, every number
present in a LOG. The rule is the reminder; the anchored paragraph is the
fact and the incident that paid for it. General discipline is the
`romhacking-methodology` skill (`[RH-NN]`); what MAME and FBNeo DO to a
probe is `mame-fbneo-instruments` (`[MFI-NN]`, board-agnostic, level 0 —
`cps2-emulation` `[CPE-NN]` is its redirect table since 14z-134); the FPGA
core is `mister-cps2-wide-core` (`[MSC-NN]`) on `mister-jtframe-core`
(`[MJC-NN]`). **Four rules of this file were lifted to level 0 at 14z-134
because they are facts about the EMULATORS' loaders, not the board** —
byte order as the loader sees it, hash-before-name resolution, sentinel
CRCs, region-vs-file-vs-sound-CPU layout — and stay below as redirects
(`[CPH-1]`, `[CPH-12]`, `[CPH-13]`, `[CPH-18]` → `[MFI-43..46]`). The other
26 are the CPS-2 board: the cipher, the gfx interleave and tile codec, the
OBJ list, QSound, and the WIDE profile.

## A.1 Bytes, views and the encryption window

- [CPH-1] → lifted to level 0 as [MFI-43] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPH-2] **The program zips store CODE encrypted; only DATA reads bypass the crypt.** Any static analysis of code — diffing against stock, disassembling, searching for an instruction pattern — uses the DECRYPTED opcode space, never the members. Data tables may be read raw from the members (with the `LOAD16_WORD_SWAP` byte order in mind).
- [CPH-3] **PC-relative operand reads are PROGRAM-space and DECRYPTED; `(An)`-based reads are DATA-space and raw.** Pick the view by the READ MODE, not by where the table lives. Absolutizing a `(d16,PC,Dn)` read as `lea` + `(a0,dn)` reads CIPHERTEXT (an odd jump target, an address error at the first hit). Fix shape: hook an instruction BEFORE the pc-relative read and `rts` back into the untouched original.
- [CPH-4] **Anything fetched through the opcode space must be written as CODE wherever it lands — instructions AND every pc-relatively-read table — because the cipher is address-aware**: inside the key range it re-encrypts so the CPU's decryption yields your bytes, outside it passes them through unchanged. `data` is right for An-relative and absolute reads only; embedded data inside a thunk body in crypt space must be `data` or a data read gets ciphertext. The trap has both directions.
- [CPH-5] **When a table's view is in doubt, DECODE BOTH VIEWS and keep the one whose targets land on real code/data** — a pc-rel WORD JUMP TABLE decodes only from the opcode view, a byte map only from the data view, and both live inside the encrypted range. The addressing mode alone is not sufficient for hand analysis; the wrong view produces plausible garbage.
- [CPH-6] **Relocating a pc-relative DISPATCHER: carry a copy of its table INSIDE the thunk body** (emitted as code, so it re-encrypts with it) and keep reading it pc-relatively — never rewrite the read as an absolute data-view load. The cheap discriminator before trusting any table read: count ODD targets per view (38 of 80 odd in the data view = ciphertext).
- [CPH-7] **The encrypted range is INCLUSIVE of its upper word** — the limit test is `<=` on the word address in the emulators (and in the original's cipher, which matches them), so the word at the boundary byte is still encrypted and the first raw word sits one word above. Found by a test whose first draft asserted the opposite; write the test before trusting the behaviour.
- [CPH-8] **Code above the encryption window is stored RAW, automatically and by the cipher's range-awareness** — which is what makes an extended program region viable for ported CODE. Locked in both directions (inside must transform and round-trip; outside must pass through byte-identical), and it FAILS the build rather than warning, because a silent failure turns ported code into executable garbage.

## A.2 Graphics: simms, tiles, identity

- [CPH-9] **Gfx simms are NOT tile-contiguous**: a tile's 32 bytes are sixteen two-byte pairs at stride 4, the even/odd word streams of each 0x80000 block feeding decoded chunks 1 MB apart. Naive contiguous slicing still MATCHES on sibling comparisons (same wrong neighbours both sides), so a sibling calibration certifies a broken method. Verify any hardware-interleaved layout against the emulator's LOADER SOURCE before bulk analysis, and fact-lock it with a test.
- [CPH-10] **Compose a tile address the way the hardware does — `code | ((y & 0x6000) << 3)` — BEFORE dumping it, and print the composition.** Dumping the code without its bank bits compared unrelated vanilla data and "exonerated" a broken band for a session. A null result from a dump is only as good as the address that produced it: give the instrument a band that MUST differ as its negative control.
- [CPH-11] **Within each 8-pixel half of an OBJ tile row, plane bit `i` is pixel `7-i`; the transparent pen is 15, not 0; an OBJ entry at `(x, y)` lands at screen `(x - 64, y - 16)`.** A byte round-trip proves a codec self-consistent, not hardware-correct — verify any SYNTHESIZED tile at the RENDER layer against its intended bitmap (an asymmetric glyph is what caught a 14-session mirror).
- [CPH-12] → lifted to level 0 as [MFI-44] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPH-13] → lifted to level 0 as [MFI-45] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.

## A.3 The OBJ sprite list

- [CPH-14] **OBJ y-word bit 15 is the sprite-list TERMINATOR, not a spare bit** — set it on a sprite and every later sprite is dropped. Before treating any bit of a hardware structure as spare, find the code that CONSUMES the structure; a census of "which bits are set" cannot tell you which bits are load-bearing.
- [CPH-15] **The CPS-2 Turbo rule is the precedent for a 19th tile-address bit: promote y bit 12 into bit 15 AFTER the terminator check, then take three bank bits** — measured never set on a live sprite in the stock game, with a control proving the probe was not blind. The bank bits are DATA (per-character bank tables and a few immediate setters), so a bank value carrying bit 12 flows through existing tables with no code change.
- [CPH-16] **OBJ RAM is double-buffered and a dump spans BOTH pages plus several drawers' output.** Filtering entries to an expected code band showed a byte-perfect match while the screen showed garbage from entries OUTSIDE the filter. When a render contradicts an OBJ-level match, diff the FULL unfiltered entry set on both sides first.
- [CPH-17] **Walk a structure the way the hardware walks it — terminators, bounds, buffer selection — and separate sentinels from values.** A raw y-word census reported 841 "sprites" with bit 15 set: stale data past the terminator, never drawn. A tilemap's raw max code is always `0xFFFF` because unused cells hold that sentinel. A census that ignores the walker confidently answers a question nobody asked.

## A.4 QSound and the Z80 driver

- [CPH-18] → lifted to level 0 as [MFI-46] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPH-19] **A sample window must live in ONE HALF of its 64K bank** — the DSP compares the playback pointer against `end` SIGNED, so a window straddling `0x8000` collapses to its silent loop tail after the attack. Register- and content-level A/Bs were BLIND to it: keep one gate at the OUTPUT level (a WAV capture and a per-window band comparison) when porting content into a player you do not fully model.
- [CPH-20] **A copied sample window must keep the SOURCE offset's BYTE PARITY** — the members are stored pre-swapped and both emulators byteswap pairs at load, so an odd→even move plays every byte pair exchanged: RMS preserved, high band doubled, "PC-speaker" harshness. File-level comparison is blind (the bytes are equal, the LANES differ); the output-level checker must flag BOTH directions of a band change.
- [CPH-21] **A sample record's `end` offset PLAYS — copy the INCLUSIVE window**, provably (native windows end at `0xFFFF`, which an exclusive bound could not express). An exclusive copy leaves one foreign byte at every record's end; where the loop tail is silence, one byte turns the sustain into an impulse train — a "pure computer beep".
- [CPH-22] **A "pure synthetic beep" IS a tight-loop sample** (a few dozen saturated bytes looping); the hardware plays samples only. Rendering a record's window once mischaracterises its sound — render attack + loop repetitions, or better, DIFFERENCE a silence-probe build's audio against the reference build's and judge the difference signal, never envelope peaks at chosen frames.
- [CPH-23] **The loaders' shape rules bind the ROMSET, and each belongs to one implementation**: gfx members come in groups of four of equal size (the FBNeo loader consumes four at a time); QSound length stays a power of two because that is FBNeo's `rom_mask` rule — MAME's ceiling is a 24-bit device interface and the FPGA core has no mask at all; stock members are never resized or reordered, new capacity is APPENDED so legacy provenance stays trivially valid.

## A.5 The CPS-2 WIDE profile as a platform artifact

- [CPH-24] **The WIDE profile is a NAMED, VERSIONED hardware shape** — program 6 MB (the first 1 MB encrypted, the rest raw), gfx 48 MB in three groups of four, QSound 16 MB, Z80 unchanged in size — implemented identically by every target, with the profile's own content-member rules (which members carry content, which sentinels) versioned with it.
- [CPH-25] **`$400000-$40000F` is reserved and never allocated**: the three implementations treat READS there differently (ROM-shadowed, readable registers, ROM under the wide decode), a divergence unobservable ONLY because nothing lives there. The reservation is load-bearing for cross-implementation agreement, not tidiness.
- [CPH-26] **Content authored into the extension is written RAW but laid out in FILE byte order** (logical words converted to file byte order — in the original, `words_to_file_bytes(words_from_logical_bytes(…))`), and the member's real CRC goes into the descriptor.
- [CPH-27] **Before widening anything, MEASURE that the stock game never touches the candidate space** — zero reads of the extension windows, the promote bit never set on a live sprite, no scroll code relying on the address wrap, free driver space — each with a control proving the probe was not blind. Widening is linear where the measurement says nothing reads it; the bit is free where the measurement says nothing sets it.
- [CPH-28] **Inertness is not functionality.** Proving a widened path HARMLESS on stock content (bit-identical RAM and framebuffer) says nothing about whether it REACHES the new space; that needs a positive control — a legacy tile moved into the new bank with the bit set and observed to render from there, a data table relocated where pointing it at zero fill DOES diverge.
- [CPH-29] **Every emulator change under the profile is governed**: bounded and declarative, profile-gated by a separate driver entry so the stock set and every other game are untouched by construction, subject to the emulator superset invariant (the patched binary on the stock set reproduces the frozen expectations bit for bit, as a battery gate), mirrored in a second implementation, ratified per profile version.
- [CPH-30] **The change budget is MEASURED, and an undercount is a retraction-class error.** The profile costs TWO gated blocks in the sprite drawer — the promote and its test-only positive control — and everything else is descriptor table data; a governance summary that said "one gated conditional" was corrected under retraction discipline, and the summary lines that still said it three sessions later were corrected again at 14z-114. Summary lines drift faster than the sections beneath them.
