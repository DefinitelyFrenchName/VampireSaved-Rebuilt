# SPEC — Vampire Saved Rebuilt

**Status: DRAFT v0.2 (2026-10-18): v0.1 with the maintainer's answers to its open questions (§0). Nothing here is built.** The ticket is
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
| 0 (in the original, before phase 1; gameplay values first) | the measured facts extracted from `build/manifest/*.toml` and the generators into documented tables with provenance, until the rule-5 census reads them as in-table | the census; the original's builds reproduce byte-for-byte from the tables (`tests/test_m3a_reproducible.sh`) |
| 1 | the romset pipeline (extract, reconcile, generate, pack) and the FBNeo and MAME WIDE profiles, in the rebuild's repository | the external acceptance suite (§5, classes E1 and the F gates): the legacy oracle bit-identical to vanilla on every replay of the corpus under its frozen class; tenant content equal to the original's frozen expectations and to native vs2 on the parity gates |
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
| F | 65 | a gate whose subject is pristine vsavj/vsav2/vhunt2 or the emulators as instruments (no build, no manifest) | runs unchanged: it locks facts the rebuild's documentation inherits |
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
