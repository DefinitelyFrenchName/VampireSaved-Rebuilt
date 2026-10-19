# port_corrections — what the original's extraction missed or got wrong for each tenant, and how it was fixed

**Shape: REFERENCE.** It gathers the original's own record (`DefinitelyFrenchName/VampireSaved` at `bf92acd2`); it
adds no measurement. The rows are `port_corrections.tsv`, one part per row, each with its source (path:line in the
original) and a verbatim anchor. `python3 tests/test_port_corrections.py` checks every anchor against the export.
Asked by the maintainer on 2026-10-18 (`SPEC.md` §0, #4): *"I would table the measurement AND I would look at the
history of Vampire Saved to gather all the missing/wrong parts that had to be added/fixed for each of the three VS2
characters"*.

## How it was gathered

Three `reader` workers searched the export, one per tenant, with one spec ([VSR-47]). Their sources, in order:
- the original's `tickets.tsv`;
- the tenant-manifest and porting documents, and `patch_notes.md`;
- the tenant's manifest (each row's comment block names what it fixes and when) and `bank_map.toml`;
- the root census in `tools/build_donovan.sh` and the special cases in `tools/extract_char.py`;
- `DECISIONS_HISTORY.md`, and `STATE_HISTORY.md` through its index.

They returned 146 parts: Donovan 55, Huitzil 59, Pyron 32. A part the tenants share appears once per tenant that
reported it. Of 146 anchors, 145 were at their line as returned. The gate caught one quote that was not verbatim
(Huitzil 54, a word dropped); its anchor was corrected to the line's own text.

**Not exhaustive.** The readers did not read `reconciliation_*.toml`, `moves_*.toml`, or all of `STATE_HISTORY.md`. A
part recorded only there is missing here. Each tenant manifest row is itself a correction on top of the extraction,
and phase 0's tables hold every one. Mapping each row to a part here is the completeness check this document lacks.

## What the parts are

| class | parts | D | H | P | what it is |
|---|---|---|---|---|---|
| engine-diff | 29 | 11 | 11 | 7 | vs2's engine does something vsavj's does not, and code copied from vs2 assumes it |
| dead-row | 29 | 11 | 11 | 7 | a vsavj per-character row at the tenant's id aliases another character's |
| short-table | 27 | 11 | 11 | 5 | a vsavj table is shorter than vs2's, or stubbed, so a vs2 index runs off its end |
| reloc | 12 | 7 | 4 | 1 | a relocation or reference the extractor or a resolver got wrong |
| reach | 11 | 4 | 6 | 1 | the extraction did not reach a region, or bounded it wrong |
| tool | 9 | 3 | 3 | 3 | a bug in the original's generator, resolver or verifier |
| gfx | 8 | 3 | 3 | 2 | tile placement, bias and art |
| sound | 6 | 2 | 3 | 1 | sound ids and their tables |
| merge | 4 | 1 | 2 | 1 | composing the three tenants into one build |
| crypt-data | 4 | 1 | 1 | 2 | data inside code placed in the crypt range, read through the wrong view |
| open | 5 | 1 | 2 | 2 | not fixed: parked, declined or open tickets |
| retracted | 2 | 0 | 2 | 0 | attempts withdrawn |

Status, by the readers: fixed 130, unclear 9, open 4, retracted 3.

## What this says about the rebuild's extraction (#4)

**The vhunt2 oracle bears on 27 parts, not 146.** Only `reach`, `reloc` and `crypt-data` are the extraction's own
errors, about bounds and pointers. Tabling the measurement (each region's bounds, twin and relocation refs, as the
original recorded them after these fixes) carries their answers without vhunt2.
- The forced bounds (`:f`), the piecewise shifts and the extra roots are already decisions in that record, or in
  `tools/build_donovan.sh`'s root census.
- The `reloc` parts that the sibling veto, the data-table records and the escape pads fixed are fixed in the refs
  themselves.

**85 parts are the engines' differences, and no extraction finds them.** They are `short-table`, `dead-row` and
`engine-diff`. The original found them one at a time: playtests, crashes on soaks, field reports (#92, #99, #103,
#104, #105), across sessions 4 to 14z-192. They are omissions, the class [VSR-186] says only enumeration finds.
Three enumerations would have found most of them up front, and phase 1 can run each as a static census of the two
games:
- **Every per-character table indexed by fighter id** (`dead-row`: physics, palettes, palette routines, OBJ bank,
  HUD, select records, win position and palette, capture and throw keyframes, AI scripts, kernel voice tables,
  defense rows). vsavj's rows `0x10`–`0x1F` are copies of `0x00`–`0x0F`, so each such table at each tenant's id
  answers with another character's row.
- **Every table indexed by a value vs2 extends** (`short-table`: object types, state ids, reaction ids, record
  classes, sub-states, hit-class and effect maps, effect-class rows, list types, the random-select roster, the win
  palette sets, the ladder's stages). Compare each length in the two games; an index past vsavj's end is a wild
  jump or a silent wrong read.
- **Every environment assumption in code copied from vs2** (`engine-diff`):
  - A5 work-variable displacements (throw and object-hit damage, the registration pair);
  - the Dark Force flags (`+0x1C3` against `+0x111`);
  - per-id special cases vsavj lacks (the air-block guard window, the facing rule 5, the class-0x52 rule);
  - the pursuit flag;
  - bank `3` hard-coded in bank setters;
  - the `+0x3800`/`+0x4200` tile bias;
  - allocators that assume virgin slots;
  - word-loaded id masks.

**Two lessons recur across tenants.**
- **A fix to a shared region is one tenant's copy.** The damage-applier rows were Donovan's from session 14n and
  were not carried to the others until 14z-85f ([VSR-84], [VSR-85]).
- **A first diagnosis was often wrong** (not counted): the type-6 deadness claim (Huitzil 35); Pyron's first Cosmo
  fix, which corrupted legacy (Pyron 15); Huitzil's first Dark Force fix, which broke Bulleta's (Huitzil 44); the
  voice-class reading (Donovan 33).

## Open and unclear, for phase 1 to settle

- Open:
  - the win-quote text and the arcade-ladder map, name and roulette tag (#123–#125, parked);
  - the two vs2 CPU-AI behaviours vsavj lacks (#129);
  - the Donovan cosmetic items (#162 parked; #112, #100 declined).
- Unclear:
  - the select-screen sword keeper (Donovan 30);
  - the parked companion overlay (Donovan 43);
  - x088512's bound on Donovan's root (Donovan 50);
  - Huitzil's still-silent voice ids (Huitzil 20);
  - the extractor's two blind spots, with no fix recorded (Huitzil 57);
  - #179 (Huitzil 58);
  - Pyron's 55 tripwired targets (Pyron 3);
  - his verifier's two open items (Pyron 31);
  - #173 (Pyron 32).
