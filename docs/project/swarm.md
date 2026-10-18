# THE AGENT SWARM — its structure and its rules

**What this document is.** The structure of record of the agents that do this project's work, and the rules that bind
them: the orchestrator, the workers driven by specs, the rule-checker before an action, the deterministic hooks, and
forks. This repository's rules are `CLAUDE.md` [VSR-46] to [VSR-50]; `SPEC.md` §7 adopts the original's swarm
unchanged: *"A change to any of these needs a measured inadequacy, recorded as a ticket with the evidence."*

**Where it comes from.** The original (`DefinitelyFrenchName/VampireSaved` at `6dee2be7`): its
`docs/project/agent_architecture_scope.md` (GitHub #172 there, built in slices S1-S5 from 2026-09-23 to 2026-09-24
and closed on a green gate), its `DECISIONS_HISTORY.md` rulings (each cited below by its heading), and its
`STATE.md` "Standing rulings". The scope document's transcript census (§1), its platform probes (§2) and its slice
log (§5) are the original's measurements and history; the facts this structure rests on are summarised below with
their provenance, and the original holds the tables. The original's scripts (`tools/agent/*`) are its implementation;
the rebuild builds its own, to the same rules.

## The ask

The maintainer, 2026-09-22, verbatim from #172 in the original:

> *"the worrying part is not that you have not polled you own background work, it's
> that you explicitly chose earlier to poll to avoid waiting forever for tasks you
> would never see finish either because they finished too fast or because of how they
> reported. Polling is likely the good option. The problem is actually doing it."*

> * **orchestrator: fable 5.1 agent**, free to choose how best to work **BUT cannot
>   go against the will of checker agents**
> * **checker: one or more opus agents** (could be lowered to sonnet if no adverse
>   effects), **only knows the rules and ways of working, no project-specific context
>   to have no bias there**: only purpose is to check if the discipline is applied
>   (e.g. are the values measured, not inferred by the workers? is the orchestrator
>   applying the procedures it should?)
> * **workers: specialized, driven by very precise specifications and directives
>   given by the orchestrator.** There should be as few or many as deemed adequate by
>   the orchestrator at any given moment. By default they should be limited to a
>   small context (and they should be at most opus-class or maybe even sonnet if
>   context is small and specs clear and precise)
> * **max acceptable effort for fable is high, for Opus and Sonnet is xHigh**

The orchestrator's model in that ask is superseded (below); the rest stands.

## The governing constraint: a block binds the task at fault, never the session

Ruled 2026-09-23 (14z-175 in the original, `DECISIONS_HISTORY.md` "Ruled 2026-09-23 (14z-175) — #172: the agent
architecture's four design questions"), verbatim: *"Hard block + written resolve is fine but that doesn't mean that
the session should grind to a halt: it means the task at fault should be redone or corrected, and when it is, it is
checked and again and if green things are unblocked. Stating this because the point of this agent architecture is to
minimize the risk while keeping the system going forward autonomously (until user input is required of course)"*.

So: a denied tool call is redone in the allowed form; a refused end-of-turn is answered by doing the outstanding
thing; a refused push waits while every other piece of work continues, and goes through when the re-check is green.
**No check may be built whose only exit is the maintainer, except where user input is genuinely required.** The same
ruling set the two kinds of check: a HARD BLOCK for the deterministic checks (the harness refuses; only the
maintainer changes the hook), and BLOCK-UNTIL-RESOLVED-IN-WRITING for a model checker (a model checker has false
positives, and an unresolvable block would deadlock; the resolution is recorded for the maintainer to audit).

## The principle: bind what can be bound mechanically, judge the rest

From the scope document's recommendation, taken by the 2026-09-23 rulings: **a check that needs no judgement should
not be given to a model.** A hook that detects a failure mechanically cannot be argued with, forgotten, or talked
round, which is the strongest available reading of *"cannot go against the will of checker agents"*. A model checker
is kept for what needs judgement. The original measured this the hard way: of two deterministic forms proposed for
"no finished job left unread", one flagged 26 tasks in one session that the agent HAD used, and the other was masked
for a whole session by a 35-hour orphaned task; whether a running thing is RELEVANT to a promise is judgement, so it
moved to the model checker (ruled 2026-09-23, *"Move it to C1 (Recommended)"*).

## 1. The orchestrator

- **A plain session, no definition** (ruled 2026-09-24, 14z-178, `DECISIONS_HISTORY.md` "Ruled 2026-09-24 (14z-178) —
  #172 slice S5"): *"Plain session (Recommended)"*. Measured first: a main session run as a definition takes the
  definition's model and tools but not its effort, keeps CLAUDE.md, and **loses Claude Code's whole default system
  prompt**, replaced by the definition's body — an orchestrator built that way would have to re-supply every harness
  instruction and drift from Claude Code's own. A plain session takes its model from settings or the launch, its
  effort from the per-model settings, and any orchestrator-only note can be appended to the default prompt.
- **Opus 5.5 at effort High** (ruled 2026-09-25, `DECISIONS_HISTORY.md` "Ruled 2026-09-25 (after the 14z-181 close) —
  the orchestrator is Opus 5.5 at effort High"). The maintainer, verbatim: *"One change I'll need to enforce for the
  foreseeable future: The orchestrator must be a Opus 5.5 High instead of Fable 5.1 (access to Fable not guaranteed so
  I need to account for it)"*. It supersedes only the model of the S5 ruling. The model is set at launch by the
  maintainer, never by a session. **A sitting that finds itself on another model says so at the opener** ([VSR-46]).
- **The orchestrator is free to choose how best to work, but cannot go against the will of the checkers** (the ask).
  It drives the workers by spec and puts its actions through the rule-checker.
- **The swarm is USED, not merely installed.** The maintainer, 14z-180 in the original (its `STATE_HISTORY.md`
  "Session 14z-180"): *"first we finish #172 because we need to use that setup for the upcoming work"*, then *"can you
  confirm you are using the swarm of agents described in #172 and that any further session will?"*. So every quoted
  figure comes from a worker spec ([VSR-47]) and every action goes through the rule-checker ([VSR-48]). Nothing
  mechanical forces delegation; it is stated at the opener.

## 2. The workers, by spec

- **Named, capped definitions** under `.claude/agents/`: `measurer` (runs the numbered commands of a spec exactly as
  written and returns each figure with the command that produced it) and `reader` (returns each fact as a verbatim
  quote with its path and line). Their template is `docs/project/worker_spec.md`: TASK as a question, pinned INPUTS,
  numbered COMMANDS, a RETURN of `FIG` and `NOT MEASURED` lines only, MUST NOT, STOP.
- **A figure that will be quoted goes through a worker** ([VSR-47]). The original's working practice since 14z-180
  (its session notes, not a ruling): exploratory reads to write a spec may stay with the orchestrator, the quoted
  figure may not, and a worker figure that disagrees with its own command output is re-derived before it is quoted.
- **The caps are enforced on the CALL and on every definition** (ruled 2026-09-23, 14z-177, `DECISIONS_HISTORY.md`
  "Ruled 2026-09-23 (14z-177) — #172 slice S4: forks, the pinned checker, QP3 wider + QP5, and the order"), because a
  cap in a definition is not a cap by itself. Measured in the original (Claude Code 2.1.280, its probe set A1-A12):
  the Agent call's `model` parameter BEATS the definition's; a definition with no `effort` runs at the CALLER's
  effort, and one with no `model` on the CALLER's model; a definition's `tools` list binds (a read-only worker could
  not create a file), but Bash stays a write path for any worker that has it; a `hooks:` block in a definition's
  frontmatter did NOT fire, while the same command as a PROJECT hook did, and a project hook sees a worker's own calls
  with its `agent_type`. So:
  - **every definition names its model and its effort**, at most Opus-class and at most `xhigh` (the ask's cap), held
    by a static gate on the definitions, which also holds that no definition carries Write, Edit or Agent;
  - **the call gate** (installed by the maintainer 2026-09-23, *"I'll install it (Recommended)"*, then *"done"*,
    `DECISIONS_HISTORY.md` "Ruled 2026-09-23 (14z-177) — #172 slice S4: the CALL GATE installed"), a project hook on
    every agent call, refuses a model above Opus-class, a model on a defined worker, no model on a type that would
    inherit the orchestrator's (the built-in `Explore` excepted, measured capped at Opus-class), and a template-driven
    worker's spec missing a heading; forks pass.
- **The worker model preference is dropped.** Ruled 2026-09-29 that workers prefer Sonnet 5.5 at `xhigh`; DROPPED
  2026-10-05 (14z-192, `DECISIONS_HISTORY.md` "Ruled 2026-10-05 (14z-192) — the opener's answers"), the maintainer:
  *"no longer desireable, let's drop it."* Never re-proposed unprompted. The definitions keep the model and effort
  they carried (`measurer` and `reader`: `sonnet`, `high`).

## 3. The rule-checker, before an action

The model checker of the swarm. Its specification of record is `docs/project/rule_checker.md`; in short ([VSR-48]):
- it runs **before an action** — a freeze, a build, an expectation, a recommendation, a ticket closure — when the
  action's work is done, never held for the close (ruled 2026-10-15, #288, and 2026-10-16, 14z-203, in the original);
- it is a **pinned, context-free reader**: the `rule-checker` definition, a VERSION model id, effort `high`, read-only
  tools, `omitClaudeMd: true`, spawned with no model parameter and never as a fork (ruled 2026-09-23, *"Pin it now
  (Recommended)"*, and 2026-09-23, 14z-177 step 4, *"Subagents (Recommended)"*);
- every run carries a **planted known violation** that must be caught, or the real verdict is void;
- a **VIOLATED is resolved question by question, in writing**, before the action proceeds.

**The procedure checker (C1) is CUT.** Built 2026-09-23 as the rule-checker's `procedure` family (QP1-QP5 over a
transcript extract, at every push and close, its push bound by a hook), it was cut on 2026-10-15 with everything but
the before-an-action check (`DECISIONS_HISTORY.md` "Ruled 2026-10-15 (14z-202) — #288: everything but the
before-an-action check is cut; …"), the maintainer: *"Then for now let's cut everything except the "before an
action" and let's open a ticket to revisit in the future when we have more data"*. Its one recurring real catch is
held by the green guard (below); its checklist is kept as the record in `rule_checker.md`; the revisit is #289 in the
original.

## 4. The deterministic hooks (C0 — no model)

Each hard-blocks, with a reason that names the allowed form, and binds the task at fault.

- **No invisible jobs (C0.1, PreToolUse on Bash; installed 2026-09-23, *"Install + protect (Recommended)"*).** Deny a
  command that detaches (`nohup`, `setsid`, `disown`, a command-ending `&`) or waits on a process-table query (a
  `pgrep` waiter, which matches its own command line and never exits), naming the tracked alternative: a background
  task the harness tracks, which notifies, or a monitor for a condition. **A job the harness tracks is a job whose end
  wakes the agent.** Why (measured in the original over eleven sessions' transcripts, §1 of its scope document): a job
  launched detached inside an ordinary call cannot produce a completion notification, so once the agent ends its turn
  only its own poll — which it cannot make while idle — or the maintainer can end the wait; in the costliest session
  every long job was launched detached, and the maintainer's status question ended eleven gaps there. One classifier
  serves the hook and every census of it, and a launch form it does not list passes until it is added: a replay of the
  hook over every archived transcript is how new forms are found.
- **No process outlives its purpose (C0.3, the close sweep; built 2026-09-23, 14z-176).** At the close, a sweep lists
  every process the session started that is still alive, and every orphan that points into the project whatever
  session left it; the list must be empty, or each survivor killed (leaves first, because killing a parent reparents
  its child) or declared in writing. The sweep must see ITSELF before it may print clean. It is the last command
  before the push. (Its first live run found an 18-day orphan that twenty session openers' `ps` greps had missed:
  check the PROCESS you started, not only the output you wanted.)
- **The green guard on commits (#290 in the original, ruled 2026-10-16, `DECISIONS_HISTORY.md` "Ruled 2026-10-16
  (14z-203) — #290: the green guard sits at the commit, with a light push check on the tip").** The maintainer:
  *"Commit, plus a light push check on the tip."* A pre-commit hook refuses a commit whose exact tree has no strict
  GREEN run of the whole static tier with the reference sets present, read from the runner's own results; a pre-push
  hook checks the pushed tip's tree, which catches a merge, cherry-pick, rebase, revert or skipped-hook commit that
  ends the range. The close stages its records and runs its tier on a snapshot of the staged tree, then commits
  (*"Tier first, then commit (Recommended)"*). Bypasses — skipping the hooks, redirecting where they are read from —
  are refused by the Bash hook; the override is the maintainer's own command. ([VSR-45].)
- **The call gate** (§2): every agent call, against the caps.
- **The enforcement protects itself (C0.4, edit locks).** The settings that wire the hooks, the hooks, their one
  classifier, the git hooks and their installer are denied to the session's file-editing tools (ruled 2026-09-23,
  *"Install + protect"*; the git hooks added on #290, *"Lock them (Recommended)"*: *"so the session cannot weaken its
  own guard"*). Only the maintainer changes them; a session proposes the change as a proven file under `build/` and the
  maintainer applies it. **What the lock does NOT cover:** an edit-tool deny rule does not refuse a write through Bash;
  that gap is never used. The original's record of the 2026-09-29 ruling treats the agent definitions as edit-locked
  too (*"the agent definitions are edit-locked, so the frontmatter change is proposed to the maintainer, not made by
  a session"*), but its settings' deny list does not name them: whether the rebuild locks them is open.

## 5. Forks

- **A fork is the orchestrator continuing, not a worker** (ruled 2026-09-23, 14z-177, *"Allow forks (Recommended)"*):
  forks pass the call gate, the worker caps bind workers, and a fork's return is read like the orchestrator's own
  statements. A worker spec does not bind a fork (`worker_spec.md`).
- **Forks run parallel work** (`SPEC.md` §7), and a merge of several forks is checked as a packet per fork, the merge
  citing each fork's run (ruled 2026-10-05, #217, `rule_checker.md`).
- **A fork is never a rule-checker reader:** it inherits the working agent's context and therefore its framing.
- **A /btw fork is exempt from the worker cap** (ruled 2026-09-25, 14z-181, `DECISIONS_HISTORY.md` "Ruled 2026-09-25
  (14z-181) — the worker cap: a /btw fork is exempt"; the maintainer chose *"Push; fork is exempt (Recommended)"*): it
  runs on the session's model and is not a worker the agent spawned; the close names the fork.

## 6. No swarm model at max effort, ever

Ruled 2026-09-29 (14z-185, `DECISIONS_HISTORY.md` "Ruled 2026-09-29 (14z-185) — … no swarm model at max effort,
ever"), the maintainer, verbatim: *"No model used in the swarm is allowed to use max effort, under any
circumstance"*. No agent of the swarm — orchestrator, worker or checker — is configured or spawned at effort `max`.
The 2026-10-05 drop of the worker model preference did not touch this sentence ([VSR-46]).

## 7. What the swarm will not catch

From the original's scope document, §7:
- **A job the agent never launches through a tool** — the hooks see only tool calls.
- **An intent the agent never states.**
- **A statement the transcript never recorded** — measured in the original: every report that ENDS a turn is kept,
  but mid-turn narration just before a tool call is sometimes absent.
- **The maintainer's time outside the session** — a notification wakes the agent; nothing here wakes the maintainer.
- **An orphan that points nowhere into the project** — the sweep finds orphans by where they point; a job started
  from `/` with no project path in its arguments or streams, whose environment is hidden, is invisible to it, and so
  is a job re-parented under anything but init.
- **A launch form the no-invisible-jobs hook does not list** — it is a denylist; a new detaching form passes until it
  is added.

## 8. Changing the swarm

A change to any part of this structure needs a measured inadequacy, recorded as a ticket with the evidence
([VSR-50], `SPEC.md` §7). A change that moves an instrument — the rule-checker's checklist, its model or its effort —
recalibrates every fixture before the next real run (`rule_checker.md` [VSP-184]). The platform facts above were
measured on specific Claude Code versions (2.1.280 and 2.1.281 in the original) and are re-measured, not assumed,
when the platform moves.
