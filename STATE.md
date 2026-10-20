# STATE — living progress log

**Opened 2026-10-18 (session R-001), `CLAUDE.md` [VSR-28].** This file holds the latest session group and the
standing sections; older groups move VERBATIM to `STATE_HISTORY.md` (created at the first move, with an index at its
head). A session key is `R-NNN`, one per sitting, never renamed or renumbered ([VSR-30]); milestones and freezes are
their own namespaces. A group's form, kept from the original: `## Session KEY — banner`, then `### opened with` and one
`### (N) TITLE` section per piece of work. An open list holds only what is open.

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

1. #4: phase 1 ports vs2's three rows of the table at `PRG:0x0BE3FA` (ruled 2026-10-20, `SPEC.md` §0: universal
   mechanics are vsavj's, character-specific ones vs2's). The state is the doll's hop after Royal Judgement (R-005
   (7)); the `doll` rig becomes the port's gate once phase 1 builds: each newcomer's hops equal native vs2's, Victor's
   unchanged ([VSR-17]).
2. #4: give `tools/build_proof.py` a second control that the original's own checks accept, so the byte compare is
   exercised end to end (R-005 (2): `perturbed-render` is stopped by the original's HUD check first).
3. #4: a census of the per-character tables the engine reads by the raw id, for the newcomers: where the build gives a
   newcomer its shell's row and vs2 has its own, the ground rule ([VSR-40]) asks for vs2's. The doll table was found
   by accident; the census makes the port's list complete before phase 1.
4. #4: the height table (`word_y_off`, `PRG:0x0BE7FA`) figures into the README, reproduced by a measurer first
   (vs2's own row, the shell's row, the patched romset: Phobos 0, Donovan 0, Pyron 78, the same on all three).
