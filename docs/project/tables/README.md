# tables — the rebuild's documented tables (rule 5, `CLAUDE.md` [VSR-6])

**What this document is.** The specification of record for the tables in this directory: what each holds, its format
and why, where its values come from, and the gate that holds them. Phase 0 (`SPEC.md` §3) fills them from the
original (`DefinitelyFrenchName/VampireSaved`), read only, at `bf92acd2` (`SPEC.md` §0). Gameplay values come first,
by the maintainer's ruling, then the facts.

## The gameplay tables (the census's `gameplay` column, 236 values)

| table | rows | what it holds |
|---|---|---|
| `variant_selection.tsv` | 182 | which roster slot each patch row applies to: `only_variant_slot`, `only_base_slot`, `unless_composed`, `roster_subst` on the tenants' `aux_poke`, `code_word`, `data_port`, `site_thunk`, `region_fix` rows |
| `roster.tsv` | 9 | the tenants' roster ids (`tenant.id`, `tenant.id_by_profile`) and Donovan's port slot (`port.dst_slot`, `port.mirror_variant`) |
| `select_wheel.tsv` | 42 | the select wheel: each tenant's `layout` pointer, the new cells' eight-way adjacency (cells 0x10, 0x11, 0x13), and the five inbound edges from legacy cells (`edges_in`) |
| `hit_class_mask.tsv` | 3 | the three pokes into the hit-class / guard-mash RNG mask table (`PRG:0x028D40`–`0x028D60`), gameplay by the address they write |

The original had 15 of these values in-table (the `edges_in` rows, in its `select_wheel.md`) and 221 baked.

## The fact tables (the census's `fact` column, 8,520 values), under `facts/`

There is one table per TOML kind, `facts/<kind>.tsv` (45 kinds, plus the top-level keys in `facts/top.tsv`), and one
per JSON manifest, `facts/json_<path>.tsv` (6), for 52 tables. A row's other fields (its gameplay keys) sit in the gameplay
tables under the same `(manifest, kind, row)`.

**What the census does not count** (a row's `name`, its `note`, and the other keys of the census's `IGNORE_KEYS`,
and JSON's `_` keys) is carried apart, under `uncounted/` (below). A row's `name` is also its id in every table.

**Hex, and what is held out.** The maintainer ruled that the fact column's 649 hex fields (6,420 bytes) are carried
as written, as discrete values (`SPEC.md` §0; `CLAUDE.md` [VSR-8]). The 7 runs longer than 64 bytes were each
checked against *"whole algorithms are not fine"*. That judgement came from each row's notes and from the original's
generators, not from disassembly.
- 2 carried: `select_sword_pal_variant_id` and `df_gold_variant_id`, the project's own resolvers.
- 5 held out, listed in the hand-written `facts/held.tsv` with the reason and the derivation, and carried as
  `HELD:sha1=<SHA-1>`:
  - `index_window_018468` (vs2's four handlers inline);
  - `hitclass_map_extend` in Huitzil and in Pyron (vanilla's map plus vs2's entries);
  - `beam_list_type6` (vanilla's routine, relocated);
  - `throw_arc_tables` (vs2's full tables).

  The rebuild derives these from the reference sets: three by the original's generators (`gen_index_window_thunk.py`,
  `gen_hitclass_map_thunk.py`), two by generators phase 1 writes.

## The uncounted tables (2,528 values the census does not count), under `uncounted/`

The census skips a TOML key of its `IGNORE_KEYS` and every JSON `_` key. The phase-0 renderer must reproduce the
manifests whole, so these values are carried too, in 18 tables:
- **one per TOML key, `uncounted/<key>.tsv`** (17 tables): `note` 627, `kind` 583, `name` 526, `status` 370, `input`
  145, `notes` 145, `profile` 43, `art` 18, `class` 9, `source` 9, `build` 6, `common` 5, `schema` 4, `extract` 3,
  `placement_suffix` 3, `same_as` 3, `description` 1;
- **`uncounted/json_underscore.tsv`**: the JSON manifests' 28 `_` keys (`_comment`, `_src`, `_*_note`, …), each
  value whole.

They are filed by key because a reviewer asks for "every `status`", not for "what is in reconciliation.toml". They
are kept apart from the census's tables, like `code/uncounted.tsv`, so the census's columns stay its own.

**Not all of them are prose.** The census ignores these keys because they are not behavioural, and most are labels
and notes. But some say what the build does: a `space` row's `class` is `raw` or `crypt`; a `file` row's `source`
names the zip member it comes from; `kind`, `status` and `profile` qualify rows of the reconciliation maps. They are
facts in all but the census's accounting.

**How the schema reads here.**
- `value` is the literal as written. The census's line grammar cuts a TOML line at its first `#`, and a note may
  cite a ticket (`#169`), so a TOML literal is the shortest cut of its line at a `#` (or the whole line) that parses
  to the value. A JSON value is written as the other JSON tables write it (`json.dumps`).
- `prov_kind` and `prov_refs` are `none` and `-`: the census attributes nothing to a value it does not count. Many
  notes carry their provenance in their own text (`MEASURED 14z-120`).

**What is still not in any table.** Four canonical manifests hold no value at all (`charmap_donovan.toml`,
`charmap_huitzil.toml`, `charmap_pyron.toml` and `fsm_census.toml` are comments only), so no table's header pins
their SHA-1. TOML comments, and each manifest's layout (key order, `[x]` against `[[x]]`), are not carried either:
the acceptance is that rendered manifests are parse-equal to the original's, and the renderer decides what it needs.

**No ROM bytes** ([VSR-8]): the 2,519 string values (105,464 characters) hold no run of 17 or more hex bytes.

## The code tables (the census's `code` column, 30 values), under `code/`

The census's third column is the module-level constants of six of the original's generators (`gen_donovan_patch.py`,
`select_port.py`, `build_gfx_donovan.py`, `build_qs_songs.py`, `gen_anita_bank2.py`, `overlay_port.py`): placement
addresses, deltas, tile anchors, site sets, a bank number, a file name.

| table | rows | what it holds |
|---|---|---|
| `code/constants.tsv` | 30 | every constant the census counts, one row each |
| `code/uncounted.tsv` | 16 | the other public module-level constants of the same six generators |

**The census's blind spot, and why the 16 are carried.** The census reads a constant with a line grammar that takes
one name (`NAME = value`). So the 16 constants bound in pairs (`SLICE_LO, SLICE_HI = 0x2A0426, 0x2A63F0`, and
`BAND_*`, `SAFE_*`, `Z01`/`Z02`, `EFF_*`, `GAP_*`, `POOL_*`, `PAD_*`) escape it. Three of the counted values are
written in terms of uncounted ones (`DELTA_A = PLACE_A - SLICE_LO`, `LEN_A`, `LEN_B`), so the 30 do not resolve
without them. A public name is the census's own grammar, `[A-Z][A-Z0-9_]*`. The three private module names
(`_SPAN_KEYS`, `_SINGLETON_MERGE`, `_STAMP_FORMS`) are not carried: they are the generator's own structure (the key
names it dedups on, the functions it dispatches to, and the byte layout of its instruction forms).

**How the shared schema reads here.**
- `manifest` is the generator's path in the export (`tools/<name>.py`).
- `kind` and `row` are both `(module)`.
- `key` is the constant's name.
- `value` is the generator's expression as written: hex stays hex, and `range(59, 76)` and `PLACE_A - SLICE_LO`
  stay expressions. A value spanning lines is carried whole on one line, with its comments dropped. The census
  keeps only the first line of such a value (a lone bracket), or its first 60 characters.
- `line` is the assignment's line.
- `prov_*` is what the census attributes, the line's trailing comment (for `uncounted`, the same rule applied):
  `measured` for 1 counted and 2 uncounted values, `none` for the rest. The comment blocks above the constants
  carry most of their provenance and stay readable at `line` in the pinned original.

**No ROM bytes** ([VSR-8]): every value is an address, a tile code, a count, a bank, an id range or a file name.
None is a run of bytes.

## The layout table, `layout/forms.tsv` (373 rows)

The value tables say what each value is, not how a manifest is shaped. To rebuild the manifests, the renderer also
needs:
- **each canonical manifest's format** (`toml` or `json`), one row each, kind and row `(file)`. This also names the
  four manifests that hold no value, and pins their SHA-1 in the header;
- **each TOML kind's form**, row `(kind)`: `table` for `[x]`, `array` for `[[x]]`, and `line` its first header;
- **each JSON container's form**, row its pointer: `{"dict": [its keys in order]}` or `{"list": its length}`. The
  order is carried because the build's consumers iterate dicts in order.

Every row's key is `(form)`. The table is generated with the others and gated by G8: a wrong form renders a manifest
that does not parse equal.

## The renderer, the held values and the build proof

`tools/render_manifests.py <tables> <out> [--held FILE]` writes the 30 canonical manifests from the tables:
- TOML: the top-level keys, then each kind in the order of its first header, and each row's keys in the order of
  their lines;
- JSON: as layout/forms.tsv gives it.

Comments are not carried, so a rendered manifest is parse-equal to the original's, not byte-equal. Without `--held`,
a held value is written as the string `"HELD:sha1=<sha1>"`, which no build accepts.

`tools/gen_held.py <export> <romdir> <scratch> <out>` derives the five held values from the decrypted reference
dumps. It refuses unless each has the SHA-1 `facts/held.tsv` names.
- `index_window_018468` and both `hitclass_map_extend` rows come from the original's own generators, run from the
  export.
- `throw_arc_tables` is vs2's installer `PRG:0x0275E4`–`0x027622`, its two `(d16,PC)` table operands made
  absolute-long placeholders.
- `beam_list_type6` has five parts: an authored range check; vs2's handler `PRG:0x01A1FC` with its three A5 scratch
  slots moved and its child call retargeted; vanilla's type-6 head; an authored two-way dispatcher; and vanilla's
  drawer `PRG:0x01B61A`–`0x01B6AA` with its bank word `$2000`→`$1000` and its code bias `$3800`→`$7A00`.

Only addresses, lengths and the authored instructions are in the tool; every copied byte is read from the dumps
([VSR-8]). Not measured: the copied drawer opens with a `bcs.w` copied unchanged, so its PC-relative target moves
with the copy ([VSR-83]). Whether that branch is reachable was not checked; it is for phase 1's own generator.

The gate on the derivation is `python3 tests/test_gen_held.py` (it needs `../ROMS`):
- H1: the tool writes one literal per distinct held SHA-1.
- H2: every held row is covered, checked by a SHA-1 computed apart from the tool's.
- H3: the 30 manifests rendered with those literals parse equal to the originals, with no placeholder left.

Its controls are `wrong-held-sha` (the tool must refuse) and `placeholder-left`.

**The build proof is phase 1's** (the maintainer's ruling of 2026-10-18, SPEC.md §0). `tools/build_proof.py` runs
the original's `build_merged.sh` on a pristine export and on one whose canonical manifests are rendered from the
tables, then compares every output file byte for byte. It needs vhunt2: the original's extractor takes `vhunt2.zip`
as its sibling oracle (#4). It is committed, unrun; its control is `perturbed-render`. Its logic is gated without a
build by `python3 tests/test_build_proof.py`:
- P1 and P2: `compare()` in both directions;
- P3: the shimmed audit, loaded, requires no vhunt2 set, key or row and still requires vsav;
- P4: the control's perturbation changes exactly one value.

Its own control is `blind-compare`.

## The format, and why

**One TSV per subject, one schema for all**: `manifest, kind, row, key, value, line, prov_kind, prov_refs`. Each line
is one value.
- `manifest` is the path under the original's `build/manifest/`, and `kind` is the table kind the census reports.
- `row` is the TOML row's `name`. It is `name#n` when the name repeats within its kind, `#n` (the row's ordinal within
  its kind) when it has none, and `(top)` for top-level keys. For JSON, `row` is a JSON Pointer (RFC 6901): a dict
  member's row is its parent, and a list element's row is the element itself, with key `[]`. A pointer can address
  any key, among them the `.` glyph of `version_font.json`.
- `key` is the field.
- `value` is the manifest's literal as written (`true`, `0x0F`, `"donovan"`), so a renderer can reproduce the
  manifest exactly. The six TOML values that span lines are carried whole, from the parse; the census keeps only
  their first line, `[`.
- `line` is the value's line in the original at the pin (`-` for JSON).
- `prov_kind` and `prov_refs` are what the original's census attributes to the value: the first of its provenance
  words (`measured`, `ruled`, `derived`, `testimony`, `maintainer`; `none` when absent or when the block is a
  retraction), and the session keys, tickets and dates the block names. The full paragraph is at `line` in the pinned
  original.

**Why this format** (`SPEC.md` §4, "the manifest subset", decided afresh):
- **TSV**, because the community reviews these values and a reviewer reads, greps and diffs a TSV without a parser.
  The original's registries are TSV for the same reason.
- **One schema**, because the census, the renderer and the gate then read every table the same way.
- **Literal values**, because phase 0's proof is that the original's manifests are reproduced from the tables.
- **References, not paragraphs**, because the comment blocks run to whole paragraphs, can quote bytes, and stay
  readable at their pinned line. Whether the rebuild carries them verbatim is decided when phase 1 needs them.

The gameplay rows are keyed by subject because a reviewer asks "which rows only apply to the variant slot", not
"what is in donovan.toml".

## Where the values come from, and the gate

GENERATED by `tools/extract_tables.py <export> <pin> <out>`. The export is made by `tools/export_original.py`. The
extractor imports the original census (`tools/audit_rule5.py` in the export) and aligns each record with its row
(`tools/phase0lib.py`); it reads the generators' constants by an AST walk. Each table's header names the pin and the SHA-1 of every manifest it was read from. Until
phase 0 closes, a generated table is not hand-edited: a change comes from the original or from a ruling, through the
extractor. `facts/held.tsv` is the one hand-written file.

The gate is `python3 tests/test_phase0_tables.py`. It has six checks:
- G1: the tables regenerate byte-for-byte, and no other generated table exists.
- G2: the export's manifests and generators have the SHA-1s the headers name.
- G3: per column, the census and the tables are the same multiset, with unique row ids (`code/uncounted` is not the
  census's, and G6 holds it).
- G4: every cell equals an independent parse (`tomli` / `json`) of its manifest, and a one-line TOML value's line
  reads `key = value` and then only a comment (a string may hold a `#`). A code cell has the same token stream as its generator's expression (so hex written as
  decimal fails) and evaluates to the same value, and its line is the assignment's.
- G5: a held value is only its hash, its hash is the manifest's value's, and no cell carries a held value in the
  clear.
- G6: the code tables name every public module-level constant of the census's generators, found by an AST walk
  written apart from the extractor's, and `code/uncounted` holds exactly those the census has no record of.
- G7: the gameplay, fact and uncounted tables hold every value of every canonical manifest exactly once, found by a
  walk of each manifest's parse written apart from the extractor's.
- G8: the renderer's 30 manifests parse equal to the originals (`tomli` / `json`, key order included), a held value
  only as the placeholder of its SHA-1. The original's own parser (`_minitoml`, its subset parser on this host's
  Python 3.9) accepts the same 21 manifests and parses each equal; it refuses `dispatch_census.toml`,
  `pcrel_escapes.toml` and `shared_writes.toml` (arrays) in both forms.

Its fourteen declared controls are perturbed copies: `perturbed-value`, `dropped-row`, `perturbed-manifest`,
`held-leak`, `perturbed-pointer-fact`, `perturbed-code`, `code-hex-as-decimal`, `uncounted-dropped`,
`perturbed-generator`, `note-dropped`, `perturbed-note`, `note-cut-at-hash` (a note cut at its `#`, as a line
grammar cutting at the first `#` would read it), `layout-form-flipped` and `json-order-swapped`.
Each must fail exactly its declared checks, and `--control <name>` runs the gate on the copy, where it must FAIL.
Every run works in its own new scratch directory under `build/tmp/`, removed when it ends, so runs can go side by
side ([VSR-143]).

Measured at the fact column's extraction (R-001): 8,756 rows in 56 tables (gameplay 236, fact 8,520), 26 manifests
pinned; G1–G5 pass (0 only-in-census and 0 only-in-tables in each column, 0 duplicate ids, 8,751 cells checked and 0
wrong, 5 held, 0 values in the clear); the five controls FIRED; the five control modes `VERDICT: FAIL`. Provenance
of the 236 gameplay values: `measured` 188, `ruled` 9, `maintainer` 3, `none` 36.

Measured at the code column's extraction (R-003): 8,802 rows in 58 tables (gameplay 236, fact 8,520, code 30 and
16 uncounted), 26 manifests and 6 generators pinned. G1–G6 pass: 0 only-in-census and 0 only-in-tables in each
column, 0 duplicate ids, 8,797 cells checked and 0 wrong, 5 held and 0 in the clear, 46 public constants and 0
missing. All nine controls FIRED, and the four new control modes each give `VERDICT: FAIL`.

Measured at the uncounted values' extraction (R-003): 11,330 rows in 76 tables (the 8,802 above and 2,528
uncounted in 18). G1–G7 pass: 11,325 cells checked and 0 wrong; 30 canonical manifests (4 with no value) hold
11,284 values, all 11,284 in the tables, 0 missing and 0 unknown. All twelve controls FIRED, and the three new
control modes each give `VERDICT: FAIL`.

Measured at the renderer (R-003): 11,703 rows in 77 tables (the 11,330 above and the 373 of `layout/forms.tsv`);
36 sources pinned (the 30 canonical manifests and the 6 generators). G1–G8 pass: the 30 manifests render and parse
equal, and `_minitoml` accepts 21 and differs on 0. All fourteen controls FIRED, and the two new control modes each
give `VERDICT: FAIL`. `tests/test_gen_held.py`: H1–H3 pass (4 literals, 5 held rows covered, 30 manifests parse
equal with 0 placeholders left), and both controls FIRED.
