# STATE — living progress log

**Opened 2026-10-18 (session R-001), `CLAUDE.md` [VSR-28].** This file holds the latest session group and the
standing sections; older groups move VERBATIM to `STATE_HISTORY.md` (created at the first move, with an index at its
head). A session key is `R-NNN`, one per sitting, never renamed or renumbered ([VSR-30]); milestones and freezes are
their own namespaces. A group's form, kept from the original: `## Session KEY — banner`, then `### opened with` and one
`### (N) TITLE` section per piece of work. An open list holds only what is open.

## Session R-007 — **#6: the five veteran moves named, rigged and gated: on the original's build every newcomer victim but one gets the shell's figures; #6: vs2's rows of the five tables tabled and built, and the gate passes, K3 15 of 15; R-006 archived.** Opened 2026-10-22 on Opus 5.5 (the ruled orchestrator); transcript `7512124a`.

### opened with

The maintainer: *"read state.md"*. Claude summarised it and offered to open R-007 on the start list's item 1 (#6:
rigs for the left-on-shell tables, gameplay first). The maintainer: *"yes"*.

### (1) #6: THE FIVE VETERAN MOVES NAMED, RIGGED AND GATED

Documented in `docs/project/tables/README.md`, "The five veteran moves".

**Which moves, from the code.** The five sites hang off the bank tables `PRG:0x0BD1FA`/`0x0BD27A`/`0x0BD2FA`, the
per-character handlers of seq `0x0E`/`0x10`/`0x12`, each dispatching on the command id `+0x106` and the sub-state:
Bulleta's ES pursuit (`0x0A`), Gallon's Wild Circular (`0x14`), Zabel's Hell Dunk (EX, `0x0A`), Morrigan's Cryptic
Needle (EX, `0x0A`) and Felicia's headsit (`0x10`, no input: a jump landing on a standing opponent). Named from the
stamping branches and mizuumi's move lists, then confirmed by the site firing on the move's input.

**The rig and its gate.** `tools/vet_moves.py` (P1 the veteran, P2 Victor or a newcomer by the doll rig's id pokes,
native vs2 against ours, the read tap at the sites plus the field trace) and `tests/test_vet_moves.py` (K1 fired, K2
Victor identical, K3 each newcomer identical; positions for 60 frames from the read, and for Zabel and Morrigan the
victim's capture pose index; four controls).

Measured (a measurer, from the run log; the original's merged build `29252167`, WIDE MAME `5b08cce7`):
- `VERDICT: FAIL (K3)`: K1 20 parts, 0 void; K2 5 of 5 identical; K3 1 of 15 identical (Gallon against Huitzil, whose
  vs2 row is the shell's, as the census says);
- three controls FIRED; `newcomer-moved` UNJUDGEABLE (K3 already fails);
- the differences: Felicia sits on Huitzil at 0,83 against native 22,96 and on Pyron at height 98 against 118;
  Bulleta's ES pursuit ends at dx −35 against −19/−22; Zabel's Hell Dunk puts Donovan, Huitzil and Pyron in pose
  `0x23`/`0x2D`/`0x2D` against `0x30`/`0x36`/`0x32` (the shells'); Morrigan's needle and Gallon's Wild Circular place
  them differently.

**Learned on the way.**
- The motion step codes are relative to the facing: forward `2`, back `1`, down `4`. My first inputs, decoded the
  other way, gave three other commands; the trace's `+0x106` showed it.
- vs2's 63214 needs all five steps: the four-step input that gives Wild Circular on vsavj gives a kick throw on vs2.
- Bulleta's site follows only the ES pursuit (`+0x102` = 6, two buttons and a stock: `PRG:0x02904A`).
- Felicia's site, read first as her air throw, is her headsit; the site fired with no button pressed.
- Zabel's row is a pose index, which no position shows ([VSR-178]): positions were identical on every leg. The pose
  is read by mapping P2's `+0x1C` through each leg's own pose table.
- **`PRG:0x027FAA` runs in play** (Zabel's and Morrigan's sites jump to it in straight-line code, and the victim's node
  is then a pose of its table), where the original recorded it as never executed (14z-98/99, one replay).
- Morrigan's capture also reads a second per-victim table, `PRG:0x03A5EA` (the pose; identical on both legs here),
  which the census does not list.
- The read tap numbers a frame one lower than the field trace; both legs carry the same offset.

### (2) #6: VS2'S ROWS OF THE FIVE TABLES TABLED, BUILT, AND THE GATE PASSES

The maintainer: *"yes"* (to building a leg with vs2's rows of the five tables). Documented in
`docs/project/tables/README.md`, "The five veteran moves", "vs2's rows, and a build that passes".
- **The rows as a gameplay table.** `docs/project/tables/vet_rows.tsv` (15 rows: 5 tables x 3 newcomers), written by
  `tools/vet_rows.py` from vs2 at the census's twin, row size and view. Its gate, `tests/test_vet_rows_table.py`, is
  anchored on the dumps and the census: V1 the table is vs2's rows, V2 the shape (vsavj's variant half a copy of its
  base half and vs2's base half equal to vsavj's, on all 32 ids of each table), V3 vs2's row differs from vsavj's where
  the census says. PASS; its three controls fire.
- **A build that can pass the gate.** `tools/vet_build.py` is `tools/doll_build.py`'s leg plus the rows, word by word:
  `poke16` `[[aux_poke]]` rows for the two tables read in the data view, `[[code_word]]` rows (checked against vanilla's
  opcode view, stored re-encrypted) for the three read pc-relatively, in the opcode view. `tools/doll_build.py`'s steps
  are now its `prepare` and `finish`, shared by both.

Measured (a measurer, from the logs and a rerun of the table gate):
- the build: 19 words, the op count 848 -> 867, `exit 0 in 155 s`; each table equals the expected rows; against the
  build proof's build, both whole views differ in exactly the 19 words written;
- `tests/test_vet_moves.py` on it: `VERDICT: PASS`. K1 20 parts, 0 void; K2 5 of 5; K3 15 of 15; Zabel's poses are
  native's (`0x30`/`0x36`/`0x32`); all four controls FIRED;
- each control's mode on it: `VERDICT: FAIL` on its own check (K2, K3, K1, K2);
- on the original's build, after the rig's fix below: `VERDICT: FAIL (K3)`, K3 1 of 15, the figures of (1).

So for what the rig reaches (one strength, distance and side per move), vs2's rows are the whole difference.

Paid for (each fixed before a figure was quoted):
- **the rig took its sites from the build under test.** `raw_id_reach.sites` keeps only the tables still on the
  shell's row on the build it is given, so on the build with vs2's rows the five tables left the list and the rig
  had no site to tap. `tools/vet_moves.py` now names its tables (`sites(..., tables=)`) ([VSR-51]);
- the renderer and the phase-0 gate read every table in `docs/project/tables/`, and took `vet_rows.tsv`'s moves for
  manifest names. Both skip it now by its generator's header, as they skip `doll_hop.tsv`;
- the table gate's first V3 control (vsavj given vs2's rows) failed V1 and V2 as well; it is now the census read as
  saying all of Gallon's rows differ, which V3 alone sees.

### CLOSE (R-007, 2026-10-23)

The maintainer: *"Close"*.

**Delivered:**
- #6: the five veteran moves that read the victim's row (Bulleta's ES pursuit, Gallon's Wild Circular, Zabel's Hell
  Dunk, Morrigan's Cryptic Needle, Felicia's headsit) named, rigged (`tools/vet_moves.py`) and gated
  (`tests/test_vet_moves.py`): on the original's build `FAIL (K3)`, 1 of 15 newcomer victims identical to native vs2.
- #6: vs2's rows of the five tables tabled (`vet_rows.tsv`, gated by `tests/test_vet_rows_table.py`) and built
  (`tools/vet_build.py`, 19 words); the gate passes on that build, K3 15 of 15, every control mode failing on its
  own check.
- R-006 moved verbatim to `STATE_HISTORY.md`, with its index row; ticket #6's row names the new gate and sections.

Two commits, `f409d49` and `6b13e15`, plus this close.

**Figures:** R-007 172 rows, collected before the close commit, so its `commits` (2) leave out this close;
`tools/metrics.py check` 938 figures, 0 bad. Its `red_min` (1368.2) is `test_vet_moves`'s normal runs on the
original's build, the defect it was born against: the figure counts from a normal run that FAILed to the gate's next
normal run, and those runs were its last normal verdict overnight and at the session's end.

**Gates at the close**, on the staged tree: the thirteen gates (verdicts in the close commit's message).
- #6 is commented with R-007's progress and stays open.

**Not done:** no rule-checker ran before any action ([VSR-48]; the tool is not built yet). The moves' other
strengths, distances and sides, Huitzil's challenger interrupt, the height table's figures and phase 1's part are on
the start list. Left outside git: the export, the instruments under `build/emu/`, the builds, rig runs, gate
runs and tiers under `build/tmp/` whose names carry `r007`, and the run log. No background process is left running.

# STANDING SECTIONS (current state — never archived)

## Standing rulings

The rulings of 2026-10-18 are verbatim in `SPEC.md` §0 (the brief, the five answers, v0.1's four questions, the
validation of `CLAUDE.md` v1.0, the read-only sources, phase 0's place and pin). The law is `CLAUDE.md`.

## Decisions pending (human)

none.

## The next session starts with

1. #6: rigs for the left-on-shell tables, gameplay first ([VSR-41]; `docs/project/tables/README.md`, "What reaches
   the left-on-shell tables"). Each rig follows the doll's pattern: a capture of native vs2 against ours, then vs2's
   rows if the difference is the newcomer's own.
   - The five veteran moves' other strengths, distances and sides: the rig reaches one of each (R-007 (2)).
   - Huitzil in the challenger interrupt (`0x0BF59A`), where our build runs Bulleta's routine.
   - Then the projectile and effect rows (Chaos Flare `0x055344` and the rest), then the cosmetic palette rows.
   Still unreached by the census: 36 loads with an outside base, 4 unpaired tables, the 7 pairing disagreements, the
   pointer tables' content, and second tables read by the same reader.
2. #6: the height table (`word_y_off`, `PRG:0x0BE7FA`) figures into the README, reproduced by a measurer first
   (vs2's own row, the shell's row, the patched romset: Phobos 0, Donovan 0, Pyron 78, the same on all three).
3. #6, phase 1's part: its pipeline writes `doll_hop.tsv` and `vet_rows.tsv`, and `tests/test_doll_hop.py` and
   `tests/test_vet_moves.py` run on its build (today's passing legs are `tools/doll_build.py`, R-006 (2), and
   `tools/vet_build.py`, R-007 (2)).
