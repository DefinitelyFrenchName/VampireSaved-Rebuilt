# SPEC — Vampire Saved Rebuilt

**Status: ACCEPTED v0.2 (2026-10-18): v0.1 with the maintainer's answers to its open questions (§0), accepted by the maintainer the same day, with the rulings of its acceptance (§0). Nothing here is built.** The ticket is
[#120](https://github.com/DefinitelyFrenchName/VampireSaved/issues/120) in the original repository ("The rebuild-from-docs
option after MiSTer"). The source project is called *the original* below: `DefinitelyFrenchName/VampireSaved`, read at
its working tree of 2026-10-18: HEAD `6dee2be7` plus that session's uncommitted changes under `tests/` (the test
inventory's first line records the scripts' content hash); the manifests and the rule-5 census tool had no uncommitted
change (the census report's first line records it), so the census figures below are `6dee2be7`'s. **What this draft does not re-verify:** the original's anchors
(`[VSP-N]`, `[CPE-N]`), rulings and documents it cites are cited, not re-checked in this draft.

## 0. The brief, and the rulings that shape this draft

The maintainer's brief (2026-10-18, verbatim):

> * Rebuild the project from docs, with the same scope and the same focus on accuracy.
> * The goal is not recreating the exact same implementation. In fact, a lot of choices and assumptions made for Vampire
>   Saved might be suboptimal (e.g. using shell characters) and should not blindly reused.
> * Reuse all the tests that apply (unless I'm mistaken, that should include at least all the end-to-end tests.) The spec
>   should include a list of all the tests that can be used for the rebuild, what the cover and how they run.
> * The agent swarm structure and rules should be kept unless demonstrably not adequate.
> * The general document structure and practices should be kept unless a better alternative emerges.
> * It should use a separate GitHub repo called Vampire Saved Rebuilt

The maintainer's answers the same day (AskUserQuestion; five, the repository's included). Only the **bold** text is the
maintainer's, verbatim (the option they chose, or their own words); the text after each label is this draft's reading of
that option, not the maintainer's words:
- test reuse: **"Both, in phases"**: the original's gates first run unchanged against the rebuild's artifacts as an external
  acceptance suite; gates are then ported, each proven against the original, until the external suite can be retired;
- scope: **"Romset first, then the rest"**: phase 1 the romset pipeline and its emulator acceptance; the MiSTer core and
  the releases in later phases;
- harness: **"Its own harness"**, written in the rebuild's repository, informed by bbh and the original's, with no
  dependency on bbh (bbh is its own project since 2026-10-09);
- location: **"The new repo"**: this spec is the rebuild repository's first commit;
- the repository: **"I create it and you push, repo will be https://github.com/DefinitelyFrenchName/VampireSaved-Rebuilt"**,
  and its visibility: **"Public"**.

The maintainer's answers to v0.1's open questions (2026-10-18, verbatim in bold; the text after each is how this draft
applies it):
- phase 0 before phase 1, gameplay values first: **"yes"** (§3);
- the harness language: **"python or rust, as is most appropriate"**: chosen per component on its merits, the reason
  recorded with the choice (§6);
- tickets: **"first of all, only ticket related to the game make sense since we're rebuilding everything, second: no open
  tickets need be moved to the rebuild."**: the rebuild opens with no tickets carried over; the original's game facts
  reach it through the documentation, not the ticket list (§9);
- the original during the rebuild: **"The original will keep receiving fixes however the only elements that might be of
  interest to the rebuild are additional tests. The rest can be fully ignored"**: no freeze is imposed on the original;
  the rebuild follows it only for tests (§5.2).

The maintainer's rulings on validating `CLAUDE.md` v1.0 (2026-10-18, verbatim in bold; the text after each is how this
spec applies it):
- vhunt2: **"vhunt2 is dropped entirely because our work on Vampire Saved proved it held no assets or code we needed:
  everything that we need to backport is in vs2."**: the rebuild's inputs are `vsavj` and `vsav2` only; no provenance
  tag, diff or gate of the rebuild has vhunt2 as its subject (§5);
- the reference romsets: **"vsavj being the reference implies the region"**, and they are in `../ROMS`, which, **"like
  anything above the working directory, must only be accessed read-only"** (`CLAUDE.md` [VSR-8]);
- the other inputs: **"in ../ROMS , ../Images , ../Videos and ../community are read-only sources of truth that were used
  in Vampire Saved and are still relevant."**: the rebuild reads all four, and only reads them (`CLAUDE.md` §7).

The maintainer's answers on starting phase 0 (2026-10-18, AskUserQuestion; the option chosen, verbatim in bold; the
text after each is how this spec applies it):
- where phase 0 runs: **"Here, original read-only (Recommended)"**: the tables live in this repository, with
  provenance (the original's commit, file and key); the original's checkout is read only through git
  (`tools/export_original.py` exports a pinned commit into a fresh directory) and never written (§3);
- the commit phase 0 reads: **"bf92acd2, current HEAD (Recommended)"**: `bf92acd271e4` (the original's 14z-205),
  committed and reproducible; its checkout's uncommitted entries are ignored.

The maintainer's answers on the two items R-001 left pending (2026-10-18, verbatim in bold): **"yes and yes"**:
- the read-only guard's gaps: the fix, prepared by Claude as a proven file outside the edit-locked paths and installed
  by the maintainer (#2, `docs/project/hooks.md`);
- tickets: Claude opens GitHub issues on `VampireSaved-Rebuilt`, and `docs/project/tickets.tsv` is the list
  (`CLAUDE.md` [VSR-29]).

The maintainer's answer on the `fact` column's hex fields (2026-10-18, AskUserQuestion; verbatim in bold): **"As
written, ruling into VSR-8 (Recommended)"**: the 649 hex fields are carried as the manifests write them, as discrete
values under the ruling quoted in #1 (*"Fundamentally adresses are fine, discrete values are fine. whole GFX or SFX
are not fine, whole algorithms are not fine either."*), which `CLAUDE.md` [VSR-8] now carries; each of the 7 runs
longer than 64 bytes is checked and reported to the maintainer as not a whole algorithm, or held out, before it is
tabled.

The maintainer's answer on phase 0's build proof and the original's ROM audit (2026-10-18, R-003, AskUserQuestion;
the option chosen, verbatim in bold): **"Shim both legs (Recommended)"**. The original's build runs
`tools/audit_roms.py` first, and it requires `vhunt2.zip` and `vhunt2r1.zip`, which vhunt2's ruling above leaves out of
`../ROMS`. So the proof tool drops vhunt2 from the copy of that audit in both exports (its required sets, its key
checks and its manifest rows), identically on each leg, and records it. Every member present is still checked, and
the original's checkout is never touched.

The maintainer's answer on phase 0's build proof once it was found that the original's extractor reads vhunt2
(2026-10-18, R-003, AskUserQuestion; the option chosen, verbatim in bold): **"Stop at parse-equality"**. With the
audit shimmed, the original's build still stops: `tools/extract_char.py` takes `vhunt2.zip` as its sibling oracle,
which decides each ported region's bounds (no vhunt2 byte reaches the output). So phase 0 closes on parse-equality
(the tables render all 30 manifests parse-equal to the original's, the five held values derived from the reference
sets), and the byte-for-byte build proof moves to phase 1, against the rebuild's own pipeline. `tools/build_proof.py`
stays committed, unrun; the shim ruling above stands for whenever it runs. (R-005: the maintainer provided `vhunt2.zip`; the proof
ran with the shim narrowed to the vhunt2 sets ROMDIR lacks, and PASSED: `docs/project/tables/README.md` "The build
proof". The phase-1 proof against the rebuild's own pipeline is still phase 1's.)

The maintainer's direction for the extraction (2026-10-18, R-003, after Claude explained what vhunt2 does for the
original's extractor: the sibling copy that bounds each region and yields its relocation map; verbatim): **"I would
table the measurement AND I would look at the history of Vampire Saved to gather all the missing/wrong parts that
had to be added/fixed for each of the three VS2 characters"**. So the extraction's measurements (each tenant's
regions: vs2 address, vhunt2 twin, length, SHA-1, relocation refs) become tables, and the original's history is
searched for every part the extraction missed or got wrong, per character (#4).

The maintainer's answer on the three vs2 rows each extraction record carries as raw bytes (`jump_params`,
`byte2d_a`, `byte2d_b`; 2026-10-18, R-003, AskUserQuestion; the option chosen, verbatim in bold): **"Readable
gameplay table (Recommended)"**. They are decoded into named fields in a gameplay table the community can review and
adjust, with provenance to vs2's row, and the build writes them from the table ([VSR-6]).

The maintainer's answer on #5, the measurer's three side-by-side runs in R-003 (2026-10-19, R-004; quoting Claude's
recommendation, then verbatim in bold): *"I recommend (a) now and (b) if it happens again."* **"agreed"**. So (a): the
`measurer` definition (`.claude/agents/measurer.md`) now says commands run one per tool call, never two in one message.
(b), a hook that refuses a worker's concurrent tool calls, is built if a worker runs side by side again; that
recurrence opens a ticket with its evidence ([VSR-50]).

The maintainer's answer on the other short bank values the extraction records carry (2026-10-19, R-004; quoting
Claude's question, then verbatim in bold): *"Should they get readable tables too?"* **"I lean yes since tables is what
we decided and that data is valuable"**. So each tenant's own short bank rows are decoded into a third gameplay
table, `docs/project/tables/bank_values.tsv`, one row per field, with provenance to vs2's address. Two rows of the
question, `rec8_a` and `rec8_b`, turned out not to be the tenant's own data. The extractor reads them 8 bytes at
`char*8`, but the original's notes put the real records at `id*0x30` (`jump_params`) and `id*0x20` (the pursuit
record). So they stay as written in `extraction/values.tsv`, and the README explains why (#4).

The maintainer's answer on the newcomers' own rows of the table at `PRG:0x0BE3FA` (2026-10-19, R-004; quoting Claude's
recommendation, then verbatim in bold): *"I recommend (c), then (a) if the difference turns out to be the newcomers'
own."* **"yes, (c) then (a) if need be"**. In the original's build, Donovan, Huitzil and Pyron read Victor's, Bulleta's
and Demitri's rows there; vs2's own rows differ, and both games index the table by the raw id. So (c) comes first: a
capture in play of which move enters that state and how native vs2 and the original's build differ there
([VSR-43]). Then (a): phase 1 ports vs2's three rows if the difference is the newcomers' own (#4).

The maintainer's ratification of the WIDE profile for this repository (2026-10-19, R-005; [VSR-2]). Asked *"Do you
ratify the CPS-2 WIDE profile v1.2 for this repository, MAME side, so I can build it and prove it before the
capture?"*, with the option *"Ratify v1.2 verbatim (Recommended) — Import the original's spec into docs/ as its one
copy and apply its MAME patch unchanged, canary included. The original's gates (test_mame_wide.sh and the E1 suite)
then run as written."*, the maintainer chose **"Ratify v1.2 verbatim (Recommended)"**. The spec's one copy is
`docs/project/cps2_wide.md`, imported from the original at `bf92acd2`; the patch is
`emu/mame-patches/0002-cps2-wide-v1.patch`, unchanged. The ratification is the MAME side; FBNeo's twin is not yet
built here.

## 1. What the rebuild is, and what it is not

**The same project, rebuilt.** The goal, the non-goals and the background facts are the original's `SPEC.md` §1-§2 and its
`CLAUDE.md` §1 (the mission), adopted unchanged: a modified `vsavj` (Japan 970519) romset in which all 18 series
characters are selectable on the genuine engine, with every original path frame-identical to vanilla. The accuracy bar is
the original's, not a new one.

**Not a port of the code.** The rebuild re-derives its implementation from the original's documentation and measured
facts, and keeps from the code only what its tests prove. §4 lists the implementation choices that are to be
reconsidered rather than copied.

**Rebuilt from the documentation — and what that requires first.** The original's own measure of feasibility is its rule-5
census (`python3 tools/audit_rule5.py --report`): how many behavioural values and measured facts sit in documented tables
rather than in manifests or code. At `6dee2be7` it reads gameplay values 15 in tables of 236 (221 baked), facts 0 in tables
and 541 derived of 8,520 (7,979 baked), code constants 30 baked. A rebuild that does not carry those facts re-pays every
session that measured them. **So phase 0 (§3) extracts them into tables with provenance, in the original, before the
rebuild writes its pipeline**, as #120's own text recommends.

## 2. The invariants carried over unchanged

These are the original's law, not choices; the rebuild adopts them verbatim (the original's `CLAUDE.md` §1-§2, by
anchor):
- **[VSP-1] the superset invariant**: any path not involving the three new characters is frame-identical to vanilla.
- **[VSP-2] emulator cores unmodified** except a ratified, profile-gated, declarative profile (the CPS-2 WIDE profile,
  `docs/project/cps2_wide.md`).
- **[VSP-3] no untested change survives a session; [VSP-4] no hand-edited binaries; [VSP-5] provenance per region;
  [VSP-6] behavioural values in documented tables; [VSP-7] a failing regression halts forward work; [VSP-8] no ROM bytes
  in the repository or any artifact.**
- The decided items: the reference set is `vsavj` (Japan 970519); the legacy oracle is MAME, FBNeo carries the emulator
  superset invariant; the oracle classes of `docs/project/oracle_classes.md` and the rule that a replay is never
  reclassified to a looser class without a new measured mechanism and the maintainer's sign-off.
- Every standing ruling of the original's `STATE.md` "Standing rulings" that concerns the GAME or the ARTIFACT (the
  tenants' Dark Force, the defense rows, the class-0x52 rule, vanilla wins ties, cosmetic is optional, …) binds the
  rebuild; the rulings about the original's own tooling do not, and are re-decided where the rebuild's tooling differs.

## 3. Phases

| phase | deliverable | acceptance |
|---|---|---|
| 0 (in this repository, the original read-only at `bf92acd2`, before phase 1; gameplay values first — §0) | the measured facts of the original's canonical manifests (`build/manifest/`, 30 files) and generators, extracted into documented tables with provenance in this repository: the tables are the rebuild's source data (the original's option B, value in the manifest and a table row beside it, has no manifest to sit beside here) | a census in this repository: every scalar the original's census counts maps to one table cell; manifests rendered from the tables equal the original's when parsed, the five held values derived from the reference sets (the byte-for-byte build proof moved to phase 1, §0) |
| 1 | the romset pipeline (extract, reconcile, generate, pack) and the FBNeo and MAME WIDE profiles, in the rebuild's repository | the byte-for-byte build proof moved from phase 0 (§0); the external acceptance suite (§5, classes E1 and the F gates): the legacy oracle bit-identical to vanilla on every replay of the corpus under its frozen class; tenant content equal to the original's frozen expectations and to native vs2 on the parity gates |
| 2 | the MiSTer core (jtcps2w) and its simulation lane | class M of §5 |
| 3 | the releases: packaging, the applier, the launchers, the per-platform binaries | class R of §5 |
| 4 | the external suite retired | every gate the rebuild needs is ported and proven equivalent (§5.3) |

The rebuild's romset need not be byte-identical to the original's: placement may differ. What must be identical is the
behaviour the gates judge. Where a frozen expectation encodes a placement (an address, an op count), it is a fact about
the original's build, and the rebuild's own expectation is re-frozen only through the original's expectation rule (a
red gate is a question; re-freezing needs a measured mechanism) — never inherited blind and never loosened.

## 4. Implementation choices to reconsider, not copy

Each is a choice the original made that its own record shows cost time; the rebuild decides each afresh, and records the
decision with its reason. Each item names where the original paid for it.
- **Shell as the test language.** The gates are POSIX `sh`: no locals (a helper's loop variable overwrote a gate's, the
  14z-204 gotcha), `set -e` and trap traps ([VSP-176], [VSP-177]), zsh/bash differences, word splitting, quoting of
  generated argument lists. Proposed: the harness and the gates in Python (already the original's tool language), with
  shell only where a process must be launched.
- **Paths and sandboxes as strings.** Relative paths resolved against a changed working directory (`proof_sheets.py`,
  14z-205), sandboxes keyed by part of a run's identity (#293), rompath search order ([VSP-58], [VSP-105], [VSP-106]).
  Proposed: one run object owns its sandbox (created fresh, refused if it exists), its rompath and its outputs, by
  construction.
- **Build directories named by hand and re-pointed at every freeze.** About 70 re-point defaults and the freeze-time sweep
  ([VSP-95], [VSP-185], `test_build_ref_rot.sh`, `test_superseded_pins.sh`). Proposed: builds addressed by their content
  key, gates reading "the current build" from one registry.
- **The manifest subset.** Flat TOML encodings forced by a parser difference ([VSP-74]); the generator's `main()`
  ([VSP-16], #50). Proposed: a schema-checked data format and small, separately testable generator stages.
- **Hand-declared inputs.** `# FOLLOWS:` declarations, their reconciler and the static-confirm predictor (#188, #225,
  #243, #286, #292). Proposed: inputs recorded by the harness at run time (what a run actually opened), so staleness is
  computed, not declared.
- **Input staging per instrument.** Half the original's Lua instruments once staged inputs one frame off ([VSP-149]).
  Proposed: one input player shared by every instrument.

## 5. The tests the rebuild can use

### 5.1 The inventory

Every top-level script of the original's `tests/` (`tests/*.sh`, 464 in the tree of §0; the helpers under `tests/lib/` are not gates) is classed in `docs/tests_inventory.tsv` (shipped with this
spec): its family, kind, tier, emulator lane and scope, what it needs to run, its class, the reason for the class, and
**what it covers** (the gate's own header sentence). The classes were assigned by a script (`classify_tests.py`, shipped
beside it: it reads the original's generated gate index, its registries and each script's code lines; the inventory's first line hashes the scripts and those three index inputs, and the generated index was checked current against the tree by `tests/test_gate_index_current.sh`). A measurer
re-ran the same script and counted its output, which confirms the counts as reported and the tree they came from, NOT
that the classes are right; **each class is to be confirmed gate by gate when the gate is ported.**

| class | count | what it is | how the rebuild uses it |
|---|---|---|---|
| E1 | 119 | a gate whose subject is a built artifact's behaviour or bytes, reading the build only through its rompath (most are emulator gates; a few static gates read a built romset's bytes) | runs unchanged against the rebuild's romset (§5.2) |
| E2 | 76 | an emulator gate that also reads the original pipeline's internals (patch.json, placements, prg/, verify images, the manifests) | its verdict applies; an adapter supplies what it reads, or the gate is ported first |
| F | 65 | a gate whose subject is pristine vsavj/vsav2/vhunt2 or the emulators as instruments (no build, no manifest) | runs unchanged: it locks facts the rebuild's documentation inherits; a gate whose subject is vhunt2 is not used (§0) |
| P | 55 | a static gate on the original's manifests, generators or ops | not reused as a script: the facts it locks are phase 0's tables, and the rebuild writes its own pipeline tests |
| T | 123 | the original's tooling and process: runners, documentation locks, the rule-checker, close and agent tooling, ROM-free tool tests | a specification for the rebuild's own tooling: port the idea and its controls, not the script |
| M | 9 | the Verilator/MiSTer lane | phase 2 |
| R | 17 | release packaging, the applier, launchers, release binaries | phase 3 |

The end-to-end tests the brief names are E1 and E2 (195 gates); with F, 260 gates run against the rebuild's artifacts in
phase 1, and 26 more (M, R) in phases 2 and 3.

### 5.2 How they run

- **Prerequisites** (each row's `needs`): `ROMDIR` with the reference sets verified against the original's
  `docs/checksums.txt`; the pinned MAME and FBNeo binaries built by the original's `tools/setup_mame.sh` and
  `tools/setup_fbneo.sh` from their recorded sources ([CPE-24]: the reference binary first); for E1/E2, the rebuild's
  romset as a rompath.
- **The external suite (phase 1).** A checkout of the original at a pinned commit. The original keeps receiving
  fixes; the rebuild ignores them except for added tests: the pin is advanced only to take in new or strengthened gates,
  and `docs/tests_inventory.tsv` is regenerated at each advance (§0); its emulator gates driven by the
  original's `tests/run_all_emulator.sh` (rows and timeouts in `tests/ci_emulator.tsv`) and its static gates by
  `tests/run_all_static.sh`, with every build path pointed at the rebuild's artifact. The gates take their build through
  `BUILD=`, a positional argument or the runner's `%MERGED%` placeholders ([VSP-107]: half read `${BUILD:-}`, half `${1:-}`);
  the adapter is one table mapping each gate to how it receives the build. Every row keeps its must-fire controls
  (`docs/project/must_fire_contract.md`), and the runner's verdicts, not exit codes, are the result.
- **Expectations.** The frozen expectation sets under the original's `tests/expected/` are the oracle; the rebuild reads
  them from the pinned checkout and never re-freezes them in place.

### 5.3 Porting a gate (phases 1-4)

A gate is ported when the rebuild's harness version reaches **the same verdict as the original on the same artifacts,
and its declared controls still fire**, on at least one passing and one failing input (a planted defect or the control's
perturbation). The port records the original gate and commit it is proven against. The external suite is retired only
when every gate the rebuild keeps is ported this way.

## 6. The harness (its own, ruled)

The language is Python or Rust, whichever is the more appropriate for each component, the reason recorded with the
choice (§0). Requirements carried from the original's discipline, whatever the language:
- every run fresh by construction (§4); canonical input staging, one implementation; deterministic, with run-to-run
  determinism tested;
- the oracle classes of `docs/project/oracle_classes.md`, each class's comparator with its ground truth ([VSP-19],
  [VSP-37]);
- must-fire controls declared, fired in the log and executable as a mode ([VSP-181]);
- the comparative capture sheets of #291 as a first-class output: a gate states its legs and moments, and every picture is
  proven against what the gate logged (checksum, fields, or the EVENT-PROVEN basis for taps);
- the run record: what each run executed on and what it opened (§4), from which staleness and re-run selection follow.

## 7. The agent swarm (kept unless demonstrably inadequate)

The original's structure is adopted: the orchestrator (Opus 5.5 at effort High); `measurer` and `reader` workers driven
by specs (`docs/project/worker_spec.md`); the pinned `rule-checker` before an action, with planted known violations
(`docs/project/rule_checker.md`, [VSP-183], [VSP-184]); the agent hooks (no invisible jobs, the green guard, edit locks;
`docs/project/agent_architecture_scope.md`); forks for parallel work. A change to any of these needs a measured
inadequacy, recorded as a ticket with the evidence.

## 8. Documentation (kept unless a better alternative emerges)

The original's structure is adopted (`docs/README.md`): `CLAUDE.md` as the law with rule-plus-pointer; `STATE.md`,
`HANDOFF.md` and `docs/NEXT_SESSION.md` as budgeted live documents; `docs/game/`, `docs/platform/`, `docs/project/` by the
one question ([VSP-12]); shapes in `docs/doc_shape.tsv`; `*_HISTORY.md` archives with generated indexes; generated
indexes regenerated in the commit that changes them; tickets with strict sources of truth ([VSP-182]); skills as the
agent-facing reminders. **What the rebuild imports rather than re-derives:** `docs/game/` and `docs/platform/` (facts
about the game and the board, true whatever is built) are carried over with their provenance and their checks
(`tools/checkdocs_rom.py`), not rewritten; `docs/project/` is rewritten for the rebuild's own tooling.

## 9. The repository

[`DefinitelyFrenchName/VampireSaved-Rebuilt`](https://github.com/DefinitelyFrenchName/VampireSaved-Rebuilt), public (the maintainer's answers, §0). It holds
tools, patches against named reference dumps, documentation and authored assets only ([VSP-8]). Its first commit is this
spec, `docs/tests_inventory.tsv` and `tools/classify_tests.py`. No open ticket of the original moves here (§0): the
rebuild's tickets are its own, and the only ones of the original that bear on it are about the game, whose facts come
through the documentation.

## 10. Open questions

None open: v0.1's four were answered by the maintainer on 2026-10-18 (§0).
