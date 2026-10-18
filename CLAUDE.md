# CLAUDE.md — Vampire Saved Rebuilt

**v1.0 (2026-10-18): VALIDATED by the maintainer** (v0.1 with the maintainer's own edits). This file governs how Claude Code works in this repository.
Read it fully at the start of every session, then `SPEC.md` (until `STATE.md` exists, the spec is the plan of record).

**Where it comes from.** It is the original project's `CLAUDE.md` (`DefinitelyFrenchName/VampireSaved` at `6dee2be7`)
with everything specific to the original's IMPLEMENTATION removed and only its rules and principles kept, plus the standing principles of that project's rulings (`STATE.md` "Standing rulings", `DECISIONS_HISTORY.md`) that bind any implementation. Each rule is `**[VSR-N]**` and names the original rule it comes from (`was [VSP-N]`); the original's anchor holds the rule's reasons and the incident that taught it, until this repository re-homes them in its own `docs/`.
The mission (§1) and the law (§2) keep the original's wording except where it named the original's own files.

## 1. Mission and prime constraint

Produce a modified `vsav` romset in which all 18 series characters (the 15+1 of Vampire Savior plus Donovan, Huitzil/Phobos, and Pyron ported from `vsav2`) are selectable, while vanilla Vampire Savior behavior remains **bit-identical** for all original content. Same scope and the same accuracy bar as the original; NOT the same implementation (`SPEC.md` §1, §4): a choice the original made is re-decided here, with its reason recorded.

**[VSR-1] THE SUPERSET INVARIANT (never violate, never weaken):** Any match, menu path, or attract sequence that does not involve the three new characters MUST produce frame-identical RAM state to vanilla `vsav` under identical inputs. This is not a quality goal; it is the definition of the project. A change that improves the new characters but perturbs one byte of legacy behavior is a failed change.

## 2. Non-negotiable rules

1. **[VSR-2] Emulator cores are never modified, except inside a ratified profile.** Only cartridge/driver *descriptors* (ROM region sizes, load maps, gfx decode lengths) may change. If a task appears to require touching CPU, sprite, timing or sound emulation code, stop and write the problem up instead. The one bounded  exception is a PROFILE: every change in it is bounded and declarative; **profile-gated** by a flag set from a new driver entry, so stock sets and every other game are untouched by construction; subject to the **emulator superset invariant** (the patched binary running the stock unmodified set reproduces the frozen vanilla expectations bit-for-bit, enforced as a battery gate); mirrored in a second emulator where practical; and ratified by the maintainer per profile version. The profile's spec has ONE copy, in `docs/`, never restated here. Anything outside a ratified profile is stop-and-escalate.
2. **[VSR-3] No untested change survives a session.** Every change, however trivial, is validated through the harness before it is committed. "It should be equivalent" is not a test result.
3. **[VSR-4] No hand-edited binaries.** All ROM modifications are produced by the build pipeline from
   source data and sources in the repository; the repository reproduces the output set from pristine inputs at any
   commit, and a gate proves it.
4. **[VSR-5] Provenance is tracked per region.** Every byte range of the output is tagged with its origin: `VSAV` (untouched), `VS2`, `GEN` (generated) or `NEW` (authored). The provenance atlas is updated in the same commit as the change that affects it.
5. **[VSR-6] Behavioral values live in documented tables, not in code.** Any tunable that defines how the ported characters play (damage, timings, meter rules, variant selection) is in the documented table format so the community can review and adjust it without re-engineering.
6. **[VSR-7] A failing regression halts forward work.** If the regression suite diverges, fixing that divergence is the only task until green.
7. **[VSR-8] No copyrighted ROM content in the repository or in any distributed artifact.** The repository holds tools, patches against named reference dumps, documentation and authored assets only. Reference romsets live outside the tree (`ROMDIR`) and are never committed, quoted at length or uploaded. Rendered frames are outside this rule : golden pictures are derived work produced by our own pipeline. ROM BYTES remain forbidden in every form.

## 3. Environment

- **[VSR-9]** MAME and FBNeo are the instruments; they are built from pinned, recorded sources, the reference binary first, and an instrument is never moved without re-proving what it measures (the `mame-fbneo-instruments` skill).
- **[VSR-10]** Every analysis tool is rerunnable, takes the ROM path as an argument and prints the SHA-1 of what it read.
- **[VSR-11]**  The harness is written in**Python or Rust, whichever is the more appropriate for each component**, the reason recorded with the choice. (`SPEC.md` §4 proposes shell only where a process must be launched; that part is a proposal, not a ruling.)

## 4. Verification protocol (the harness is the project's spine)

- **[VSR-12] Oracle replays.** Input scripts (per-frame joystick and button state) run on vanilla and on the hacked set, checksumming work RAM every frame; legacy-content replays must match for the whole script. The first divergent frame plus its RAM diff is the standard bug report.
- **[VSR-13] Which emulator runs which oracle.** MAME is the per-frame whole-corpus legacy oracle. FBNeo carries the emulator superset invariant on the pristine set, the inertness of a profile build, and a sampled hacked-vs-vanilla legacy check. A measured FBNeo-vs-MAME disagreement on legacy content opens a ticket.
- **[VSR-14] Comparison classes are a ratified vocabulary.** The class spec has one copy in `docs/` (imported from the original's `oracle_classes.md`). Every non-exact class is mechanism-attributed and its expectation FROZEN as a measured inventory, never a window: a difference inside a window but outside the frozen inventory FAILS as growth. A replay is never reclassified to a looser class without a new measured mechanism and the maintainer's sign-off.
- **[VSR-15] The standing watch:** if flickers grow beyond the frozen inventory or divergences turn systematic, stop and root-cause; that pattern is a deeper issue, never tolerance noise. Whole-RAM frame-exact remains the standard for vanilla oracles, run-to-run determinism and hook-free builds.
- **[VSR-16] Dual-emulator agreement for new content.** Where no vanilla oracle exists, the same replay runs on both patched emulators and they must agree on the MAPPED gameplay state at sync anchors (match start, round transitions: character ids, HP, positions, timer, meter and the other mapped RAM fields), not on whole-RAM checksums frame by frame. Whole-RAM frame-exact remains the standard within each emulator.
- **[VSR-17] Every new capability adds replays.** Minimum coverage for a ported character: vs each of the 18 (both sides), each stage, Dark Force activation and expiry, the life-marker transition, timeout, throw and tech situations, pursuit attacks, Shadow/Marionette interaction once enabled.
- **[VSR-18] Edge-case bias:** prefer pathological inputs (simultaneous presses, frame-1 actions, corner interactions, KO-frame events). Bugs live at state transitions, not in the middle of matches.
- **[VSR-19] FIELD REPORTS ARE RECORDINGS.** Every reproducible crash or misbehaviour a human can produce is captured FIRST as a hand-played recording, BEFORE any mechanism theory, tracked in the repository and named for the build it was played on; every tracked recording is replayed on the current build at every freeze, and the first exception fails.
- **[VSR-20] THE PERSISTENT SUITE DOCTRINE:** every in-emulator test run during development —measurement, probe or verification — is captured as a scripted, rerunnable case before the session ends. No throwaway manual checks. The suite only grows.
- **[VSR-21] Verdict logic is itself tested.** A test's classification code (HIT/BLOCK/TECH, …) is validated against known ground-truth scenarios, in BOTH directions, before its verdicts are trusted; a gate born against a live defect has never exercised PASS, so its first green is read by its printed values, not its verdict word.
- **[VSR-22] The must-fire contract:** a gate's controls are DECLARED with the gate, FIRED at run time (the gate's log shows each one firing) and EXECUTABLE as a mode in which the gate must FAIL.
- **[VSR-23] One command validates any build variant;** the runner identifies the build under test and selects its expectations, and the engine-invariant rule locks for vanilla behaviour run on every build.
- **[VSR-24] Saved states are tagged to the exact build they were made on**, and the procedure to regenerate each is documented.
- **[VSR-25] A red gate is a question:** first establish which side's expectation rests on a measurement. Never re-freeze an expectation to make a gate green.
- **[VSR-26] Cross-game comparisons run at a matched speed level and a pinned RNG.**
- **[VSR-27] Release scope:** every test whose subject is the released artifact runs at release; anything red or skipped is a hard fail unless approved at release time.

## 5. Working style

- **[VSR-28] Sessions begin by reading `STATE.md` and end by updating it.** `STATE.md` is the single source of truth for progress; never rely on chat memory. It holds the latest session group and the standing sections; older session records move VERBATIM to `STATE_HISTORY.md`and `STATE_HISTORY.md` begins with an index to allow for immediate lookup of a given session. **An open list holds only what is open:** "Decisions pending" and the next session's start list never carry a closed item. **The close ends with a push:** when every check of the close is green and nothing is pending, push `main`; a red, a skip or an unresolved item leaves the commits local and the close says so.
- **[VSR-29] Tickets have strict sources of truth.** Every bug, cosmetic item and evolution is a ticket; the list is one file in the tree, the story its GitHub issue, the facts the subject documents. Live documents name a ticket by number and never restate its status. Without GitHub, the tree answers four questions about every ticket: what it was and how to reproduce it, what was decided, what was learned, what went wrong. Closed means nothing is left to do.
- **[VSR-30] A session key names one sitting and is never renamed, renumbered or tidied:** it is the archive's lookup key. Sessions, milestones and freeze marks are three namespaces, never conflated.
- **[VSR-31] Address notation:** 68k addresses as `PRG:0x0F1234` (program ROM offset) or `CPU:$0F1234` (address space); tiles as `GFX:tile 0x1A2B3`; RAM as `RAM:$FF8000`. Never bare hex without a namespace.
- **[VSR-32] Documentation taxonomy: file by the FACT.** `docs/` is divided by one question — would this still be true if the roster hack were abandoned tomorrow? — into `docs/game/`, `docs/platform/` and `docs/project/`. Every hand-written document declares its shape; chronology lives in `<name>_history.md` twins; a generated index is regenerated in the commit that changes what it indexes, never hand-edited. A gotcha is written the moment it is paid for. An undocumented discovery is a discovery we will pay for twice.
- **[VSR-33] RETRACTION DISCIPLINE: when a claim changes, search for the CLAIM** — its wording and its paraphrases, across the whole repository including the archives — not for the files you remember writing it in. Fix the header and the summary line first, re-search and show the empty result, and keep the superseded analysis marked RETRACTED with what replaced it. Status headers track reality; historical entries are not rewritten.
- **[VSR-34] BUG ARCHAEOLOGY FIRST:** before fixing a bug, check whether it was fixed once already (the history, the archives, searched through their indexes); find the build where it was last known good and diff it against its predecessor; if the record is ambiguous, ask the maintainer before measuring.
- **[VSR-35] Anti-hyperfocus checkpoint:** at natural boundaries — a finding confirmed, a suite green, ~20 tool iterations on one problem — stop unprompted: update the documents, capture the scratch tests into the suite if applicable, then reassess the approach, check `STATE.md` for drift. The human should never have to be the one to say "step back and document."
- **[VSR-36] Build conventions:** a builder takes `(src, out)` so it chains onto any input; every tunable is a builder option, never a hex edit; a bundle chains builders and is diffed ONCE against clean, never built by chaining standalone binary patches; every shipped build carries a visible in-game version string, and every build's SHA-1 goes in the registry.
- **[VSR-37] A decision with gameplay consequences (anything a player could feel) is not Claude's:** record it under "Decisions pending" with options and a recommendation, and continue on unblocked work. A ruling leaves the pending list in the commit that records it.
- **[VSR-38] Diff-driven reverse engineering:** the three romsets are three official builds of one engine; before free-form disassembly of any subsystem, check what the three-way diff says about it.
- **[VSR-39] Don't assume; measure first; ask if  necessary.** The failure is ASSUMING; asking stays right when a measurement cannot settle the question.
- **[VSR-40] Vanilla wins ties:** when another game or version and arcade vsav differ and both would work, take vanilla. The test is: does keeping vanilla still let the feature work?
- **[VSR-41] Cosmetic is optional:** competitive 2P versus is the focus; cosmetic and single-player-only surfaces are nice-to-have.
- **[VSR-42] Community/external data: measurement is king.** A perfect match or a constant offset validates ours; an inconsistent pattern means re-check OUR measurement first.
- **[VSR-43] Captures before conclusions:** a behavioural claim about feel gets a capture first.
- **[VSR-44] Performance:** under one frame of added cost is good, under two frames needs validation, two or more is unacceptable; the COMBINED overhead of all fixes never adds a frame of lag.
- **[VSR-45] Commit only at a boundary that needs one**, and only a tree that a strict GREEN tier was run on (the staged tree, on a snapshot). A runner's exit status is not its verdict: read the verdict line.

## 6. The agent swarm (kept unless demonstrably inadequate)

- **[VSR-46] The orchestrator is Opus at effort High;** a sitting on another model says so at its opener. **No swarm model runs at max effort, ever**.
- **[VSR-47] A figure that will be quoted is produced by a worker spec:** a `measurer` runs numbered commands exactly as written and returns every figure with the command that produced it; a `reader` returns each fact as a verbatim quote with its path and line.
- **[VSR-48] An independent rule-checker runs before an action** (a freeze, a build, an expectation, a recommendation, a ticket closure), when the action's work is done, never held for the close. It is context-free and pinned, reads only the packet's artifacts, and runs beside a planted known violation that must be caught. A VIOLATED is resolved question by question, in writing, before the action proceeds.
- **[VSR-49] Deterministic hooks hard-block:** no invisible background jobs, the  green guard on commits, edit locks on the hooks themselves and their settings. A block binds the task at fault, never the session.
- **[VSR-50]** (`SPEC.md` §7) **A change to the swarm needs a measured inadequacy**, recorded as a ticket with the evidence.

## 7. What the human provides

Vision and final say on all gameplay-feel decisions; playtesting (structured reports welcome as replay scripts when possible); base resources (reference dumps, community docs); community liaison for the VS2-vs-VH2 variant policy.
Claude does the code archaeology, tooling, patch engineering, and testing. Neither side skips the harness.
