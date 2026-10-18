---
name: cps2-emulation
description: The CPS-2 layer of driving MAME and FBNeo as instruments - since 14z-134 a THIN layer. Every one of its 42 rules turned out to be true of MAME/FBNeo on any board, so all 42 were lifted to the board-agnostic mame-fbneo-instruments skill ([MFI-N] lifts [CPE-N], same number) and this file keeps each CPE ID as a redirect so citations resolve. Load mame-fbneo-instruments for the rules; load this to resolve a [CPE-N] citation or to find the CPS-2-specific emulator facts, which live in cps2-hardware ([CPH-23], [CPH-25]) and mister-cps2-wide-core ([MSC-32]). Game-independent; the board's own laws are cps2-hardware, the project's rigs are vampire-saved-port.
---

# CPS-2 emulation — MAME and FBNeo as instruments (level 1, game-independent)

**Anchors in Vampire Saved Rebuilt.** Rules whose anchor is in `docs/game/` or
`docs/platform/` resolve once those are imported; rules anchored in the original's
`docs/project/`, `HANDOFF.md` or `STATE.md` point at the original
(`DefinitelyFrenchName/VampireSaved` at `6dee2be7`) until this repository re-homes them.
The lock (the original's `tools/checkskills.py`) is to be rebuilt; until then nothing
checks the anchors. Session keys (`14z-N`) and issue numbers (`#N`) cited in a rule are
the original's.

Agent-facing rules, IDs `[CPE-NN]`, each ANCHORED `**[CPE-NN]**` at the
paragraph of `docs/platform/gotchas.md`, `docs/project/gotchas.md`,
`docs/project/cps2_wide.md` or `HANDOFF.md` it distils, locked in the original by
`tools/checkskills.py`.

**THE 14z-134 LEVEL-0 CUT, and what it found about this skill.** Asked of
every rule, "would this still be true if the board were not CPS-2?" was
answered YES for all 42: `-debug` timing, watchpoint spaces, tap
alignment, focus theft, hash-before-name member resolution, the pinned
source builds, the shared EEPROM, the two-implementation protocol — none of
it is a CPS-2 fact. They now live in **`mame-fbneo-instruments` as
`[MFI-N]`, N unchanged**, and this file is a REDIRECT TABLE: each `[CPE-N]`
below stays DEFINED (the doc paragraph carries both anchors, `**[CPE-N]**
**[MFI-N]**`) so the citations in gate headers, docs and archives keep
resolving, and the original's lock (`tools/checkskills.py`) fails if a redirect is deleted. The
CPS-2-SPECIFIC emulator facts were never here: the loaders' shape rules
are `[CPH-23]`, the reserved window's per-implementation reads `[CPH-25]`,
the complemented key-range word `[MSC-32]`. The theme the rules share,
paid for more than any other in this project: **an emulator reports
success while measuring something else.** Board laws are `[CPH-NN]`;
which rig to reach for is the port skill; the FPGA lane is `[MSC-NN]`.

## B.1 MAME as an instrument: what a probe sees

- [CPE-1] → lifted to level 0 as [MFI-1] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-2] → lifted to level 0 as [MFI-2] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-3] → lifted to level 0 as [MFI-3] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-4] → lifted to level 0 as [MFI-4] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-5] → lifted to level 0 as [MFI-5] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-6] → lifted to level 0 as [MFI-6] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-7] → lifted to level 0 as [MFI-7] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-8] → lifted to level 0 as [MFI-8] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-9] → lifted to level 0 as [MFI-9] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-10] → lifted to level 0 as [MFI-10] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-11] → lifted to level 0 as [MFI-11] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-12] → lifted to level 0 as [MFI-12] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-13] → lifted to level 0 as [MFI-13] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-14] → lifted to level 0 as [MFI-14] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-15] → lifted to level 0 as [MFI-15] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-16] → lifted to level 0 as [MFI-16] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-17] → lifted to level 0 as [MFI-17] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-18] → lifted to level 0 as [MFI-18] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-19] → lifted to level 0 as [MFI-19] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-20] → lifted to level 0 as [MFI-20] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.

## B.2 Building MAME without changing the instrument

- [CPE-21] → lifted to level 0 as [MFI-21] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-22] → lifted to level 0 as [MFI-22] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-23] → lifted to level 0 as [MFI-23] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-24] → lifted to level 0 as [MFI-24] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-25] → lifted to level 0 as [MFI-25] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.

## B.3 FBNeo as an instrument

- [CPE-26] → lifted to level 0 as [MFI-26] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-27] → lifted to level 0 as [MFI-27] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-28] → lifted to level 0 as [MFI-28] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-29] → lifted to level 0 as [MFI-29] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-30] → lifted to level 0 as [MFI-30] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-31] → lifted to level 0 as [MFI-31] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-32] → lifted to level 0 as [MFI-32] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.

## B.4 Two implementations: what transfers and what does not

- [CPE-33] → lifted to level 0 as [MFI-33] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-34] → lifted to level 0 as [MFI-34] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-35] → lifted to level 0 as [MFI-35] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-36] → lifted to level 0 as [MFI-36] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-37] → lifted to level 0 as [MFI-37] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-38] → lifted to level 0 as [MFI-38] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-39] → lifted to level 0 as [MFI-39] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-40] → lifted to level 0 as [MFI-40] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-41] → lifted to level 0 as [MFI-41] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
- [CPE-42] → lifted to level 0 as [MFI-42] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.
