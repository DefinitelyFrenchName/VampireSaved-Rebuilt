# port_corrections — what the original's extraction missed or got wrong for each tenant, and how it was fixed

**Shape: REFERENCE.** It gathers the original's own record (`DefinitelyFrenchName/VampireSaved` at `bf92acd2`); it
adds no measurement. The rows are `port_corrections.tsv`, one part per row, each with its source (path:line in the
original) and a verbatim anchor. `port_corrections_map.tsv` maps every row of the tenants' manifests to a part, or says
it is not a fix ("The map" below). `python3 tests/test_port_corrections.py` checks every anchor against the export and
the map's coverage.
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

**Not exhaustive, as gathered.** The readers did not read `reconciliation_*.toml`, `moves_*.toml`, or all of
`STATE_HISTORY.md`. R-004 mapped every row of the tenants' manifests, those two included, to a part ("The map"), which
added 16 parts. A part recorded only in `STATE_HISTORY.md` or another document, with no manifest row, can still be
missing.

## The map: every manifest row against a part (R-004)

`port_corrections_map.tsv` has one line per row of each tenant's manifest, move list and reconciliation overlay, as
phase 0's tables key them, `(manifest, kind, row)`; a section's form record `(kind)` is not a row. Each line gives a role
and a verbatim anchor from the row's own comment block or body:
- `fix`: the row is there because the extraction or an engine difference left the character wrong without it. `part`
  names the tenant's parts it carries, comma-separated when one row carries several (12 rows: a tenant row's
  `alloc_wrap` and `port_param32`, a reaction hook holding three fixes).
- `frame`: what any port of the character needs by design: where it lives (spaces, holes), who it is (the tenant row,
  the boot title), its move list, a feature (the Oboro select hook), and a row its tenant carries verbatim from
  another's (the 21-cell wheel for Huitzil and Pyron). `part` is `-`.
- `unclear`: none was needed.

**How it was made.** Three forks drafted it, one per tenant, from the manifests' text, each checked by a script that
the gate's C3 and C4 later replaced. The orchestrator then made it consistent across the tenants by one rule: **a row a
part names maps to that part, and the same row in another tenant maps to that tenant's part for the same fix,
added if missing.** So Huitzil's bank setters, palettes, select records, drawer gates and HUD rows map to its parts
26–28 (the fork had them as frame), and Pyron's select family, carried from the Huitzil/Donovan template, got part
38.

**What it found: 16 parts, the readers' count of 146 now 162.**
- Donovan:
  - 56: the unseeded secondary pools (Huitzil 13's fix, never recorded for him);
  - 57: the authored voice ids' live facing-alias rows;
  - 58: the HUD tables' Victor alias at 0x13;
  - 59: the three drawer bank gates;
  - 60: the select sword's grey palette row;
  - 61: the layout groups (session 5's repacked `jsr`);
  - 62: the companion anim-table thunks' baked literal (14z-78; catalogued until now only as Huitzil 55).
- Huitzil:
  - 60: the companion-effect tiles' bank-5 flip;
  - 61: the voice-class borrow rows, live bytes under a retracted reading (unclear);
  - 62: the bare-long engine-data refs, 16 of 20 still open.
- Pyron:
  - 33: the companion queue class;
  - 34: the short type-dispatch tables;
  - 35: the voice alias thunk;
  - 36: the stubbed farm sounds;
  - 37: the capture-pose victim rows (part 26 covers him as attacker);
  - 38: the select family at the variant id.

Of the 16, three are the extraction's own (`reloc`), eight are the engines' differences, and five are sound and gfx.

**What the map does not cover.** It reads manifests. A correction made in a generator, a resolver or the extractor
(`tools/extract_char.py`, `tools/build_donovan.sh`) has no manifest row, and neither has a part sourced only in a
history. 18 of Donovan's 62 parts, 23 of Huitzil's 62 and 9 of Pyron's 38 have no map row. Most are of that kind;
others are open with no fix, retracted with no live row, or anchored in a comment above a row that carries another
fix (Pyron 7, below). The gate reports the count and does not require it to be zero.

**Read while mapping, not settled:**
- Donovan 9 (the type-0x51 thunk): the thunk now routes class 0x52 on the KO branch (`donovan.toml` line 1561), and the
  map gives its row to 7.
- Donovan 33 and Huitzil 61: the reading is retracted, and the rows are live bytes (`donovan.toml` line 2208).
- Pyron 7 (the escape-fix pass clobbering the OBJ bank table) is a generator fix. Its anchor sits in `table_fix`'s
  comment, and no row implements it.
- Pyron's move row `Zodiac Fire` records #161's residual (P1's HP, 12 native and 13 ours). Huitzil 49 calls that
  residual "not ours", so the row stays frame and no part was added.

## What the parts are

| class | parts | D | H | P | what it is |
|---|---|---|---|---|---|
| dead-row | 34 | 13 | 12 | 9 | a vsavj per-character row at the tenant's id aliases another character's |
| engine-diff | 30 | 12 | 11 | 7 | vs2's engine does something vsavj's does not, and code copied from vs2 assumes it |
| short-table | 29 | 11 | 11 | 7 | a vsavj table is shorter than vs2's, or stubbed, so a vs2 index runs off its end |
| reloc | 15 | 9 | 5 | 1 | a relocation or reference the extractor or a resolver got wrong |
| reach | 11 | 4 | 6 | 1 | the extraction did not reach a region, or bounded it wrong |
| gfx | 10 | 4 | 4 | 2 | tile placement, bias and art |
| tool | 9 | 3 | 3 | 3 | a bug in the original's generator, resolver or verifier |
| sound | 9 | 3 | 3 | 3 | sound ids and their tables |
| merge | 4 | 1 | 2 | 1 | composing the three tenants into one build |
| crypt-data | 4 | 1 | 1 | 2 | data inside code placed in the crypt range, read through the wrong view |
| open | 5 | 1 | 2 | 2 | not fixed: parked, declined or open tickets |
| retracted | 2 | 0 | 2 | 0 | attempts withdrawn |

162 parts: Donovan 62, Huitzil 62, Pyron 38. Status: fixed 144, unclear 10, open 5, retracted 3. The readers' 146 had
fixed 130, unclear 9, open 4, retracted 3; the map's 16 are 14 fixed, one unclear (Huitzil 61) and one open (Huitzil
62).

## What this says about the rebuild's extraction (#4)

**The vhunt2 oracle bears on 30 parts, not 162** (27 of the readers' 146, and three of the map's). Only `reach`, `reloc` and `crypt-data` are the extraction's own
errors, about bounds and pointers. Tabling the measurement (each region's bounds, twin and relocation refs, as the
original recorded them after these fixes) carries their answers without vhunt2.
- The forced bounds (`:f`), the piecewise shifts and the extra roots are already decisions in that record, or in
  `tools/build_donovan.sh`'s root census.
- The `reloc` parts that the sibling veto, the data-table records and the escape pads fixed are fixed in the refs
  themselves.

**93 parts are the engines' differences, and no extraction finds them** (85 of the readers' 146, and eight of the
map's). They are `short-table`, `dead-row` and
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
