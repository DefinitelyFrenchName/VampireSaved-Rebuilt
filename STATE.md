# STATE — living progress log

**Opened 2026-10-18 (session R-001), `CLAUDE.md` [VSR-28].** This file holds the latest session group and the
standing sections; older groups move VERBATIM to `STATE_HISTORY.md` (created at the first move, with an index at its
head). A session key is `R-NNN`, one per sitting, never renamed or renumbered ([VSR-30]); milestones and freezes are
their own namespaces. A group's form, kept from the original: `## Session KEY — banner`, then `### opened with` and one
`### (N) TITLE` section per piece of work. An open list holds only what is open.

## Session R-007 — **(open)** Opened 2026-10-22 on Opus 5.5 (the ruled orchestrator); transcript `7512124a`.

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

## Session R-006 — **#4's off-subject work split into #6 and #7; #6: vs2's doll-hop rows tabled and gated, and the gate PASSES on the original's build with them; #7 done: a second build-proof control reaches the byte compare; #6: the raw-id census, 61 newcomer rows in 23 tables left on the shell's row; #6: what reaches them: 5 of 23 tables reached in the corpus, the two palette dispatches with the newcomers' ids, and Huitzil's challenger-interrupt routine found to be Bulleta's; R-005 archived.** Opened 2026-10-20 on Opus 5.5 (the ruled orchestrator); transcript `aebff6ad`.

### opened with

The maintainer: *"read state.md"*. Claude summarised it and noted that #4's GitHub title (the extractor needing
vhunt2 as its sibling oracle) is narrower than the four start-list items `STATE.md` filed under it. The maintainer:
*"please fix that gap. Then open R-006"*.

### (1) #4 SPLIT: #6 AND #7

#4 keeps its title's subject: phase 1's extractor bounds regions without vhunt2. That covers the extraction tables,
the corrections per tenant and the build proof as phase 0's acceptance. Two subjects filed under it in R-004/R-005 now
have their own tickets (GitHub issues, stories in their bodies; #4 commented with the split):
- **#6** (evolution): the newcomers read their shell's rows of tables indexed by raw id where vs2 has their own. It
  covers the doll's hop at `PRG:0x0BE3FA` (ruled 2026-10-20), the census of the other such tables and the height
  table's figures (start-list items 1, 3, 4).
- **#7** (bug): the build proof's control is caught by the original's HUD check, so no control exercises the byte
  compare end to end (item 2).

`docs/project/tickets.tsv` gains both rows; #4's `decided`/`learned` lose the doll's hop (now #6's) and its `wrong`
records the misfiling. The live pointers move: `SPEC.md` §0's two "phase 1 ports vs2's three rows" (#6), the tables
README's doll paragraph (#6) and its build-proof control (#7), `tools/state_capture.py`'s header (#6). R-005's group
above is history and keeps #4.

### (2) #6: VS2'S DOLL-HOP ROWS TABLED, GATED, AND PROVEN ON AN INTERIM BUILD

The maintainer: *"yes"* (to starting #6's first item). Phase 1's pipeline does not exist yet, so the port has three
parts, each now in the tree (`docs/project/tables/README.md`, "The doll's hop, vs2's rows"):
- **The rows as a gameplay table.** `docs/project/tables/doll_hop.tsv` (6 rows: 3 newcomers x 2 variants, 16.16
  fields, each row's vs2 address), written by `tools/doll_hop.py` from vs2's data view. Its gate,
  `tests/test_doll_hop_table.py`, is anchored on the dumps: H1 the table equals vs2's rows, H2 each game's one reader
  indexed by the raw id, H3 each vs2 row differs from vsavj's at the id. PASS; its three controls fire.
- **The rig as a gate.** `tests/test_doll_hop.py <build> <out>` runs the R-005 `doll` rig unchanged. It judges every
  hop's per-frame (dx, dy): K1 traced, hopped, and the right id (a void part is never judged); K2 Victor identical
  (the instrument check); K3 each newcomer identical to native vs2.
- **A build that can pass it.** `tools/doll_build.py` is the build proof's rendered leg plus vs2's rows as 24
  `poke32` `[[aux_poke]]` rows, with the original's frozen op count raised by exactly 24 (848 -> 872).

Measured (a measurer, from the run logs):
- the build: `exit 0 in 154 s`; the built table differs from vanilla in 19 bytes and from the expected rows in 0;
- the gate on the original's merged build: `VERDICT: FAIL (K3)`, K3 0 of 6 identical (the defect);
- the gate on the build with vs2's rows: `VERDICT: PASS`, K3 6 of 6, every hop of every part;
- each control's mode: `VERDICT: FAIL` with its own check.

So for what the rig reaches (variant 1, U and UR), vs2's three rows are the whole difference. Variant 0 is unreached.

Paid for, in the tools' first runs (each fixed before any figure was quoted):
- the table gate's first run was red from its own code: it compared the header's `../ROMS/…` against the resolved
  paths;
- `unfixed` returns bytes, not an integer;
- the original's build refused 872 ops against its frozen 848, which led to the shim;
- the doll gate's `hop-missing` control first failed K3 as well, because K3 counted judged parts. A void part is
  K1's alone.

Also: the phase-0 gate (`tests/test_phase0_tables.py`) and the renderer skip `doll_hop.tsv` by its generator's
header, as they skip the extraction's gameplay tables.

### (3) #7 DONE: A SECOND BUILD-PROOF CONTROL THAT ONLY THE BYTE COMPARE CATCHES

The maintainer: *"#7"*. `tools/build_proof.py --control perturbed-shared` raises the `val` of
`[[aux_poke]] boot_title_saved_1` (the boot title, `PRG:0x01C822`) by 1 in donovan.toml, huitzil.toml and pyron.toml
alike. The original's generator emits the three identical rows as one shared row, so the op count stays 848. No check
of the original's build reads the boot title. `tests/test_build_proof.py` gains P5: exactly one value changes per
manifest, and the three rows stay identical.

Measured (a measurer, from the run log):
- both legs build (`exit 0`, 158 s and 155 s);
- the compare finds 7 differing non-log files, the program member `vm3j.03d` among them, and 1 differing log;
- `VERDICT: FAIL (7 files differ)`.
So the byte compare is exercised end to end. `perturbed-render` stays; it is stopped by the original's HUD check, as
R-005 found. The run directory was deleted after the measurer read the log (`build/tmp/proof_r006_shared.log` stays).

### (4) #6: THE RAW-ID CENSUS

The maintainer: *"Start census"*. `tools/raw_id_census.py` lists every table vsavj reads by the raw id `+0x382`, its
vs2 twin and the newcomers' rows; `docs/project/tables/raw_id_census.tsv` (79 rows, the dumps' facts) and its gate
`tests/test_raw_id_census.py` (C1 regenerates, C2 the doll table as measured, C3 the scans; three controls fire).
Method and limits: `docs/project/tables/README.md`, "The raw-id census".

Measured (a measurer):
- 196 id loads in vsavj, 209 in vs2; 79 tables paired, 4 unpaired;
- to port (vsavj's row a shell copy, vs2's its own): 167 rows in 61 tables;
- on the original's merged build, 61 of them in 23 tables are left on the shell's row: the doll table (the anchor,
  reproduced), one pointer table (`PRG:0x0BF59A`, Huitzil), 2 code dispatches, and 19 value tables inside code.

Paid for, on the way to the tool (each before any figure was quoted):
- **The original's bank map is not the engine's layout.** Compared by its slices, the doll table reads as vs2's for
  all three (`rec8_b` slices 8 bytes per id; the engine reads 0x20). So the census takes row sizes from the readers.
- **A `(d8,PC,Xn)` read is a program-space fetch**, decrypted like an opcode: a pc-indexed table is read in the
  opcode view, others in the data view. Read in the data view, the dispatch tables' shell copies were invisible.
- **A word dispatch table's entry count** must stop at the running smallest offset. The first version read past the
  table into code and gave 0 or 1 entries.
- **A walk that cannot resolve the index's base** must stop there; the first version ran on to a later instruction.
- the read-only guard refused a heredoc naming `../ROMS` on the line that writes the script; scratch scripts take
  the rom dir as an argument now.
- `tools/doll_build.py` was re-wrapped (line width only) and rebuilt to prove it unchanged: 175 files and 25 zip
  members identical to (2)'s build, but `vsavjw.zip`'s SHA-1 differs (`c924f883` against `bdb58c14`). A zip's SHA-1
  names its container, timestamps included, not the build: compare members, as the build proof does.

Not done in (4): the census is static. (5) takes the next step.

### (5) #6: WHAT REACHES THE LEFT-ON-SHELL TABLES

The maintainer: *"start on them"* (the census's 22 other tables). Two tools, documented in
`docs/project/tables/README.md`, "What reaches the left-on-shell tables":
- `tools/raw_id_owners.py`, static: whose id each reading site reads and whose code reaches it (a backward walk to a
  bank row or an object TYPE table);
- `tools/raw_id_reach.py`, in the emulator: the original's 97 top-level replays under its non-debug read tap on both
  fighters' `+0x382`, filtered to the reading sites. Two controls fire in every run (a defense read that runs on every
  hit, and the select's writes).
`tools/raw_id_census.py`'s `measure()` now also returns its site alignment (`twins`); its TSV and gate are unchanged.

Measured (a measurer; the run `build/tmp/reach_r006_1`, on the original's build):
- the controls fired: *"97 replays, 97 complete"*, the control site *"4076"* reads on our build and *"118"* on
  vsav2, *"every replay wrote +0x382"*;
- *"5 of 23 tables"* reached. The two palette dispatches (`0x02ADEC`, `0x02B650`) are read with all three newcomers'
  ids, every match frame. Chaos Flare's (`0x055344`) and a Jedah effect's (`0x06139C`) are reached with veterans'
  ids only. The challenger interrupt's routine table (`0x0BF59A`) is reached in `08_challenger_join` only;
- static: five tables are read by veterans' own moves (Bulleta, Gallon, Zabel, Morrigan, Felicia) by the opponent's
  id. None is reached by the corpus.

Read from the code (addresses only), and what it means:
- **The palette dispatches are cosmetic** ([VSR-41]): Huitzil and Donovan miss vs2's palette effects in-match,
  Donovan on the other one too.
- **Huitzil runs Bulleta's challenger-interrupt routine** (`0x0BF59A` row `0x10` = row `0x00`'s), where vs2 runs the
  default. It is a spurious inherited routine, the Pyron-blink shape (the original's 14z-75). The original recorded
  the table as unread (14z-98, one stall).
- **Zabel's move calls the capture-pose entry `PRG:0x027FAA`.** The original recorded that entry as never executed
  (14z-98/99, one replay). A caller exists; whether it runs is not measured.

Paid for:
- the linear disassembly decodes data before `PRG:0x058786` and never lands on it. The owner tool decodes locally
  there.
- my first scratch walk printed nothing at pointer ends: a malformed edit made the line an expression that discarded
  its string. It was caught because the roots all read "no reference", and was rewritten before any figure.
- the object handlers are reached through pc-relative long tables (the two pool walkers' TYPE tables). Those are read
  in the opcode view; a scan of the data view finds none ([VSR-87]).
- the census follows the first indexed access of a reader; `0x06D6F4`'s reader indexes a second per-id table
  (`PRG:0x06D7CA`), which is not listed. Noted in the README's limits.

No rule-checker was run before this commit ([VSR-48]; the tool is not built yet).

### CLOSE (R-006, 2026-10-21)

The maintainer: *"Close"*.

**Delivered:**
- #4 split: its off-subject work became #6 (the newcomers read their shell's rows) and #7 (a build-proof control
  that reaches the byte compare). #4 keeps its title's subject.
- #6: vs2's doll-hop rows tabled (`doll_hop.tsv`) and gated (`tests/test_doll_hop_table.py`); the gate passes on the
  original's build with them (`tools/doll_build.py`).
- #7 done: the control `perturbed-shared` builds through every check of the original's and only the byte compare
  fails it.
- #6: the raw-id census (`tools/raw_id_census.py`, its gate): 61 newcomer rows in 23 tables left on the shell's row.
- #6: what reaches them (`tools/raw_id_owners.py`, `tools/raw_id_reach.py`): 5 of 23 tables reached in the corpus;
  the palette dispatches are cosmetic; Huitzil runs Bulleta's challenger-interrupt routine; five veteran moves read
  the opponent's row and need rigs.
- R-005 moved verbatim to `STATE_HISTORY.md`, with its index row.

Five commits, `3e3c340` to `2e8fb4d`, plus this close.

**Figures:** R-006 167 rows, collected before the close commit, so its `commits` (5) leave out this close;
`tools/metrics.py check` 766 figures, 0 bad. The dashboard "Rebuilt Session Ledger" reads the re-uploaded table.

**Gates at the close**, on the staged tree: the twelve gates (verdicts in the close commit's message).
- #6 is commented with R-006's progress and stays open; #7 is closed on GitHub; #4 stays open.

**Not done:** no rule-checker ran before any action ([VSR-48]; the tool is not built yet). The rigs for the
left-on-shell tables, the height table's figures and phase 1's doll part are on the start list. Left outside git:
the export, the instruments under `build/emu/`, the proof's run directory `build/tmp/proof_r005_3`, the reach run
`build/tmp/reach_r006_1`, the census's scratch outputs and the run log. No background process is left running.

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
   - The five veteran moves (R-007 (1)): a build with vs2's rows of their five tables on which
     `tests/test_vet_moves.py` passes (the `tools/doll_build.py` pattern), and the gate's control modes on it.
   - Huitzil in the challenger interrupt (`0x0BF59A`), where our build runs Bulleta's routine.
   - Then the projectile and effect rows (Chaos Flare `0x055344` and the rest), then the cosmetic palette rows.
   Still unreached by the census: 36 loads with an outside base, 4 unpaired tables, the 7 pairing disagreements, the
   pointer tables' content, and second tables read by the same reader.
2. #6: the height table (`word_y_off`, `PRG:0x0BE7FA`) figures into the README, reproduced by a measurer first
   (vs2's own row, the shell's row, the patched romset: Phobos 0, Donovan 0, Pyron 78, the same on all three).
3. #6, phase 1's part: its pipeline writes `doll_hop.tsv`, and `tests/test_doll_hop.py` runs on its build (today's
   passing leg is `tools/doll_build.py`, R-006 (2)).
