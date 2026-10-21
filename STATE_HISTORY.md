# STATE_HISTORY — the archive of STATE.md's session groups

**Opened 2026-10-18 (session R-002), `CLAUDE.md` [VSR-28].** Every session group that leaves `STATE.md` moves here
VERBATIM, newest first, never edited after the move; the index below is the lookup by session key ([VSR-30]).

## Index

| session | date | banner | line |
|---|---|---|---|
| R-005 | 2026-10-19 | vhunt2 provided; the build proof PASSES: the tables rebuild the original's frozen merged build byte for byte (#4); the reference MAME built from the pin and proven the instrument that froze the oracle; the WIDE profile ratified, built and proven on MAME; #4's table at `PRG:0x0BE3FA` found to be the doll's hop, ruled vs2's rows for the newcomers; [VSR-40] re-worded by the maintainer, `CLAUDE.md` v1.1; R-004 archived | 17 |
| R-004 | 2026-10-19 | #5 ruled: (a) the measurer runs one command per tool call; #4: the extraction tabled, its jump, cancel and short bank rows decoded; every manifest row mapped to a correction, 16 parts added; the rec8 writes read statically, the newcomers' own rows found to be veterans' copies, ruled (c) then (a); R-003 archived | 201 |
| R-003 | 2026-10-18 | Phase 0 closed on parse-equality (the build proof moved to phase 1); vhunt2's role found (#4); the original's corrections per tenant gathered; R-002 archived | 351 |
| R-002 | 2026-10-18 | #3 built and closed: the figures, their gate, the run log, the dashboard; R-001 archived | 460 |
| R-001 | 2026-10-18 | CLAUDE.md v1.0 validated, SPEC v0.2 accepted; the read-only guard installed; phase 0 started | 518 |


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

## Session R-004 — **#5 ruled: (a) the measurer runs one command per tool call; #4: the extraction tabled, its jump, cancel and short bank rows decoded; every manifest row mapped to a correction, 16 parts added; the rec8 writes read statically, the newcomers' own rows found to be veterans' copies, ruled (c) then (a); R-003 archived.** Opened 2026-10-19 on Opus 5.5 (the ruled orchestrator); transcript `dc3ff4f7`.

### opened with

*"read state.md"*, then, on the pending decision #5 quoted back with Claude's recommendation (*"I recommend (a) now
and (b) if it happens again."*): *"agreed"*.

### (1) #5 RULED: THE MEASURER RUNS ONE COMMAND PER TOOL CALL

The ruling is verbatim in `SPEC.md` §0. (a) is applied: `.claude/agents/measurer.md` step 1 now says commands run one
at a time, one per Bash call and one tool call per message, even when two look independent. `docs/project/swarm.md`
§2 records it. (b), a hook that refuses a worker's concurrent calls, is built if it happens again; that recurrence
opens a ticket with its evidence. #5 is done in `docs/project/tickets.tsv`. The definitions are not edit-locked here
(`.claude/hooks/guard_readonly.py` locks only the settings and the hooks; `swarm.md` §4 leaves that open), so the
session made the edit.

Checked on one live run: a measurer given three commands, each printing its start and end times around a 2 s
sleep, returned C1 1792397861.051–863.056, C2 863.185–865.190, C3 865.309–867.312: in order, no overlap. That is
one sample. It does not show that the sentence prevents a recurrence, and whether the worker read the edited
definition or a copy loaded at session start was not measured. The gates were run on the working tree before this
record: the six gates PASS and `tools/metrics.py check` 311 figures, 0 bad. No rule-checker ran before closing #5
([VSR-48]; the tool does not exist yet). Committed `4a06b38`.

### (2) #4: THE EXTRACTION TABLED, ITS JUMP AND CANCEL ROWS DECODED

The maintainer: *"yes"* to starting the next-session list's item 1. `tools/extract_regions.py` writes the three
records the original's merged build reads (`tools/build_merged.sh` lines 36–38: `m5_wide`, `hui32`, `pyron21`;
the original's `pcrel_escapes.toml` names other extract directories, `don_m27`/`hui61`/`pyron46`, for a pcrel
measurement, and they are not in the export) into 13 tables under `docs/project/tables/extraction/`, one per section
of the record, in its own columns. It also writes two gameplay tables: `jump_physics.tsv` (`jump_params` as 16.16
exact decimals, the original's layout and field names) and `cancel_windows.tsv` (`byte2d_a`/`_b`, the special- and
EX-cancel windows per move index, from the original's 14z-194 measurement). Each row names its vs2 address. Format,
sources and figures are in `docs/project/tables/README.md` "The extraction tables". The original notes that
`m5_wide`'s record predates two `extract_char.py` changes, so the tables are what the merged build consumed, not
what the extractor computes today.

Gate `tests/test_extraction_tables.py`, E1–E4: fresh, whole (renders back to each record), anchored (every gameplay
value equals vsav2's byte at an address the gate computes from the fact tables), no ROM runs. Six controls, all FIRED,
every mode FAIL. Its first green was read by its printed values ([VSR-21]). That reading found one check I had
written wrong: E3 skipped `vsav2.key` as "not a zip member", and it is one. It is now checked. A measurer reproduced
the figures (30,401 rows; 153,013 scalar values, R-003's count; E3 189 values, 0 differing), and a reader quoted the
original's claims the README cites.

Paid for this sitting: the phase-0 gate and the renderer glob every top-level table, so the two new gameplay tables
crashed G2 and broke G8, and five controls went DEAD with them. Both now skip a table whose header says
`GENERATED by tools/extract_regions.py`, and all 14 controls fire again. A phase-0 table given that header would
leave G1 the same way; the README says so.

Left open at this point: the other short bank values were carried as written; the ruling named three rows. (3)
settles it. Committed `93e25a5`.

### (3) THE SHORT BANK ROWS DECODED; TWO OF THEM ARE NOT THE TENANT'S

Asked whether the other short bank values get readable tables too, the maintainer: *"I lean yes since tables is what
we decided and that data is valuable"* (verbatim in `SPEC.md` §0). The third gameplay table, `bank_values.tsv`, has
33 rows: per tenant, `param32_a` (walk speeds), `param32_b` (the pursuit leap, by the original's 14z-121 note; its
two fields named by position, their meaning not measured), the minimum air-dash height (`gap_be23a`, a real table
among the auto gaps, #222 there), and the five words and one byte, whose meaning is not recorded. Each row names
its vs2 address. The gate's E3 covers it (222 values, 0 differing), with a seventh control, `air-dash-zeroed`.
Donovan's forward walk reads 3, which agrees with the original's measurement in play after his vs2 rows were ported
(the X-velocity word 2.5 -> 3.0, 14z-119 there).

Found while decoding: `rec8_a` and `rec8_b` are not the tenant's data. The extractor reads every `rec8` row 8 bytes
at `char*8`, but the original's 14z-121 notes put `rec8_a` inside `jump_params` (`id*0x30`) and `rec8_b` inside the
pursuit record (four longs × 2 variants, `id*0x20`). So Donovan's 8 bytes are char 3's neutral-jump `yv`/`gravity`
and char 4's second pursuit variant's `yv`/`yacc` (arithmetic: `0x13*8 = 0x98`). They stay as written in
`extraction/values.tsv`. **Not measured, for #4's next item:** what the original's build wrote for these two rows
and where, and whether the tenants' own pursuit records (`id*0x20`) were ported at all. They are not in the
extraction record.

Paid for this sitting: the README's first measurement quoted `extraction/` as 1,484 KB from `du -sk`. That counts
allocated disk blocks, and it read 2,372 KB after the files were rewritten with nearly the same content (the
apparent size is 1,456 KB). The figure was dropped from the README, not replaced: a size is no part of what the
tables claim.

### (4) #4: EVERY MANIFEST ROW MAPPED TO A CORRECTION; 16 PARTS THE READERS MISSED

The maintainer: *"continue"*, to the next-session list's item 1. `docs/project/port_corrections_map.tsv` (hand-written)
has one line for each of the 714 rows of the tenants' manifests, move lists and reconciliation overlays that phase 0's
tables carry. Each line gives a role: `fix` with the parts it carries, or `frame` (where the character lives, who it
is, its move list, a feature). Each also has a verbatim anchor from the row's own comments. Three forks drafted it,
one per tenant. The orchestrator then made it consistent across the tenants: a row a part names maps to that part,
and the same row in another tenant maps to that tenant's part for the same fix. Figures (a measurer): fix 176/246/118, frame
66/58/50, unclear 0; 12 rows carry several parts. The catalogue grew from 146 to 162 parts (Donovan 56–62, Huitzil
60–62, Pyron 33–38): three `reloc`, eight engine differences, five sound and gfx. The extraction's own parts are now 30
and the engines' differences 93. Parts with no map row: 18/23/9. Most are fixed in a generator or recorded only in a
history, which a map of manifests cannot see. So the catalogue is complete for manifest rows, not beyond. Read while
mapping and not settled (`port_corrections.md` "The map"): Donovan 9's thunk now serves the class-0x52 route; Donovan 33
and Huitzil 61 are live bytes under a retracted reading; Pyron 7 has no row.

The gate `tests/test_port_corrections.py` gains C3 (coverage: every manifest row once, roles and parts known) and C4
(each anchor at its line, inside its row's reach), with three controls (`row-dropped`, `part-unknown`,
`anchor-outside`). All five controls FIRED, `--control part-unknown` FAILs, and the first green was read by its
printed values. That reading found 20 reconciliation rows anchored on a bare `vsav2 = `; they now quote their whole line.

### (5) #4: WHAT THE BUILD WROTE FOR REC8_A/REC8_B; THE NEWCOMERS' OWN ROWS ARE VETERANS' COPIES

The maintainer: *"take than on"*, to the next-session item, read from the generator because the original's image
cannot be built here (no vhunt2). `tools/rec8_writes.py` and its gate `tests/test_rec8_writes.py` (R1–R3, three
controls, all FIRED; the first green read by its printed values). Detail and quotes: `docs/project/tables/README.md`
"What the build wrote for rec8_a and rec8_b".
- **The six writes change nothing.** The generator writes each tenant's 8 bytes at the table's vsavj base + id*8
  (Donovan at 0x13 on the merged build's profile). That lands inside veterans' rows. A measurer: *"rec8 writes equal
  to vsavj's bytes: 6 of 6"*. A reader quoted the write rule, the empty skip set (`port_param32 = true` in all three
  manifests) and the disabled gap tables.
- **The newcomers' own rows of the table at `PRG:0x0BE3FA` (id*0x20) are never written**, by reading the generator
  and phase 0's tables (absence, [VSR-52]).
  - In vsavj they equal rows 3, 0 and 1: Donovan, Huitzil and Pyron hold Victor's, Bulleta's and Demitri's.
  - vs2's rows for the three differ.
  - Both games' one load of the table (vsavj `PRG:0x026646`, vs2 `PRG:0x0252DC`) indexes by `+0x382`, the raw id. So
    a newcomer in that state takes a veteran's values.
- **Not measured:** which move the state (`+0x04` = `0x02100600`) is, and whether a newcomer reaches it. The original
  calls the table "the PURSUIT physics record pair", tied to chain `a2:0x4C`, and this reading does not confirm it.
  A capture in play settles it ([VSR-43]). Porting vs2's rows has gameplay consequences, so it is under "Decisions
  pending".

The disassembly was read in a scratch, and nothing of it is committed beyond addresses and the instruction shapes the
gate checks.

### (6) RULED: CAPTURE FIRST, THEN PORT VS2'S ROWS IF NEED BE

On the decision (5) put under "Decisions pending", quoting Claude's recommendation (*"I recommend (c), then (a) if
the difference turns out to be the newcomers' own."*), the maintainer: **"yes, (c) then (a) if need be"** (verbatim
in `SPEC.md` §0). It left the pending list in the close commit. The capture is the next session's item 1; it waits
on an instrument that can run the original's build.

### CLOSE (R-004, 2026-10-19)

**Delivered:**
- #5 ruled and done: the measurer runs one command per tool call.
- #4:
  - the extraction tabled, with three gameplay tables (jump physics, cancel windows, bank values);
  - every manifest row mapped to a correction (16 parts added, 162 in all);
  - the `rec8` writes read statically, and the newcomers' own rows at `PRG:0x0BE3FA` found to be veterans' copies,
    ruled (c) then (a).
- R-003 moved verbatim to `STATE_HISTORY.md`, with its index row.

Five commits, `4a06b38` to `830e809`, plus this close.

**Figures:** R-004 131 rows, collected before the close commit, so its `commits` (5) leave out this close;
`tools/metrics.py check` 442 figures, 0 bad. The dashboard "Rebuilt Session Ledger" now reads the re-uploaded table.

**Gates at the close**, on the staged tree: the eight gates (verdicts in the close commit's message).
- #5 is commented with its ruling, and the close commit's subject closes it on GitHub at the push.
- #4 stays open: its capture item is on the list.

**Not done:** no rule-checker ran before any action ([VSR-48]; the tool does not exist yet), the closing of #5
included. Left outside git: the export `build/export_bf92acd2` and the run log. No background process is left
running.

## Session R-003 — **Phase 0 closed on parse-equality (the build proof moved to phase 1); vhunt2's role found (#4); the original's corrections per tenant gathered; R-002 archived.** Opened 2026-10-18 on Opus 5.5 (the ruled orchestrator); transcript `5e9e8b49`.

### opened with

*"read state.md"*, then *"yes"* to opening R-003 and starting on the next-session list's item 1.

### (1) PHASE 0: THE 30 GENERATOR CONSTANTS TABLED, AND THE 16 THE CENSUS CANNOT SEE

The census's `code` column is the public module-level constants of six generators. `tools/phase0lib.py` now reads
them by an AST walk, which `tools/extract_tables.py` writes into `docs/project/tables/code/constants.tsv` (the
census's 30). Each value is the expression as written (hex stays hex), and a value that spans lines is carried
whole, with its comments dropped.

Found while building it: the census's line grammar takes one name, so the 16 constants bound in pairs
(`SLICE_LO, SLICE_HI = …` and seven more pairs) escape it. Three counted values are written in terms of them
(`DELTA_A = PLACE_A - SLICE_LO`, `LEN_A`, `LEN_B`). They are carried in `code/uncounted.tsv`. Gate
`tests/test_phase0_tables.py`: G2–G4 extended to the code column (G4 compares token streams, so hex written as
decimal fails). The new G6 checks that the code tables name every public constant, by an AST walk written apart
from the extractor's, and that `uncounted` is exactly what the census misses. Four new controls (`perturbed-code`,
`code-hex-as-decimal`, `uncounted-dropped`, `perturbed-generator`), all FIRED, every mode FAIL. Its first green was
read by its printed values ([VSR-21]). The format and the figures are in `docs/project/tables/README.md`. A
measurer reproduced every figure there before the commit.

Paid for this sitting: the measurer ran the four control modes side by side, which showed that every run of the
gate regenerated into the same scratch directory. Two concurrent runs could have compared each other's output. Its
verdicts matched the sequential runs, but the gate now makes a new scratch directory for each run and removes it
at the end ([VSR-143]). Committed `a002c98`, the three gates green on the staged tree.

### (2) PHASE 0: THE 2,528 VALUES THE CENSUS DOES NOT COUNT, AND THE MANIFESTS WHOLE

The census skips the keys of its `IGNORE_KEYS` and JSON's `_` keys. They are carried now, so the renderer can
reproduce the manifests whole: `docs/project/tables/uncounted/<key>.tsv`, one per TOML key (17 tables), and
`uncounted/json_underscore.tsv` (28 values), 2,528 rows. Not all of them are prose: a `space` row's `class` is
raw or crypt, and a `file` row's `source` names its zip member. The census's line grammar cuts a line at its first
`#`, and notes cite tickets, so a literal is recovered from the whole line (the shortest cut at a `#` that parses
to the value). The gate's G4 line check had the same cut and now reads past it. The new G7 (WHOLE) proves, by an
independent walk of each manifest's parse, that the tables hold all 11,284 values of the 30 canonical manifests
exactly once. Four manifests are comments only, so no table pins their SHA-1: that is for the renderer. Three new
controls, among them `note-cut-at-hash`, which plants the cut. Format and figures in
`docs/project/tables/README.md`.

Paid for this sitting: `dropped-row`'s declaration predicted too few failing checks once G7 existed (a dropped
gameplay row is also a missing manifest value). The declaration was corrected from the printed values, and the gate
was not loosened. The measurer corrected two of the README's figures, both mine from the survey (`name` 526, not
525; 2,519 strings, not 2,521). One of its commands failed on my spec (`python3 -I` hides the user site-packages
that hold `tomli`). Both times this sitting, the measurer ran two commands side by side against a spec that ran
them in order. Harmless here (the second was a read-only count), but noted against [VSR-50]. Committed `d9429be`,
the three gates green on the staged tree.

### (3) PHASE 0: THE RENDERER, THE HELD VALUES FROM THE DUMPS, AND THE BUILD PROOF MOVED TO PHASE 1

The maintainer: *"start it, we have ample context"*.
- **The renderer.** `tools/render_manifests.py` writes the 30 canonical manifests from the tables. What the value
  tables do not say about shape (each manifest's format, each TOML kind's `[x]`/`[[x]]`, each JSON container's form
  and member order) is the generated `layout/forms.tsv` (373 rows). Its header also pins the four comment-only
  manifests.
- **The gate.** The new G8 renders all 30 and requires them parse-equal to the originals (`tomli`/`json`, key order
  included). It also requires the original's own parser to agree: the host's Python is 3.9, so `_minitoml` is its
  subset parser, which accepts the same 21 manifests and refuses the same three with arrays. G8 is green, with two
  new controls. Seven older controls now also fail G8, as they should, and were re-declared from the printed values.
- **The held values.** `tools/gen_held.py` derives all five from the decrypted dumps, each refused unless it has its
  `held.tsv` SHA-1. Three come from the original's generators. The other two are rebuilt from their source spans
  with each edit named: `throw_arc_tables` is vs2's installer with two operands made placeholders; `beam_list_type6`
  is five parts. The first `throw_arc_tables` derivation was refused (I resumed the copy at the operand's
  displacement); fixed from the decomposition. Gate `tests/test_gen_held.py`: H1–H3 green, two controls; with the
  derived values the 30 manifests parse equal and no placeholder is left.
- **The build proof.** The maintainer ruled the vhunt2 audit shim on both legs (`SPEC.md` §0). The original's build
  then still stopped: its extractor reads `vhunt2.zip` as its sibling oracle (#4). Asked, the maintainer ruled
  *"Stop at parse-equality"*: the byte-for-byte proof moves to phase 1 (`SPEC.md` §0, §3). `tools/build_proof.py` is
  committed, unrun. Its logic is gated without a build by `tests/test_build_proof.py` (P1–P4, control
  `blind-compare`), whose first red was its own check (it read a docstring as a requirement), now made to load the
  shimmed module.
- **Not measured, for phase 1.** `beam_list_type6`'s copied drawer opens with a `bcs.w` copied unchanged, so its
  PC-relative target moves with the copy ([VSR-83]); whether it is reachable was not checked.
Committed `5c0f149`, the five gates green on the staged tree.

### (4) WHAT VHUNT2 DOES, AND THE ORIGINAL'S CORRECTIONS PER TENANT (#4)

The maintainer: *"to be clear, I could provide vhunt2 but I don't understand what it brings to the table"*. Read
from the extractor: vhunt2 is the sibling copy of the three newcomers. Diffing it against vs2 bounds each region and
yields its relocation map (about 7,000–9,000 pointers per tenant); no vhunt2 byte reaches the output. The
original tracks the results per tenant (`regions.json`: 21/31/26 regions, 7,736/8,915/6,882 refs). The maintainer's
direction (verbatim, `SPEC.md` §0, #4): *"I would table the measurement AND I would look at the history of Vampire
Saved to gather all the missing/wrong parts that had to be added/fixed for each of the three VS2 characters"*.
- **The history.** Three reader workers, one per tenant, returned 146 parts: Donovan 55, Huitzil 59, Pyron 32.
  They are `docs/project/port_corrections.tsv` (hand-written), each with its source line and a verbatim anchor,
  gated by `tests/test_port_corrections.py` (C1, C2, two controls). The gate's first run caught one non-verbatim
  quote. The classes are in `docs/project/port_corrections.md`. Only 27 parts are the extraction's own errors
  (reach, reloc, crypt-data); 85 are the engines' differences (short tables, aliased per-character rows, vs2
  environment assumptions), which the original found one by one and which three static enumerations would find.
- **The measurement, not yet tabled.** Each `regions.json` holds about 49,000–55,000 values (153,013 in all). Each
  tenant's `values` section carries three vs2 rows as raw bytes: `jump_params` (48 bytes) and `byte2d_a`/`_b`
  (30 bytes each). These are gameplay values ([VSR-6]), so how to carry them is the maintainer's call.
- **Guard refusal (1).** A command mixing a heredoc and escaped backticks was refused as unparseable. It was split
  into two calls.

### CLOSE (R-003, 2026-10-19)

Delivered: phase 0 met as amended (`SPEC.md` §3): the census's code column, the uncounted values, the layout,
the renderer, the five held values from the dumps; #4 opened, with the maintainer's direction and the corrections
catalogue (`docs/project/port_corrections.*`); #5 opened (the measurer's side-by-side runs, evidence only). Four
commits, `a002c98` to `7c9b3ce`, plus this close. Figures: R-003 127 rows, collected before the close commit, so its
commits (4) and `tickets_open` (2: the committed list, before #5) leave out this close. `red_min` 353.7 is mostly
`build_proof`'s one FAIL (02:01, the vhunt2 stop), which no PASS follows: the proof is phase 1's by ruling. The
dashboard "Rebuilt Session Ledger" was re-published from the table (311 figures). Gates at the close, on the
committed tree: the six gates (verdicts in the close commit's message). Not done: no rule-checker ran before any
action ([VSR-48]; the tool does not exist yet); the extraction measurements are not tabled (the next session's first
item). Left outside git: the export `build/export_bf92acd2` and the run log. No background process is left running.

## Session R-002 — **#3 built and closed: the figures, their gate, the run log, the dashboard; R-001 archived.** Opened 2026-10-18 on Opus 5.5 (the ruled orchestrator); transcript `c6b8c007`.

### opened with

*"read state.nd"*, then *"yes"* to opening R-002 and starting on #3.

### (1) #3: THE FIGURES, THEIR GATE, THE RUN LOG, THE BACKFILL

`tools/metrics.py` writes `docs/project/metrics/figures.tsv` (one row per figure per session, `{value, class,
source, rule}`, ABSENT rows for what no source holds); what each figure is and how it is timed:
`docs/project/metrics/README.md`. `tools/runlog.py`: every gate appends one JSON line per run to
`build/runs/runs.jsonl`; the two existing gates and the new one write it. Gate `tests/test_metrics.py`: a synthetic
session whose every figure is known by construction, ten checks (C1–C10), five controls (`late-result`,
`usage-twice`, `ask-as-tool`, `absent-filled`, `rule-dropped`), all FIRED, every mode FAIL. Its first green was read
by its printed values ([VSR-21]): the first run's two reds were the fixture's (an answer placed at minute 202 where
its design said 203), not the tool's.

Found while building it: the transcript carries a `cost-state` record with the harness's own totals, which R-001's
survey missed. On R-001 the DERIVED buckets agree with it: working is 5.8 % under its API time, and tool calls are
12.2 % over its tool time once the two `AskUserQuestion` waits (610 s) are given to the maintainer. A worker
transcript's `usage.output_tokens` is a streaming snapshot (201 against the harness's 4,600), so workers' tokens come
from the harness. Backfilled: R-001 (88 figures) and 14z-205's drafting share (13; EXTRAPOLATED, an undercount, its
rule says why). Committed `bb79816`, the three gates green on the staged tree.

### (2) #3: THE DASHBOARD

The view: "Rebuilt Session Ledger", a private claude.ai dashboard (https://claude.ai/artifact/EpBKcPyqtdSbePUso6jDd5)
over one source, the tracked table uploaded as `figures.csv`. A tab per session; time (the four buckets beside the
harness's cross-check, and session by session), activity, tokens and workers, commits by area, phase 0 against the
census, gates and the inventory by class, health, gate runs, and every figure with its source and rule. Each figure
shows its class as a chip. It is re-published from the table at each close (`docs/project/metrics/README.md`).

### (3) 14z-205 RULED OUT OF THE TABLE

The maintainer, on the dashboard: *"dashboard looks good, session 14z=205 that you inherited from Vampire Savior can
honestly be removed."* Its 13 rows were dropped with a new `tools/metrics.py drop` (the table is never hand-edited);
the gate gained C11 (drop removes exactly one session's rows and refuses a key with none) and its control
`drop-overreach`. The backfill line of (1) is superseded by this: the table holds R-001 alone before R-002.

### (4) THE CLOSE'S OWN FINDING: GUARD REFUSALS WERE COUNTED BY TEXT

Collecting R-002 counted 1 guard refusal where there was none: my survey of R-001's errors had printed R-001's
refusal text. R-001's 4 was inflated the same way (gate outputs quote the message); its real refusals are 2, as its
record says. A refusal is now the hook's own error result (`PreToolUse:<tool> hook error:` and the message); the
gate's fixture quotes the message in a passing result, and the control `guard-by-text` (C3) proves the case is read.
R-001 and R-002 re-collected. Gotcha in `docs/project/metrics/README.md`.

### CLOSE (R-002, 2026-10-18)

Delivered: #3 built and closed (`tools/metrics.py`, `tools/runlog.py`, `tests/test_metrics.py`,
`docs/project/metrics/`, the dashboard "Rebuilt Session Ledger"); R-001 moved verbatim to `STATE_HISTORY.md`, which
opens with its index. Figures: R-001 88 rows, R-002 96 rows, collected before the close commit, so R-002's count of
commits (2) and its last commit (`7b1fea3`) leave out the close commit, and it has no `cost-state` record yet
(ABSENT). Gates at the close, on the committed tree: the three gates (verdicts in the close commit's message). Not
done: no rule-checker ran before any action ([VSR-48]; the tool does not exist yet). Left outside git: the run log
`build/runs/runs.jsonl` and the export `build/export_bf92acd2` (both git-ignored). No background process is left
running.

## Session R-001 — **CLAUDE.md v1.0 validated, SPEC v0.2 accepted; the read-only guard installed; phase 0 started.** Opened 2026-10-18 on Opus 5.5 (the ruled orchestrator); transcript `dde4a561`.

### opened with

*"CLAUDE.md has been validated, the spec.md draft is accepted"*; then the maintainer's answers on the draft's loose
ends, the four read-only sources, *"Please add the hook and after that start phase 0"*.

### (1) THE LAW AND THE SPEC ACCEPTED; THE FOLLOW-UPS

`791d5bb`: both status lines. `c185504`: the filiation of [VSR-1]..[VSR-50] moved out of `CLAUDE.md` into
`docs/carried/ledger_claude_md.tsv`; vhunt2 dropped entirely ([VSR-38] narrowed to vsavj/vsav2, §7's VH2 clause
removed); `../ROMS` named in [VSR-8] with the read-only rule; typos. `9adf1a1`: the four read-only sources of truth
named in `CLAUDE.md` §7. Every ruling is verbatim in `SPEC.md` §0.

### (2) THE READ-ONLY GUARD

`ac61157`: `.claude/hooks/guard_readonly.py`, a PreToolUse hook refusing a write outside the working tree or to the
edit-locked hook files ([VSR-49]); record and gaps in `docs/project/hooks.md`; gate `tests/test_readonly_guard.py`
(59 cases, both controls FIRED, both control modes FAIL). Live: a no-op `rm -f` outside the tree was refused. Two gaps
found the same hour (Decisions pending, item 1).

### (3) PHASE 0 STARTED: WHERE, FROM WHICH COMMIT, AND THE BASELINE

The spec put phase 0 in the original, which the ruling of (1) made read-only; asked, the maintainer ruled it runs
here, reading the original at `bf92acd2` (`SPEC.md` §0, §3 amended). `tools/export_original.py` exports a pinned
commit through `git ls-tree`/`git cat-file` only, into a directory that must not exist. The baseline, measured by a
measurer worker ([VSR-47]) on its own export:

| figure | value |
|---|---|
| export of `bf92acd2` | tree `0a40f749ea3a`, 17,068 files (542,160,969 bytes); 3 submodules skipped (emu/fbneo, emu/jtcores, emu/mame) |
| the original's checkout, status entries before / after | 936 / 936 |
| census manifests | 30 |
| gameplay: in-table / derived / baked / total | 15 / 0 / 221 / 236 |
| fact: in-table / derived / baked / total | 0 / 541 / 7,979 / 8,520 |
| code: in-table / derived / baked / total | 0 / 0 / 30 / 30 |

These equal `SPEC.md` §1's figures at `6dee2be7`. What the census counts: every scalar of the 30 canonical manifests
and every module-level constant of six generators, by (kind, key); the gameplay column is variant selection
(`only_variant_slot`, `only_base_slot`, `unless_composed`, `id_by_profile`, `dst_slot`, `mirror_variant`,
`roster_subst`, the select wheel's `layout`, adjacency and `edges_in`, `tenant.id`, and three `aux_poke.val` judged by
address), held in `donovan.toml`, `huitzil.toml`, `pyron.toml`, `shared_writes.toml` and `effect_tail.json`.

**Not done in this sitting:** no rule-checker ran before any action ([VSR-48]): the rebuild has no rule-checker tool
yet (`docs/project/rule_checker.md` is its spec), so none of this sitting's commits had one.

### (4) THE TWO PENDING ITEMS RULED: THE GUARD'S FIX PREPARED, TICKETS OPENED

The maintainer: *"yes and yes"* (`SPEC.md` §0). The fix is `build/proposed/hooks/guard_readonly.py` (#2): where git
acts now includes `--git-dir`/`--work-tree` (both forms) and `GIT_DIR`/`GIT_WORK_TREE`; `-c` values are skipped;
`archive` is a read (its `-o` judged); `fetch` leaves the read list and `config`/`branch`/`remote` read only in their
reading forms. The gate gained `--hook <path>` and 14 cases. On the proposal: 73 cases (48 block, 25 allow), PASS, both
controls FIRED, both control modes FAIL. On the installed hook: FAIL on exactly the 10 cases #2 names. A replay of the
sitting's 59 calls through both hooks: 0 differences. Tickets: `docs/project/tickets.tsv` holds #1 (the umbrella
ticket carried from the original's #120, already open) and #2.

### (5) #2 INSTALLED AND CLOSED

The maintainer installed the proposal (`cp`, 2026-10-18); the installed hook is byte-identical to it (`cmp`). The gate
on the installed hook: 73 cases, `VERDICT: PASS`, both controls FIRED, both control modes `VERDICT: FAIL`. Live: `git -C
<original> archive bf92acd2 SPEC.md | tar -t` ran; `GIT_DIR=../ROMS/.git git reset --hard` was refused. The proposal
file was removed once installed (it is in this sitting's history).

### (6) PHASE 0: THE 236 GAMEPLAY VALUES TABLED

The format, decided as `SPEC.md` §4 asks, with its reasons in `docs/project/tables/README.md`: one TSV per subject,
one schema for all (`manifest, kind, row, key, value, line, prov_kind, prov_refs`), values as the manifest's literal,
provenance as the census's attribution (vocabulary word and references) with the paragraph left at its pinned line.
`tools/extract_gameplay_tables.py` imports the original's census from the export and aligns each record with its
row (`tools/phase0lib.py`): `variant_selection` 182, `select_wheel` 42, `roster` 9, `hit_class_mask` 3 = the
census's 236. Gate `tests/test_phase0_gameplay.py`: G1 regenerated equal, G2 the export's manifests are the pinned
SHA-1s, G3 the census column and the tables are the same multiset, G4 every cell equals an independent parse; three
controls (perturbed-value, dropped-row, perturbed-manifest). Exports now live under `build/` (git-ignored), inside
the tree. The figures in the README were reproduced by a measurer before the commit.

Paid for this sitting: the first control declarations predicted too few failing checks (a changed value also moves
G3's multiset); the declarations were corrected from the printed values, not the gate loosened. The JSON alignment
first compared the wrong tuple fields; fixed by one tuple layout for TOML and JSON.

### (7) PHASE 0: THE HEX RULING, AND THE 8,520 FACTS TABLED

Asked how the fact column's 649 hex fields (6,420 bytes, the largest 470) are carried, the maintainer chose "As
written, ruling into VSR-8" (`SPEC.md` §0): `CLAUDE.md` [VSR-8] now carries the #120 ruling's line, and each of the
7 runs over 64 bytes was checked before tabling. 2 are the project's own resolvers, carried. 5 hold whole vanilla or
vs2 routines or tables and are held out (`docs/project/tables/facts/held.tsv`, carried as `HELD:sha1=…`):
`index_window_018468`, `hitclass_map_extend` (Huitzil and Pyron), `beam_list_type6`, `throw_arc_tables`. Three of
them are produced by the original's generators.

The extractor and the gate were generalized and renamed: `tools/extract_tables.py` (was `extract_gameplay_tables.py`)
and `tests/test_phase0_tables.py` (was `test_phase0_gameplay.py`). Both columns: 8,756 rows in 56 tables (4 gameplay,
52 under `facts/`). JSON rows are JSON Pointers now (the `.` glyph of `version_font.json` broke dotted paths), which
changed `select_wheel.tsv`'s row column. Gate: G1–G4 as before over both columns, plus G5 (held values are only
their hashes, and none is in the clear); five controls, the two new ones `held-leak` and `perturbed-pointer-fact`.
The README's figures were reproduced by a measurer before the commit.

### (8) THE SESSION DASHBOARD, PROPOSED AND RULED (#3)

The maintainer asked for a dashboard of where time goes and the project's metrics. Proposed, then ruled: both
Claude's time and the maintainer's, split into Claude working, Claude waiting on tools, and the total; every figure
classed by how it was obtained, after the dashboard the maintainer named (the original's `tools/session_metrics.py`,
its #264: MEASURED, DERIVED, ESTIMATED, INFERRED, EXTRAPOLATED); a backfill "to the extent that you can"; built in
the next session, after this one closes. The plan and the maintainer's words are in #3. Measured this sitting: the
transcript carries per-turn wall time (`system/turn_duration`, on 11 turns only) and thinking time
(`thinkingDurationMs`, 141 messages), but no tool duration (to be DERIVED from timestamps); `0de1913b` is a 3-record
stub, and the drafting before R-001 ran in the original's 14z-205 (`995e7259`).

### CLOSE (R-001, 2026-10-18)

Delivered, all pushed: `CLAUDE.md` v1.0 and `SPEC.md` v0.2 accepted, with the follow-ups the maintainer ruled; the
read-only guard and its edit lock (#2 found, fixed and closed the same sitting); the ticket list (#1 carried, #2, #3);
`STATE.md`; phase 0's two value columns, 8,756 values in 56 tables with five held out. Gates at the close, on the
committed tree: `tests/test_readonly_guard.py` and `tests/test_phase0_tables.py` (verdicts in the close commit's
message). Not done: no rule-checker ran before any action ([VSR-48]; the tool does not exist yet). Left outside git:
the export `build/export_bf92acd2` (542 MB, git-ignored, kept for the gate; `tools/export_original.py` remakes it)
and this sitting's scratchpad exports. No background process is left running.
