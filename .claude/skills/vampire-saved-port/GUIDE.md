# Vampire Saved Rebuilt — the port's own discipline (level 2, this project only) — the guide

The human rendition of `SKILL.md` in this directory: the same rules, the same IDs, each followed by the reason it exists —
the incident that taught it in the original (`DefinitelyFrenchName/VampireSaved` at `6dee2be7`). An incident about the
game, the board, the instruments or a principle is quoted from the original's GUIDE; one that was all about the original's
implementation is shortened to one sentence naming its lesson. Written for the rebuild, not generated (the original's
`tools/gen_skill_guide.py` is to be rebuilt with the anchor lock). Inside a quote, `[VSP-N]` is the original's ID — the
rule that carries it ends `(was [VSP-N])` — and session tags, gate names and paths are the original's.

**Anchors.** Rules whose anchor is in `docs/game/` or `docs/platform/` resolve once those are imported; rules anchored in the original's `docs/project/`, `HANDOFF.md` or `STATE.md` point at the original (`DefinitelyFrenchName/VampireSaved` at `6dee2be7`) until this repository re-homes them. The lock (the original's `tools/checkskills.py`) is to be rebuilt; until then nothing checks the anchors.

## D.1 The law, by citation (CLAUDE.md)

**[VSR-1]** The superset invariant (was [VSP-1]).

**[VSR-2]** Cores unmodified outside a ratified profile (Rule 1 v2) (was [VSP-2]).

> **Why:** The original's rule once named sprite code as stop-and-escalate while its tree carried a modified `cps_obj.cpp` under a ratification the rule never mentioned (corrected 14z-91, #35): the exception is written where the rule is, and the profile's spec has one copy because two copies drift.

**[VSR-3]** No untested change survives a session (was [VSP-3]).

> **Why:** Inherited from the Sailor Moon S project, where systematic in-emulator verification was the difference between working and *shipping*.

**[VSR-4]** No hand-edited binaries (was [VSP-4]).

**[VSR-5]** Provenance per region (was [VSP-5]).

**[VSR-6]** Behavioural values in documented tables (was [VSP-6]).

**[VSR-7]** A failing regression halts forward work (was [VSP-7]).

**[VSR-8]** No ROM bytes, in any form (was [VSP-8]).

> **Why:** Rendered frames are outside the rule by ruling (14z-91, #73), recorded so it is not re-litigated; ROM BYTES stay forbidden in every form, excerpts pasted into documents included.

**[VSR-9]** The reference sets, SHA-1 verified (was [VSP-9]).

**[VSR-10]** Analysis tools print the SHA-1 of what they read (was [VSP-9]).

**[VSR-11]** Python or Rust, per component.

**[VSR-12]** Oracle replays.

**[VSR-13]** Which emulator runs which oracle (was [VSP-24]).

> **Why:** The original accepted and deferred a full FBNeo legacy track: every FBNeo gate is a live A/B by design (no frozen corpus), which is what makes them machine-independent; its revisit point, MiSTer, answered with its own oracles, and the ticket that held the track (#141) was closed `declined` (2026-09-29, maintainer-ruled).

**[VSR-14]** Comparison classes are a ratified vocabulary, frozen as inventories (was [VSP-25], [VSP-26]).

> **Why:** [VSP-25]: the stock and WIDE builds carry DIFFERENT ROSTERS by construction, so every select-reaching replay must differ; inertness is bit-identical up to select entry outside six frozen execution-position offsets (`RAM:$FF055B-$FF055D`, `RAM:$FF7FF3-$FF7FF5`), never outside a window (class v6, amended 2026-09-05). [VSP-26]: the FBNeo-only windows `RAM:$FF0500-$FF05FF` and `RAM:$FF06D0-$FF06EF` are execution POSITION, not state; the expectation is the measured offset inventory (`$FF055B-$FF055D`, `$FF06D1/D4/DB`), and a byte inside a window but outside it FAILS as growth — stop and root-cause, never widen.

**[VSR-15]** The standing watch (was [VSP-31]).

> **Why:** Measured in the original: hooks cost cycles, interrupts land at skewed instruction boundaries in otherwise-vanilla frames, and zero-cycle hooking is impossible on this engine ([VSR-65]).

**[VSR-16]** Dual-emulator agreement for new content (was [VSP-32]).

> **Why:** The emulators traverse identical states on slightly different frame indices after boot, so frame-exact whole-RAM equality is unachievable between codebases; field-level agreement at anchors keeps the intent, since a bug would still have to manifest identically in two unrelated codebases to slip through.

**[VSR-17]** Every new capability adds replays (was [VSP-33]).

**[VSR-18]** The edge-case bias (was [VSP-33]).

> **Why:** The Sailor Moon S experience: bugs live at state transitions, not in the middle of matches.

**[VSR-19]** Field reports are recordings (was [VSP-20]).

> **Why:** 14z-109..111 spent three sessions and two shipped fixes on a rig-derived mechanism that was never the field crash; the first recording found the real one (#99) in an evening, because win-fast rigs never give a CPU opponent's AI time to reach its rarer scripts. A captured-but-unfixed defect is declared as such so the capture cannot rot.

**[VSR-20]** The persistent suite doctrine (was [VSP-18]).

> **Why:** These behavioural tests are the project's most valuable artifact, above unit and integration tests; budget the time.

**[VSR-21]** Verdict logic is itself tested (was [VSP-19]).

> **Why:** The Sailor Moon S project shipped a wrong conclusion ("blockable frame trap") from a verdict bug, not a game bug.

**[VSR-22]** Every gate carries must-fire controls (was [VSP-181]).

> **Why:** The original's contract: a control is declared in the gate's header, fired in its log, and executable as a mode that must reach the gate's own FAIL (exit 0 is LIES, a refusal is a dead mode, a crash is DIED); a declared control that did not fire, a DEAD line, or a firing no header declares is plain FAIL, with no fourth verdict. Each perturbation is written once, called by both the control and the mode, so what the mode proves is what the control claims.

**[VSR-23]** One command validates any build variant.

**[VSR-24]** Saved states tagged to their build.

**[VSR-25]** A red gate is a question.

**[VSR-26]** Cross-game comparisons at matched speed and pinned RNG.

**[VSR-27]** Release scope.

**[VSR-28]** STATE at both ends of a session; open lists hold only what is open; the close ends with a push (was [VSP-17]).

> **Why:** A ruled decision moves VERBATIM to the decisions archive in the commit that records it, leaving a one-line statement under the standing rulings while it still constrains work; archived session records are never rewritten, corrections are marked in place.

**[VSR-29]** Tickets have strict sources of truth (was [VSP-182]).

> **Why:** Rulings are decisions, so they are recorded locally whichever channel gave them; what was learned and what went wrong live in a live document, never only in an archive. In the original, a ticket done but held open until a release ships it carries a comment saying so (ruled 2026-10-08).

**[VSR-30]** A session key is never renamed (was [VSP-162]).

> **Why:** Hundreds of pointers into the original's archive live in gate headers, tag messages, patch notes, gotcha datelines and the ledger; a renamed key breaks every one silently, and a citation that cannot resolve cannot be corrected ([VSR-33]).

**[VSR-31]** Address notation (was [VSP-11]).

**[VSR-32]** File by the FACT (was [VSP-12]).

**[VSR-33]** Retraction discipline (was [VSP-13]).

> **Why:** A finding propagates into section HEADERS, summary lines, registry rows, gate comments, indexes and the next-session notes, and the copies outlive the correction: the original's `engine_internals.md` once carried "the 214+P explosion is NOT a tile-inventory defect" as a HEADER above the subsection proving it was (14z-71).

**[VSR-34]** Bug archaeology first (was [VSP-14]).

> **Why:** The maintainer was there and will usually remember; wrong in both directions is expensive.

**[VSR-35]** The anti-hyperfocus checkpoint (was [VSP-15]).

**[VSR-36]** Build conventions (was [VSP-16]).

> **Why:** The Sailor Moon S bank-collision trap came from chaining standalone binary patches; the version string is the playtesters' naked-eye A/B tell.

**[VSR-37]** Gameplay decisions are not Claude's (was [VSP-10]).

> **Why:** A ruling's entry leaves the pending list in the same commit; it is never marked DECIDED in place.

**[VSR-38]** Diff-driven reverse engineering.

**[VSR-39]** Measure first, ask if necessary.

**[VSR-40]** Vanilla wins every universal mechanic; vs2 wins what is character-specific to the vs2-only characters; in doubt, ask (was [VSP-21], re-worded by the maintainer 2026-10-20).

> **Why:** "vsav vanilla is always better when we can." The newcomers' own behaviour has no vanilla to win, so their source game is the reference ([VSR-177]). A console port's choice is evidence of what its designers preferred, not that vanilla is wrong.

**[VSR-41]** Cosmetic is optional.

**[VSR-42]** Community data: measurement is king.

**[VSR-43]** Captures before conclusions.

**[VSR-44]** Performance.

**[VSR-45]** Commit at a boundary, on a strict green tier; the verdict line, not the exit status (was [VSP-176]).

> **Why:** [VSP-176]: in the original a `${VAR:?}` demand after an armed EXIT trap exits 0 on macOS bash 3.2, and a 65-minute Verilator gate recorded `PASS 0s` on four lines of log during the M16 release run; a PASS whose log has no verdict line of the gate's own is a crash until read.

**[VSR-46]** The orchestrator's model; no max effort.

**[VSR-47]** Quoted figures come from worker specs.

**[VSR-48]** The rule-checker before an action, with a plant (was [VSP-183], [VSP-184]).

> **Why:** [VSP-183]: the packet is the decision kind, ONE claim sentence saying what is claimed and what was NOT tested, and the artifacts by path — never a narrative, which hands over the framing — answered by a FRESH agent, never a fork; not at the session end, where the sunk cost already exists. [VSP-184]: the checker's output is reported to the maintainer VERBATIM, never summarised, because paraphrase is where softening happens; a VIOLATED is answered question by question; an answer that blames the instrument names an open ticket; a finding that recurs across packets and sessions is a red until a ticket owns its cause; and a plant that is not caught VOIDS the verdict.

**[VSR-49]** Deterministic hooks hard-block.

**[VSR-50]** A swarm change needs a measured inadequacy.

## D.1b Beside the law — where a classifier looks, and the deadness register

**[VSR-51]** **Where the classifier LOOKS is validated too, and never from our own generator** — before re-targeting an instrument onto a new site, state what the new expectation is ANCHORED to and check the anchor sits outside the artifact under test. Resolving a probe site from the build's own metadata and concluding the question is answerable there is writing the test from the algorithm: we do not get to write that what we coded is indeed what we coded. When the only anchor available is our own build data, the honest options are a control built from the CURRENT source data whose expected answer follows from DESIGN independently of the machinery under test, or dropping the gate — re-pointing at a site merely believed equivalent is neither, and it silently orphans the liveness control that made the old site's zero meaningful. (was [VSP-166])

> **Why** (was [VSP-166], the original's `docs/project/gotchas.md`):
>
> RE-TARGETING AN INSTRUMENT FROM THE BUILD'S OWN METADATA IS WRITING THE TEST FROM THE ALGORITHM — name what the new site's expectation is anchored to, and it must not be the artifact under test (paid: 14z-129)
>
> `audit_type_dispatch_range` probes an `obj_hook` thunk whose address it
> scrapes from the build's own `patch_notes_fragment.md`. 14z-91 DELETED those
> thunks (each walker relocated with its union table at copy+0x2C, only the 23
> caller operands rewritten), so the scrape returns empty and the gate has been
> unrunnable since. The decision recorded in STATE was RE-TARGET or DROP.

**[VSR-52]** **THE DEADNESS REGISTER's rule for a row** — a claim of the form "legacy never reaches this, so we may reuse it" is measured by ABSENCE, the weakest evidence accepted here, so it needs a POSITIVE CONTROL on the same instrument and leg, a named guard, and a stated fallback if wrong. Prefer designs where being wrong is SAFE AND LOUD (the type-6 fallback held when its deadness claim turned out false) over designs that are merely well-measured. (was [VSP-22])

> **Why** (was [VSP-22], the original's `STATE.md`):
>
> Rules for adding a row: the claim must be measured with a POSITIVE CONTROL
> on the same instrument and leg (a blind instrument and a real zero look
> identical — paid for three times in 14z-71); it must name its guard; and
> it must say what happens if the claim is wrong. Prefer designs where being
> wrong is *safe and loud* over designs that are merely well-measured.

**[VSR-53]** **The register is the FIRST place to look** for any unexplained regression in vanilla assets, engine behaviour or rendering — before anything else is suspected; its withdrawn rows show the claim class does fail. (was [VSP-23])

> **Why** (was [VSP-23], the original's `STATE.md`):
>
> Every claim of the form **"legacy never reaches this, so we may reuse
> it"**. Each is measured by ABSENCE, which is the weakest kind of evidence
> we accept, so each is listed here with its guard. **These are the FIRST
> PLACES TO CHECK for any unexplained regression in vanilla assets, engine
> behaviour or rendering** — before anything else is suspected.

## D.2 Oracles and frozen expectations — what a class is, and what may never loosen one

Which emulator runs which oracle, the class vocabulary, dual-track inertness, the FBNeo-only phase inventories, the standing watch, dual-emulator agreement and the test matrix are CLAUDE.md law: [VSR-13]..[VSR-18] (D.1).

**[VSR-54]** **Hooked-build legacy comparison is live RAM under exactly the named masks (the class spec of record, imported from the original's `oracle_classes.md` v1/v2)** — the dead-stack window `RAM:$FF7F00-$FF7FFF` and the QSound latch `RAM:$FF043C`; on that basis the classes are exact (default), flicker-tolerated (isolated ≤2-frame divergences, ≥60-frame re-convergence, ≤8 divergent frames, by a ground-truthed checker), and frozen first-divergence constant. A replay may not be reclassified to a looser class without a new measured mechanism AND maintainer sign-off. (was [VSP-27])

> **Why** (was [VSP-27], the original's `docs/project/oracle_classes.md`):
>
> **Hooked-build legacy comparison** (v1 2026-07-25, v2
> 2026-07-27, both maintainer-approved): for builds carrying engine hooks
> (code the vanilla game executes routed through added instructions), the
> legacy oracle compares **live RAM**: all work RAM except two named windows,
> both documented in `docs/game/atlas/ram.md` — the dead-stack window
> `RAM:$FF7F00-$FF7FFF` (below resting SP at the frame-done sample point) and
> the QSound handshake latch `RAM:$FF043C` (one-frame phase). On that masked
> basis, per-replay comparison classes: **exact** by default;
> **flicker-tolerated** where measurement shows isolated ≤2-frame
> divergences that fully re-converge (≥60 frames) with ≤8 divergent frames
> total (`tools/compare_flicker.py`, ground-truth tested — the
> input-accept/spawn-boundary phase artifact); **frozen first-divergence
> constant** where a masked byte's phase provably propagates into live state
> on a path with no gameplay surface (test mode reading the sound latch).

**[VSR-55]** **The bounded re-convergent window (class v3) needs all four, frozen per replay** — one CONTIGUOUS divergent run, a fixed ONSET, full RE-CONVERGENCE to bit-identical, and match state untouched; introduced for the select wheel's three added cells and STRICTER than the first-divergence constant. Its checker is ground-truthed like every comparator ([VSR-61]). (was [VSP-28])

> **Why** (was [VSP-28], the original's `docs/project/oracle_classes.md`):
>
> **v3 (2026-08-05, maintainer-approved): the bounded
> re-convergent window** — for a screen the roster work deliberately alters.
> A replay may sit in this class only when all four hold, each frozen per
> replay: a single CONTIGUOUS divergent run; a fixed ONSET frame; full
> RE-CONVERGENCE to bit-identical; and **match state untouched**. Introduced
> for the select screen, whose wheel gains three cells for the roster;
> ratified on five replays — onset 890 in every one, one run each, windows
> ending 1051/1622/1802/1882/1622, 2469-10498 bit-identical frames after
> (mechanism: select-screen init caches the record pointer the wheel extension
> repoints, `docs/GOTCHAS.md` class 4). STRICTER than the first-divergence
> constant, which never re-converges — a narrower licence for one screen.
> Checker `tools/compare_window.py`, ground truth `tests/test_compare_window.sh`.

**[VSR-56]** **Composite (class v4) is the strict CONJUNCTION of flicker and window and adds NO tolerance** — every divergent run accounted for by name, the flicker set equal to its frozen inventory, the window list exact, full re-convergence; a bit-identical pair FAILS it. (was [VSP-29])

> **Why** (was [VSP-29], the original's `docs/project/oracle_classes.md`):
>
> **v4 (2026-08-06, maintainer-ratified): composite** — the
> strict CONJUNCTION of flicker-tolerated and bounded re-convergent window,
> for replays that exhibit both. It adds NO tolerance: every divergent run
> must be accounted for by name, the flicker set must match its frozen
> inventory exactly, the window list must match exactly, and the run must
> fully re-converge; it permits nothing that either component permits alone,
> and a bit-identical pair FAILS it. On a build carrying BOTH engine hooks and
> the extended wheel, every select-reaching legacy replay measures as "the
> frozen hook-flicker inventory + one bounded window per select-screen ENTRY"
> (seven replays at 14z-61; a challenger join re-enters the screen and gives
> TWO windows; a mid-attract start moves the onset to 3190). Checker
> `tools/compare_composite.py`, ground truth `tests/test_compare_composite.sh`.

**[VSR-57]** **The ≥60-frame rule is INTRA-MECHANISM (class v5, maintainer-ruled)** — it governs the tail after the last divergence of ONE mechanism and does not bind across the gap between two separately attributed ones; the cross-mechanism alternative stays default-off and the two named palette-fade exemptions are recorded against the day it is turned on. A third exemption means measure the real minimum, not lengthen the list. (was [VSP-30])

> **Why** (was [VSP-30], the original's `docs/project/oracle_classes.md`):
>
> **v5 (2026-08-16, maintainer-ruled): THE ≥60 RULE IS
> INTRA-MECHANISM.** The 60-frame non-propagation figure is a
> single-mechanism proof: it governs the RE-CONVERGENCE TAIL after the last
> divergence, and it does NOT bind across the gap between two SEPARATELY
> ATTRIBUTED mechanisms. So a flicker run followed by a window onset, or one
> flicker run followed by another, is not constrained by it.
> `--min-converge-flicker` in `tools/compare_composite.py` implements the
> alternative and stays DEFAULT-OFF, opted into by no spec (nothing measured
> suggests the mechanisms interact, and applying it across a boundary would
> have redded 99 of 121 composite specs when the select-window onset moved
> 890 -> 889 at 14z-63). **Two NAMED EXEMPTIONS are recorded against the day
> the flag is ever turned on**, both 56 frames apart (55 identical between)
> and both the palette-fade staging family: `donovan-m7/22_don_dualmash`
> (11862/11918) and `huitzil-m15/26_don_arcade_mash` (8744/8800). A third
> would mean the gap is a property of the mechanism, and the right response
> is to measure the real minimum, not to lengthen this list. (No current spec
> exercises the boundary: the flicker that opened the question, frame 829,
> was the obj_hook cycle-skew removed at 14z-91.)

**[VSR-58]** **A masked window is a BASIS, not a flag** — a mask removes bytes from the checksummed stream, so adding a window changes every frame's checksum: the vanilla masked expectations are REGENERATED under the new mask as a new, named basis, every masked expectation is re-based onto it, and every consumer that names the old basis or the old mask set is updated. (was [VSP-34])

> **Why** (was [VSP-34], the original's `docs/project/gotchas.md`): Adding a fourth window to the original's mask without regenerating the vanilla basis under it cost one red battery and a triage session (14z-88): the mask is part of what the expectation measures.

**[VSR-59]** **Palette CONTENT in a fade's row set is CYCLE-relevant** — data-only is not cycle-neutral; the select→VS fade runs at the VBL edge and a recoloured processed row cost a legacy pairing one main-loop iteration, never re-converging. Before moving or recolouring any select palette row, run the legacy pairings against vanilla (not just the masked set) and attribute every moved self-frozen expectation before re-freezing. (was [VSP-35])

> **Why** (was [VSP-35], the original's `docs/project/gotchas.md`): A palette-ROW move (the 14z-87b medallion 0x1A -> 0x1D) is also a staging-slot move (`RAM:$FF3F02` + row*0x20), and a different palette in a processed row moved one legacy pairing's main loop across a VBL (replay 38: one iteration lost, whole-RAM never re-converging against vanilla) while every masked legacy class stayed frozen; the same sweep found the class already present on reverted builds, so it is not only a rule for future row moves (14z-88, 14z-89).

**[VSR-60]** **A self-frozen expectation cannot see a legacy regression** — it answers "did this build change since I froze it", and re-freezing makes any behaviour correct by definition; only an expectation against the frozen VANILLA basis compares against vanilla. Classify replays by MEASUREMENT (the `+0x60` hitbox-base signature, the distinct-value sequence, not a frame-indexed trajectory), never by filename or authoring intent; a legacy pairing guarded only by a self-frozen expectation fails a gate. (was [VSP-36])

> **Why** (was [VSP-36], the original's `docs/project/gotchas.md`):
>
> A self-frozen `.sha1` cannot see a legacy regression — and a replay's FILENAME does not tell you what it loads (14z-88 paid it, 14z-89 measured the extent)
>
> `run_suite.sh`'s default expectation kind is `.sha1`: the whole-log
> checksum of the build's OWN earlier run. It answers "did this build
> change since I froze it", which is a determinism/change detector — and
> it is structurally incapable of answering the superset question, because
> re-freezing makes any behaviour correct by definition. Only a `.masked`
> spec compares against the frozen VANILLA basis.

**[VSR-61]** **A comparator's own ground-truth test can RATIFY a deviation from the ratified text** — three artifacts agreeing with each other looks like validation; check the comparator against the governing spec's own wording (CLAUDE.md, the class spec), and scope any "unmeasurable" claim to the instrument that governs it (19 flicker specs, tails a `wc -l` away). (was [VSP-37])

> **Why** (was [VSP-37], the original's `docs/project/gotchas.md`):
>
> A comparator's own ground-truth test can RATIFY a deviation from the governing spec (paid: 14z-95, GitHub #52)
>
> `tools/compare_flicker.py` exempted the LAST divergent stretch from the
> `>=60` re-convergence requirement entirely. CLAUDE.md §4 v2 has no
> end-of-log clause — but the code, its docstring ("end of log ok") and
> `tests/test_compare_flicker.sh` (`ok: end-of-log flicker -> FLICKER (no
> converge window needed)`) all agreed **with each other**. Three artifacts
> agreeing looks exactly like a validated behaviour, and CLAUDE.md §4's
> "verdict logic is itself tested" is satisfied on its face.

**[VSR-62]** **Moving a frozen ONSET frame can silently cross a verification-class boundary** — an onset shift of one frame re-dated ~30 composite specs into a stricter class; re-classify by measurement when an onset moves, never by editing the number. (was [VSP-38])

> **Why** (was [VSP-38], the original's `docs/project/gotchas.md`):
>
> Moving a frozen ONSET frame can silently cross a verification-class boundary (paid: 14z-90, GitHub issue #4)
>
> The §4 v3 `window` class freezes an onset frame; the §4 v2 `flicker`
> class requires >=60 identical frames of re-convergence. On the current
> builds every composite legacy replay is "hook flicker at 829, then the
> select window". When the select-wheel work moved the frozen onset from
> 890 to 889 (14z-63), the gap between the flicker frame and the window
> onset went from exactly 60 to 59 — i.e. a one-frame content change
> stepped across the numeric threshold of a DIFFERENT class's rule, in 94
> frozen specs at once, with nothing in the tree asserting either way.
> Nobody noticed because no checker compared runs to each other; the
> composite checker only measures re-convergence after the LAST run.
> Whether >=60 binds across a flicker->window boundary at all is a
> class-definition question (two mechanisms, separately attributed), and
> it is open with the maintainer. The lesson is the general one: an onset
> or tolerance constant is not a private number — check what OTHER frozen
> rule sits within a few frames of it before moving it.

**[VSR-63]** **A hook on a hot shared path can flip a frame-boundary parity PERMANENTLY** — flicker's evil twin: a marginal same-frame multi-writer field locked to the other side of a VBL from added cycles. Before thunking a site, census its CALLER SET across all screens; review late-replay tails, not just known windows; treat a one-frame flicker in the inventory as a tripwire for added cycles. (was [VSP-39])

> **Why** (was [VSP-39], the original's `docs/project/gotchas.md`): An added hook's cycles moved a field written twice in one frame to the other side of a VBL for good, which reads as a divergence that never re-converges, not as flicker (14z-64).

**[VSR-64]** **Build in one step, measure in another — never in one command** — a chained rebuild+check gave two contradictory verdicts on one image and one of them was committed as a finding. Re-run before believing a gate that contradicts a previous green; if the text you are writing disagrees with the last tool output, stop. (was [VSP-40])

> **Why** (was [VSP-40], the original's `docs/project/gotchas.md`):
>
> Never chain a legacy measurement onto a build in one step — it produced a WRONG COMMIT (paid: 14z-74)
>
> Running a rebuild and then the legacy check inside ONE command block gave a
> false FAIL twice in a row: once on a build carrying `port_param32` (which I
> then recorded as "breaks legacy" and refused) and once on a build that did
> NOT carry it. The second false failure is what exposed the first, because
> that same build had passed the identical check minutes earlier.

**[VSR-65]** **Engine hooks break whole-RAM comparison BY CONSTRUCTION** — a hook on a path vanilla executes costs cycles, interrupts land at skewed boundaries, and dead-stack ghosts plus a one-frame latch phase appear on otherwise-vanilla content; the ghost-clean topology (patch only the `movea/moveq` to `jmp thunk`, keep the vanilla `jsr` at its address) removes the return-address source and nothing removes the skew — zero-cycle extension is impossible here. (was [VSP-41])

> **Why** (was [VSP-41], the original's `docs/project/gotchas.md`):
>
> Engine hooks on hot paths break whole-RAM legacy comparison — by construction (paid: 2026-07-25 session 7, ~2h)
>
> Any hook on a path vanilla executes (the secondary-object dispatch runs for
> every object every frame) adds CPU cycles. Two measured consequences on
> otherwise-vanilla content, both invisible to gameplay:
> 1. **Dead-stack ghosts:** interrupts land at skewed instruction boundaries;
>    the handler's exception frame + register saves write the same stack
>    addresses with different VALUES (e.g. a mid-frame work pointer that has
>    advanced further). After return these bytes sit below resting SP
>    ($FF8000 at frame-done) — dead, but inside the whole-RAM checksum.
>    Observed window: `RAM:$FF7F00-$FF7FFF`.
> 2. **Sound-handshake phase:** the 68k↔QSound latch byte `RAM:$FF043C`
>    (values 04/08) can phase-shift by one frame. (This once read "the same
>    mechanism as the `-debug` GOTCHA's $FF1CF0 latch"; that latch's shift was a
>    frame_done-counting clock, not a scheduler effect — [MFI-2], corrected 14z-196.)
> With BOTH masked (`MASK_RANGES="043c-043d,7f00-8000"` on replay.lua), the
> patched stage-4 build is bit-identical to vanilla for the full 02 replay.
> Note the dispatch pump also runs for MENU-time objects (cursor sparkles,
> UI effects): ghost divergence starts at frame ~470 even in the pick
> replay, long before any match — unmasked divergence constants measured on
> hook-free stage builds (2886, 1080, 4278) are void on hooked builds;
> their masked (live-state) equivalents still hold.
> A jsr-thunk hook additionally pushes a DIFFERENT return address than the
> vanilla site — the ghost-clean topology (patch only the movea/moveq to
> `jmp thunk`, keep the vanilla `jsr (A0)` at its original address, thunk
> jumps back to it) eliminates that source; the interrupt-skew ghosts remain.
> Zero-cycle table extension was investigated and is IMPOSSIBLE here: the
> brief-format dispatch reaches only its inline table, and the code following
> both tables is hot engine code with short branches — not relocatable
> cycle-exactly. RESOLVED 2026-07-25 (maintainer-approved CLAUDE.md §4
> … *(continues in the original's document)*

**[VSR-66]** **GFX and coordinate data are INVISIBLE to every RAM-basis gate** — tile ROM content, scroll/OBJ byte sharing, and ROM→OBJ coordinate lists never transit work RAM, while cached list POINTERS do; a pixel gate detects the first class and the masked gate the last, and it takes BOTH to make pool surgery safe. Never change a host record's cptr; never write pool bytes another consumer shares. (was [VSP-42])

> **Why** (was [VSP-42], the original's `docs/project/gotchas.md`):
>
> GFX and coordinate data are INVISIBLE to every RAM-basis gate
>
> Playtest round 16: the overlay build's tile placements corrupted the
> title screen, select screen and speed menus — and the full masked
> legacy battery stayed green, twice. Three distinct blind spots, now
> covered by the pixel gate (tests/test_gfx_menus.sh, wired into
> test_m2b_stage6.sh):
> 1. TILE ROM CONTENT: work-RAM checksums never see gfx ROM bytes. Any
>    wrong placement renders garbage with perfect RAM.
> 2. SCROLL/OBJ BYTE SHARING: CPS-2 scroll1/2/3 layers decode THE SAME
>    ROM bytes as OBJ tiles at different granularities. An "OBJ-dead"
>    position proves nothing about the scroll tiles backed by those
>    bytes — the overlay's dead-Jedah OBJ pool trashed menu tilemap art.
>    A placement pool must be BYTE-dead for every consumer, not
>    index-dead for one decoder. (The proven-safe classes so far: bytes
>    of art the port itself replaced, and 0xFF padding runs.)
> 3. COORDINATE LISTS flow ROM -> OBJ RAM at draw time, never through
>    work RAM. select_port's in-place list write shifted the speed-menu
>    TURBO/AUTO text 8px for seven shipped builds: Jedah's 1-pair
>    name-banner list [0x32A196,0x32A19A) IS the speed-menu record's
>    first coordinate pair — the pool nests lists inside lists.
> 4. ...but CPTR VALUES ARE RAM-VISIBLE (the fourth stored-anchor
>    class): relocate-and-repoint diverged 02/03/08 masked at select
>    entry (~frame 820) — select-screen init caches list pointers into
>    work RAM on legacy paths. The working rule pair: NEVER change a
>    host record's cptr, and NEVER write pool bytes another consumer
>    shares (SHARED_LISTS in select_port.py; shared lists keep the
>    host's coordinates and the ported art draws at the host position).
>    The pixel gate is the detector for class 3; the masked gate for
>    class 4 — it takes BOTH to make pool surgery safe.

**[VSR-67]** **The RAM gate cannot see NEW-CHARACTER visual wrongness** — masked gates cover legacy content, the oracle compares mapped fields, the pixel gate covers menus: any change touching the effect/display path ships with a before/after snapshot pixel A/B on a replay that exercises it, and no object field is declared dead by RAM alone. (was [VSP-43])

> **Why** (was [VSP-43], the original's `docs/project/gotchas.md`):
>
> The RAM gate cannot see NEW-CHAR visual wrongness — pixel A/B is the tool
>
> Round-25 lesson, twice in one change: (1) spark_bank_swap drew garbled
> tile blocks (bank 0x4000 under vanilla strips) and (2) spark_spawn_mark
> made ANITA vanish while a marked spark was live (+0x9A carries display
> semantics — it is the owner-char-id field other spawner paths write).
> BOTH passed the full battery: masked legacy gates only cover legacy
> content (the thunks were slot-0F-gated), the oracle gate compares mapped
> FIELDS, and the menu pixel gate covers menus. New-character VISUAL
> correctness has no automated gate — any change touching the effect/
> display path must ship with a before/after SNAP_FRAMES pixel comparison
> on a replay that exercises it (replay 17 hit frames 3477-3481 is the
> ready-made spark probe). Also: never assume an object field is dead
> because one path leaves it stale — prove it by pixel A/B, not by RAM.

**[VSR-68]** **Sound and anything leaving the 68k address space needs its own detector** ([CPE-36]) — a sound gate exists because every RAM and pixel gate was green while a tenant was silent, and equally green when a path played MUSIC ids; the per-node sfx helper and its record array are enabled by ONE data field so they cannot be enabled separately. (was [VSP-44])

> **Why** (was [VSP-44], the original's `docs/project/gotchas.md`):
>
> The sfx helper and the record array must be impossible to enable separately
>
> Un-stubbing the per-node sfx helper (vs2 `0x5122` -> vsavj `0x4CE2`) while
> slot 0x0F's pointer row still resolves to JEDAH's array means reading PAST
> that array (~40 entries) with indices up to 43 — enqueuing whatever follows,
> including the vsavj `0x700-0x7FF` MUSIC range. That is the original
> 214P/214K "music instead of sfx" bug.

## D.3 Extraction, reconciliation and generation — the law of the pipeline

**[VSR-69]** **Sibling-coincident engine refs are INVISIBLE to the diff oracle, and the coincident vsavj address is usually a WRONG routine** — the extractor merges scanner-LABELED operands (jsr/jmp/pea/lea/movea/move source, never bare longs) into every twinned region's ref list; identity rows are legal only with byte-verified identical targets; sound-farm entries resolve by their save+sfx-id signature; a no-exception display freeze is diagnosed by VIDEO-HASH BISECTION. (was [VSP-45])

> **Why** (was [VSP-45], the original's `docs/project/gotchas.md`):
>
> Sibling-coincident engine refs are INVISIBLE to the diff oracle — and the coincident vsavj address is usually a WRONG routine (paid: 2026-07-27 sessions 11c-12, ~a full session across three playtest rounds)
>
> vs2 and vhunt2 are sibling builds: large engine bands (the sound farm,
> kernel services) have IDENTICAL layout across them. An engine operand in
> ported code that COINCIDES across the siblings is not a diff site, so the
> oracle extraction never surfaces it — the operand is carried raw and, on
> vsavj (whose layout DID drift), silently calls whatever happens to live
> at that address. The mash-wedge hang was exactly this: the ported meter
> code's `jsr 0x3B2C` (stock-gain chime, vs2==vhunt2) landed on a DIFFERENT
> vsavj farm entry — an unpaired tail that "restores" stale registers via
> 0x3306 without a matching 0x330E save — handing the caller a garbage D0
> and turning a bounded loop into an infinite one (sound-request spam =
> "different music"; main loop never returns = display frozen while
> interrupt-driven RAM keeps changing; no exception ever fires, so crash
> guards are blind to the whole class).

**[VSR-70]** **Bare-long "pointers" in 68k code are usually OPERAND PAIRS** — sibling-veto every candidate (a real pointer differs by the host region's sibling shift, operand bytes are identical); conflicting or absent evidence REJECTS loudly, never rewrites silently; immediates are refs only when they land inside a ported region. (was [VSP-46])

> **Why** (was [VSP-46], the original's `docs/project/gotchas.md`):
>
> Bare-long "pointers" in code are usually operand pairs — sibling-veto them (paid: 2026-07-25 session 7, ~3h incl. diagnosis)
>
> The bare-long relocation heuristic (any ROM-plausible 32-bit value inside a
> ported code region whose target lands in another ported region) is wrong far
> more often than right in 68k CODE: adjacent instruction operands fuse into
> plausible pointers. Measured in the x088512 companion zone: **47 of ~55
> bare-long candidates were false** — e.g. `clr.b $6(a6); moveq #0,d0`
> read as "pointer 0x00067000" into a ported region and
> rewritten, silently destroying the `moveq`. The resulting crash (vec3 at
> engine 0x015096, frame 3025 — the whole "anim state-index delta" frontier
> of session 6) surfaced thousands of frames later, in ENGINE code, with a
> plausible-looking wrong value: nothing pointed back at the corrupted
> instruction. Diagnosis instrument: conditional logging breakpoint
> (`GUARD_PROBE`/`GUARD_PROBE_COND` on `run_replay_guarded.sh`) at the engine
> consumer, filtering on the relocated table base.

**[VSR-71]** **PC-relative word tables are DATA** — record every discovered table's full extent, exclude it from the relocation heuristic, bound its length by the smallest forward displacement, and keep table-referencing regions in one layout group so source-relative spacing survives. (was [VSP-47])

> **Why** (was [VSP-47], the original's `docs/project/gotchas.md`):
>
> PC-relative word tables are DATA — never let a pointer heuristic rewrite them (paid: 2026-07-25, ~1h)
>
> 68k brief-format dispatch (`jsr/jmp (d8,PC,Dn.w)`) reads a table of 16-bit
> self-relative displacements sitting *inline in the code stream*. Two
> adjacent entries decode, to any 32-bit scanner, as a
> plausible ROM pointer `0x00060068` — and a relocation pass will happily
> "fix" them, silently corrupting the table (symptom: a jsr through the
> table lands in the weeds one or two states into the ported behavior, far
> from the actual damage).

**[VSR-72]** **Blind long relocation over data blobs corrupts streams** — for a MIXED zone the rewrite set comes from a STRUCTURAL CLOSURE walk (tables → strips → streams → records), never a flat scan; the narrow-window + record-validation approach holds only where the pointer web is known. (was [VSP-48])

> **Why** (was [VSP-48], the original's `docs/project/gotchas.md`):
>
> Blind long-relocation over ported data blobs corrupts streams
>
> Relocating every even-aligned long that "looks like" an in-window
> pointer (the overlay slice: 293 rebased longs, 2811 tile words in 163
> scan-validated records) corrupted enough stream/coordinate data to
> crash the Donovan path at match start (watchdog boot-loop), while the
> identical placement with no rewrites was stable. Coordinate words and
> stream commands alias pointer prefixes at data-blob scale. For record
> regions with a known pointer web (anim, x2b7ef4) the narrow window +
> record validation held; for a MIXED zone (tables + strips + tag
> streams + records + coordinate runs) the rewrite set must come from a
> STRUCTURAL CLOSURE walk (tables -> strips -> streams -> records),
> never from a flat scan. The closure requires decoding the stream node
> language first — that is the stage-7 blocker, not the architecture.

**[VSR-73]** **Never write an unverified gap** — a gap between known tables is not a table row; no write without a decoded consumer. Restore-bisection (vanilla bytes over patched spans) attributes engine deltas, hardened with a liveness check because spans cutting executing ported code read as false "fixed". Verify the per-char-row + dark-mirror assumption PER TABLE. (was [VSP-49])

> **Why** (was [VSP-49], the original's `docs/project/gotchas.md`):
>
> Never write an unverified gap (the Felicia wall-jump lesson)
>
> The generator's auto_tables "gap" heuristic treated untyped gaps
> between per-char tables as more per-char rows and wrote slot-0x0F
> values plus 0x1F "dark mirrors" into them — 42 writes, 31 changing
> vanilla engine bytes. The gaps are JUMP-PHYSICS PARAMETER tables:
> index 0x1F holds the wall-jump-back velocity, and 0xFFFF4800 ->
> 0xFFFFEC00 broke Felicia's triangle jump in PURE LEGACY matches
> (rounds 18/19; she rides to Y~0x4AB and wraps). Invisible to every
> gate: no replay played Felicia (coverage), and per-char physics
> tables only surface when that char uses that move. Rules earned:
> 1. A gap between known tables is NOT a table row. No write without a
>    decoded consumer — speculative "it's probably the same layout"
>    writes into engine space are how legacy mechanics break.
> 2. Restore-bisection (copy vanilla bytes over patched spans in a test
>    rompath) is the reliable attribution method for engine deltas —
>    but spans that cut through EXECUTING ported code crash the boot
>    and read as false "fixed"; harden the verdict with liveness
>    (timer tick + match flag), and treat only same-sign results as
>    evidence.
> 3. The per-char-row + dark-mirror assumption must be verified PER
>    TABLE (the bank table has 0x18 rows with 0x10-0x17 dark forms;
>    these physics tables are not char-indexed at all).

**[VSR-74]** **Disabling a heuristic CLASS wholesale reverts load-bearing writes** — enumerate what the class actually wrote and re-port its load-bearing members explicitly; build-timeline correlation is attribution, only a mechanism trace convicts; a play-sampled "fixed" is weaker than a replay trace. (was [VSP-50])

> **Why** (was [VSP-50], the original's `docs/project/gotchas.md`):
>
> Disabling a heuristic CLASS wholesale can revert load-bearing writes
>
> Session 14w disabled the gap auto-table class to fix Felicia's jump
> physics — collateral: the class had ALSO been covering the throw
> victim-keyframe pointer table (gap_be27a), so the throw cinematic broke in
> the SAME build that carried the 14v grab rows and the winpal copies. Three
> suspects on one commit produced two successive wrong convictions (grab
> rows, then winpal copies), each "confirmed" by build-timeline correlation.
> Lessons: (1) when killing a heuristic class, enumerate what it was
> actually writing and re-port the load-bearing members explicitly; (2)
> build-timeline correlation is attribution, not proof — only a mechanism
> trace (here: the tap on the victim's X/Y naming PC 0xCE51C and its table
> read) convicts; (3) a "fixed/broken" verdict from play sampling is weaker
> than a replay trace — the round-21 "throw restored" confirmation sampled
> clean-looking throws on a build where the replay shows 21 teleport-scale
> jumps.

**[VSR-75]** **Early generic rows can masquerade over later-understood structures** — when a structure class becomes understood (farm, dispatch bank), re-audit every earlier generic row whose source address falls in its range; match MECHANISM, not row kind. (was [VSP-51])

> **Why** (was [VSP-51], the original's `docs/project/gotchas.md`):
>
> Early-session generic rows can masquerade over later-understood structures
>
> The session-5 bare-long pass resolved refs by unique byte match and
> labeled everything it placed `engine_data`. Two of those rows were
> sound-farm entries — so when session 13's farm audit enumerated
> `kind`-tagged farm rows, they were invisible, and the byte match had
> locked onto same-id vsavj entries (ids are in the matched bytes), i.e.
> the same-id-different-meaning trap with a `verified` sticker on it.
> Cost: a second playtest round (214P/214K music). Rule: when a structure
> class gets understood (farm, dispatch bank, …), re-audit ALL earlier
> generic rows whose vs2 address falls in the structure's range — match
> mechanism, not row kind, decides what a row really is.

**[VSR-76]** **Sibling twins can differ by ONE hoisted instruction** — when a source ref lands a few bytes past a routine head, check what the skipped bytes DO; "wrong data, right table" presents as plausible behaviour invisible to RAM and crash gates; the fix is a patched clone (vanilla bytes minus the divergent instruction, ported refs only). (was [VSP-52])

> **Why** (was [VSP-52], the original's `docs/project/gotchas.md`):
>
> Sibling twins can differ by ONE hoisted instruction — codebyte-matching lies
>
> The round-26 sword root cause: vs2 refactored the set-anim-by-number
> resolver into TWO entries — 0x5C77A applies `andi.w #$ff,d0` and falls
> through; 0x5C77E skips it (so Savior-2 extended anim numbers 0x100+ can
> resolve). vsavj's twin embeds the mask MID-routine with a single entry.
> The auto-matcher byte-matched the shared prefix and emitted a "verified"
> row mapping the UNMASKED vs2 entry to the MASKED vsavj routine — every
> ported call truncated its anim number (0x127 -> 0x27) and resolved a
> wrong-but-valid node in the right table. Nothing crashed; the sword
> simply played idle anims through every attack. Lessons: (1) when a vs2
> ref lands a few bytes past a routine head, check what those skipped
> bytes DO — an entry that skips a masking/clamping instruction is a
> different function; (2) "wrong data, right table" bugs present as
> plausible-but-wrong behavior, invisible to every RAM/crash gate — only
> behavior probes (the sword gate) catch the regression class. Fix
> mechanism: reconciliation kind `patched_clone` (vanilla bytes minus the
> divergent instruction, ported refs only).

**[VSR-77]** **Fuzzy code-similarity reconciliation collapses near-identical helpers** — for helper families the identity that matters is the PARAMETER (table content + dispatcher kind), content-verified; porting the parameter table behind a stub is the fallback when no exact twin exists. (was [VSP-53])

> **Why** (was [VSP-53], the original's `docs/project/gotchas.md`): Near-identical sound-farm helpers differ only in the table they pass, so a code-shape match picked a twin with the wrong parameter; content-verify the parameter tables, not just the code shape.

**[VSR-78]** **Twin sites are paired through the DISPATCH TABLE, never by byte pattern** — decode both engines' per-seq jump tables and pair by row index; and before porting any per-char handler entry, check whether the target table's tenant row is ALREADY repointed on the built image. (was [VSP-54])

> **Why** (was [VSP-54], the original's `docs/project/gotchas.md`): A twin found by byte pattern alone landed on the wrong subsystem and refuted half of an entry theory (14z-67/68); the per-seq jump tables pair sites by row index.

**[VSR-79]** **A single-shift sibling scan dies at the newcomer window's PIECEWISE structure** — group dispatch targets by their own pair delta first; never classify refs inside a tolerated filler run; a boundary probe must require the instruction-start opcode word to MATCH. (was [VSP-55])

> **Why** (was [VSP-55], the original's `docs/project/gotchas.md`): The newcomer code window shifts piecewise between the siblings, and junk filler decodes as pointers, so one global shift mis-classified refs (14z-65).

**[VSR-80]** **A window constant is a census, not a fact** — the newcomer-code window was Donovan-era triage and mis-classified thirteen of Huitzil's rows as veteran aliases; re-derive per tenant, and compare the SOURCE game's per-char row against its alias row even when every target is engine space. (was [VSP-56])

> **Why** (was [VSP-56], the original's `docs/project/gotchas.md`): The vanilla-alias assumption failed where per-char rows hide in engine space: a window measured for one tenant mis-classified the next tenant's rows (14z-65).

**[VSR-81]** **CODE-region ref fields are word-aligned by ISA; an idempotence latch on a pool-head is false mid-match** — the classifier enforces even offsets wherever engine refs are allowed, and a robust one-shot latch is phase-gated or a dedicated byte. (was [VSP-57])

> **Why** (was [VSP-57], the original's `docs/project/gotchas.md`): An odd-offset "engine ref" was rewritten through a jsr opcode, and a latch on a pool-head re-seeded live pools at round 2 (14z-65).

**[VSR-82]** **A SET-NAME MISMATCH IS A FALSE GREEN** — when a build's pack flips to the WIDE set (`vsavjw`), any probe still run as `vsavj` boots the PRISTINE ROM from `$ROMDIR` and soaks "clean"; a run derives the set from what its rompath holds, and a suspiciously clean result after a build-shape change is a prompt to verify WHAT ROM ran. (was [VSP-58])

> **Why** (was [VSP-58], the original's `docs/project/gotchas.md`):
>
> Three lessons from the day Huitzil came alive (14z-65)
>
> - A SET-NAME MISMATCH IS A FALSE GREEN, silently: when a build's first
>   wide_ext allocation flips the pack to vsavjw, every probe still run
>   with SET=vsavj falls back to the PRISTINE ROM in $ROMDIR — boots,
>   plays, soaks "clean", and tests nothing (an 11,000-frame attract-mode
>   "soak" passed this way). Every H gate now derives the set from the
>   rompath contents. Corollary: a "suspiciously clean" result after a
>   build-shape change is a prompt to verify WHAT ROM actually ran
>   (the loaded hitbox base names the character; the snapshot names the
>   screen).
> … *(continues in the original's document)*

**[VSR-83]** **PC-relative escapes in engine-style regions are INVISIBLE to the sibling oracle and unrewritable in place** — the fix reserves an adjacent trampoline pad and bounces each escape through an absolute `jmp` to the twin; run its census on EVERY engine-style region. (was [VSP-59])

> **Why** (was [VSP-59], the original's `docs/project/gotchas.md`): A pc-relative branch out of a ported engine-style region resolves relative to its new placement, the sibling diff never shows it, and the instruction cannot be widened in place, so it is bounced through a trampoline.

**[VSR-84]** **A tenant porting SHARED regions inherits every region-scoped mechanism row those regions carry** — diff the other tenants' source data for every row scoped to the region and copy them BEFORE the first probe run; the crashes are pre-paid knowledge. (was [VSP-60])

> **Why** (was [VSP-60], the original's `docs/project/gotchas.md`): Huitzil's port of regions Donovan already carried re-paid crashes whose fixes sat in Donovan's rows (14z-67).

**[VSR-85]** **A fix on a shared engine-family region fixes ONE tenant's copy** — every tenant carries its own copy of the ported engine-family regions, so when a new tenant imports a region, find every row any tenant's data scopes to it and bring them; and never blanket-copy a parked family without reading why it is parked (the original's reason for one such family was later RETRACTED). (was [VSP-61])

> **Why** (was [VSP-61], the original's `docs/project/gotchas.md`):
>
> A port_patch on a shared engine-family region fixes ONE tenant's copy (14z-85f)
>
> Every tenant carries his OWN copy of the ported engine-family regions
> (x028122 = the vs2 object-hit damage applier + reaction handlers; the
> merged image holds three). Donovan's session-14n throw-damage fix — six
> port_patch rows reconciling the applier's A5 staging displacements to
> the vsavj layout (same-value class #4) — lived only in donovan.toml, so
> Huitzil's and Pyron's copies shipped with the vs2 displacements intact:
> their object-path hits staged damage into $FF3494/96/98, which the
> vsavj engine never reads. Face: Phobos' FINAL GUARDIAN beam ticking 12
> times, combo counting, ZERO HP — while hitstop, sparks and satellites
> all worked (the applier's other effects don't route through the dead
> vars). Cost: the defect survived TWO playtest cycles because most
> moves' contacts take the fighter-path stager, which was never broken.
> Rule: when a new tenant imports a region that carries port_patch rows
> in ANY existing manifest, the rows come with it — grep
> `region = "<name>"` across build/manifest/*.toml is the two-second
> check. And its converse from 14x still binds: do NOT blanket-copy the
> rolled-back families (the grab-pointer/state rows are stage-99 parked
> in donovan.toml ~~because ported READERS consume those vars at vs2
> offsets~~ — **that reason was RETRACTED 14z-166: no ported instruction reads
> them, and the rows' price is GitHub #157**; ~~they stay parked until the
> maintainer schedules the re-attempt~~ — **the six pair-store rows LANDED at stage 6 in
> the 14z-183 M20 freeze; the `-0x4B3D` state-byte clears stay parked**).

**[VSR-86]** **The four checks before rooting a code region** — bound it by the sibling oracle, then check what the bound cut (forcing a bound is safe over plain-value tables only); census the pc-relative DATA tables (indexed AND post-increment shapes); census the pc-relative BRANCH escapes; check the span contains the CONSTANTS its own code loads (disassemble BACKWARD from the first instruction). (was [VSP-62])

> **Why** (was [VSP-62], the original's `docs/project/porting_code_regions.md`):
>
> The four checks, before you build
>
> Run all four on any new root. The `x093460` root (14z-71, the beam
> handler) is the worked clean case: it passed all four, and it built and
> ran correctly first time.

**[VSR-87]** **Crypt placement: the opcode view executes, the data view is garbage** — a region placed below `PRG:0x100000` is stored re-encrypted; a table inside it that is read as data must be emitted RAW (split at the FIRST table, not the oracle boundary) or relocated out as data. Moving a whole code region to raw space does NOT fix an embedded table (one byte image, opcode view). (was [VSP-63])

> **Why** (was [VSP-63], the original's `docs/project/porting_code_regions.md`):
>
> Crypt placement: opcode vs data views
>
> A region placed in the crypt hole (`hole_a`, below `PRG:0x100000`) is
> stored **re-encrypted**, so opcode fetches decrypt correctly and **runtime
> DATA reads see garbage**. Any table inside a crypt-placed code region that
> is read as data must be emitted RAW.

**[VSR-88]** **Put an execution breakpoint on code before attributing a symptom to it** — co-location is not causation; a region with genuinely broken tables was not the region whose code ran in the scenario. (was [VSP-64])

> **Why** (was [VSP-64], the original's `docs/project/porting_code_regions.md`):
>
> The habit that would have saved all four sessions
>
> **Put an execution breakpoint on code before attributing a symptom to it.**
> `x088512` had genuinely broken tables *and* was the region the explosion's
> machine lived in — both true, and unrelated: the code that reads those
> tables never runs in that scenario. Co-location is not causation, and one
> breakpoint costs a single run.

**[VSR-89]** **A ported region must CONTAIN its constants and its tables** — pc-relative data pointers are copied verbatim and resolve to `target + delta`, correct only if those bytes travelled; a separate root for the table does not work; decide on the BUILT image by comparing DATA views. Re-verify the twin delta at a NEW root start. (was [VSP-65])

> **Why** (was [VSP-65], the original's `docs/project/gotchas.md`): A ported region's pc-relative data pointers are copied verbatim, so a region cut short of the table it reads points at whatever the placement put there (14z-68).

**[VSR-90]** **A dead-filler classifier comparing the OPCODE view is blind to DATA** — if the siblings' DATA views of a candidate filler run are byte-identical, it is data; and a region census must not treat `lea (An,Xn),An` as a redefinition. (was [VSP-66])

> **Why** (was [VSP-66], the original's `docs/project/gotchas.md`): A filler run classified dead from its opcode view was a data table, and dropping it cost the air-214+P bug (14z-74).

**[VSR-91]** **A LINEAR placement map cannot see the extractor's sub-region shifts** — CORRELATE (slide the candidate source, take the offset with the most matching bytes) before reading a sub-90% match as corruption; ~85% with every mismatch a pointer field is what "correctly ported" looks like. (was [VSP-67])

> **Why** (was [VSP-67], the original's `docs/project/gotchas.md`): Comparing through the original's linear dst/src map fabricated "the ported data is corrupt" where the extractor had shifted a sub-region (14z-75).

**[VSR-92]** **A built-image walk VERIFIES the source's structure; it never re-derives it** — a pointer-shaped heuristic is placement-dependent (an unrelocated longword that happens to land in the placement window validates a phantom record); both walker passes take the source's accepted offsets and a pointer is allowed only when its target matches; any allocator growth re-rolls the dice, so "it was green before" is not evidence. (was [VSP-68])

> **Why** (was [VSP-68], the original's `docs/project/gotchas.md`):
>
> A pointer-shaped heuristic is placement-dependent — merged5 passed by luck (14z-92)
>
> `verify_gfx_build.py` compares a walk of the SOURCE anim region against a
> walk of the BUILT image. Both of `obj_records.walk`'s passes decide what
> is a record using predicates that ask about ADDRESSES, and placement
> moves the addresses out from under the same bytes:

**[VSR-93]** **Every TYPE/CLASS byte in a ported record indexes some engine dispatch, and the engines RENUMBERED families** — enumerate EVERY dispatcher the byte reaches (not the first found), validate each ported byte against vsavj's bounds at BUILD time with a family-aware census (never a blanket byte scan), and remember a dispatcher-exact remap can still change gameplay through stored-class property lookups. (was [VSP-69])

> **Why** (was [VSP-69], the original's `docs/project/gotchas.md`): A ported type byte valid for vs2's dispatcher indexed a different family in vsavj's renumbered one and crashed in the field (#99, 14z-109).

**[VSR-94]** **"Entry N" past the end of a word-displacement jump table is the NEXT routine's OPERAND** — compute the entry count `(first_code_addr − table_base) / 2` and refuse any index ≥ it; a "0 reads" deadness check proves nothing unless the replay set exercises the code around the address. (was [VSP-70])

> **Why** (was [VSP-70], the original's `docs/project/gotchas.md`): An index read past a jump table's end landed on the next routine's operand, and a deadness check that never exercised the code around it read zero.

**[VSR-95]** **"16 + the same 16 repeated" is a silent tenant trap** — an aliasing guard never faults, it plays another character's data ([VSE-12]); when a tenant misbehaves ONLY under CPU control, audit every `stride 0x80` table for PARKED rows, and give a CPU-behaviour soak TIME, not hits. (was [VSP-71])

> **Why** (was [VSP-71], the original's `docs/project/gotchas.md`):
>
> "16 + the same 16 repeated": an aliasing guard is a silent tenant trap; and a rig that wins fast cannot see a time-dependent AI crash (paid: 14z-111)
>
> **The fact.** Several per-class tables in vsavj are 32 entries with the
> second half a COPY of the first (`0xBF01A/09A/11A/19A`, the CPU AI action
> scripts). Vanilla never faults on an id with bit 4 set — it silently plays
> class `id & 0x0F`. For a tenant at 0x10/0x11/0x13 that means the table
> "works": no tripwire, no crash at the read, just another character's data
> flowing into the tenant's object. `bank_map.toml` had these rows PARKED
> ("Donovan's vs2 rows point outside his regions; unfired") for months. The
> symptom surfaced 2 characters and 3 dispatch levels away (a sub-state the
> tenant's private handler lacks), on CPU-controlled tenants only, after
> enough match time for the RNG to pick the offending script.

**[VSR-96]** **The placement hole inside the CPS-2 crypt range is opcode-view only; thunks with EMBEDDED DATA go outside it** — placed bytes plaintext in the packed set means outside the crypt range, garbled means inside; any thunk whose body is read as data is placed outside it ([VSR-87]). (was [VSP-72])

> **Why** (was [VSP-72], the original's `docs/project/gotchas.md`): A thunk carrying an embedded table was placed in the hole inside the crypt range and read its data through the encrypted view.

**[VSR-97]** **A slot id or a PLACED ADDRESS baked into hand-authored machine code tracks NOTHING** — authored code names the tenant id and placed addresses symbolically, substituted at build; a literal id compared against `RAM:$FF8782`/`RAM:$FF8B82` that mismatches the tenant FAILS the build; grep the ENCODED form (`000f`, `#$0f`) as well as the source form; when a stale value is identical on two builds, grep for the VALUE before tracing the code. (was [VSP-73])

> **Why** (was [VSP-73], the original's `docs/project/gotchas.md`): A placed address baked into an authored thunk kept pointing at the old placement after the allocator moved it, cost a session, and read as a hardware limit (14z-78).

**[VSR-98]** **Source data parses the same on every host, and an unknown key FAILS** — one pinned parser and a schema that hard-fails on an unknown or orphaned key; a format feature that resolves differently per host makes fingerprints host-dependent, which no single-machine gate can catch. (was [VSP-74])

> **Why** (was [VSP-74], the original's `docs/project/gotchas.md`): The original's TOML subset parsed a nested table differently from `tomllib`, so a fix row never applied on one machine and a newer host would have built different bytes (14z-62c).

**[VSR-99]** **Descriptor CRCs for variable-content members are SENTINELS** — a real member's CRC or the fill member's CRC resolves BY HASH onto something in the search path (a zero QSound member loaded silent zeros); sentinels match nothing so the member always resolves by NAME; `-verifyroms` reporting them bad is the honest cost, and it cannot be a liveness check on this project's sets. (was [VSP-75])

> **Why** (was [VSP-75], the original's `docs/project/gotchas.md`):
>
> Descriptor CRCs for variable-content members: use SENTINELS (14z-62d)
>
> Group C carries per-build content, so its descriptor CRC can never match.
> Two wrong answers were paid for before the right one:
> - **A real member's CRC** (the pristine group-B copies): resolves BY HASH
>   onto any pristine parent in the path — the 14z-60z shadow.
> - **The fill member's CRC** (4MB zeros = 0x1147406a): collides with the
>   ZERO QSOUND MEMBERS in the same zip — vsw.31m resolved by hash to
>   vsw.21m and group C loaded silent zeros. Measured: the whole B4 canary
>   section failed at once; sections 1-2 stayed green because zero==zero.
> Any CRC that ANYTHING in the search path carries is a latent shadow. The
> answer is a SENTINEL that matches nothing (0xdec0de31/33/35/37 + sha1s of
> sentinel strings), so the member ALWAYS resolves by NAME — the loaders'
> name-fallback demonstrably loads CRC-mismatched members on both emulators
> (every patched vm3 member ships that way). -verifyroms reports them bad;
> that is the cost, and it is honest.

**[VSR-100]** **A build's output is fresh, and what a mode does not regenerate is asserted pristine** — stale members of an earlier build were re-packed by a glob for a generation; a mode that does not write a group ASSERTS that group pristine in the packed set. "The file exists" says nothing about which build wrote it. (was [VSP-76])

> **Why** (was [VSP-76], the original's `docs/project/gotchas.md`): When one generation mode stopped writing a group of graphics members, the previous build's files stayed in the output and were re-packed every build; Jedah drew Donovan's band, caught only by the maintainer's playtest (14z-62h).

**[VSR-101]** **Exactly one writer per WORD** — the patcher hard-fails on an overlap and names both ops; a section that pokes a table row claims it explicitly rather than relying on emission order; overlap granularity is the word because odd-aligned pokes merge pristine neighbour bytes; a measured section owns a row over a triage tag. (was [VSP-77])

> **Why** (was [VSP-77], the original's `docs/project/gotchas.md`): Two generator sections silently owned one table row and last-write-wins decided the shipped bytes (14z-65).

**[VSR-102]** **A first-fit placement pool CASCADES** — the tile pool is block-aware first-fit, so carving cells out moves every later placement; fixed-position tile needs allocate at the pool TAIL or ride the existing exception flow; a mid-run reservation moved hundreds of placements and desynchronised every frozen artifact that referenced cells. (was [VSP-78])

> **Why** (was [VSP-78], the original's `docs/project/gotchas.md`): A reservation carved out of the middle of the tile pool moved hundreds of placements and invalidated every frozen artifact naming a cell.

**[VSR-103]** **"Inside the placed band window" is NOT "overwritten"** — the placement inside the bound is SPARSE; decide survival by intersecting with the ACTUAL placed tile set or by measuring pixels; the window exonerates only when the intersection is EMPTY. (was [VSP-79])

> **Why** (was [VSP-79], the original's `docs/project/gotchas.md`):
>
> "Inside the placed band window" is NOT "overwritten" (14z-62)
>
> `remap_spec.json`'s `placed` is a `[min, max]` BOUND of the tenant's tile
> placement, and the placement inside it is SPARSE (per-record tiles from the
> OBJ walk, not a wholesale block copy). Intersecting a record's tiles with
> the WINDOW says "may be clobbered", not "is clobbered" — Jedah's name
> banner (8/8 tiles inside the window) renders perfectly on the 0x13 build
> because its tiles fall in placement gaps, while his portrait (89/92
> inside) garbles. Concluding from the window alone gets both wrong.

**[VSR-104]** **In-place substitution has invisible slot dependencies** — every per-slot value the host already had RIGHT becomes a defect when the tenant moves off the slot; the de-substitution acceptance (a bounded window class) is the behavioural net, and a RAM diff at the frame names each culprit's subsystem. (was [VSP-80])

> **Why** (was [VSP-80], the original's `docs/project/gotchas.md`):
>
> "The substitution landed for free" — invisible slot dependencies (14z-62c)
>
> The slot-0x0F port never poked the engine's OBJ bank-word table
> (`PRG:0x282D4`, PC-relative, unmasked id) because Jedah's row was ALREADY
> `0x4000` — the very band the port placed Donovan's tiles in. Nothing
> recorded that the row mattered, no gate exercised it, and the first
> `0x13` match drew grey blocks: Donovan's remapped codes composed with
> row 0x13's Victor alias (`0x2000`, the wrong band). Found only by the
> measure-diff loop (snapshot -> OBJ dump -> write tap at `$FF8418` ->
> writer PC `0x282C0` -> hand-decode).

**[VSR-105]** **A record's BANK is a property of the DRAWING OBJECT, not of the record** — attribute by breakpointing the OBJ format handlers and reading `+0x18(A6)` live, then close the set STRUCTURALLY from the sub-object's own record stream, never from a global scan or content voting. (was [VSP-81])

> **Why** (was [VSP-81], the original's `docs/project/gotchas.md`):
>
> Per-record BANK attribution: the effect-tail triage has no bank column
>
> The x2b7ef4 gfx triage (same-index / +0x47 reloc / tail-place) is a
> BANK-1 model. Records drawn by #$4000-bank sub-objects (Anita's feet
> strip: 54 records, vs2 codes 0x0F8B-0x0FBC) went through the bank-1
> maps and rendered garbage from the wrong page (solid green, then +0x47
> garble — playtest rounds 10-13). A record's bank is a property of the
> DRAWING OBJECT (+0x18), not of the record: it cannot be derived from
> record content (that was f8eda2ca's content-voting failure, reverted).
> Attribution method that works: breakpoint the OBJ format handlers
> (fmt2 0x1B234 / fmt0 0x1AFC6; A0 = record+2, A6 = object) and read
> +0x18(A6) live — tests/lua/obj_record_bank_trace.lua — then close the
> set STRUCTURALLY from the sub-object's own record stream (obj+0x1C
> cursor), never from a global scan. Fix data lives in
> … *(continues in the original's document)*

**[VSR-106]** **The A5-relative work-var displacements differ between engines** — a ported damage applier staging into vs2's offsets ticks, combos and sparks correctly while HP never moves; the same-value class is reconciled per tenant copy ([VSR-85]). (was [VSP-82])

> **Why** (was [VSP-82], the original's `docs/game/gotchas.md`):
>
> Same-value class #4: A5-relative work-var displacements
>
> The engines' A5 work-variable layouts differ (vsavj damage vars at
> -0x4BBE/BC/BA vs vs2 at -0x4B6C/6A/68 — a uniform -0x52 family shift).
> Ported code writing engine work vars by displacement writes DEAD MEMORY
> on vsavj — no crash, no diff visibility (vs2/vhunt2 share the layout),
> just silently-wrong behavior (the zero-damage throw). Any ported code
> that communicates with engine routines through A5 work vars needs its
> displacements reconciled like ROM refs. Sweep pattern: displacement
> words in the vs2 work-var bands inside ported code regions.

**[VSR-107]** **A ported region whose consumers index NEGATIVELY needs headroom below its base** — never allocate it at the bottom of the WIDE extension space, whose first bytes sit against the reserved register window; an address error on an ODD address is a louder signal than "wrong data" and is read as such. (was [VSP-83])

> **Why** (was [VSP-83], the original's `docs/project/gotchas.md`): A region allocated at the very bottom of the extension space was indexed below its base into the reserved window.

**[VSR-108]** **Route objects to a ported machine on facts baked at BUILD time** — dispatch-time owner reads are transient at spawn instants (recycled slots, the type byte rewritten within the spawn frame); use spawn-time tags and per-tenant type numbers, never runtime state near a spawn. (was [VSP-84])

> **Why** (was [VSP-84], the original's `docs/project/gotchas.md`):
>
> Dispatch-time owner reads are transient at spawn instants — two measured counterexamples (14z-81c)
>
> The withdrawn multi-owner obj_hook stub design read the dispatching
> object's owner at runtime (+0x30/+0x32 walks to a player struct, then
> `(0x382)` for the id). Six replays produced two distinct failure modes:
> a type-119 creator hop walked through a RECYCLED slot to the wrong player
> (donovan/12, a regression on a replay first-wins served correctly), and
> the type-115 census showed +0x30 AND the type byte itself rewritten
> WITHIN the spawn frame. Owner facts measured on healthy steady-state
> ticks do not hold at the spawn instants where this family dispatches —
> and spawn instants are exactly when a per-tenant machine needs routing.
> Route on facts baked at BUILD time (spawn-time tags, per-tenant type
> numbers), not on runtime state near a spawn.

**[VSR-109]** **The discriminator for a ported machine is PER-EFFECT, not per-hit or per-character** — a stamp at a victim-spawn site serving every hit routed Dark Force's objects into the wrong machine; run the tenant's object-pairing gate on any change that routes objects, not only the gates for the move being fixed. (was [VSP-85])

> **Why** (was [VSP-85], the original's `docs/project/gotchas.md`): A per-hit stamp routed Dark Force's objects into the wrong ported machine; only the pairing gate, not the move's own gate, saw it (14z-68).

**[VSR-110]** **An "owner-gated" thunk on a shared routine is not scoped by owner alone** — sibling effect families share subtypes, so enumerate every family of the tenant's OWN content that reaches the site; base, stream, count and updater are ONE unit — port the region or nothing. (was [VSP-86])

> **Why** (was [VSP-86], the original's `docs/project/gotchas.md`): An owner-gated thunk on a shared engine routine also caught a sibling effect family of the same tenant that shared its subtypes (14z-68).

**[VSR-111]** **Per-char dispatch on a COMMON seq state needs the target flow's FULL closure first, and a "cold" site can be legacy-hot** — an owner-gated thunk there costs legacy cycles and breaks masked-EXACT legs; run the tenant boot gate (legacy EXACT) after ANY site-thunk addition, and verify a park/comment edit actually changed the file. (was [VSP-87])

> **Why** (was [VSP-87], the original's `docs/project/gotchas.md`): A per-char thunk on a seq state believed cold ran on legacy paths and broke masked-exact legs (14z-67).

**[VSR-112]** **A stamp census must enumerate WRITE FORMS** — the `move.b #imm,(d16,An)` form hid ~26 stamp sites behind a one-form scan; the census carries a positive control, a dynamic writer-PC audit maps every observed family write to a frozen row, and d16 distinguishes the type field from the owner byte. (was [VSP-88])

> **Why** (was [VSP-88], the original's `docs/project/gotchas.md`):
>
> A stamp census must enumerate WRITE FORMS, not just the known immediate shape (14z-82)
>
> The 14z-81b type-stamp scan matched `move.l #$01xxTTss,(An)` and concluded
> "types 114/115/118/120 are stamped elsewhere or computed". Productizing the
> census (tools/audit_type_stamps.py) with the `move.b #imm,(d16,An)` form
> found ~26 MORE stamp sites — type 115 alone has 20+ byte-stamp sites in the
> pod code, all following the one spawn idiom. A one-form scan reads
> exactly like a complete inventory, and a renumbering fix built on it would
> … *(continues in the original's document)*

**[VSR-113]** **Sampled uniformity is not uniformity** — disassemble ALL N sibling cases and diff them before synthesising N parallel engine cases; add a build-time assertion against the source engine's own table so config drift fails the build (8 of 12 synthesized stubs were wrong). (was [VSP-89])

> **Why** (was [VSP-89], the original's `docs/project/gotchas.md`): Twelve engine cases synthesised from a sample of their siblings were eight wrong.

**[VSR-114]** **"Run once at match start" is a TIMING TRAP** — char-init, the first per-frame tick and `RAM:$FF8004` all fire during the VS screen; arm a counter at init and act at zero while match-active, in the object-UPDATE phase so the same frame's list rebuild hides it. (was [VSP-90])

> **Why** (was [VSP-90], the original's `docs/project/gotchas.md`):
>
> "Run once at match start" is a TIMING TRAP — use a match-active countdown
>
> Three failed single-shot placements for the OBJ-tail clear (14z-7, all
> measured): char-init fires DURING the VS screen (which redraws the
> polluted buckets every frame until ~30 frames before round start); the
> sword routine's first per-frame execution ALSO lands mid-VS (companion
> objects live from char-init); and $FF8004==0x40000 is set during the VS
> screen too, so it cannot distinguish "round visually started". The
> robust pattern: arm a counter at init, decrement per frame while
> match-active, act at zero (~0x50 frames) — replay-timing independent,
> and doing the action in the object-UPDATE phase means the same frame's
> list rebuild hides it (no visible blank).

**[VSR-115]** **A 0x7xx sfx id's faithfulness is a property of its CONTENT, not its number** — before marking a sound stubbed or planning a sample port, CONTENT-SEARCH vsav's QSound image for the vs2 keyon's window (inclusive endpoint included) and check vsavj's keyon table at the hit; attribute the CALL PATH before the record. (was [VSP-91])

> **Why** (was [VSP-91], the original's `docs/project/gotchas.md`):
>
> A 0x7xx sfx id's faithfulness is a property of its CONTENT, not its number (14z-85g)
>
> The 14z-65 silencing sweep classed every vs2 sound-farm stub playing a
> 0x7xx id as "newcomer voice-bank range, keep silent pending M5" — a
> NUMBER-based rule. For 0x73A (the trap detonation chirp) it was wrong:
> the sample bytes are byte-identical in vsav's own QSound image at the
> same address (0x6C0000), keyed there as the 0x198/0x199 family
> [CORRECTED 14z-95, GitHub #93: for 20,480 of 20,481 bytes — the
> INCLUSIVE endpoint 0x6C5000, the played byte, differs: vsav 0xFF,
> vsav2 0x00; the gotcha's lesson stands, but "identical" claims must
> include the inclusive endpoint] — the
> maintainer could HEAR the sound existed in the build while the docs
> said it needed a sample port. Cost: the item shipped through two
> closure attempts (14z-84 "proximity not-a-bug", 14z-85g first reading
> "restoration = M5") before the content check — two python lines
> (extract the vs2 keyon's window, bytes.find in vsav's image) — settled
> it. Rule: before writing a stubbed_sound row (or planning a sample
> port), CONTENT-SEARCH vsav's QSound image for the vs2 keyon's window
> and check keyons_vsavj for an id at the hit address; the fix may be a
> kind=sound_stub row instead of an M5 dependency. And attribute the
> … *(continues in the original's document)*

**[VSR-116]** **A tenant's overrides are scoped to the tenant, and every staged recipe is rehearsed on the MERGED composition** — rows carrying the slot baked into an address, a table row index or a thunk body were silently wrong at a variant id until the data had words for slot-relative rows; a per-tenant reconciliation override placed at document root went GLOBAL on a merged build and killed another tenant's rows; a value swap is staged as an edit, never as a duplicate key. (was [VSP-92])

> **Why** (was [VSP-92], the original's `docs/project/tenant_manifest.md`):
>
> The slot-row vocabulary (14z-62c — how a row states its tenant behavior)
>
> Step 2 (the move to `0x13`) surfaced a class the schema had no words for:
> manifest rows carrying the SLOT baked into an address, a table row index,
> or a hand-authored thunk body. Each was silently wrong at a variant id —
> either still aimed at row `0x0F` (repointing the HOST's data: the sprite
> palette table, the sfx pointer row) or still gating on `#$0F` (the
> An-relative id compares the TT guard could not see). The vocabulary that
> … *(continues in the original's document)*

**[VSR-117]** **The hardening register is maintained in the SAME commit as any change to its classes** — the partition (VANILLA / PATCHED / RAM / PATCHED-TRIPWIRE / HW / SENTINEL / WIDE-HOLE) is frozen by a gate; STRONG findings are reviewed individually before freezing, WEAK ones frozen by COUNT so growth fails; score is not risk — CONSUMPTION is. (was [VSP-93])

> **Why** (was [VSP-93], the original's `docs/project/hardening_register.md`):
>
> Maintenance rule: this register is updated in the same commit as any
> change to the classes above (a new tripwire, a resolved row, a rig that
> covers a listed surface). A register that lags its classes is the
> reference-rot disease this program exists to cure.

## D.4 Freezes, the registry, releases and the suite

Must-fire controls are [VSR-22], the rule-checker [VSR-48], and "the exit status is not the verdict" [VSR-45] (D.1).

**[VSR-118]** **Every frozen build is recorded with the commit that reproduces it** — the record carries the fingerprint and how to reproduce it, and is the only way back for a superseded build whose sources moved on; the stock twin is rebuilt at every freeze and its fingerprint stated as MOVED or UNCHANGED with the reason. (was [VSP-94])

> **Why** (was [VSP-94], the original's `HANDOFF.md`): In the original an annotated `freeze/<name>` tag carries the fingerprint and the reproduction, and the HANDOFF registry row names it.

**[VSR-119]** **A profile bump invalidates every frozen build as a REFERENCE (not as a record)** — a frozen CONSTANT that follows the romset (a placement address, a first-executed extension address) re-freezes at every freeze, whatever lane it lives in ([VSR-129]); sort references by "does it BOOT?" when triaging; a comparator reports a missing operand as a DEAD LEG, never compares it. (was [VSP-95])

> **Why** (was [VSP-95], the original's `docs/project/gotchas.md`): A WIDE profile bump made MAME refuse every build frozen before it, so the only render gate of two tenants compared against a build that no longer booted (14z-92).

**[VSR-120]** **A gate never pins a superseded build** — it reads the current build from the registry; a live pin on a SUPERSEDED registry key is a red, with a planted pin as its control; and a freeze runs its full freeze-cadence tier, `ROMDIR` set, BEFORE it records the freeze, since without `ROMDIR` the ROM gates SKIP. (was [VSP-185])

> **Why** (was [VSP-185], the original's `docs/project/gotchas.md`): The original's freeze re-pointed 304 build references by name and still left two gates on the old freeze, because one pinned a FINGERPRINT the name sweep could not see (14z-170).

**[VSR-121]** **A gate's fixture is a whole build, reproducible from its recorded commit** — a "tracked" fixture that depends on untracked generator outputs cannot be restored by the version control that tracks it; restoring one is a historical rebuild from its commit, and re-pointing the gate at a current build is REFUSED when it would launder an unreviewed inventory into the gate that exists to review it. (was [VSP-97])

> **Why** (was [VSP-97], the original's `docs/project/build_dir_triage.md`):
>
> THE DEEPER FLAW THE SWEEP EXPOSED: "tracked" build dirs are only PARTLY tracked
>
> `build/don_m7` is a TRACKED build dir — 18 files — but
> `tests/test_shared_writes.sh` needs the 23 generator outputs
> (`patch/fixed_*.bin`, `effect_lists.bin`, …) that are NOT tracked. Deleting
> the dir therefore removed a gate fixture that git could not restore:
> `git checkout HEAD -- build/don_m7` brought back the 18 and the gate went
> … *(continues in the original's document)*

**[VSR-122]** **Recordings: tracked the moment they have a consumer, deleted the moment they have none** — a search of the tree for the recording's name coming back empty means delete; the working copy is deleted once the recording is tracked ([VSR-19]). (was [VSP-98])

> **Why** (was [VSP-98], the original's `docs/project/build_dir_triage.md`): Applied at the original's 14z-111 close: three unreferenced recordings deleted, one renamed to the freeze-set convention and its cache copy deleted.

**[VSR-123]** **The patch registry is updated in the same commit as any patch change** — status, dependencies, exclusivity and deprecation on one page; byte detail and mechanism rationale live in the build's generated notes and the source data, not in it. (was [VSP-99])

> **Why** (was [VSP-99], the original's `docs/project/patch_index.md`): The original's registry page had never grown past M1 when a close audit found it stale (14z-66); it was rebuilt from the generated notes and the manifests (14z-67).

**[VSR-124]** **A release is ONE DIRECTORY PER PLATFORM, each self-sufficient, with no ROM bytes** — deltas against the reference dumps' members, a manifest, and an applier that refuses to write unless EVERY member's sha1 matches; the MiSTer bitstream is a build resource named by its seed, hash-verified in and never copied from another release ([MSV-16]); a gate round-trips the release and scans it for reference-ROM chunks. **Prebuilt emulator binaries are RELEASE ASSETS, never git content** (ruled 2026-09-11), published only after their gate is green. **EVERY PUBLISHED ASSET CARRIES THE SAME SELF-SUFFICIENCY** (ruled 2026-09-12): README + patch set + manifest + applier + exactly ONE emulator route (the prebuilt binary and its record, OR the patch and its recipe, OR the whole MiSTer directory); one download plus the user's dumps is playable and nothing in it can be misapplied, asserted both ways by a gate. (was [VSP-100])

> **Why** (was [VSP-100], the original's `docs/project/release_format.md`): Ruled 2026-08-28 (14z-113): every version releases every platform even if only one changed; the 2026-09-12 ruling followed one release whose published assets lacked the property its directories had (14z-151).

**[VSR-125]** **ONE pre-commit command, and SKIP IS NOT PASS** — the runner reports PASS / SKIP / FAIL separately, a strict mode makes SKIP fatal, and a coverage check names any gate no runner registers; emulator gates have their own runner ([VSR-126]). (was [VSP-101])

> **Why** (was [VSP-101], the original's `HANDOFF.md`): The original's portable tier treats a SKIP on a clean checkout as failure; a gate that needs ROMDIR, a build or a binary is not portable.

**[VSR-126]** **The emulator tier DECLARES a release's emulator scope, one row per gate, complete both ways** — the prerequisite lane (the instruments' own proofs) runs FIRST and a red there STOPS the run: a measurement taken after a moved instrument is not evidence ([CPE-24]). Taking a gate out of release scope is a RELEASE decision — the maintainer's, not yours — carries a reason, and NEVER means "do not run" (a sweep runs them and keeps them honest), nor "resolved", nor "quietly green". What a gate FOLLOWS is a separate question from its scope; a gate runs on its OWN defaults unless a triage says what else it should measure ([VSR-119]); each gate's timeout comes from its MEASURED runtime, never one cap for all; parallel slots each get their own scratch. (was [VSP-164])

> **Why** (was [VSP-164], the original's `HANDOFF.md`): One 90-minute cap killed two 3-hour Verilator gates whose notes documented the runtime in prose (14z-134).

**[VSR-127]** **A FROZEN EXPECTATION SAYS WHERE ITS NUMBERS CAME FROM, and a gate's documentation states the default its CODE uses** — every expectation names its subject, its EVIDENCE CLASS (`in-emulator` / `derived` / `static` / `hash-lock` / `registry`) and its re-freeze invocation, because a red gate is a QUESTION whose first question is which side rests on a measurement ([VSR-25]); `hash-lock` locks CURRENCY and never correctness, and `derived` is only as good as the reader. A documented default is locked against the code's; a quoted token is code under discussion, and a verbatim archive block is never rewritten ([VSR-33]). (was [VSP-165])

> **Why** (was [VSP-165], the original's `HANDOFF.md`):
>
> WHERE A FROZEN EXPECTATION'S NUMBERS CAME FROM (since 14z-128)
>
> **`tests/expected/PROVENANCE.md`** — one row per file directly under
> `tests/expected/`: what the numbers DESCRIBE, what evidence they REST ON, and
> the invocation that re-freezes them. It exists because of the maintainer's
> rule for adjudicating a red gate — a red gate is a QUESTION, and its first
> question is which side rests on a measurement. The evidence classes are
> defined and enforced: `in-emulator`, `derived`, `static`, `hash-lock`,
> `registry`. **`hash-lock` locks CURRENCY, never correctness**, and `derived`
> … *(continues in the original's document)*

**[VSR-128]** **A tool that provisions from nothing has a control that provisions one and RUNS something in it** — a provisioning branch only a FRESH scratch reaches is dead code to every test run on the existing one; a heal test on a hollowed scratch is not that control. (was [VSP-177])

> **Why** (was [VSP-177], the original's `docs/project/gotchas.md`): A shell slip in the original's simulator driver killed every fresh scratch clone's module init, invisible because the one existing clone never ran that branch (14z-134).

**[VSR-129]** **A frozen expectation FOLLOWS whatever moves it, whatever the gate's cadence says** — a gate run only on the MiSTer lane's cadence may freeze nothing a romset freeze can move (the first extension address executed is the relocated walker's PLACEMENT, and it moved five freezes before a release run noticed), or it runs with the romset. And a freeze is finished only when everything it produced is recorded: a release run that finds the freeze's release directory unrecorded has found an unfinished freeze. (was [VSP-178])

> **Why** (was [VSP-178], the original's `docs/project/gotchas.md`):
>
> **A frozen expectation FOLLOWS whatever moves it, whatever the gate's cadence says.** `test_mister_prg_window` was `bitstream` cadence — run at a release, and at a freeze only when the freeze targets MiSTer — while its frozen pair records the FIRST EXTENSION ADDRESS the 68k executes, which is the relocated OBJ walker's PLACEMENT: the hole allocator moves it whenever a freeze adds extension content before it. Frozen on merged-m10 (14z-107 (11)), stale from merged-m11 (14z-115), and nobody could know for five freezes because the lane is opt-in and the row never ran at a freeze. The M16 release run found it: `first_addr 4be7c0 -> 4c13d0`, every structural assertion green. Cadence follows the EXPECTATION: a bitstream-cadence gate may freeze nothing that a romset freeze can move, or it is `romset`. The same run found `release/merged-m16/` PRODUCED at the 14z-132 freeze and never `git add`ed — every earlier release directory went in with its freeze commit — so the freeze commit is where the release directory lands, and a release run that finds it untracked has found a freeze that was not finished. Both are now in the release-day checklist and `test_expectation_provenance` covers `tests/expect/`.

**[VSR-130]** **A gate no runner runs can sit FAILING for sessions** — when a freeze changes design semantics, run every gate whose recorded inputs touch the changed surface BEFORE closing; a red gate nobody runs reads as "regression" to whoever finally runs it. (was [VSP-103])

> **Why** (was [VSP-103], the original's `docs/project/gotchas.md`): A gate outside the battery sat red across a design change and was paid for twice in one day (14z-67).

**[VSR-131]** **A fixture's deliberate FAIL never writes where real evidence lives** — a self-test's stubbed failures, preserved to the shared failure-evidence path, presented as a post-close gate failure; a run's outputs are its own. (was [VSP-104])

> **Why** (was [VSP-104], the original's `docs/project/gotchas.md`): 141 stub logs a self-test fed through a real gate accumulated in the original's shared failure path over five days, and the newest cost a session-open triage (14z-103).

**[VSR-132]** **A builder's failure propagates, and a run measures only the build it names** — a crashed builder whose status was lost to a pipe re-packed the PREVIOUS build's tiles under fresh logs; a rompath that chains to `$ROMDIR` resolves the PRISTINE set when the build output is missing, measuring vanilla against vanilla; assert the build exists before measuring it. (was [VSP-105])

> **Why** (was [VSP-105], the original's `docs/project/gotchas.md`): Two consecutive "fix" builds shipped byte-identical graphics behind fresh-looking logs; the tell was an artifact an hour older than its pack.

**[VSR-133]** **A fingerprint names the set you built** — a fingerprint call that did not name its set fell through to `$ROMDIR` and reported the pristine ROM's fingerprint as a WIDE build's; a fingerprint equal to a known reference row is a bug until proven otherwise. (was [VSP-106])

> **Why** (was [VSP-106], the original's `docs/project/gotchas.md`): A WIDE build was reported with the pristine reference's fingerprint because the fingerprint tool searched the rompath (2026-08-04, 14z-59i).

**[VSR-134]** **In the external suite, each original gate receives its build the way ITS code reads it** — half the original's gates read `BUILD=`, half a positional argument, and a gate that ignores the one you set measures its DEFAULT build with full confidence; the adapter table says which (SPEC §5.2), and when a differential comes out identical, check that the variable was varied. (was [VSP-107])

> **Why** (was [VSP-107], the original's `docs/project/gotchas.md`): A per-build result was quoted from a gate that silently ignored `BUILD=` and measured its default (14z-110b).

**[VSR-135]** **Print the resolved fingerprint of what was actually opened, and tell "rejected" from "died"** — a path checked one way and handed to the emulator another fell through to `$ROMDIR` and labelled pristine vanilla with the build's name, and the printed fingerprint is what caught it; a verdict control that CRASHES reads as a control that fired. (was [VSP-108])

> **Why** (was [VSP-108], the original's `docs/project/gotchas.md`):
>
> two ways a tool measures the wrong thing and says nothing (paid: 14z-97)
>
> **A path argument must be CANONICALISED before anything uses it — the
> "correct only when called one way" trap, and this is its THIRD instance in
> two sessions.** `tools/propose_masked_specs.sh` existence-checked
> `$BUILD/rompath` but handed `$PWD/$BUILD/rompath` to MAME and to
> `build_fingerprint.py`. With a repo-relative builddir the two agree; with an
> ABSOLUTE one they do not — the checks pass, the emulator gets a path that
> cannot exist, and MAME falls through the `;`-separated rompath to `$ROMDIR`.
> The tool then measures PRISTINE VANILLA and prints the build's name over it.
> Measured live: an absolute-path run reported fingerprint `b0eb9ecd` (vanilla)
> for a stage-6 build. Two rules: `case "$X" in /*) ;; *) X="$PWD/$X" ;; esac`
> at the top (the convention `audit_mask_window_ff42a2.sh` already follows), and
> … *(continues in the original's document)*

**[VSR-136]** **A gate does not depend on the caller's environment** — paths reach a gate as arguments of its run, never through inherited variables; a new gate's first run is in a clean environment; printed identifiers a human might compare across runs are stable digests, never a salted `hash()`. (was [VSP-109])

> **Why** (was [VSP-109], the original's `docs/project/gotchas.md`): A relative `ROMDIR` failed two gates resolving from another working directory, and a value read from a set-but-unexported variable was green only under the author's shell (14z-96).

**[VSR-137]** **A check on a process distinguishes three outcomes: true, false and crashed** — a status test reads a crash as the false branch, and a check whose tool lacks a builtin passes by erroring; capture the value and compare it, and compare hex fields as strings, never as numbers. (was [VSP-111])

> **Why** (was [VSP-111], the original's `docs/project/gotchas.md`): An awk check compared hex fields as numbers and reported a confident 0 for a twin site from the same file and run (14z-91).

**[VSR-138]** **ABSENT, ZEROS and a value are three outcomes** — guard the input itself, never the pipeline that read it; a fallback must read the status of what failed. (was [VSP-112])

> **Why** (was [VSP-112], the original's `docs/project/gotchas.md`): A fallback after a pipeline read the last command's status and reported a machine that died at frame 3020 as a loaded character (14z-93).

**[VSR-139]** **A measurement to be quoted records the tooling commit it ran on** — a worktree branched from a STALE `origin/main` silently changed the instrument; check a worktree is at the commit you meant before measuring in it; a rompath overlay of absolute links into `$ROMDIR` dangles on a rename. (was [VSP-113])

> **Why** (was [VSP-113], the original's `docs/project/gotchas.md`): A worktree created from a stale remote branch measured with an older instrument while every record named the current one (2026-08-04, 14z-60).

**[VSR-140]** **A verdict line may state only what its OWN branch measured** — a PASS message restating a control's conclusion kept printing under a dead control; gate any restatement on the control's result, and grep success messages that describe another section's measurement. (was [VSP-114])

> **Why** (was [VSP-114], the original's `docs/project/gotchas.md`): A gate's section 0 printed a control's conclusion unconditionally, and kept printing it after the control died (14z-93).

**[VSR-141]** **A two-leg A/B that bails on leg 1 leaves leg 2's health an ASSUMPTION** — run the reference leg anyway and print MERGE-SPECIFIC vs LATENT IN THE FROZEN BUILD as part of the verdict; a covering gate that rebuilds at a different stage covers a DIFFERENT build. (was [VSP-115])

> **Why** (was [VSP-115], the original's `docs/project/gotchas.md`):
>
> A two-leg A/B that bails on leg 1 leaves leg 2's health an ASSUMPTION — and the assumption was false (14z-82b)
>
> `audit_merged_legacy`'s leg-b ran the MERGED build first and returned on
> its crash, so "the single-tenant reference is clean" was never a
> measurement — it was the natural reading of a report that only ever
> showed the merged leg failing. pyron-m2 crashes at f7997 SOLO: the defect
> sat in the FROZEN build for two sessions while every record called it a
> merge artifact, and the fix hunt started in the wrong codebase half. The
> repair is structural, not procedural: on a leg-1 crash the gate now runs
> the reference leg anyway and prints MERGE-SPECIFIC vs LATENT IN THE
> FROZEN BUILD — the attribution is part of the verdict, not homework left
> to the reader. Related gap, same lesson: the only gate that ran the
> crashing replay at all (`test_pyron_soak.sh`) built STAGE 4, so the
> … *(continues in the original's document)*

**[VSR-142]** **A pre-armed attribution is a hypothesis** — comments and headers may carry predictions; the printed verdict carries only what was measured, or points at the probe that measures it. (was [VSP-116])

> **Why** (was [VSP-116], the original's `docs/project/gotchas.md`):
>
> A pre-armed attribution is a hypothesis, not a finding — print the measured mechanism (14z-81)
>
> `audit_merged_legacy.sh` was written with F2 (the merged shim serving only
> tenant 0 → unseeded pools) as the pre-armed attribution for any Huitzil
> leg-(b) crash, and its failure message SAID so. The measured crash was a
> different mechanism entirely (the satellite anim-base defect, at spawn,
> before seeding could matter) — the message was corrected the same day, but
> only because the measurement happened to run the same session. A plausible
> mechanism written into a script's output becomes "the finding" the moment
> someone reads a failure without re-measuring. Pre-arm attributions in
> comments and headers as PREDICTIONS; make the printed verdict carry only
> what was measured, or point at the probe that measures it.

**[VSR-143]** **A sandbox is NEW for every run** — reuse is a declared exception (an nvram-carrying scenario), never what a run gets by sharing part of another run's identity; "the instrument control passed" is not "nothing moved" — check the artifact's status after anything that can write it. (was [VSP-117])

> **Why** (was [VSP-117], the original's `docs/project/gotchas.md`): The original's masked-basis canary keyed its sandbox by the replay name alone, so a second run inherited the first one's nvram and corrupted the basis it verified (14z-91).

**[VSR-144]** **A fingerprint covers every member of the set** — two builds differing only in WIDE extension content hashed identically until the fingerprint's member pattern included the extension members; a fingerprint blind to a region is a fingerprint of a different artifact. (was [VSP-118])

> **Why** (was [VSP-118], the original's `docs/project/gotchas.md`): The original's fingerprint pattern did not match the WIDE extension members, so extension content was invisible to it.

## D.5 Rigs, pokes and probes — the instruments and how each has lied

**[VSR-145]** **RECORD YOUR SESSION, on MAME** — a playtest records a MAME `.inp` from a FRESH named nvram start state; playback is frame-exact on the same pinned binary against a throwaway COPY of that nvram, never the canonical one; FBNeo's SDL frontend has no equivalent, so record on MAME. A report with an `.inp` is a replay protocol any instrument can ride ([VSR-19]). (was [VSP-119])

> **Why** (was [VSP-119], the original's `HANDOFF.md`): Recording was available since 14z-99 and made mandatory for crash reports at 14z-111: host keys never enter an `.inp`, which records the emulated ports.

**[VSR-146]** **Forced-pick pokes on `RAM:$FF8782`/`RAM:$FF8B82` end by ~frame 1500** — the early window 1400-1500 only; pokes held later leak into the SECOND player's load in the 2P flow (a whole "victim sweep" loaded as one id); a no-poke control verifies the flow. (was [VSP-120])

> **Why** (was [VSP-120], the original's `docs/project/gotchas.md`): A victim sweep whose pokes ran past the early window loaded every leg as one id.

**[VSR-147]** **The forced pick does not populate the HUD index field** — in-match HUD stagers index a SEPARATE field only the real pick flow writes; verify HUD rows with real-cursor replays (in the original's corpus `36`/`37`/`40`, [MSV-28]), never the poke rig. (was [VSP-121])

> **Why** (was [VSP-121], the original's `docs/project/gotchas.md`): HUD verification on the poke rig read a field the forced pick never writes (14z-67).

**[VSR-148]** **The forced pick holds through SELECT only** — on a vs-CPU rig P2's loaded struct is rebuilt from the CPU's REAL pick, so `(0x382,P2) == my tenant` is true on 2P forced-pick replays and false on vs-CPU ones. (was [VSP-122])

> **Why** (was [VSP-122], the original's `docs/project/gotchas.md`):
>
> Forced-pick pokes hold through SELECT only — a vs-CPU P2 carries the CPU's REAL pick at match time (14z-81c)
>
> `(0x382,$FF8800)` read 0x06 (the CPU's actual character) at f2886 on
> `12_donovan_vs_cpu` despite the rig poking `$FF8B82 = 0x13` at frames
> 1400-1500 — the pokes force the SELECT commit, and the loaded struct is
> rebuilt from the real pick. On 2P replays both structs hold the poked id
> (test_shim_charid measured exactly that), which makes it easy to assume
> the same on vs-CPU rigs. Any check of the form "(0x382,P2) == my tenant"
> is rig-dependent: true on 2P forced-pick replays, false on vs-CPU ones.

**[VSR-149]** **The native leg is reachable for ANY tenant screen with the same poke** — force the tenant on `vsav2` (`RAM:$FF8782` = `0x10` from frame 1400, the early window), poke BOTH sides when sprite lists are compared, and when the state under test is a MODE prove it was ENTERED (Dark Force: poke `RAM:$FF8509`, assert `RAM:$FF802E` = 1 — never infer a mode from the fighter block). Do not characterise a tenant symptom without this leg. (was [VSP-123])

> **Why** (was [VSP-123], the original's `docs/project/operations.md`): Huitzil can be forced on native vsav2 with the ordinary early-window poke, with no vs2 cursor path and no savestate (14z-69).

**[VSR-150]** **Rig grammar from the #103 hunt** — an opponent-class poke overlapping a LIVE match kills the match (window it BETWEEN matches from a prior no-poke run); repeated HP pokes across a KO un-KO the loser (kill pokes at round start +~100f, three pokes 20f apart, hands off); identify a screen from the STATE WORDS (`RAM:$FF8004/8008/800C`), never from banner text; before declaring RAM "frozen", diff a WIDE slice at two distant times past the longest plausible timeout. (was [VSP-124])

> **Why** (was [VSP-124], the original's `docs/project/gotchas.md`):
>
> five traps from the #103 hunt — four are RIG grammar, one is a classifier lying by omission (paid: 14z-97b)
>
> **A blanket opponent-class poke window that overlaps a LIVE match kills the
> match.** `+0x382` is live in-match state (the character id, ram.md `+0x382`);
> writing the next opponent's class into `$FF8B82` mid-match ended the running
> match at the poke onset and read as a mysterious early game-over — a full
> run lost to diagnosis. The opponent poke must be windowed BETWEEN matches,
> aimed with selection frames measured from a prior no-poke run of the same
> config.

**[VSR-151]** **Kill/heal pokes write BOTH HP words** — the 2-byte shape leaves white HP positive and manufactures the unjudgeable round on any character; a return address read at `(SP)` names a caller only for jsr-reached code (a branch-reached callee needs a history of the stream); a `-debug` trace run carries its own dumps and is interpreted only against anchors from the SAME run. (was [VSP-125])

> **Why** (was [VSP-125], the original's `docs/project/gotchas.md`):
>
> the kill/heal POKE SHAPE trap from the #103 close (paid: 14z-98; the instrument-grammar half of this entry was re-filed to `platform/gotchas.md` at 14z-118)
>
> **A kill/heal poke that writes ONLY the 2-byte HP word manufactures
> #103's unjudgeable state — on ANY character, vanilla engine included.**
> The round judge kills on WHITE HP's sign (+0x52, engine_internals "THE
> ROUND JUDGE") and the pipeline keeps white <= hp; `f:ff8450:0001`
> leaves white at ~288, so the next real hit underflows hp while white
> stays positive and the round can NEVER judge. Measured on a pure-legacy
> Victor leg: 2-byte shape UNRESOLVED >= 8,760f; the 4-byte idiom
> `f:ff8450:00010001` (hp AND white — test_don_column's shape) FLOWED 600.
> Frozen both ways in tests/audit_kill_poke_shape.sh. Consequence already
> paid: the 14z-97 (7) continue rig's "HP set to 1" pokes (byte-width not
> committed) mean "#103 instance 2" (Phobos x Bishamon) is UNVERIFIED —
> possibly the rig's own poke. Kill pokes write BOTH words, always.

**[VSR-152]** **Probe ENTRY addresses, never the crash-line PC** — a group-0 exception pushes a mid-instruction PC no breakpoint can match, and a probe PC inside an operand measures NOTHING while looking green; compute a farm entry from the FARM BASE, and demand a must-fire control at the SITE under the rig's own conditions (a plausible site can be dead code; a control site can be unreachable under the pokes). (was [VSP-126])

> **Why** (was [VSP-126], the original's `docs/project/gotchas.md`):
>
> The pushed group-0 exception PC is mid-instruction — probing it reads a clean zero (14z-81)
>
> The merged-legacy audit's Huitzil crash reported `CRASH 2886 vec3 PC 015098`.
> A `GUARD_PROBE=15098` breakpoint produced ZERO probe lines on the crashing
> build — at the crash itself — and zero on the healthy reference across 11,017
> frames. Nothing was wrong with the probe machinery: a 68000 group-0 exception
> (address/bus error) pushes a PC from INSIDE the faulting instruction, so
> `0x15098` is the middle of the `move.l (a0),(0x20,a6)` that starts at
> `0x15096`, and no instruction ever BEGINS there for a breakpoint to match.
> The dead-instrument class again, in a new coat: a probe that cannot fire
> prints the same clean zero as a site that is never reached.

**[VSR-153]** **One output directory per rig iteration and per leg** — dumps named by frame and address silently overwrite an earlier iteration's evidence and reassign one leg's dumps to another; every iteration and every leg is its own run. (was [VSP-127])

> **Why** (was [VSP-127], the original's `docs/project/gotchas.md`): A third iteration of a contact rig overwrote the second's satellite-bearing frames and cost a re-run (14z-100).

**[VSR-154]** **Cross-build A/B dumps run PROBE-FREE** — debugger overhead lands at different instruction boundaries on two builds and phase-shifts an animation per leg (a persistent 23-byte "diff" that was zero clean); find the address under a probe, then re-run the A/B with write taps or plain dumps. (was [VSP-129])

> **Why** (was [VSP-129], the original's `docs/project/gotchas.md`):
>
> Cross-build A/B dumps must run PROBE-FREE — debugger overhead lands differently on two different builds (14z-84)
>
> The Bulleta-DF A/B's first run compared vanilla-vs-merged palette RAM
> dumps taken under `GUARD_PROBE=2ad82` (hundreds of logging-breakpoint
> stops on the palette-seq resolver) and found a persistent 23-byte diff in
> row 0x0A — which a probe-free re-run proved to be ZERO. The probe's
> per-stop overhead perturbs frame timing, and on two DIFFERENT BUILDS the
> perturbation lands at different instruction boundaries, phase-shifting a
> palette-seq animation differently per leg: the "diff" was two legs of one
> animation sampled at different steps. This is the `-debug`-timeline
> caveat's cross-build instance (STATE 14z-82c: "debug timelines do NOT
> transfer to checksum timelines"): a probe that is harmless WITHIN one
> leg's measurements still invalidates a CROSS-LEG comparison. Rule: any
> A/B whose verdict is a byte-diff between two builds' dumps runs with
> taps (tap_writes.lua) or plain DUMPS only — never under GUARD_PROBE /
> -debug; if a probe is needed to find an address, find it first, then
> re-run the A/B clean.

**[VSR-155]** **`-debug` fire counts do not transfer to checksum timelines** — on collision-sensitive content the debug timeline plays a different match; attribute a moved baseline with a whole-work-RAM dump (`RAM:$FF0000-$FFFFFF`) on BOTH builds at a divergent frame and diff the bytes. (was [VSP-130])

> **Why** (was [VSP-130], the original's `docs/project/gotchas.md`):
>
> -debug fire counts do not transfer to checksum timelines on vs-CPU/chaos content — attribute divergences with DUMPS, not debug probes (14z-82c)
>
> The three moved don-mash `.sha1` baselines were first "attributed" by
> probing the new thunk under the guard (-debug): two replays showed ZERO
> fires and the third fired 3,000 frames AFTER its divergence onset — a
> contradiction that would have read as "the thunk is not the cause" and
> sent the hunt somewhere wrong. The documented caveat ("-debug runs are
> deterministic but NOT checksum-comparable") cuts deeper than checksums:
> on collision-timing-sensitive content (vs-CPU AI, input chaos) the debug
> timeline plays a DIFFERENT MATCH by the ten-thousandth frame, so its
> event counts say nothing about the run being attributed. The attribution
> that works: DUMPS=<frame>:ff0000-ffffff on BOTH builds at a divergent
> frame (replay.lua, non-debug, replay-exact) and diff the bytes — here: 3
> bytes, all in the $FF7Fxx dead-stack ghost window, zero live state = the
> ratified hook-cycle class, re-freeze licensed. Also paid for twice in
> one day: DUMPS writes land next to CHECKSUM_OUT, so two runs into one
> directory silently clobber the first dump — separate out dirs per leg.

**[VSR-156]** **A scripted motion input is NOT the move you named** — the buffer folds leading directions, scripted strengths are not authoritative, and a special's button press must OVERLAP the final direction frames; identify an activated move by measured EFFECTS (stock cost, seq id, spawned objects, the screen) and send disagreeing captures to the maintainer before building on the identification. (was [VSP-131])

> **Why** (was [VSP-131], the original's `docs/project/gotchas.md`):
>
> A scripted motion input is NOT the move you named — the buffer FOLDS leading directions, so identify by effects, never by the script (14z-101)
>
> The #109 native-reference hunt scripted "6236+2P" and confidently called
> the result the clone-mode EX; it was the ES — vs2's buffer reader kept
> the identified pattern 236+2P and IGNORED the leading 6 (the maintainer
> named the mechanism). Meanwhile a dp-shaped attempt whiffed entirely and
> a 263 shape fired the real EX. Motion parsers are lenient in ways that
> make the SCRIPT'S name for an input worthless as an identification: two
> different scripted shapes can land the same move, and the shape you
> intended can land a different one. The rule: identify an activated move
> by its measured EFFECTS (stock cost, seq id, spawned objects, the
> screen), and when captures disagree with expectations, send them to the
> maintainer BEFORE building on the identification — one reply named three
> moves this session. Related trap, same family: the 87 rig's scripted-LK
> "crashes where the real LK does not" (scripted strengths are not
> authoritative either).

**[VSR-157]** **A 1P-arcade rig is silently pinned to the ARCADE DRAW** — any timing change re-rolls its opponent and stage, so a frozen fight-derived value describes a fight nobody's build has run; PIN the opponent (2P + early-window pokes) and, when a frozen-value audit goes red, check WHICH match it measured before how the fight went. (was [VSP-132])

> **Why** (was [VSP-132], the original's `docs/project/gotchas.md`):
>
> A 1P-arcade rig is silently pinned to the ARCADE DRAW — any timing change re-rolls its opponent and stage (14z-103, GitHub #110)
>
> `audit_fg_damage`'s frozen 10/10 and `audit_pool_free_byte`'s pcosmo
> formation window were measured on 1P rigs whose opponent came from the
> arcade CPU draw. The 14z-87 batch (voice-borrow + beep sound members)
> shifted match-setup state enough to re-roll that draw — merged6 fights
> char 0x0C on stage 0x12, merged7 and every build since fight char 0x00
> on stage 0x0E — so both audits' constants silently described a fight
> nobody's build has run for five generations (fgA measured 24-vs-10
> against a DIFFERENT victim; the cosmo rig's scripted motions spent the
> stock on a different move against the new opponent and formed zero
> satellites). The behavioral first-divergence was at MATCH START
> (opponent spawn X), not mid-fight cycle skew — a draw change, not
> drift. The rule: an audit that freezes fight-derived values must PIN
> the opponent (2P + early-window pokes, the replay-80 shape), never
> inherit the arcade draw; and when a frozen-value audit goes red on a
> build its own generation column says was green, check WHICH match it
> is measuring before checking how the fight went. Re-derived rigs:
> hui/74, hui/75 (2P dummy, bit-identical across generations), pcosmo ->
> 106_pyron_cosmo_clash.

**[VSR-158]** **A fixed-frame rig verified on ONE character whiffs on another** — reach, knockdown arcs, down windows and wake timing are per-character on BOTH sides; a multi-character audit measures (input, frame) pairs per leg and its checker REFUSES to judge a leg whose setup event did not happen. (was [VSP-133])

> **Why** (was [VSP-133], the original's `docs/project/gotchas.md`):
>
> A fixed-frame rig verified on ONE character whiffs on another — reach, knockdown arcs, down windows and wake timing are ALL per-character, on BOTH sides (14z-104)
>
> Three instances in one session, each first misread as a build finding:
> Phobos' standing LP WHIFFS at the spacing where Demitri's connects (the
> downwin audit's first red); heavies cannot be mashed into a down window
> (each whiff's recovery eats the next attempt — the "wider mash" fix made
> even the control red); and Victor's sweep throws the victim clear out of
> down-attack reach while Demitri's keeps them close. On the VICTIM side
> the same applies: Phobos wakes from a knockdown in 24 frames (window
> f3086-3092) where Victor lies until ~f3145. The rule extends
> rig-must-produce-the-real-event: a multi-character audit needs per-leg
> (input, frame) pairs MEASURED per character, and its checker must REFUSE
> to judge a leg whose setup event did not happen (whiff/no-knockdown),
> never pass it and never report it as the surface failing. All four new
> combat audits (timeout/downwin/throws/down_attack) carry that refusal.
> … *(continues in the original's document)*

**[VSR-159]** **An entry-set A/B needs a QUIET-FRAME presence profile** — an entry present far from the event is scenery (the stock-meter pips read as beam segments and cost a window session its first hours). (was [VSP-134])

> **Why** (was [VSP-134], the original's `docs/project/gotchas.md`):
>
> An "attack-only" entry-set A/B needs a QUIET-FRAME presence profile, or a constant fixture becomes your defect (14z-102)
>
> The 14z-101 (8) #109 A/B compared per-clone OBJ entry sets "at the
> attack" on both legs and read the cycling `0x4302/0A/0C` vs
> `0x4D00-0x4D0C` pieces as the beam segments 0xA00 low. They were the two
> games' STOCK-METER PIP animations — present at EVERY frame of both runs,
> and the piece counts even matched the rigs' poked stock counts (ours 3,
> native 5). One dump at quiet frames (pre-attack, post-cooldown) would
> have excluded them in seconds; instead the misread survived into the
> window prep as located sub-defect "A1" and cost the window session its
> first hours. The rule: before attributing any entry to an EVENT, profile
> its presence across frames far from the event on BOTH legs — an entry
> present in quiet frames is scenery, whatever its codes suggest. (Same
> family as "the observation window bounds the claim", RH-19 — here the
> window was only ever placed ON the event.)

**[VSR-160]** **Cross-emulator POSITION A/B compares RELATIVE offset, never absolute x** — the two builds sit at a fixed ~21px global shift; `p2 − p1` was 42 on both legs while absolute x "proved" the rig incomparable; pre-event agreement is the free positive control. (was [VSP-135])

> **Why** (was [VSP-135], the original's `docs/project/gotchas.md`): Absolute x "proved" a cross-emulator rig incomparable and lost a session (14z-72); the relative offset agreed on both legs (14z-73).

**[VSR-161]** **Cross-game pixel A/B aligns by DISPLAYED RECORD, not frame** — the legs skew 1-2 frames (each game's default play mode and RNG draws differ unless pinned, [VSE-84]), so same-frame snapshots compare different anim records; align on the victim's cursor value, and remember the sibling games' VANILLA characters have differing script data. (was [VSP-136])

> **Why** (was [VSP-136], the original's `docs/project/gotchas.md`):
>
> Cross-game A/B pixel comparison: align by DISPLAYED RECORD, not frame
>
> Two false "garble" verdicts in one session (14z-9): the engines skew
> 1-2 frames *(CORRECTED 14z-158, #135: the LEGS skew — each game's default play mode,
> vsav2 TURBO against vsavj NORMAL, and their RNG draws; pinned, they do not, [VSE-84])*,
> so same-frame snapshots can compare DIFFERENT anim records
> — a mid-flail pose against a settle pose reads as scattered garbage.
> Align by the victim's cursor value (dump +0x1C, snapshot the frames
> where both games display the SAME mapped node). Also: the sibling
> games' VANILLA characters have differing script data (vs2-Victor
> commands hold poses in the opposite order from vsavj-Victor) — a
> divergence in what the two games DISPLAY is not automatically a port
> bug; check who commands the difference before blaming the port.

**[VSR-162]** **A soak must assert the mechanism it exists to exercise fired** — scripted ES pairs silently fell back to LP while the DP-spam gate stayed green on END-clean; and a hit-path defect fires per COLLISION, not per frame, so pair a soak with a FIRE CENSUS on the dispatcher. (was [VSP-137])

> **Why** (was [VSP-137], the original's `docs/project/gotchas.md`): A no-crash soak silently lost the behaviour it was written to exercise and stayed green; soak length is not coverage (14z-82b).

**[VSR-163]** **Validate a fix against the reporter's EXACT input and A/B fix-on/fix-off on the reproducing replay** — snapshot every phase of a cyclic effect; "the metric improved" is not "the pixels changed". (was [VSP-138])

> **Why** (was [VSP-138], the original's `docs/project/gotchas.md`):
>
> Phantom fixes: validate against the USER'S repro, at the RIGHT frames
>
> 14z-7 shipped a fix validated by (a) a probe move that only resembled
> the reported one and (b) snapshots taken only at zap frames, where the
> flash silhouette hides the victim's body. The fix cleared buckets the
> real defect never reads; a controlled A/B on the correct move (replay
> 33) showed pixel-identical output with the fix on and off. Rules paid
> for: reproduce with the reporter's EXACT input first; snapshot every
> phase of a cyclic effect (zap AND between-zap); and before shipping a
> visual fix, A/B the fix-on/fix-off builds on the reproducing replay —
> "the metric improved" (buckets zeroed) is not "the pixels changed".

**[VSR-164]** **Verify at the RENDER layer before believing the RAM layer** — an OBJ-record dump and frame snapshots (both poke-capable) answer "is it on screen?" in one run; correct-looking writes on the ONE object you watch say nothing about objects never spawned. Reach for them before the third RAM-layer iteration. (was [VSP-139])

> **Why** (was [VSP-139], the original's `docs/project/gotchas.md`): Rounds of RAM-layer fixes looked right on the watched object while the effect's other objects never spawned; one render-layer run showed it.

**[VSR-165]** **Know where in the frame each instrument samples, and replicate the gate's exact mask set** — the masked checksum samples EARLIER in the frame than frame-done dumps, so data staged mid-frame diverges in checksums while dumps match: inspect at the checksum's sample point (or diff checksum halves, then trace writes); per-frame UNMASKED checksums (and dumps spanning `RAM:$FF043C`) READ the QSound latch and perturb the run, so mixed-mask runs are not comparable. (was [VSP-140])

> **Why** (was [VSP-140], the original's `docs/project/gotchas.md`):
>
> Mid-frame transients and perturbing probes (win-palette post-mortem)
>
> Two diagnosis traps from session 14t, each of which produced a round of
> false conclusions before the mechanism emerged:
> 1. The masked checksum samples EARLIER in the frame than DUMPS do. A
>    divergence in data that is staged into work RAM mid-frame and
>    reused/cleared by frame-done is checksum-visible but INVISIBLE to
>    frame-done dumps — comparing dumps "at the divergent frame" showed
>    byte-identical RAM while 3229 frames of checksums diverged. To
>    inspect a masked-gate divergence, compare at the checksum's sample
>    point (or diff the checksum halves to localize, then trace writes).
> 2. Per-frame UNMASKED checksums (and dumps spanning $FF043C) READ the
>    QSound handshake latch and perturb the run — both builds get
>    perturbed identically, so a live patched-vs-vanilla comparison can
>    look clean while the gate's masked (non-perturbing) runs genuinely
>    diverge. Legacy comparisons must replicate the gate's exact mask
>    set. (This also likely explains the session-14 standing-watch gate
>    anomaly: mixed-mask runs are not comparable.)

**[VSR-166]** **A RENDER verdict from a gfx-free build is VOID** — a program image over a zero-filled graphics overlay answers RAM questions only; palette and work-RAM dumps are gfx-free-safe, pixels are not. (was [VSP-141])

> **Why** (was [VSP-141], the original's `docs/project/gotchas.md`):
>
> three traps from the #105 fix arc (paid: 14z-99 (2))
>
> **A RENDER verdict from a gfx-free build is void — and it fails by
> looking like a new defect.** The merged1-style pack (program image over
> the zero-filled overlay) is the right probe for RAM-level questions and
> the WRONG one for anything drawn from tenant art: the win-screen
> portrait and the VS-splash side art drew blank/pale on the #105 fix
> probe, which read as "the fix half-works" and "a SECOND sel-indexed
> surface is white" — both observations were VOID (the full-gfx probe
> renders both correctly). Ask what the verdict READS: palette/work-RAM
> dumps are program-data-driven and gfx-free-safe; pixels are not.

**[VSR-167]** **Resolve placements PER TENANT** — a lookup hardcoding one tenant's region mapped two tenants through the wrong dst/src and published a false mismatch that shaped a fix design; "the delta differs per tenant" is a smell about the mapping before it is a finding about the game. (was [VSP-142])

> **Why** (was [VSP-142], the original's `docs/project/gotchas.md`):
>
> two traps from the #104 re-measurement — both produced a CONFIDENT WRONG ANSWER from a working instrument (paid: 14z-99)
>
> **A placement lookup that hardcodes ONE region name is wrong on a MERGED
> build, and it fails by pointing somewhere plausible.** `placements.json`
> carries `anim` (Donovan), `anim@huitzil` and `anim@pyron`. A tenant
> verdict resolved through `placements["regions"]["anim"]` unconditionally
> therefore maps Huitzil and Pyron through DONOVAN's dst/src — arithmetic
> that succeeds and yields an address in the right ballpark. Measured cost:
> `audit_don_grab_pose.sh` reported "Pyron's held record mismatches too,
> ours 0x26654C vs native 0x26614C" in 14z-98 (7); through `anim@pyron` it
> maps to `0x26614C`, IDENTICAL to native. That false datum was published to
> the issue and then shaped a fix design ("a DIFFERENT delta than Donovan's
> -> per-victim wrong row selection"). Resolve the region PER TENANT, and
> treat "the delta is different for each tenant" as a smell that the mapping
> is wrong before it is a finding about the game.

**[VSR-168]** **A cited address in a session log is a CLAIM** — check the source row AND read the built image at the call site before building a theory on it; one misread hex digit cost a session plan and survived two summaries. (was [VSP-143])

> **Why** (was [VSP-143], the original's `docs/project/gotchas.md`): One misread hex digit in a logged address cost a session plan and survived two summaries.

**[VSR-169]** **A pool measurement is a claim about ONE pool** — decode the dispatch walker's own base+stride from the opcode view before trusting that a slot-level fact transfers to a family; two pools shared a layout and the census numbers looked healthy. (was [VSP-144])

> **Why** (was [VSP-144], the original's `docs/project/gotchas.md`):
>
> A pool measurement is a claim about ONE pool — decode the walker first (14z-85)
>
> The 14z-84 owner-tag census measured $FFB800 (0x80-stride) and its
> conclusion was carried into the ruling brief as "the tag byte" — but
> the 59-75 family the tag serves lives in $FF9400 (0x100-stride, walker
> head 0x54458 `lea ($1400,A5),A6`, stride `lea ($100,A6),A6`). The two
> pools share a layout family, the same replays exercise both, and the
> census numbers looked healthy — nothing about the measurement itself
> said "wrong pool". What said it: decoding the DISPATCH WALKER's own
> base+stride from the opcode view (two instructions), plus ram.md's
> $FF9400 row and the 14z-82 dynamic census's own $FF94xx stamp
> addresses, all already on record. Before trusting that a slot-level
> fact transfers to a family, decode the family's walker. Re-measured on
> the right pool the byte WAS free — the mechanism survived, but only by
> luck, and the $FFB800 result turned out doubly wrong (see the platform
> byte-lane entry).

**[VSR-170]** **A0-at-write is post-increment** — subtract the movem batch size from EVERY logged value before taking min/max of a read window; the misread placed a fix on dead ground for a playtest round. (was [VSP-145])

> **Why** (was [VSP-145], the original's `docs/project/gotchas.md`):
>
> A0-at-write is post-increment — SECOND payment (14z-18 tail row)
>
> The "accent super-cycle phase 2 reads 0x39FC00-0x39FC3F" conclusion
> derived a 0x40-byte window from two logged A0 values without
> subtracting the movem batch size: the real march reads exactly T0
> (0x39FBE0-FF) and T1 (0x39FC00-1F), overlapping by design (the slide
> IS Jedah's glow animation). The misread placed a "tail" replacement on
> dead ground and left the visible bug alive through a playtest round.
> When deriving a read WINDOW from tap A0 values: subtract batch size
> from EVERY logged value first, then take min/max.

**[VSR-171]** **A same-slot "vanilla control" controls nothing** — to test "is X per-char?", the control varies the CHARACTER, not just the build. (was [VSP-146])

> **Why** (was [VSP-146], the original's `docs/project/gotchas.md`): A control that kept the slot and changed only the build could not answer a per-character question.

**[VSR-172]** **The `-debug` write-trace never disagreed with the non-debug dumps** — a MAME watchpoint logs REGISTERS, so a "value written" quoted from a trace is a table lookup that must name WHICH IMAGE it read; check the build's op list for the table's range before declaring it unpatched; when in doubt take the non-debug write tap. (was [VSP-147])

> **Why** (was [VSP-147], the original's `docs/project/gotchas.md`):
>
> The -debug write-trace and non-debug dumps can DISAGREE about one write (14z-100; RESOLVED 14z-101 — they never disagreed)
>
> On the SAME build and replay, `trace_writes.lua` (-debug) recorded the
> fighter's `+0x18` receiving table[0x11]=0x6000 from the vanilla init,
> while non-debug dumps read 0x1000 at the same phase. **RESOLVED
> (14z-101, GitHub #108): there was no instrument disagreement.** The
> FBNEO_HTAP tap showed the same single writer (`PRG:0x282C0`) writing
> 0x1000 on the canonical timeline — the -debug leg's "0x6000" was never
> OBSERVED, it was INFERRED by reading the table from the PRISTINE opcode
> view, and our own `obj_bank_word_slot` ops patch that table row
> (0x282F6 := 0x1000, deliberate). Two lessons, both old ones biting
> together: a MAME watchpoint logs REGISTERS, not the datum (14z-76), so
> any "value written" quoted from a -debug trace is a table lookup in
> disguise — and a table lookup must name WHICH IMAGE it read. Before
> declaring a table "not covered by any patch op", grep patch.json for
> the table's address range; that archaeology takes one command and would
> … *(continues in the original's document)*

**[VSR-173]** **A measurement returning a clean null is a bug report about the measurement** — capstone mnemonics carry a size suffix (compare on the stem); a register-dataflow walk cannot see a mask applied in place to memory (enumerate the ADDRESSING MODES that can touch the value); two agreeing methods sharing a premise are one method. (was [VSP-148])

> **Why** (was [VSP-148], the original's `docs/project/gotchas.md`): A disassembler's size-suffixed mnemonics made an equality test match nothing, and a register-dataflow walk missed two masks applied straight to memory for a whole session.

**[VSR-174]** **One input player, staged the canonical way** — a frame number from one instrument is not a frame number from another unless both stage inputs identically; the canonical player checksums frame N and THEN stages the inputs for N+1, the frozen expectations were measured that way, and the rebuild's one input player stages the same way; a frame number quoted from the original's probe-family instruments is one frame early. (was [VSP-149])

> **Why** (was [VSP-149], the original's `docs/project/gotchas.md`): Half the original's Lua instruments staged inputs at the start of the callback, one frame earlier than its replay player: every divergence-attribution instrument was canonical, the probe family was not (14z-90, #10).

**[VSR-175]** **For an out-of-range index, read the CONSEQUENCE before valuing any evidence** — name the danger windows (entries vsavj's table cannot answer but vs2's can), say which tenant data lands in one (report, never filter), attribute a live dispatch to the MOVE (prove the watch fires on everything before trusting its quiet); "no crash" clears a LOUD entry completely and a SILENT one not at all. (was [VSP-150])

> **Why** (was [VSP-150], the original's `docs/project/operations.md`): Two crashes had already landed in the same danger window before anyone asked who drives it (14z-78).

**[VSR-176]** **The DF palette-seq block census is MEASURED, never derived from the request table** — the routine is conditional; the resolver masks to 12 bits, so a tenant block must sit inside the vanilla range and cannot go in the WIDE extension space. (was [VSP-151])

> **Why** (was [VSP-151], the original's `docs/project/operations.md`):
>
> THE DF PALETTE-SEQ BLOCK CENSUS — measured, and it had to be (measured 14z-79b)
>
> Which palette-seq ids each character requests in Dark Force, measured on
> vanilla vsavj with `$FF802E`=1 asserted per row:
> `docs/game/engine_internals.md` "THE DARK FORCE PALETTE-SEQUENCE BLOCKS".
> Occupied: `0x1E-0x21` Bulleta, `0x26/0x27` Demitri, `0x44-0x47` Zabel,
> `0x6F-0x72` Bishamon+Oboro, `0x264-0x267` Q-Bee, `0x29C-0x2A0` char 0x12
> (five ids), and `0xAA-0xAD` **Sasquatch** — the corpus census
> `tests/expected/df_palette_seq_census.txt` (14z-118 (14)); this line said
> … *(continues in the original's document)*

## D.7 Gate scoping — building a comparison gate that survives review

**[VSR-177]** **A ported character's reference is the SOURCE GAME, and a second leg is an INSTRUMENT CHECK, never a baseline** — every throw/move is character-specific, so no other character can say what this one should look like; what a second leg can do is prove the two games agree on the coordinate convention, index space, rig timing and poke path. Say which of those it demonstrates: the "legacy control" here proved *ported row → ours matches native*, NOT that VS and VS2 natively agree. (was [VSP-167])

> **Why** (was [VSP-167], the original's `docs/project/gate_scoping_method.md`):
>
> **A ported character's reference is the game it came from, and a
> "control" leg is an INSTRUMENT CHECK, never a baseline for the thing under
> test.** For a tenant the only vanilla reference is `vsav2` — not VS, and not
> another character: *every throw is character-specific, so no second character
> can tell you what this one should look like.* What a second leg CAN do is
> establish that the comparison is readable at all — that the two games agree on
> the coordinate convention, the pose-index space, the rig's timing and the poke
> path — by running content whose behaviour is already pinned. Label it as an
> instrument check; labelling it a "control" invites the reading that it is a
> reference, which is a category error a reviewer will (rightly) reject.

**[VSR-178]** **Check the mechanism can PRODUCE the observable, and exclude the ones it cannot** — the capture positioner writes only `+0x10/+0x14`, so a POSE difference is a second unnamed mechanism, not evidence about it. Cross-generation art is the same trap: a legacy victim is VS's version on our leg and VS2's on the native one, so the victim's PIXELS are never evidence about the port — compare the logical slot through each game's own index table and say in the gate that pixels are excluded. (was [VSP-168])

> **Why** (was [VSP-168], the original's `docs/project/gate_scoping_method.md`):
>
> **Before attributing a difference to a mechanism, check the
> mechanism can PRODUCE that observable — and exclude observables it cannot.**
> The capture positioner at `PRG:0x02802E` writes only the victim's `+0x10/+0x14`.
> It therefore cannot change which sprite is drawn, so a POSE difference is not
> evidence about it, and a first analysis that reported one had a second
> mechanism in play it had not named.

**[VSR-179]** **Compare the ORDERED sequence of states, not sets; assert structure and REPORT timing** — a set comparison is blind to order and dwell. Assert which states in which order, and damage as (amount, state); report dwell, frame numbers and the ours/native ratio, because unless the play mode and the RNG are pinned the two legs run at different rates ([VSE-84]) and any frame-indexed assertion is a trap. (was [VSP-169])

> **Why** (was [VSP-169], the original's `docs/project/gate_scoping_method.md`):
>
> **A comparison of SETS is blind to order and dwell; compare the
> ORDERED sequence of states, and report — never assert — the timing.** The
> first cut compared the set of position offsets and the sequence of *distinct*
> poses. Two runs can visit the same states in a different order and pass that.
> Replaced by the ordered `(pose, dx, dy)` sequence with dwell counts over every
> sampled frame, which is what actually says "the same thing happened".

**[VSR-180]** **Refuse to judge a leg that did not produce the event, and assert any RESOURCE it consumes** — an ES move with an empty meter degrades SILENTLY to its normal version and returns healthy-looking numbers for the wrong move; the discriminator is the stock dropping, with the non-ES replay under the same poke not dropping it. A leg with no event is VOID, neither pass nor fail. (was [VSP-170])

> **Why** (was [VSP-170], the original's `docs/project/gate_scoping_method.md`):
>
> **A comparison gate must refuse to judge a leg that did not
> produce the event, and must assert any RESOURCE the event consumes.** Two
> distinct ways this bit one gate:

**[VSR-181]** **Measure the cost of widening before arguing about the sample, and re-check every constant the narrow version froze** — one victim vs eighteen was 27.7 s vs 186 s here, which ended the discussion. Widening then found a residue the narrow gate could not see AND exposed a frozen arc constant as victim-specific (it was one victim's number all along). Where a widened expectation turns out UNIFORM, freeze the one shape rather than N literals and read the uniformity as evidence. (was [VSP-171])

> **Why** (was [VSP-171], the original's `docs/project/gate_scoping_method.md`):
>
> **When the sample is a judgement call ("one victim or all
> eighteen?"), MEASURE THE COST before arguing about it — and when you widen,
> re-check every constant the narrow version froze.** Measured here: one victim
> 27.7 s, all eighteen 186 s at 6-way parallelism — ~6.7x the time for 18x the
> coverage, which ended the discussion.

**[VSR-182]** **Diff a strengthened gate against what it REPLACED** — widening silently dropped the arc comparison, the one assertion that had just retired a nine-session-old suspicion. Nothing announces a check you delete. (was [VSP-172])

> **Why** (was [VSP-172], the original's `docs/project/gate_scoping_method.md`):
>
> **A rewrite that strengthens one assertion must be diffed
> against what it REPLACED, because the check you silently drop is the one that
> earned its keep.** Widening this gate dropped the post-release arc comparison
> — the single assertion that had just retired a nine-session-old suspicion in a
> replay header. It was restored, and its frozen value corrected in the same
> pass. Nothing announced its absence; only re-reading the old version did.

**[VSR-183]** **Capture the picture BEFORE writing the sentence about it** — a correct measurement plus an invented direction word is a false claim, and the SENTENCE is what the next session acts on. Put a known-good pair in the same sheet so the reader validates the comparison by eye, and name the columns that are NOT comparable. (was [VSP-173])

> **Why** (was [VSP-173], the original's `docs/project/gate_scoping_method.md`):
>
> **Capture the picture BEFORE writing the sentence about it, not
> merely before concluding a defect exists.** A correct measurement plus an
> invented direction word is a false claim, and it is the SENTENCE — not the
> number — that the next session acts on. One finding here was measured twice by
> independent methods and then described as "hurls the victim ~130 px overhead
> and drops them behind", which the captures refuted: the raw `dy`/`dx` signs had
> been read as up/behind without ever establishing the engine's screen
> convention. Put a legacy/known-good pair in the SAME capture sheet so the
> reader can validate the comparison by eye in one second, and say plainly which
> columns are NOT comparable (here: frame-aligned columns, because our hold runs
> longer).

**[VSR-184]** **A "divergence" appearing exactly on the rows with a special resolution rule is the RESOLVER** — all three tenant victims "diverged" with unresolved pose pointers because a tenant victim on our leg is held on the PLACED copy of vs2's table, not vsavj's. The rule was already written in `audit_don_grab_pose`; not reading it first bought one alarming false result. (was [VSP-174])

> **Why** (was [VSP-174], the original's `docs/project/gate_scoping_method.md`):
>
> **A "divergence" that appears on exactly the rows with a special
> resolution rule is the resolver, not the build.** Widened to all eighteen
> victims, this gate reported that all three TENANT victims diverged — and their
> pose pointers came back unresolved. That `?` was the tell: a tenant victim on
> our leg is held on the PLACED copy of VS2's table, not vsavj's, and the
> analysis had used vsavj's for everyone. With the documented rule applied, the
> unresolved count went to zero and every tenant matched. `audit_don_grab_pose`
> had already written that rule down; the cost of not reading it first was one
> alarming and entirely false result.

**[VSR-185]** **A gate is SOLO-SPECIFIC only if a single-tenant build is the SUBJECT of its assertion — everything else runs on the MERGED build, the one that ships** — a solo build used as a REFERENCE LEG, a fixture or a rig convenience does not qualify. "Solo behaves like merged" is measured FALSE: merged deviated from the single-tenant builds in eight places at 14z-91, and the mechanism is named — merged hook chains are longer (N=3), so cycle skew can move a flicker frame or a window end. A solo-specific gate is OUT of release scope; if it has no meaningful merged form, deprecate it permanently and keep it as history. A gate that resolves its expectation set by fingerprint cannot be re-pointed until the merged build is registrable. (was [VSP-175])

> **Why** (was [VSP-175], the original's `docs/project/gate_scoping_method.md`):
>
> **A gate is SOLO-SPECIFIC only if a single-tenant build is the
> SUBJECT of its assertion. A single-tenant build appearing as a REFERENCE LEG,
> a fixture or a rig convenience does not qualify — and every gate that is not
> solo-specific runs on the MERGED build at release, because the merged build is
> what ships.** (Maintainer-ruled 2026-09-04, 14z-132.) The maintainer's own
> statement of the belief: *"regardless of how low the odds of a change between
> a solo build and the merged build are for a given test, these odds are not
> zero, so the test is brittle intrinsically. However, unless they are specific
> to solo builds, tests on solo builds are likely to hold value even now,
> therefore they likely should be run but on the merged build."*

**[VSR-186]** **When the defect class is an OMISSION, ENUMERATE — targeted testing structurally cannot reach it** — a missing or mis-scoped table row produces no symptom to steer toward, so no amount of symptom-driven testing finds it. Both capture-geometry defects were omissions found by inventories, not by play or rigs: Pyron's attacker row `0x11` (the bank-map ownership audit, 14z-130) and Donovan's victim entry `[0x0F]` (the full matrix's first run, 14z-143, after seventeen sessions of throw work). For any table the port claims to own row by row, the gate is the FULL CROSS-PRODUCT against the reference, not a sample — and a green targeted gate covering three cells says nothing about the other 637. (was [VSP-179])

> **Why** (was [VSP-179], the original's `docs/project/gate_scoping_method.md`):
>
> **A defect that is a MISSING or MIS-SCOPED table row has no
> symptom to steer toward, so no amount of targeted testing finds it.** Both of
> the capture-geometry defects this project has found are omissions, and neither
> was found by play or by a rig: Pyron's attacker row `0x11` was a row nobody
> claimed (surfaced 14z-130 by the `bank_map` ownership audit — an INVENTORY —
> and measured 14z-131), and Donovan's victim entry `[0x0F]` is a correct fix
> applied at the wrong scope (surfaced 14z-143 by `audit_capture_matrix.sh` on
> its first run, after seventeen sessions of throw work had not). Nothing
> crashes, nothing renders obviously wrong, and the cell is only reachable in one
> matchup — so a symptom-driven test never points there. **For any table the port
> claims to own row by row, the gate is the FULL CROSS-PRODUCT against the
> reference, not a sample.** The corollary for reading a green targeted gate:
> `audit_pyron_capture_block` was green for its entire life while Pyron's row was
> unported, because it asserted the OBSERVED difference; a gate that covers three
> cells says nothing about the other 637.

**[VSR-187]** **ANCHOR, THEN ENUMERATE** — pay the expensive measurement once to prove the cheap one predicts it, then run the cheap one over the whole space. One capture cell behaviourally is ~4 minutes of emulator; 640 cells statically is ~2 seconds, and the licence is that ONE cell was measured both ways with no shared premise (work RAM 14z-131, ROM bytes 14z-142) and agreed exactly. Name the anchor in the gate's header, keep the behavioural gates alive as what keeps the licence honest, and make the static gate state what it does NOT claim. A SCOPED fix (by track, profile or slot) must be checked against everyone else who indexes what it rewrites, and a comment asserting harmlessness is a claim to test. And an ALARMING result is as much a bug report about the instrument as a clean null is ([VSR-173]'s mirror): the first matrix run's four "differing" attackers were exactly the four whose spacing was under its fixed record count, and that is now the gate's own must-fire control. (was [VSP-180])

> **Why** (was [VSP-180], the original's `docs/project/gate_scoping_method.md`):
>
> **ANCHOR, THEN ENUMERATE: pay the expensive measurement once to
> prove the cheap one predicts it, then run the cheap one over everything.** The
> behavioural comparison for ONE capture cell is ~4 minutes of emulator; the
> static comparison for **640** cells is ~2 seconds. What licenses substituting
> the second for the first is that one cell was measured BOTH ways with no shared
> premise — work RAM in a running game (14z-131) and ROM bytes (14z-142) — and
> they agreed exactly, deltas and poses. State the anchor in the gate's header
> and keep the behavioural gates alive as the thing that keeps the licence
> honest; the static gate must say what it does NOT claim. This generalises past
> keyframes: it is the shape for any claim of the form "our table equals the
> reference's", where the data is cheap to compare and the behaviour is not.

## D.6 Attribution — how a wrong conclusion was reached, and the cheaper method

**[VSR-188]** **A symptom grouping is a HYPOTHESIS — test it member by member, cheapest first** — write "possibly one root", ask what measurement would DISTINGUISH the members, and check the cheap member (one playtest) before the expensive one; never carry a filter (palette, bank, code range) across effects; look at a capture before sending it. (was [VSP-153])

> **Why** (was [VSP-153], the original's `docs/project/gotchas.md`): Three sessions treated an effect family's symptoms as one root without testing its members (14z-71).

**[VSR-189]** **Cross-build A/B is the cheapest attribution and is routinely skipped for analysis** — every registered build is playable by its key; bisect the BUILDS before analysing the code; a launcher never rebuilds into an existing output, so a pruned rompath is never silently refilled. (was [VSP-154])

> **Why** (was [VSP-154], the original's `docs/project/gotchas.md`): The cheapest attribution available, playing the kept builds side by side, was skipped for code analysis that it would have settled.

**[VSR-190]** **PRIOR ART FIRST** — before porting a per-character subsystem for tenant B, read that subsystem's section of `docs/game/engine_internals.md` and diff tenant A's data against what you are about to write; a maintainer's "this looks like the thing we fixed for X" is a high-confidence pointer, not a hypothesis; a check that is self-labelling beats one that only proves internal consistency. (was [VSP-155])

> **Why** (was [VSP-155], the original's `docs/project/operations.md`):
>
> PRIOR ART FIRST — check the subsystem doc before re-deriving (14z-68m)
>
> Huitzil's win screen was re-derived from scratch and got two of three
> pieces wrong; Donovan's identical solution had been sitting in
> STATE.md since 14z-45. The analysis existed, it just was not
> DISCOVERABLE from "I am working on tenant X's screen Y".

**[VSR-191]** **A REPLAY'S NAME IS A CLAIM ABOUT THE BUILD** — an artifact whose meaning depends on the build needs asserting like any instrument constant ([MSC-52]); the expectation class and the gate that names the replay in words are the cheap assertions; consult them before scoping a measurement on a filename. (was [VSP-156])

> **Why** (was [VSP-156], the original's `docs/project/gotchas.md`):
>
> A REPLAY'S NAME IS A CLAIM ABOUT THE BUILD (paid: 2026-08-24, 14z-107)
>
> `tests/replays/11_pick_donovan.rpl` **does not pick Donovan** on any build
> after 14z-64's M3a de-substitution. It walks to wheel slot `0x0F`, which was
> Donovan only while he was SUBSTITUTED over Jedah; post-M3a the tenants sit at
> their native ids (Donovan `0x13`, Huitzil `0x10`, Pyron `0x11`) on appended
> cells, and slot `0x0F` is plain **Jedah** again. The filename outlived the
> fact by dozens of generations.

**[VSR-192]** **Root-causing a stochastic crash: determinism first, vector+address second, history third, conditional register probe last** — keep ANY deterministic repro as the lab rat (contamination matters for the PATH, not the mechanism), read the fault address's parity, take a history of the stream, then a probe conditioned on the faulting register value; extend the instrument the moment it cannot name what you need. (was [VSP-157])

> **Why** (was [VSP-157], the original's `docs/project/gotchas.md`): The #99 hunt made its first repro deterministic and then interrogated the corpse (14z-109).

**[VSR-193]** **Never chain "the fix" from a poke-contaminated mechanism when a field recording exists** — win-fast rigs never give a CPU opponent's AI time to reach its rarer scripts; the first natural-path capture beat two shipped fixes ([VSR-19], [VSR-95]). (was [VSP-158])

> **Why** (was [VSP-158], the original's `docs/project/gotchas.md`):
>
> **How to apply.** (1) A bank-family table whose upper half duplicates the
> lower is NOT free for tenants by accident — it is free ON PURPOSE only if
> the port fills the tenant rows; audit every `stride 0x80` table for
> "parked" status when a tenant misbehaves ONLY under CPU control. (2) Rigs:
> `audit_don_vs_cpu` mashed and won fast, so the AI never reached the script;
> the maintainer's rig (win fast, then KEEP AWAY and give the CPU time)
> crashed every time. A CPU-behaviour soak must give the opponent TIME, not
> hits. (3) Capture with the game's own exception record (`$FF0000` write
> tap, `tools/run_inp_guarded.sh`) on a hand-played `.inp` — the first natural-
> path capture beat two fixes derived from a poke-contaminated one. **(4) The
> tooling was never the gap — its SYSTEMATIC use was:** WIDE_RECORD existed
> since 14z-9x, HANDOFF called a recorded report "a replay protocol", and no
> gate consumed one until `tests/test_inp_corpus.sh` (14z-111). Now law in
> CLAUDE.md §4 ("FIELD REPORTS ARE RECORDINGS").

**[VSR-194]** **A tenant replay is a claim about the build it was authored for, and a POSITION confound-check does not establish IDENTITY** — replay 48's `U,U,R` walks to slot `0x0F`, which is the tenant only on the SUBSTITUTED stock track; since the 14z-115 wheel separation a WIDE build puts the tenants on their own appended row, so the same path selects the cell's vanilla occupant and every number is that character's. GitHub #114 was opened on such a run, and its confound check PASSED — positions were byte-identical until contact, because Jedah and Donovan stand at the same x. Any gate that reads a number and calls it a tenant's asserts the tenant's `+0x60` hitbox base against the frozen roster-pairing bases FIRST (re-derived at every freeze, so it cannot rot), or forces the pick ([VSR-149]) so the wheel path is irrelevant. The wrong character is a false RED as readily as a false green. (was [VSP-163])

> **Why** (was [VSP-163], the original's `docs/project/gotchas.md`):
>
> A TENANT REPLAY AUTHORED FOR THE SUBSTITUTED WHEEL SELECTS A LEGACY CHARACTER ON THE SEPARATED (WIDE) WHEEL — and a POSITION confound-check cannot see it (paid: 14z-126b -> 14z-127, GitHub #114)
>
> Replay 48's P1 path is `U,U,R` from the default Demitri cell: on the
> SUBSTITUTED stock track that walks to slot `0x0F`, where the build puts
> Donovan. **Since the 14z-115 select-wheel separation the tenants live on
> their own APPENDED ROW**, so on a WIDE build the same path lands on the cell's
> vanilla occupant — **Jedah** — and every number the run produces is his.
> Measured 2026-09-02 on `merged-m14`: P1 `+0x60` = `0x000b0d2e` (jedah), not
> `0x003fa9d0` (donovan). **32 of the tenant-era replays carry this path**
> (the `17..65_don_*` / `_victor_*` family); all are correct on a stock build
> and all mis-select on a WIDE one. `tests/test_don_sound.sh` still ADVERTISES
> `SET=vsavjw` in its usage line for exactly this family — its WIDE mode is
> void, and is not invoked anywhere.

## D.3b Sprite lists and their art

**[VSR-195]** **The four questions of any ported effect, in order** — does the host have the CLASS row (vsav ships some effect-class rows as stubs; port the handler family and point the row at it with a code op, never a raw 32-bit poke, and the row must be dead in vanilla with a positive control); does it have the LIST TYPE (the drawer table can neither grow nor move — take over a type dead in vanilla with a `jmp` and retype the tenant's lists, discriminating on an ADDRESS RANGE with the host's original code as fallback and a tripwire a gate keeps at zero; never repoint a type whose handler is a bare `rts`, legacy dispatches it thousands of times); does the handler carry a game-specific CONSTANT (the per-handler code bias differs between the games — port a copy with the SOURCE bias plus the placement shift); where does the art's BANK come from (some types read the object's bank word, one hardcodes bank 1 — a character's effects may draw from more than one bank). (was [VSP-159])

> **Why** (was [VSP-159], the original's `docs/project/porting_sprite_lists.md`): Each of the four questions has cost the original a session at least once.

**[VSR-196]** **Strip placement: inventories are SPANS, not samples** — the strip-tile shift must be 16-aligned, equal to the bias baked into the ported handler (one number in two places, a gate freezes both), below the frozen ceiling and clear of the tenant's band, and never into the host's own bank 1 (measured occupied); take the whole span of the effect's family, because sampling native and sampling ours both missed strips. (was [VSP-160])

> **Why** (was [VSP-160], the original's `docs/project/porting_sprite_lists.md`): Sampling what the game draws gave a partial answer twice over: native sampling and our sampling both missed strips.

**[VSR-197]** **The order of work and the check at each step, ending with LOOKING** — class row (the tenant boot gate, legacy EXACT), list-type takeover (its gate and the effect-class-row audit with its tripwire), ported handler, tile span (the empty-tile audit ON THE EFFECT'S OWN REPLAY — on its defaults it never fires the effect and passes vacuously), then snapshots against native at matched frames; step 4 does not replace step 5, since real-but-wrong tiles pass the empty-tile audit at full opacity. (was [VSP-161])

> **Why** (was [VSP-161], the original's `docs/project/porting_sprite_lists.md`): Real-but-wrong tiles pass an empty-tile audit at full opacity, so the last step is always to look at it against native.
