# STATE — living progress log

**Opened 2026-10-18 (session R-001), `CLAUDE.md` [VSR-28].** This file holds the latest session group and the
standing sections; older groups move VERBATIM to `STATE_HISTORY.md` (created at the first move, with an index at its
head). A session key is `R-NNN`, one per sitting, never renamed or renumbered ([VSR-30]); milestones and freezes are
their own namespaces. A group's form, kept from the original: `## Session KEY — banner`, then `### opened with` and one
`### (N) TITLE` section per piece of work. An open list holds only what is open.

## Session R-005 — **vhunt2 provided; the build proof PASSES: the tables rebuild the original's frozen merged build byte for byte (#4); the reference MAME built from the pin and proven the instrument that froze the oracle.** Opened 2026-10-19 on Opus 5.5 (the ruled orchestrator), in R-004's transcript `dc3ff4f7` after its close.

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
the dual-emulator rule need ([VSR-13], [VSR-16]); the capture needs only MAME WIDE.


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

# STANDING SECTIONS (current state — never archived)

## Standing rulings

The rulings of 2026-10-18 are verbatim in `SPEC.md` §0 (the brief, the five answers, v0.1's four questions, the
validation of `CLAUDE.md` v1.0, the read-only sources, phase 0's place and pin). The law is `CLAUDE.md`.

## Decisions pending (human)

none.

## The next session starts with

1. #4, ruled (c) then (a) (`SPEC.md` §0, R-004): when an instrument can run the original's build (R-005 builds it;
   the reference MAME is built and proven, R-005 (4); the instrument is that MAME with the WIDE profile, which needs
   the maintainer's ratification, [VSR-2]: present the original's profile spec and its MAME patch, then build it and
   prove the emulator superset invariant), capture which move enters state `0x02100600` (vsavj `PRG:0x026670`) for
   each newcomer, native vs2 against the build. Then phase 1 ports vs2's three rows of the table at `PRG:0x0BE3FA`
   if the difference is the newcomers' own.
2. #4: give `tools/build_proof.py` a second control that the original's own checks accept, so the byte compare is
   exercised end to end (R-005 (2): `perturbed-render` is stopped by the original's HUD check first).
