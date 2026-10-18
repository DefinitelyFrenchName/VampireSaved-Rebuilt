# The session dashboard's figures — what each is, where it comes from, and how sure it is

**Shape: reference.** What `docs/project/metrics/figures.tsv` holds and how each figure is obtained; the story of the
request is #3, the tool `tools/metrics.py`, its gate `tests/test_metrics.py`. The table is GENERATED (never
hand-edited) and tracked: it is the record, and the dashboard is a view of it re-published at each close.

## The five classes, and ABSENT

Every row carries `{value, class, source, rule}`, with the classes of the original's `tools/session_metrics.py` (its
#264), as the maintainer asked (#3):

| class | meaning | `rule` |
|---|---|---|
| MEASURED | read directly from a record the work wrote (a transcript field, a commit, a table row, a run-log line) | optional |
| DERIVED | arithmetic on measured figures | the formula |
| ESTIMATED | a heuristic classification of measured data; it can be wrong | the heuristic |
| INFERRED | a judgement about meaning | how it was judged (the tool emits none) |
| EXTRAPOLATED | a projection, or a backfill from a session that also did other work | how |

A figure no source holds is a row of class **ABSENT** with an empty value: never a zero, never filled in.
`python3 tools/metrics.py check` refuses a row that breaks any of this.

## Where time goes (`time`)

The session's span, from its transcript's first record to its last, is cut at every boundary below. Each slice goes to
exactly one bucket, so the buckets sum to the span:

| bucket | the slices it gets (first match wins) |
|---|---|
| Claude working | inside an API request: from its `api-request` record to the last assistant record answering it (`requestRef`) |
| Waiting on the maintainer | inside an `AskUserQuestion` call |
| Claude waiting on tools | inside any other tool call (the `tool_use` record to its `tool_result`) |
| idle → maintainer or tools | an idle stretch, up to its last prompt, goes to whoever sent that prompt: the maintainer (origin `human`) or background work (any other origin: a subagent's hand-back, a notification), counted as tools |
| Unaccounted | idle after a stretch's last prompt (harness overhead, mostly), or idle with no prompt |

All five are DERIVED. The transcript's `cost-state` record, when there is one, holds the harness's own totals
(duration, API time, tool time, cost). They are MEASURED and shown beside the buckets, with the difference as the
method's cross-check. On R-001: working came out 5.8 % under the harness's API time, and the tool calls' own time 12.2 %
over the harness's tool time. Also MEASURED: thinking time (`thinkingDurationMs`, part of working), and the turns
that carry a `system/turn_duration` (12 of R-001's turns, not all).

**What it cannot see.** A transcript's timestamps are when records were written, not when work started; the
`cost-state` record appears once, near the end, so a session still running has none (ABSENT). Workers run in
parallel with Claude and with each other: their time is shown apart (summed spans, summed working), never added to
the session's buckets.

## The other sections

| section | figures | class |
|---|---|---|
| `activity` | working and tool time split by activity: records, verify, rework, author, measure, converse | ESTIMATED; the rule is on every row |
| `events` | maintainer prompts (typed, queued), questions asked, tool calls by tool, background launches, errors, unanswered requests | MEASURED |
| `tokens` | the orchestrator's tokens by model (once per message id), the harness's output tokens by model | MEASURED |
| `workers` | workers by kind; their output tokens and share (the harness's total minus the orchestrator's); their summed span and working time | MEASURED, DERIVED |
| `output`, `area` | the session's commits, files, lines, files by area | DERIVED: a commit is the session's when its subject starts with the key or its committer time falls inside the transcript's span |
| `progress` | phase 0's tabled rows per column, the census's totals (`SPEC.md` §1), gates in the tree, gates ported (a `Ported from` line, `SPEC.md` §5.3), the original's gates by class (`docs/tests_inventory.tsv`) | MEASURED, read at the session's last commit |
| `health` | open tickets, decisions pending, the session's commits not on `origin/main` (at collection), guard refusals, minutes with a gate red, rule-checker runs before an action ([VSR-48]) | MEASURED, DERIVED |
| `gates` | per gate: runs, last verdict, cases, controls declared and fired, runtime, control-mode runs and how many reached their FAIL | MEASURED, DERIVED, from the run log |

## The run log

Each gate appends one JSON line per run to `build/runs/runs.jsonl` (`tools/runlog.py`; `SPEC.md` §6's run record):
the gate, its mode (`normal`, `control:<name>`), start, end, duration, HEAD and whether the tree differed from it (with
a digest of the difference), the verdict, the failed checks, the case count, and the controls declared, fired and
dead. `build/` is git-ignored, so the log belongs to the host that ran the gates. Its figures enter the tracked table at
the close. Sessions before R-002 have no run log, so their gate figures are ABSENT.

## The backfill

- **R-001**: collected from its transcript (`dde4a561`), which carries a `cost-state` record.
- **The drafting before R-001** ran in the original's session 14z-205 (transcript `995e7259`), alongside that
  session's other work. It is NOT in the table. Its share was collected once in R-002 (`--share-pattern`, an
  EXTRAPOLATED undercount) and dropped the same sitting, on the maintainer's ruling (2026-10-18): *"session 14z=205
  that you inherited from Vampire Savior can honestly be removed."* `--share-pattern` stays in the tool and its gate
  (C10) for a session that shares its transcript with other work.
- `0de1913b` holds 3 records and no work: not collected.

## Gotchas paid for

- **A worker transcript's `usage.output_tokens` is a streaming snapshot** (16–25 a message, measured R-002): the three
  measurers of R-001 read as 201 output tokens there, and as 4,600 in the harness's total for their model. Workers'
  tokens come from the harness's totals, never from their transcripts.
- **A guard refusal is the hook's own error result, not any text carrying its message.** Counted by the message
  alone, R-001 had 4 refusals and R-002 1: gate outputs and a survey of R-001's errors quote it. The rule now
  requires an error result whose text begins `PreToolUse:<tool> hook error:`: R-001 has 2 (its STATE records both),
  R-002 none. The gate's fixture quotes the message in a passing result, and the control `guard-by-text` proves
  that case is read.
- **An `AskUserQuestion` call is a tool call in the transcript**, but its time is the maintainer's: R-001's two
  questions held 610 s, more than all its other tool calls together (365 s).

## How it runs

At every close, before the close commit: `python3 tools/metrics.py collect <key>` (the transcript is the id on the
session's STATE heading), then `python3 tools/metrics.py check`, then re-publish the dashboard from the table. A
transcript is deleted after `cleanupPeriodDays`, so a session not collected at its close cannot be collected later.
