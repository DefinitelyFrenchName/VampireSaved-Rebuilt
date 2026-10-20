# STATE — living progress log

**Opened 2026-10-18 (session R-001), `CLAUDE.md` [VSR-28].** This file holds the latest session group and the
standing sections; older groups move VERBATIM to `STATE_HISTORY.md` (created at the first move, with an index at its
head). A session key is `R-NNN`, one per sitting, never renamed or renumbered ([VSR-30]); milestones and freezes are
their own namespaces. A group's form, kept from the original: `## Session KEY — banner`, then `### opened with` and one
`### (N) TITLE` section per piece of work. An open list holds only what is open.

## Session R-006 — **#4's off-subject work split into #6 and #7; #6: vs2's doll-hop rows tabled and gated, and the gate PASSES on the original's build with them; #7 done: a second build-proof control reaches the byte compare; #6: the raw-id census, 61 newcomer rows in 23 tables left on the shell's row; #6: what reaches them: 5 of 23 tables reached in the corpus, the two palette dispatches with the newcomers' ids, and Huitzil's challenger-interrupt routine found to be Bulleta's.** Opened 2026-10-20 on Opus 5.5 (the ruled orchestrator); transcript `aebff6ad`.

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

## Session R-005 — **vhunt2 provided; the build proof PASSES: the tables rebuild the original's frozen merged build byte for byte (#4); the reference MAME built from the pin and proven the instrument that froze the oracle; the WIDE profile ratified, built and proven on MAME; #4's table at `PRG:0x0BE3FA` found to be the doll's hop, ruled vs2's rows for the newcomers; [VSR-40] re-worded by the maintainer, `CLAUDE.md` v1.1; R-004 archived.** Opened 2026-10-19 on Opus 5.5 (the ruled orchestrator), in R-004's transcript `dc3ff4f7` after its close.

### opened with

After R-004's close, asked *"should we close now ? prep the emulator with access to vhunt2?"*. Claude proposed R-005:
first the build proof, then the emulator. The maintainer: *"vhunt2 is in the ROMS folder"*.

### (1) VHUNT2 VERIFIED

`../ROMS/vhunt2.zip` (SHA-1 `daf0caa87cae62f29d9061a0a9878537317d294e`): its 21 members match the 21 the original's
`docs/checksums.txt` records, by size and SHA-1, with none missing and none extra. `vhunt2r1.zip`, which the
original's audit also requires, is still absent, so the audit shim ruled in R-003 (`SPEC.md` §0) still applies.
Asked *"do you need vhunt2r1 ?"*: no. Nothing in the original's build reads it but the ROM audit; it is also named in
the release preflight and a character-page script.

### (2) THE BUILD PROOF PASSES

`tools/build_proof.py` on the original at `bf92acd2`, `../ROMS`, `docs/project/tables`. A measurer read the logs:
- both legs build (151 s pristine, 149 s rendered);
- *"compare 175 files (25 zip members); differing non-log files 0, differing logs 0"*, `VERDICT: PASS`;
- both legs' program fingerprint is `6148d0b1…`, the merged fingerprint the original recorded at its last freeze
  (its `HANDOFF.md` line 161, *"merged `110467a7` -> `6148d0b1`"*).

So the tables reproduce the original's frozen merged build through its own pipeline. That is phase 0's first
acceptance, which R-003 had to stop short of. The phase-1 proof against the rebuild's own pipeline stays phase 1's.

Paid for on the way (written into the README as gotchas):
- **The shim** dropped every vhunt2 row, so the provided `vhunt2.zip` failed the audit as an unknown file. It now
  drops only the sets ROMDIR lacks, today `vhunt2r1.zip`. This applies the "Shim both legs" ruling; it does not widen
  it, and the audit is stricter.
- **A relative ROMDIR** (`../ROMS`) resolved inside each leg found nothing. The tool now resolves it.
- **The control `perturbed-render` was DEAD.** Its run gave `VERDICT: PASS` (the runlog's `control:perturbed-render
  PASS`). It perturbed the first `[[aux_poke]]`, which is `only_base_slot`, and the merged build (Donovan at 0x13)
  never applies it. It now takes the first row the build applies (`hud_mug_entry_13`). Its re-run FAILs: the original's
  own HUD check rejects the rendered build before the compare. So this control does not exercise the compare end to
  end. That remains open; `compare()` is P2's.
- `tests/test_build_proof.py` P3 now covers both ROMDIR cases, and P4 the applied row.

Runs, from the runlog:
- normal: FAIL ×2 (the shim, then ROMDIR), then PASS;
- control: PASS (dead), then FAIL.

### (3) THE REC8 READING CONFIRMED ON THE BUILT IMAGE

`tools/rec8_writes.py --built` reads the proof's pristine build:
- the six writes hold the records' values;
- of 848 ops, 3 touch the table at `PRG:0x0BE3FA`, each equal to vanilla;
- 0 bytes of that table differ from vanilla.

R-004 (5)'s static reading holds on the build. The pending capture is unchanged (it is about play, not bytes).

### (4) THE REFERENCE MAME BUILT FROM THE PIN, AND PROVEN THE INSTRUMENT THAT FROZE THE ORACLE

On Claude's proposal (plain MAME from the pinned source first, proven against vanilla; the WIDE patches only after
the maintainer ratifies them, [VSR-2]), the maintainer: *"session has been compacted so you can"*. On the proof run
directories: *"if we don't need them anymore, delete them"*. `proof_r005_1`, `_2`, `_4` and `_5` are deleted; no file
in the tree named them. `proof_r005_3` stays: it holds the built image the capture needs.

`tools/setup_mame.py` builds the original's pin (`27a8d9e8`, tag `mame0288`) as the reference binary, with no profile
patch, into `build/emu/mame-ref`. `tests/test_mame_reference.py`, a class F gate, runs the original's own
`tests/test_mame_parity.sh` unchanged with that binary, against Homebrew's MAME 0.288 as the reference. It PASSes:
- the 24 vanilla `vsavj` logs and the 65 frozen reference logs, each reproduced twice;
- 8 replays frozen nowhere, identical on both binaries.
Both controls FAIL in their modes. Detail and figures: `docs/project/instruments.md`.

Paid for: M2 was first written from the original's header ("every replay frozen", so the A/B sections empty) and
FAILed a PASSing run. At `bf92acd2` eight `118_*` replays are frozen nowhere and run in section 2. M2 now requires
every A/B row identical and none skipped.

Not done: no FBNeo reference yet (the original's `tools/setup_fbneo.sh`), which the emulator superset invariant and
the dual-emulator rule need ([VSR-13], [VSR-16]); the capture needs only MAME WIDE. Committed `3d94486`.

### (5) THE WIDE PROFILE RATIFIED, BUILT AND PROVEN ON MAME

Asked whether to ratify the original's CPS-2 WIDE v1.2 for this repository, MAME side, the maintainer: **"Ratify v1.2
verbatim (Recommended)"** (question and option verbatim in `SPEC.md` §0). The spec's one copy is
`docs/project/cps2_wide.md` (the original's, byte for byte below an import note); the patch is
`emu/mame-patches/0002-cps2-wide-v1.patch`, unchanged. `tools/setup_mame.py --profile wide` builds it beside the
reference. `tests/test_mame_wide.py` runs the original's `tests/test_mame_wide.sh` unchanged over its 12 replays, on
work RAM and framebuffer:
- the emulator superset invariant 12/12;
- inertness 12/12;
- the B4 canary 12/12.
Its control `canary-unreached` (the canary run fed zero-filled banks) fails 11 of 12 on the framebuffer alone.
Detail: `docs/project/instruments.md`.

Paid for:
- **A relink moves the instrument.** Re-running the build relinked the proven reference binary, and its SHA-1 changed
  each time (three relinks). Between two of them the code and data sections are equal; the UUID and one import stub
  differ. The setup now never rebuilds a binary whose recorded SHA-1 matches, and prints `INSTRUMENT MOVED` when one
  changes. The relinked reference (`f17f851c`) was proven again: PASS, the same figures.
- **W2 counted 14 replays**: the original's corpus list continues its lines with `\`. Fixed; the count is 12.

Committed `84e4bc9`.

### (6) #4, THE CAPTURE (FIRST PASS): THE PURSUIT IS NOT THE STATE; NOTHING CAPTURED REACHES IT

The maintainer: *"start"*. `tools/state_capture.py` runs the original's own rigs on native vs2 and on its merged
build (`build/tmp/proof_r005_3`), on the WIDE MAME, tracing both fighters' `+0x04` every frame. Kinds: `naming`
(the six parts holding a pursuit), `victim` (real picks, as the original's victim gate), `roll` (its tech-roll rig,
both directions) and `corpus` (the original's 97 top-level replays). Detail: `docs/project/tables/README.md`, "The
capture, R-005".
- The newcomers' pursuits run in routine `0x00`, sequence `0x0E`, on both games, so the table's handler is not the
  pursuit. The original's "pursuit" label for the table does not hold for these pursuits.
- `0x02100600` is a sub-state of fighter routine `0x10` (handler `PRG:0x026258`, a scratch reading, addresses only).
  Nothing captured enters routine `0x10`, on either game, for any fighter, veterans included. So the rigs do not reach
  it; that says nothing yet about whether a newcomer can.
- In the 96 naming events, the newcomer's states match the two legs in 85. The rest are Dark Force and the
  original's #179 (closed `not-ours`).

Not done: which hit gives the reaction. A fighter enters routine `0x10` only through `PRG:0x026D9A`, from the damage
routine's reaction classes `0x16` (air) and `0x36` (ground) (the `0x06FD34` store is an effect object's). The shape
~~suggests a stun, which no rig builds up~~ (RETRACTED in (7)); the README has the trail. The tool is not yet a gate ([VSR-20]: its rerunnable form is the tool;
the gate follows once there is an expectation to freeze).

### (7) RULED: VS2'S ROWS FOR THE NEWCOMERS; THE STATE IS THE DOLL'S HOP AFTER ROYAL JUDGEMENT

The maintainer, on the table at `PRG:0x0BE3FA` (verbatim in `SPEC.md` §0): the newcomers take vs2's rows, by the
ground rule already on record (universal mechanics vsavj's, character-specific ones vs2's; Dark Force the boundary
case). There is no universal stun in either game (the maintainer), so the "stun" guess of (6) is dropped.

The trace, continued (scratch reading of vsavj, addresses only, not yet reproduced by a measurer):
- the hit routine copies the attack record's reaction byte `+0x17` into the victim's `+0x54` (records 0x20 bytes, base
  attacker `+0x8C`, index the attack box's `+0x0A`; the selector `PRG:0x018438`, tables `PRG:0x018468`/`0x018510`);
- the damage routine's sequence 0 dispatches on `+0x54` (`PRG:0x02384E`, table `PRG:0x02385C`); entry `0x18` is
  `PRG:0x023E58`, which sets reaction class `0x36`, the class that leads to routine `0x10`;
- a scratch scan of every character's attack records for byte `0x18`: in both games, char `0x06` (Anakaris) record
  `0x24`; other hits at indices `0x5D`–`0x7E` (chars `0x00`, `0x02`, `0x09`, `0x0A`, `0x0D`, `0x0F`), past where
  the record count is known, so unconfirmed. None in the newcomers' own vs2 records: they would be the victims.
- the per-id height rows that are not 0 (`0x01`, `0x05`, `0x0C`, `0x0E`, `0x0F`) look like the winged characters; not
  checked.

**The state is the doll's hop (measured).** The maintainer named Anakaris's Ouke no Sabaki (Royal Judgement, which
turns the opponent into a paper doll). `tools/state_capture.py --rigs doll` (8 parts, 16 legs, all traced complete):
the doll hops while the victim holds up or up-forward, and the hop is sequence 6 of routine `0x10`, the STATE. Victor
(the control) hops identically on native vs2 and the build; each newcomer's first hop differs (a measurer from the
report: Donovan straight up peaks 76 native, 87 on the build, Victor's hop frame for frame; Phobos 60 against 76;
Pyron 76 both, airborne 30 against 32 frames). Table in `docs/project/tables/README.md`. So the rows are the
newcomers' own, as ruled. The rig is not yet a gate: its expectation (vs2's hops) can only be met once phase 1 builds.


### (8) [VSR-40] RE-WORDED BY THE MAINTAINER; CLAUDE.md v1.1

The maintainer, on the ground rule behind (7): *"I agree that VSR-40 is ambiguous because vanilla does wins ties but
true ties are very rare, it probably should state that vanilla wins everything that is not character specific for a
non-vanilla character.."*. The original's [VSP-21] was about console ports against arcade vsav, so it never covered
the newcomers. The maintainer edited `CLAUDE.md` itself: *"Vanilla wins everything that is not character-specific: for
any universal mechanic, vanilla wins. For character-specific vs2 wins for the vs2-only characters. In doubt, ask the
maintainer."*, and ruled the header to v1.1 (*"let's make it v1.1"*). The ledger row
(`docs/carried/ledger_claude_md.tsv`), the skill's two citations and `SPEC.md` §0 follow it. Committed `88ee09c`; the
header with this close.

### CLOSE (R-005, 2026-10-20)

**Delivered:**
- #4: vhunt2 verified; the build proof PASSES, the tables rebuild the original's frozen merged build byte for byte;
  the rec8 reading confirmed on the built image.
- The instruments: the reference MAME built from the pin and proven the instrument that froze the original's oracle;
  the CPS-2 WIDE profile ratified, built and proven on MAME (`docs/project/instruments.md`).
- #4: the capture. The table at `PRG:0x0BE3FA` is the doll's hop after Royal Judgement; each newcomer hops
  differently on the original's build; ruled: vs2's rows for the newcomers (phase 1).
- [VSR-40] re-worded by the maintainer; `CLAUDE.md` v1.1.
- `tools/metrics.py collect --after REV`: a session that continues an earlier one's transcript is counted from that
  session's close commit (R-005 shares `dc3ff4f7` with R-004). Its gate gains C12 and the control `after-ignored`;
  `absent-filled` now also fails C12, as it should (a missing cost-state on a bounded session).
- R-004 moved verbatim to `STATE_HISTORY.md`, with its index row.

Six commits, `260f030` to `88ee09c`, plus this close.

**Figures:** R-005 157 rows, collected with `--after 87fb697` before the close commit, so its `commits` (6) leave out
this close; `tools/metrics.py check` 599 figures, 0 bad. The dashboard "Rebuilt Session Ledger" reads the re-uploaded
table.

**Gates at the close**, on the staged tree: the ten gates (verdicts in the close commit's message).
- #4 is commented with R-005's progress and stays open: the port of vs2's rows and a second build-proof control are
  on the list.

**Not done:** no rule-checker ran before any action ([VSR-48]; the tool does not exist yet). The scratch trace in (7)
(the reaction byte to routine `0x10`) was not reproduced by a measurer; the doll capture measures its conclusion.
The height table (`word_y_off`) figures given to the maintainer in chat are not in the README yet (a measurer first).
Left outside git: the export, the instruments under `build/emu/`, the WIDE romsets, the proof's run directory
`build/tmp/proof_r005_3` (the original's merged build the capture runs on), the captures and the run log. No background
process is left running.

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
   - The five veteran moves keyed by the opponent's id (Bulleta `0x02E970`, Gallon `0x0331EA`, Zabel `0x0373CA`,
     Morrigan `0x03A60A`, Felicia `0x0402BA`), each performed on each newcomer. First find which move each is.
   - Huitzil in the challenger interrupt (`0x0BF59A`), where our build runs Bulleta's routine.
   - Then the projectile and effect rows (Chaos Flare `0x055344` and the rest), then the cosmetic palette rows.
   Still unreached by the census: 36 loads with an outside base, 4 unpaired tables, the 7 pairing disagreements, the
   pointer tables' content, and second tables read by the same reader.
2. #6: the height table (`word_y_off`, `PRG:0x0BE7FA`) figures into the README, reproduced by a measurer first
   (vs2's own row, the shell's row, the patched romset: Phobos 0, Donovan 0, Pyron 78, the same on all three).
3. #6, phase 1's part: its pipeline writes `doll_hop.tsv`, and `tests/test_doll_hop.py` runs on its build (today's
   passing leg is `tools/doll_build.py`, R-006 (2)).
