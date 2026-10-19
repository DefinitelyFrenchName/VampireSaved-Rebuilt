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
at the end ([VSR-143]). Committed `a002c98`, the three gates green on the staged tree.

### (2) PHASE 0: THE 2,528 VALUES THE CENSUS DOES NOT COUNT, AND THE MANIFESTS WHOLE

The census skips the keys of its `IGNORE_KEYS` and JSON's `_` keys. They are carried now, so the renderer can
reproduce the manifests whole: `docs/project/tables/uncounted/<key>.tsv`, one per TOML key (17 tables), and
`uncounted/json_underscore.tsv` (28 values), 2,528 rows. Not all of them are prose: a `space` row's `class` is
raw or crypt, and a `file` row's `source` names its zip member. The census's line grammar cuts a line at its first
`#`, and notes cite tickets, so a literal is recovered from the whole line (the shortest cut at a `#` that parses
to the value). The gate's G4 line check had the same cut and now reads past it. The new G7 (WHOLE) proves, by an
independent walk of each manifest's parse, that the tables hold all 11,284 values of the 30 canonical manifests
exactly once. Four manifests are comments only, so no table pins their SHA-1: that is for the renderer. Three new
controls, among them `note-cut-at-hash`, which plants the cut. Format and figures in
`docs/project/tables/README.md`.

Paid for this sitting: `dropped-row`'s declaration predicted too few failing checks once G7 existed (a dropped
gameplay row is also a missing manifest value). The declaration was corrected from the printed values, and the gate
was not loosened. The measurer corrected two of the README's figures, both mine from the survey (`name` 526, not
525; 2,519 strings, not 2,521). One of its commands failed on my spec (`python3 -I` hides the user site-packages
that hold `tomli`). Both times this sitting, the measurer ran two commands side by side against a spec that ran
them in order. Harmless here (the second was a read-only count), but noted against [VSR-50]. Committed `d9429be`,
the three gates green on the staged tree.

### (3) PHASE 0: THE RENDERER, THE HELD VALUES FROM THE DUMPS, AND THE BUILD PROOF MOVED TO PHASE 1

The maintainer: *"start it, we have ample context"*.
- **The renderer.** `tools/render_manifests.py` writes the 30 canonical manifests from the tables. What the value
  tables do not say about shape (each manifest's format, each TOML kind's `[x]`/`[[x]]`, each JSON container's form
  and member order) is the generated `layout/forms.tsv` (373 rows). Its header also pins the four comment-only
  manifests.
- **The gate.** The new G8 renders all 30 and requires them parse-equal to the originals (`tomli`/`json`, key order
  included). It also requires the original's own parser to agree: the host's Python is 3.9, so `_minitoml` is its
  subset parser, which accepts the same 21 manifests and refuses the same three with arrays. G8 is green, with two
  new controls. Seven older controls now also fail G8, as they should, and were re-declared from the printed values.
- **The held values.** `tools/gen_held.py` derives all five from the decrypted dumps, each refused unless it has its
  `held.tsv` SHA-1. Three come from the original's generators. The other two are rebuilt from their source spans
  with each edit named: `throw_arc_tables` is vs2's installer with two operands made placeholders; `beam_list_type6`
  is five parts. The first `throw_arc_tables` derivation was refused (I resumed the copy at the operand's
  displacement); fixed from the decomposition. Gate `tests/test_gen_held.py`: H1–H3 green, two controls; with the
  derived values the 30 manifests parse equal and no placeholder is left.
- **The build proof.** The maintainer ruled the vhunt2 audit shim on both legs (`SPEC.md` §0). The original's build
  then still stopped: its extractor reads `vhunt2.zip` as its sibling oracle (#4). Asked, the maintainer ruled
  *"Stop at parse-equality"*: the byte-for-byte proof moves to phase 1 (`SPEC.md` §0, §3). `tools/build_proof.py` is
  committed, unrun. Its logic is gated without a build by `tests/test_build_proof.py` (P1–P4, control
  `blind-compare`), whose first red was its own check (it read a docstring as a requirement), now made to load the
  shimmed module.
- **Not measured, for phase 1.** `beam_list_type6`'s copied drawer opens with a `bcs.w` copied unchanged, so its
  PC-relative target moves with the copy ([VSR-83]); whether it is reachable was not checked.
Committed `5c0f149`, the five gates green on the staged tree.

### (4) WHAT VHUNT2 DOES, AND THE ORIGINAL'S CORRECTIONS PER TENANT (#4)

The maintainer: *"to be clear, I could provide vhunt2 but I don't understand what it brings to the table"*. Read
from the extractor: vhunt2 is the sibling copy of the three newcomers. Diffing it against vs2 bounds each region and
yields its relocation map (about 7,000–9,000 pointers per tenant); no vhunt2 byte reaches the output. The
original tracks the results per tenant (`regions.json`: 21/31/26 regions, 7,736/8,915/6,882 refs). The maintainer's
direction (verbatim, `SPEC.md` §0, #4): *"I would table the measurement AND I would look at the history of Vampire
Saved to gather all the missing/wrong parts that had to be added/fixed for each of the three VS2 characters"*.
- **The history.** Three reader workers, one per tenant, returned 146 parts: Donovan 55, Huitzil 59, Pyron 32.
  They are `docs/project/port_corrections.tsv` (hand-written), each with its source line and a verbatim anchor,
  gated by `tests/test_port_corrections.py` (C1, C2, two controls). The gate's first run caught one non-verbatim
  quote. The classes are in `docs/project/port_corrections.md`. Only 27 parts are the extraction's own errors
  (reach, reloc, crypt-data); 85 are the engines' differences (short tables, aliased per-character rows, vs2
  environment assumptions), which the original found one by one and which three static enumerations would find.
- **The measurement, not yet tabled.** Each `regions.json` holds about 49,000–55,000 values (153,013 in all). Each
  tenant's `values` section carries three vs2 rows as raw bytes: `jump_params` (48 bytes) and `byte2d_a`/`_b`
  (30 bytes each). These are gameplay values ([VSR-6]), so how to carry them is the maintainer's call.
- **Guard refusal (1).** A command mixing a heredoc and escaped backticks was refused as unparseable. It was split
  into two calls.

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
