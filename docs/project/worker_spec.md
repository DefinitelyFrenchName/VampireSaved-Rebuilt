# THE WORKER SPEC — the template every task handed to a worker is written from

**What this is.** Carried from the original (`DefinitelyFrenchName/VampireSaved` at `6dee2be7`,
`docs/project/worker_spec.md`; GitHub #172 there, slice S4, ruled 2026-09-23 — its `DECISIONS_HISTORY.md`
"Ruled 2026-09-23 (14z-177)"), unchanged in substance; this repository's rule is `CLAUDE.md` [VSR-47] and the swarm
it belongs to is `docs/project/swarm.md`. A worker is a named, capped definition under `.claude/agents/`
(`measurer`, `reader`) that the orchestrator drives by a SPEC — a prompt written from this template, nothing else.
The template exists for two readers besides the worker: a check that reads the SPEC against the worker's RETURN (in
the original, the procedure check's QP5, `docs/project/rule_checker.md` "THE PROCEDURE FAMILY" — cut there
2026-10-15, #288, and kept as the record), and the call gate (`docs/project/swarm.md` §2), which refuses a call to a
defined worker whose prompt lacks the headings below (installed in the original by the maintainer 2026-09-23,
14z-177). So the headings are fixed, spelled exactly, and each on its own line.

**Why a spec and not a request.** The maintainer's ask (#172 in the original): *"workers: specialized, driven by
very precise specifications and directives given by the orchestrator"*. The blind spot it names
— the orchestrator's framing propagating into every worker — is answered by making the framing
INSPECTABLE: what the worker was told, what it ran, and what it returned are three things a checker can
put side by side.

## The template

Copy it, fill every section, delete nothing. A section with nothing to say says `none`.

```
TASK: <one sentence: the question the worker answers — a question, not a conclusion to confirm>

INPUTS:
- <path, commit, build or session id the commands read; each pinned where it can move>

COMMANDS:
C1: <the exact command, as it is to be run>
C2: <...>

RETURN:
FIG <name> = <value> <- C<n>
NOT MEASURED: <what> — <why>
(nothing else: no conclusion, no recommendation, no summary line)

MUST NOT:
- infer, estimate or recall a figure: every FIG comes from a command's output
- run a command that is not in COMMANDS; if one is needed, stop and say which and why
- edit, create or delete a tracked file; launch a detached job; spawn an agent
- <anything else this task forbids>

STOP:
- at the first command that fails or prints something the task did not expect: report the
  command and its output verbatim, and return what was measured before it
```

## What each section is for

- **TASK** is a QUESTION. "Confirm that X is 12" hands the worker the answer; "how many rows does
  X have" does not. A check of the return asks whether it answers the question asked (the original's QP5, ruled
  2026-09-23), so the question has to be written down.
- **INPUTS** pins what can move. A figure from `HEAD` is a figure about a commit nobody named; a
  figure from `git show <sha>:<path>` is reproducible forever.
- **COMMANDS** are numbered so each figure can name its source. The worker runs them as written;
  a worker that improvises a better command has answered a different question, and says so under
  STOP instead. A command that may run past the Bash tool's 120 s default says so in the spec
  ("run C2 with the Bash tool's timeout at 600000 ms"): otherwise the tool moves it to the
  background, and the worker either polls for it with commands no spec named or stops with
  nothing (paid in the original: two measurers polled, 14z-200, its rule-checker runs 2026-10-14-1068 and -1071).
- **RETURN** is one line per figure, `FIG <name> = <value> <- C<n>`, because a figure without its
  command cannot be re-derived, and a figure that cannot be found in the worker's own tool results was not measured
  by the worker (the original widened its QP3 to a worker's figures for that reason, ruled 2026-09-23).
  `NOT MEASURED` lines are how a worker says what it could not do without guessing.
- **MUST NOT** is where the orchestrator writes what the task forbids beyond the four standing
  items. The standing items restate rules the hooks and the definitions already enforce (the no-invisible-jobs check
  is a project hook, and a project hook was measured in the original to see a worker's own calls; and the
  definitions carry no Write, Edit or Agent tool, which a static gate on the definitions holds); they are
  repeated so a checker can hold the return to them. Bash can still write a file: that one is held by the spec and
  by the check of the return, not by a tool.
- **STOP** makes a failed command a report rather than a detour.

## What a spec does not do

- It does not make a figure RIGHT. It makes it traceable: the command that produced it, run again,
  must reproduce it, and whether that command answers the TASK is the checker's to judge.
- It does not bind a fork. A fork is the orchestrator continuing (ruled 2026-09-23 in the original), not a worker,
  and a checker reads a fork's return like the orchestrator's own statements.
