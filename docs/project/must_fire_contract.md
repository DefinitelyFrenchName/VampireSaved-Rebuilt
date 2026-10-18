# The must-fire contract — a control is DECLARED, FIRED and EXECUTABLE

**What this document is.** The principle of record for how a gate in this repository proves it can fail: every
must-fire control is declared, reported when it runs, and executable as a mode that must reach the gate's own FAIL.
This repository's rule is `CLAUDE.md` [VSR-22] (was [VSP-181]); the law it serves is [VSR-21] (was [VSP-19], "Verdict
logic is itself tested").

**Where it comes from.** The original (`DefinitelyFrenchName/VampireSaved` at `6dee2be7`) holds the contract in
`docs/project/must_fire_contract.md` and its rule [VSP-181] in `docs/project/operations.md` (14z-147, step two of the
maintainer's ruling on the BBX finding). There the contract is a shell grammar — a header comment line read by one
regex, `CONTROL FIRED:` / `CONTROL DEAD:` lines at column 0, a `CONTROL=<name>` environment mode, a census of three
frozen classes — and a copy of BBX's R10/R29/R30 kept by hand, *independent but compatible* (maintainer, 2026-09-08),
evolving on its own since 2026-10-10 (14z-197, bbh is its own project). That grammar is the original's implementation
and is NOT carried here: the rebuild's harness (Python or Rust, [VSR-11]) declares controls in its own form. What
follows is what any form must deliver. The original's grammar, runners and census are the reference for what was
built and paid for.

## The three properties

**1. DECLARED.** A gate that asserts a property declares every must-fire control it runs, in one place the harness
reads, before anything runs: a NAME unique within the gate, a SHAPE, and a sentence saying what must fail and why that
proves the gate can fail. The shapes the original uses:
- *perturbed copy* — one byte or one value of a copied artifact changed;
- *shadow tool* — a copy of a tool with a line stripped, under a throwaway root; the tracked tool is never written;
- *known bad* — a synthetic input or a reference known to be wrong.

A gate that asserts nothing (a fixture generator, a registry lister) declares that it has no control, and why, so
silence is distinguishable from omission. A declaration the harness cannot read is not a declaration: a malformed
one declares nothing and is counted as nothing.

**2. FIRED.** When a declared control fails for its stated reason, the gate reports it FIRED, with the evidence. When
it does not — it passed, or failed for another reason — the gate reports it DEAD, with what happened. For a PASSING
gate the harness compares declared against fired: a declared control that did not fire, a DEAD control, or a firing
no declaration names turns the verdict into plain **FAIL**. There is no fourth verdict (maintainer, 2026-09-10:
*"NO fourth verdict"*). A gate with no declaration is counted as undeclared. A skipped gate ran nothing and a failed
gate is already red; neither is touched.

**3. EXECUTABLE.** FIRED is the gate's SELF-report, and a control can report it while testing nothing — it wrote a
value and asserted the value was not something else (14z-144 in the original, the case the maintainer raised). So
each declared control is also a MODE: running the gate in that mode applies the control's perturbation to the gate's
REAL input and runs to the gate's OWN verdict, which must be FAIL. The gate announces the mode, and refuses a name it
does not declare. The harness's verdict on a control run:

| verdict | when | meaning |
|---|---|---|
| HONOURED | the gate reached its own FAIL, no crash | the perturbation was caught |
| LIES | the gate passed, or skipped | the perturbation left the gate green — the control tests nothing |
| REFUSED | the gate refused the mode | declared, never read by the gate |
| DIED | a crash | a crash is not a verdict ([VSP-108] in the original) |
| TIMEOUT | the run timed out | as for any gate |

Anything but HONOURED is a failure of the run, named by its gate and control.

## The pattern that keeps a mode honest

Write each perturbation ONCE, and have both the control's own section and the mode use it: under the mode the
perturbed copy becomes the INPUT the main check reads. What the mode proves is then exactly what the control claims,
and the two cannot drift. A mode may run ONLY the part of the gate its perturbation reaches (the original paid ~8
minutes a mode re-running sections none of its perturbations touched, #268, 14z-199): the verdict is still the
gate's own. A gate whose control cannot run on a machine (a bench needing a missing tool) REFUSES the mode there
rather than passing it.

## When controls run (the original's rulings, to be re-decided against the rebuild's costs)

The original's cadence, each a ruling there: a mid-session commit runs the declared controls of every gate the commit
adds or changes (maintainer-ruled 2026-09-14, `DECISIONS_HISTORY.md` "Ruled 2026-09-14 (14z-154)"); a session close
executes every control of every gate it re-runs (#269, ruled 2026-10-12); a freeze and a release run every gate and
every control; the emulator tier's controls run at every RELEASE, not at the freeze sweep (maintainer-ruled 2026-09-10,
14z-148), because they multiply a tier measured in hours. The principle under the cadence: a control's cost is paid
where the gate or its real inputs changed, and in full at a freeze and a release.

## The retrofit census

The original freezes three classes: gates that DECLARE (grows only); declaring gates whose code reports no firing
(shrinks only); gates that mention a control in an older form and declare nothing (shrinks only — the debt the
retrofit works down, each pass ending with one strict run as the identity bar, every verdict unchanged before and
after). A gate ported into the rebuild arrives declaring ([VSR-22]; `SPEC.md` §5.3: a ported gate's declared controls
still fire).

## What the contract does not do

It does not prove a control is RIGHT — a control that fires on a perturbation unrelated to the property is a control
that lies about what it guards. That judgement is a review per control ([VSR-21]); the contract makes each control
findable, its silence loud, and its self-report checkable by execution. The rule-checker's Q4 holds the same line
for a claim: *"A control that proves the instrument sees a different thing than the claim rests on does not count as
covering it."* (`docs/project/rule_checker.md`).
