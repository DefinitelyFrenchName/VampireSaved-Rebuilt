# STATE — living progress log

**Opened 2026-10-18 (session R-001), `CLAUDE.md` [VSR-28].** This file holds the latest session group and the
standing sections; older groups move VERBATIM to `STATE_HISTORY.md` (created at the first move, with an index at its
head). A session key is `R-NNN`, one per sitting, never renamed or renumbered ([VSR-30]); milestones and freezes are
their own namespaces. A group's form, kept from the original: `## Session KEY — banner`, then `### opened with` and one
`### (N) TITLE` section per piece of work. An open list holds only what is open.

## Session R-003 — **Phase 0: the generators' constants tabled (in progress).** Opened 2026-10-18 on Opus 5.5 (the ruled orchestrator).

### opened with

*"read state.md"*, then *"yes"* to opening R-003 and starting on the next-session list's item 1.

### (1) PHASE 0: THE 30 GENERATOR CONSTANTS TABLED, AND THE 16 THE CENSUS CANNOT SEE

The census's `code` column is the public module-level constants of six generators. `tools/phase0lib.py` now reads
them by an AST walk, which `tools/extract_tables.py` writes into `docs/project/tables/code/constants.tsv` (the
census's 30). Each value is the expression as written (hex stays hex), and a value that spans lines is carried
whole, with its comments dropped.

Found while building it: the census's line grammar takes one name, so the 16 constants bound in pairs
(`SLICE_LO, SLICE_HI = …` and seven more pairs) escape it. Three counted values are written in terms of them
(`DELTA_A = PLACE_A - SLICE_LO`, `LEN_A`, `LEN_B`). They are carried in `code/uncounted.tsv`. Gate
`tests/test_phase0_tables.py`: G2–G4 extended to the code column (G4 compares token streams, so hex written as
decimal fails). The new G6 checks that the code tables name every public constant, by an AST walk written apart
from the extractor's, and that `uncounted` is exactly what the census misses. Four new controls (`perturbed-code`,
`code-hex-as-decimal`, `uncounted-dropped`, `perturbed-generator`), all FIRED, every mode FAIL. Its first green was
read by its printed values ([VSR-21]). The format and the figures are in `docs/project/tables/README.md`. A
measurer reproduced every figure there before the commit.

Paid for this sitting: the measurer ran the four control modes side by side, which showed that every run of the
gate regenerated into the same scratch directory. Two concurrent runs could have compared each other's output. Its
verdicts matched the sequential runs, but the gate now makes a new scratch directory for each run and removes it
at the end ([VSR-143]).

## Session R-002 — **#3 built and closed: the figures, their gate, the run log, the dashboard; R-001 archived.** Opened 2026-10-18 on Opus 5.5 (the ruled orchestrator); transcript `c6b8c007`.

### opened with

*"read state.nd"*, then *"yes"* to opening R-002 and starting on #3.

### (1) #3: THE FIGURES, THEIR GATE, THE RUN LOG, THE BACKFILL

`tools/metrics.py` writes `docs/project/metrics/figures.tsv` (one row per figure per session, `{value, class,
source, rule}`, ABSENT rows for what no source holds); what each figure is and how it is timed:
`docs/project/metrics/README.md`. `tools/runlog.py`: every gate appends one JSON line per run to
`build/runs/runs.jsonl`; the two existing gates and the new one write it. Gate `tests/test_metrics.py`: a synthetic
session whose every figure is known by construction, ten checks (C1–C10), five controls (`late-result`,
`usage-twice`, `ask-as-tool`, `absent-filled`, `rule-dropped`), all FIRED, every mode FAIL. Its first green was read
by its printed values ([VSR-21]): the first run's two reds were the fixture's (an answer placed at minute 202 where
its design said 203), not the tool's.

Found while building it: the transcript carries a `cost-state` record with the harness's own totals, which R-001's
survey missed. On R-001 the DERIVED buckets agree with it: working is 5.8 % under its API time, and tool calls are
12.2 % over its tool time once the two `AskUserQuestion` waits (610 s) are given to the maintainer. A worker
transcript's `usage.output_tokens` is a streaming snapshot (201 against the harness's 4,600), so workers' tokens come
from the harness. Backfilled: R-001 (88 figures) and 14z-205's drafting share (13; EXTRAPOLATED, an undercount, its
rule says why). Committed `bb79816`, the three gates green on the staged tree.

### (2) #3: THE DASHBOARD

The view: "Rebuilt Session Ledger", a private claude.ai dashboard (https://claude.ai/artifact/EpBKcPyqtdSbePUso6jDd5)
over one source, the tracked table uploaded as `figures.csv`. A tab per session; time (the four buckets beside the
harness's cross-check, and session by session), activity, tokens and workers, commits by area, phase 0 against the
census, gates and the inventory by class, health, gate runs, and every figure with its source and rule. Each figure
shows its class as a chip. It is re-published from the table at each close (`docs/project/metrics/README.md`).

### (3) 14z-205 RULED OUT OF THE TABLE

The maintainer, on the dashboard: *"dashboard looks good, session 14z=205 that you inherited from Vampire Savior can
honestly be removed."* Its 13 rows were dropped with a new `tools/metrics.py drop` (the table is never hand-edited);
the gate gained C11 (drop removes exactly one session's rows and refuses a key with none) and its control
`drop-overreach`. The backfill line of (1) is superseded by this: the table holds R-001 alone before R-002.

### (4) THE CLOSE'S OWN FINDING: GUARD REFUSALS WERE COUNTED BY TEXT

Collecting R-002 counted 1 guard refusal where there was none: my survey of R-001's errors had printed R-001's
refusal text. R-001's 4 was inflated the same way (gate outputs quote the message); its real refusals are 2, as its
record says. A refusal is now the hook's own error result (`PreToolUse:<tool> hook error:` and the message); the
gate's fixture quotes the message in a passing result, and the control `guard-by-text` (C3) proves the case is read.
R-001 and R-002 re-collected. Gotcha in `docs/project/metrics/README.md`.

### CLOSE (R-002, 2026-10-18)

Delivered: #3 built and closed (`tools/metrics.py`, `tools/runlog.py`, `tests/test_metrics.py`,
`docs/project/metrics/`, the dashboard "Rebuilt Session Ledger"); R-001 moved verbatim to `STATE_HISTORY.md`, which
opens with its index. Figures: R-001 88 rows, R-002 96 rows, collected before the close commit, so R-002's count of
commits (2) and its last commit (`7b1fea3`) leave out the close commit, and it has no `cost-state` record yet
(ABSENT). Gates at the close, on the committed tree: the three gates (verdicts in the close commit's message). Not
done: no rule-checker ran before any action ([VSR-48]; the tool does not exist yet). Left outside git: the run log
`build/runs/runs.jsonl` and the export `build/export_bf92acd2` (both git-ignored). No background process is left
running.

# STANDING SECTIONS (current state — never archived)

## Standing rulings

The rulings of 2026-10-18 are verbatim in `SPEC.md` §0 (the brief, the five answers, v0.1's four questions, the
validation of `CLAUDE.md` v1.0, the read-only sources, phase 0's place and pin). The law is `CLAUDE.md`.

## Decisions pending (human)

none.

## The next session starts with

1. Phase 0: the 30 generator constants (the census's `code` column).
2. Phase 0: the keys the census does not count (`name`, `note` and the rest of its `IGNORE_KEYS`, JSON's `_` keys),
   carried so the renderer can reproduce the manifests whole.
3. Phase 0: the renderer (tables to manifests, parse-equal to the original's under its own `_minitoml`) and the
   byte-for-byte build proof on an export; the five held values come from generators run on the reference sets.
