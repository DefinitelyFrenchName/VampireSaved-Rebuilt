# STATE — living progress log

**Opened 2026-10-18 (session R-001), `CLAUDE.md` [VSR-28].** This file holds the latest session group and the
standing sections; older groups move VERBATIM to `STATE_HISTORY.md` (created at the first move, with an index at its
head). A session key is `R-NNN`, one per sitting, never renamed or renumbered ([VSR-30]); milestones and freezes are
their own namespaces. A group's form, kept from the original: `## Session KEY — banner`, then `### opened with` and one
`### (N) TITLE` section per piece of work. An open list holds only what is open.

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

### WHERE THE SITTING STANDS

Phase 0's next steps are the start list below. Nothing is red; there is no suite beyond the guard's gate.

# STANDING SECTIONS (current state — never archived)

## Standing rulings

The rulings of 2026-10-18 are verbatim in `SPEC.md` §0 (the brief, the five answers, v0.1's four questions, the
validation of `CLAUDE.md` v1.0, the read-only sources, phase 0's place and pin). The law is `CLAUDE.md`.

## Decisions pending (human)

none.

## The next session starts with

1. Phase 0, gameplay values first (`SPEC.md` §3): choose and record the table format (`SPEC.md` §4, "the manifest
   subset": a schema-checked format, rows keyed by manifest, kind and row name, each value with its provenance block),
   then extract the 236 gameplay values from the export of `bf92acd2` into `docs/project/tables/`.
2. The rebuild's own census: every scalar the original's census counts mapped to exactly one table cell, gated, with
   must-fire controls.
3. Then the 8,520 facts by kind and the 30 generator constants; then the renderer (tables to manifests, parse-equal to
   the original's) and the byte-for-byte build proof on an export.
