---
name: mister-cps2-wide-core
description: The CPS-2 layer of extending Jotego's jtcps2 into a WIDE CPS-2 core on MiSTer - the CPS-2 core's format caps, the Turbo promote after the terminator test, the complemented decryption-range word, the tile-code-is-SDRAM-address law, the key latched from the download, and Rule 1 v2's MiSTer form. Since 14z-134 it SITS ON the board-agnostic mister-jtframe-core skill, which carries the separate-core mechanism, the runtime profile bit, SDRAM tiers and placement, the simulation lane, synthesis and MRA generation ([MJC-N] lifts [MSC-N], same number; the lifted MSC IDs stay here as redirects). Load both before touching cores/cps2w or any CPS-2 MiSTer measurement. Game-independent - the Vampire Savior specifics are the mister-vampire-saved skill.
---

# CPS-2 WIDE on MiSTer — the core (level 1, game-independent)

Agent-facing rules, IDs `[MSC-NN]`. Each rule is ANCHORED to the paragraph
of the project documentation it distils — the doc carries `**[MSC-NN]**` at
that paragraph. In the original, `tools/checkskills.py` asserted the two sets
match both ways, that this file names nothing game-specific (the liftability
test of its `docs/project/mister_scope.md` §1), and that every number quoted
here appears in a LOG (`docs/platform/mister.md`, `docs/project/mister_map.md`,
`docs/project/mister_fit.md`, the gotchas, `release_format.md`) and never
only in the synthesis. **Read the anchored paragraph before acting on a
rule; the rule is the reminder, the doc is the fact.** Reading order for a
stranger: `docs/project/mister_core.md` (synthesis, causal order) → the log
for any figure you doubt → the gotchas before touching an instrument. (The
original's `HANDOFF.md` "MiSTer" held ITS commands; this repository's
commands are its own.) General RE/measurement discipline is the
`romhacking-methodology` skill (`[RH-NN]`); this file is the platform layer
and cites it rather than restating it.

**Anchors in this repository (Vampire Saved Rebuilt).** Rules whose anchor is in `docs/game/` or
`docs/platform/` resolve once those are imported; rules anchored in the original's `docs/project/`,
`HANDOFF.md` or `STATE.md` point at the original (`DefinitelyFrenchName/VampireSaved` at `6dee2be7`)
until this repository re-homes them. The lock (the original's `tools/checkskills.py`) is to be rebuilt;
until then nothing checks the anchors. Here MiSTer is phase 2 (`SPEC.md` §3). The rules are the
original's; a rule that named the original's own scripts, gates or layout is restated as its lesson
and ends with an *(adapted: …)* note naming what was dropped.

**THE 14z-134 LEVEL-0 CUT.** Asked of every rule, "would this still be
true if the core were not CPS-2?", 63 of the 73 answered YES — the
separate-core mechanism, the header profile bit, every SDRAM tier and
placement law, the gated-RTL method, the whole simulation lane, synthesis
and MRA generation are jtframe/MiSTer facts. They now live in
**`mister-jtframe-core` as `[MJC-N]`, N unchanged**, and stay below as
one-line REDIRECTS (the doc paragraph carries both anchors, `**[MSC-N]**
**[MJC-N]**`) so every citation resolves and the checker fails if a
redirect is deleted. **The ten that stay are the CPS-2 core**: a tile code
IS its SDRAM address ([MSC-21]), the object pipeline's all-ones skip
([MSC-25]), the format caps ([MSC-27]), the Turbo promote after the
terminator ([MSC-28]), the complemented key-range word ([MSC-32]) and
data-vs-code above the window ([MSC-34]), Rule 1 v2's MiSTer form
([MSC-35]), the key latched from the download ([MSC-38]), and the two
unknowns of THIS core ([MSC-70], [MSC-71]).

## 1.1 The separate-core mechanism

- [MSC-1] → lifted to level 0 as [MJC-1] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-2] → lifted to level 0 as [MJC-2] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-3] → lifted to level 0 as [MJC-3] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-4] → lifted to level 0 as [MJC-4] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-5] → lifted to level 0 as [MJC-5] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-6] → lifted to level 0 as [MJC-6] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-7] → lifted to level 0 as [MJC-7] (`mister-jtframe-core`); the anchored paragraph is unchanged.

## 1.2 The runtime profile bit

- [MSC-8] → lifted to level 0 as [MJC-8] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-9] → lifted to level 0 as [MJC-9] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-10] → lifted to level 0 as [MJC-10] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-11] → lifted to level 0 as [MJC-11] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-12] → lifted to level 0 as [MJC-12] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-13] → lifted to level 0 as [MJC-13] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-14] → lifted to level 0 as [MJC-14] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-15] → lifted to level 0 as [MJC-15] (`mister-jtframe-core`); the anchored paragraph is unchanged.

## 1.3 SDRAM: tiers, slots and placement laws

- [MSC-16] → lifted to level 0 as [MJC-16] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-17] → lifted to level 0 as [MJC-17] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-18] → lifted to level 0 as [MJC-18] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-19] → lifted to level 0 as [MJC-19] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-20] → lifted to level 0 as [MJC-20] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-21] **A CPS-2 tile code IS its SDRAM address**: the download scramble undoes the `.rom`'s 4-way interleave, so tile `c` lives at `c * 128`, contiguous and monotonic. Consequences: a read probe's distinct-128-byte-block list is a TILE-CODE list; sparse art cannot be compacted without renumbering codes, which is game data; and never re-derive the tile→member mapping — run the canonical one and reproduce a number somebody already measured first.
- [MSC-22] → lifted to level 0 as [MJC-22] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-23] → lifted to level 0 as [MJC-23] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-24] → lifted to level 0 as [MJC-24] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-25] **GFX ROM CONTENT changes object TIMING** — the object pipeline skips its draw loop on an all-ones fetched word — so anchors are frozen PER BUILD, and "identical inputs, identical RAM" across two builds differing only in GFX is not a safe expectation on this core.
- [MSC-26] → lifted to level 0 as [MJC-26] (`mister-jtframe-core`); the anchored paragraph is unchanged.

## 1.4 The CPS-2 core's format caps and the WIDE RTL

- [MSC-27] **Widening SDRAM does not widen the core.** The caps are FORMAT: a 16-bit tile code + a 2-bit bank from the object table's y-word (32 MB), a flat `rom_cs` decode (4 MB), a 7-bit QSound sample-bank latch (8 MB, aliasing — legacy audio MIS-PLAYS rather than going silent), scroll with no bank input anywhere in its chain (8 MB). No tier lifts any of them; each is the ratified WIDE profile expressed in a third implementation, not an invention.
- [MSC-28] **Promote AFTER the terminator test.** y-word bit 15 is the sprite-list TERMINATOR; the CPS-2 Turbo rule promotes bit 12 into it in the ELSE arm of a terminator test kept VERBATIM from the reference core, and the gate asserts the promote is read at a LATER LINE. Reading bit 15 directly ends the list at the first promoted sprite. The encoding is a contract with the romset build's object-bank encoding — bench every encoding to its own bank with none setting bit 15. *(adapted: the original named its build's encoder, `tools/gfx_tiles.py` `bank_word`.)*
- [MSC-29] → lifted to level 0 as [MJC-29] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-30] → lifted to level 0 as [MJC-30] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-31] → lifted to level 0 as [MJC-31] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-32] **The CPS-2 key's encrypted-opcode RANGE word is stored COMPLEMENTED; MAME and FBNeo read it that way and the reference core reads it STRAIGHT** (decrypting to `$F03FFF` where the hardware stops at `$0FFFFF`). Every stock game hides it — only Capcom-encrypted code executes, and DATA reads bypass the decryptor on every implementation — so EXECUTABLE content above the window is the first thing that sees it. When two implementations read the same configuration word, DIFF THE EXPRESSION, not the result. Fix it gated, one level upstream of the unvalidated comparison, and leave that comparison untouched for the rest of the library.
- [MSC-33] → lifted to level 0 as [MJC-33] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-34] **"Data read from above the window" is not "code executed from above the window."** A relocation test that moves only data tables passes on every implementation and proves nothing about the decryptor; nothing had executed from the extension on a core that decrypts by address until the boot died nine frames after the first opcode fetch.
- [MSC-35] **Rule 1 v2 has a MiSTer form for every clause**: bounded = the enumerated, frozen override set; profile-gated = the runtime bit; the superset invariant = the new core run on the STOCK set against expectations measured on the REFERENCE core and never re-measured on the new one, plus the stock `.rom` bit-identical with its profile byte at the fill; mirrored = the patch series; ratified = per SLICE, each with its own smallest proof and must-fire control.
- [MSC-36] → lifted to level 0 as [MJC-36] (`mister-jtframe-core`); the anchored paragraph is unchanged.

## 1.5 The simulation lane and its instruments

- [MSC-37] → lifted to level 0 as [MJC-37] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-38] **On CPS-2 pass `-load` on EVERY run and drop `-setname`.** The transfer latches the decryption key into core REGISTERS, so a preloaded run boots into ciphertext (work RAM all zeros, a dead 68k); `-setname` always re-links (`ln -srf` relative vs an absolute `$ROMFILE`) and moves your dumps into `sdram.old/`.
- [MSC-39] → lifted to level 0 as [MJC-39] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-40] → lifted to level 0 as [MJC-40] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-41] → lifted to level 0 as [MJC-41] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-42] → lifted to level 0 as [MJC-42] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-43] → lifted to level 0 as [MJC-43] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-44] → lifted to level 0 as [MJC-44] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-45] → lifted to level 0 as [MJC-45] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-46] → lifted to level 0 as [MJC-46] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-47] → lifted to level 0 as [MJC-47] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-48] → lifted to level 0 as [MJC-48] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-49] → lifted to level 0 as [MJC-49] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-50] → lifted to level 0 as [MJC-50] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-51] → lifted to level 0 as [MJC-51] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-52] → lifted to level 0 as [MJC-52] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-53] → lifted to level 0 as [MJC-53] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-54] → lifted to level 0 as [MJC-54] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-55] → lifted to level 0 as [MJC-55] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-56] → lifted to level 0 as [MJC-56] (`mister-jtframe-core`); the anchored paragraph is unchanged.

## 1.6 Synthesis and release of a bitstream

- [MSC-57] → lifted to level 0 as [MJC-57] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-58] → lifted to level 0 as [MJC-58] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-59] → lifted to level 0 as [MJC-59] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-60] → lifted to level 0 as [MJC-60] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-61] → lifted to level 0 as [MJC-61] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-62] → lifted to level 0 as [MJC-62] (`mister-jtframe-core`); the anchored paragraph is unchanged.

## 1.7 MRA and `.rom` generation mechanics

- [MSC-63] → lifted to level 0 as [MJC-63] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-64] → lifted to level 0 as [MJC-64] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-65] → lifted to level 0 as [MJC-65] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-66] → lifted to level 0 as [MJC-66] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-67] → lifted to level 0 as [MJC-67] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-68] → lifted to level 0 as [MJC-68] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-69] → lifted to level 0 as [MJC-69] (`mister-jtframe-core`); the anchored paragraph is unchanged.

## 1.8 What is NOT known — state it, never hide it

- [MSC-70] **Pixels have never been compared by an instrument between the core and an emulator, and audio has never been measured** — the OBJ list agrees, a voice was heard by a person. The reference core's missing one-read QSound bank latency (vs MAME LLE) is recorded and unresolved.
- [MSC-71] **Real silicon's decryption window is INFERRED, never measured** — both emulators share the same research heritage and are not independent witnesses. The complemented reading is almost certainly the hardware's; a profile that executes above the window depends on it.
- [MSC-72] → lifted to level 0 as [MJC-72] (`mister-jtframe-core`); the anchored paragraph is unchanged.
- [MSC-73] → lifted to level 0 as [MJC-73] (`mister-jtframe-core`); the anchored paragraph is unchanged.
