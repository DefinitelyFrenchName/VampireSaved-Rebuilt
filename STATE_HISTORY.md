# STATE_HISTORY — the archive of STATE.md's session groups

**Opened 2026-10-18 (session R-002), `CLAUDE.md` [VSR-28].** Every session group that leaves `STATE.md` moves here
VERBATIM, newest first, never edited after the move; the index below is the lookup by session key ([VSR-30]).

## Index

| session | date | banner | line |
|---|---|---|---|
| R-002 | 2026-10-18 | #3 built and closed: the figures, their gate, the run log, the dashboard; R-001 archived | 14 |
| R-001 | 2026-10-18 | CLAUDE.md v1.0 validated, SPEC v0.2 accepted; the read-only guard installed; phase 0 started | 72 |


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

## Session R-001 — **CLAUDE.md v1.0 validated, SPEC v0.2 accepted; the read-only guard installed; phase 0 started.** Opened 2026-10-18 on Opus 5.5 (the ruled orchestrator); transcript `dde4a561`.

### opened with

*"CLAUDE.md has been validated, the spec.md draft is accepted"*; then the maintainer's answers on the draft's loose
ends, the four read-only sources, *"Please add the hook and after that start phase 0"*.

### (1) THE LAW AND THE SPEC ACCEPTED; THE FOLLOW-UPS

`791d5bb`: both status lines. `c185504`: the filiation of [VSR-1]..[VSR-50] moved out of `CLAUDE.md` into
`docs/carried/ledger_claude_md.tsv`; vhunt2 dropped entirely ([VSR-38] narrowed to vsavj/vsav2, §7's VH2 clause
removed); `../ROMS` named in [VSR-8] with the read-only rule; typos. `9adf1a1`: the four read-only sources of truth
named in `CLAUDE.md` §7. Every ruling is verbatim in `SPEC.md` §0.

### (2) THE READ-ONLY GUARD

`ac61157`: `.claude/hooks/guard_readonly.py`, a PreToolUse hook refusing a write outside the working tree or to the
edit-locked hook files ([VSR-49]); record and gaps in `docs/project/hooks.md`; gate `tests/test_readonly_guard.py`
(59 cases, both controls FIRED, both control modes FAIL). Live: a no-op `rm -f` outside the tree was refused. Two gaps
found the same hour (Decisions pending, item 1).

### (3) PHASE 0 STARTED: WHERE, FROM WHICH COMMIT, AND THE BASELINE

The spec put phase 0 in the original, which the ruling of (1) made read-only; asked, the maintainer ruled it runs
here, reading the original at `bf92acd2` (`SPEC.md` §0, §3 amended). `tools/export_original.py` exports a pinned
commit through `git ls-tree`/`git cat-file` only, into a directory that must not exist. The baseline, measured by a
measurer worker ([VSR-47]) on its own export:

| figure | value |
|---|---|
| export of `bf92acd2` | tree `0a40f749ea3a`, 17,068 files (542,160,969 bytes); 3 submodules skipped (emu/fbneo, emu/jtcores, emu/mame) |
| the original's checkout, status entries before / after | 936 / 936 |
| census manifests | 30 |
| gameplay: in-table / derived / baked / total | 15 / 0 / 221 / 236 |
| fact: in-table / derived / baked / total | 0 / 541 / 7,979 / 8,520 |
| code: in-table / derived / baked / total | 0 / 0 / 30 / 30 |

These equal `SPEC.md` §1's figures at `6dee2be7`. What the census counts: every scalar of the 30 canonical manifests
and every module-level constant of six generators, by (kind, key); the gameplay column is variant selection
(`only_variant_slot`, `only_base_slot`, `unless_composed`, `id_by_profile`, `dst_slot`, `mirror_variant`,
`roster_subst`, the select wheel's `layout`, adjacency and `edges_in`, `tenant.id`, and three `aux_poke.val` judged by
address), held in `donovan.toml`, `huitzil.toml`, `pyron.toml`, `shared_writes.toml` and `effect_tail.json`.

**Not done in this sitting:** no rule-checker ran before any action ([VSR-48]): the rebuild has no rule-checker tool
yet (`docs/project/rule_checker.md` is its spec), so none of this sitting's commits had one.

### (4) THE TWO PENDING ITEMS RULED: THE GUARD'S FIX PREPARED, TICKETS OPENED

The maintainer: *"yes and yes"* (`SPEC.md` §0). The fix is `build/proposed/hooks/guard_readonly.py` (#2): where git
acts now includes `--git-dir`/`--work-tree` (both forms) and `GIT_DIR`/`GIT_WORK_TREE`; `-c` values are skipped;
`archive` is a read (its `-o` judged); `fetch` leaves the read list and `config`/`branch`/`remote` read only in their
reading forms. The gate gained `--hook <path>` and 14 cases. On the proposal: 73 cases (48 block, 25 allow), PASS, both
controls FIRED, both control modes FAIL. On the installed hook: FAIL on exactly the 10 cases #2 names. A replay of the
sitting's 59 calls through both hooks: 0 differences. Tickets: `docs/project/tickets.tsv` holds #1 (the umbrella
ticket carried from the original's #120, already open) and #2.

### (5) #2 INSTALLED AND CLOSED

The maintainer installed the proposal (`cp`, 2026-10-18); the installed hook is byte-identical to it (`cmp`). The gate
on the installed hook: 73 cases, `VERDICT: PASS`, both controls FIRED, both control modes `VERDICT: FAIL`. Live: `git -C
<original> archive bf92acd2 SPEC.md | tar -t` ran; `GIT_DIR=../ROMS/.git git reset --hard` was refused. The proposal
file was removed once installed (it is in this sitting's history).

### (6) PHASE 0: THE 236 GAMEPLAY VALUES TABLED

The format, decided as `SPEC.md` §4 asks, with its reasons in `docs/project/tables/README.md`: one TSV per subject,
one schema for all (`manifest, kind, row, key, value, line, prov_kind, prov_refs`), values as the manifest's literal,
provenance as the census's attribution (vocabulary word and references) with the paragraph left at its pinned line.
`tools/extract_gameplay_tables.py` imports the original's census from the export and aligns each record with its
row (`tools/phase0lib.py`): `variant_selection` 182, `select_wheel` 42, `roster` 9, `hit_class_mask` 3 = the
census's 236. Gate `tests/test_phase0_gameplay.py`: G1 regenerated equal, G2 the export's manifests are the pinned
SHA-1s, G3 the census column and the tables are the same multiset, G4 every cell equals an independent parse; three
controls (perturbed-value, dropped-row, perturbed-manifest). Exports now live under `build/` (git-ignored), inside
the tree. The figures in the README were reproduced by a measurer before the commit.

Paid for this sitting: the first control declarations predicted too few failing checks (a changed value also moves
G3's multiset); the declarations were corrected from the printed values, not the gate loosened. The JSON alignment
first compared the wrong tuple fields; fixed by one tuple layout for TOML and JSON.

### (7) PHASE 0: THE HEX RULING, AND THE 8,520 FACTS TABLED

Asked how the fact column's 649 hex fields (6,420 bytes, the largest 470) are carried, the maintainer chose "As
written, ruling into VSR-8" (`SPEC.md` §0): `CLAUDE.md` [VSR-8] now carries the #120 ruling's line, and each of the
7 runs over 64 bytes was checked before tabling. 2 are the project's own resolvers, carried. 5 hold whole vanilla or
vs2 routines or tables and are held out (`docs/project/tables/facts/held.tsv`, carried as `HELD:sha1=…`):
`index_window_018468`, `hitclass_map_extend` (Huitzil and Pyron), `beam_list_type6`, `throw_arc_tables`. Three of
them are produced by the original's generators.

The extractor and the gate were generalized and renamed: `tools/extract_tables.py` (was `extract_gameplay_tables.py`)
and `tests/test_phase0_tables.py` (was `test_phase0_gameplay.py`). Both columns: 8,756 rows in 56 tables (4 gameplay,
52 under `facts/`). JSON rows are JSON Pointers now (the `.` glyph of `version_font.json` broke dotted paths), which
changed `select_wheel.tsv`'s row column. Gate: G1–G4 as before over both columns, plus G5 (held values are only
their hashes, and none is in the clear); five controls, the two new ones `held-leak` and `perturbed-pointer-fact`.
The README's figures were reproduced by a measurer before the commit.

### (8) THE SESSION DASHBOARD, PROPOSED AND RULED (#3)

The maintainer asked for a dashboard of where time goes and the project's metrics. Proposed, then ruled: both
Claude's time and the maintainer's, split into Claude working, Claude waiting on tools, and the total; every figure
classed by how it was obtained, after the dashboard the maintainer named (the original's `tools/session_metrics.py`,
its #264: MEASURED, DERIVED, ESTIMATED, INFERRED, EXTRAPOLATED); a backfill "to the extent that you can"; built in
the next session, after this one closes. The plan and the maintainer's words are in #3. Measured this sitting: the
transcript carries per-turn wall time (`system/turn_duration`, on 11 turns only) and thinking time
(`thinkingDurationMs`, 141 messages), but no tool duration (to be DERIVED from timestamps); `0de1913b` is a 3-record
stub, and the drafting before R-001 ran in the original's 14z-205 (`995e7259`).

### CLOSE (R-001, 2026-10-18)

Delivered, all pushed: `CLAUDE.md` v1.0 and `SPEC.md` v0.2 accepted, with the follow-ups the maintainer ruled; the
read-only guard and its edit lock (#2 found, fixed and closed the same sitting); the ticket list (#1 carried, #2, #3);
`STATE.md`; phase 0's two value columns, 8,756 values in 56 tables with five held out. Gates at the close, on the
committed tree: `tests/test_readonly_guard.py` and `tests/test_phase0_tables.py` (verdicts in the close commit's
message). Not done: no rule-checker ran before any action ([VSR-48]; the tool does not exist yet). Left outside git:
the export `build/export_bf92acd2` (542 MB, git-ignored, kept for the gate; `tools/export_original.py` remakes it)
and this sitting's scratchpad exports. No background process is left running.
