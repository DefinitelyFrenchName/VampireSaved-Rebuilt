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

Three more gameplay tables, `jump_physics.tsv`, `cancel_windows.tsv` and `bank_values.tsv`, are decoded from the original's extraction
records, not from the census (below, "The extraction tables"; #4). A fifth, `doll_hop.tsv`, is read from vs2 itself
(below, "The doll's hop, vs2's rows"; #6).

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

**The build proof** (ruled phase 1's on 2026-10-18, SPEC.md §0, while vhunt2 was absent; run in R-005).
`tools/build_proof.py` runs the original's `build_merged.sh` on a pristine export and on one whose canonical manifests
are rendered from the tables, then compares every output file byte for byte. It needs vhunt2: the original's
extractor takes `vhunt2.zip` as its sibling oracle (#4). The maintainer provided `vhunt2.zip` in R-005 (its 21 members
match the original's `docs/checksums.txt`).
- **The audit shim** (ruled "Shim both legs") now drops only the vhunt2 sets ROMDIR lacks, `vhunt2r1.zip` today, so the
  original's audit checks the vhunt2 it has. Nothing in the original's build reads `vhunt2r1.zip` but that audit (it
  is named only there, in the release preflight and in a character-page script).
- **Paid for in R-005** (gotcha, [VSR-32]):
  - a relative ROMDIR resolved inside each leg found no ROMs; the tool now resolves it first;
  - the control's perturbation took the first `[[aux_poke]]`, `only_base_slot`. The merged build (Donovan at 0x13)
    never applies that row, so the control ran DEAD on the first real build. It now takes the first row the build
    applies. A control written before its instrument could run was never exercised: run it once the instrument
    exists.

Its logic is gated without a build by `python3 tests/test_build_proof.py`:
- P1 and P2: `compare()` in both directions;
- P3: the shimmed audit, loaded for a ROMDIR with no vhunt2 set and for one with `vhunt2.zip` alone, requires exactly the
  sets present (and still requires vsav);
- P4: `perturbed-render`'s perturbation changes exactly one value, in a row the merged build applies;
- P5: `perturbed-shared`'s changes exactly one value in each of the three tenant manifests, and the three rows stay
  identical, so the original's generator still emits one shared row (R-006, #7).

Its own control is `blind-compare`.

Measured (R-005, a measurer, from the run logs):
- **The proof PASSES.** Both legs build: pristine in 151 s, rendered in 149 s. It compared 175 files (25 zip members),
  with 0 non-log files and 0 logs differing.
- **The program fingerprint matches the original's last freeze.** Both legs report `6148d0b1…`, the merged program
  fingerprint the original recorded at that freeze (its `HANDOFF.md` line 161: *"merged `110467a7` -> `6148d0b1`"*).
  So the tables reproduce the original's frozen merged build, through its own pipeline.
- **The control** (`perturbed-render`, `hud_mug_entry_13` `val` +1) FAILs. The rendered leg's build is rejected by
  the original's own HUD check (*"expected one poke16 at 0x898aa val 0x8690"*), so this control does not reach the
  byte compare.
  - ~~**Not exercised end to end:** a perturbation the original's own checks accept, which only the compare would
    catch. `compare()`'s sensitivity is P2's, on synthetic files (#7).~~ RESOLVED (R-006): `perturbed-shared`, below.
- **The second control** (`perturbed-shared`, R-006, #7): `boot_title_saved_1` (the boot title, `PRG:0x01C822`)
  `val` +1 in donovan.toml, huitzil.toml and pyron.toml alike. The original's generator emits the three as one
  shared row, so the op count is unchanged, and no check of its build reads the boot title. Measured (a measurer,
  from the run log):
  - both legs build: *"pristine exit 0 in 158 s"*, *"rendered exit 0 in 155 s"*, each ending *"OK: merged build
    with gfx"*;
  - *"compare 175 files (25 zip members); differing non-log files 7, differing logs 1"*: `README.txt`,
    `patch/patch.json`, `patch/patch_notes_fragment.md`, `prg/vm3j.03d`, `rompath/vsavjw.zip` (member `vm3j.03d`),
    `verify_data.bin`, `verify_op.bin`; the log `patch_prg.log`;
  - `VERDICT: FAIL (7 files differ)`.
  So the byte compare is exercised end to end: the original's checks accept the build, and only the compare fails it.

## The extraction tables, under `extraction/`, and the three gameplay tables decoded from them (#4)

**What they are.** The original's extractor (`tools/extract_char.py`) diffs vsav2 against its sibling vhunt2 and
writes one record per tenant, `regions.json`. It holds every ported region with its vhunt2 twin and shift, every
relocation ref, the code scan, the dispatch pairs and the per-character bank values. No vhunt2 byte reaches the
output, but the measurement needs vhunt2 (#4). The maintainer's direction (`SPEC.md` §0) was to table it. The records
tabled are the three the original's merged build reads, `tools/build_merged.sh` lines 36–38: `D_EX="build/m5_wide/extract"`,
`H_EX="build/hui32/extract"`, `P_EX="build/pyron21/extract"`. Together they hold 153,013 scalar values: Donovan
49,141, Huitzil 54,872, Pyron 49,000.

**They record what was measured, not what the extractor computes today.** The original notes that `m5_wide`'s
record *"predates two `extract_char.py` changes"* (its `HANDOFF_HISTORY.md` line 2412, on `test_merged_inputs.sh`,
#27 there: the merged ARTIFACT is reproducible, the input directories are not byte-equal). Re-running the original's
extractor today would not reproduce these tables. They are what its merged build consumed.

**The format.** These tables keep the record's own columns, not the shared schema. Each section of the record is one
table, with a leading `tenant` column:

| table | rows | what it holds |
|---|---|---|
| `extraction/runs.tsv` | 3 | each record's path, the source and sibling sets (`vsav2`, `vhunt2`) and the character id |
| `extraction/inputs.tsv` | 27 | the SHA-1 of every vsav2 member each record read |
| `extraction/shifts.tsv` | 64 | each shift family's vsav2 → vhunt2 shift |
| `extraction/regions.tsv` | 78 | each region: `src` (vsav2), `orc` (its vhunt2 twin), `len`, `grow`, `kind`, `shift`, the `source_only` / `pre_classified` flags, `raw_from`, `sha1` |
| `extraction/region_lists.tsv` | 1,823 | each region's lists, in order: `dead` and `ins` spans (`start,end`), `charid_sites`, `table_bytes`; `(empty)` for an empty list |
| `extraction/refs.tsv` | 23,533 | every relocation ref, in the record's order: `off`, `width`, `target`, `orc_target`, `shift`, `class` |
| `extraction/variant_sites.tsv` | 35 | the bytes where vsav2 and vhunt2 differ inside a region |
| `extraction/pcrel_refs.tsv` | 11 | the PC-relative table entries of the source-only regions |
| `extraction/code_scan.tsv` | 4,524 | the code scanner's operands, in order |
| `extraction/dispatch.tsv` | 58 | the per-character dispatch targets, vsav2 and vhunt2 |
| `extraction/engine_dispatch.tsv` | 2 | the engine dispatch targets that differ by a delta |
| `extraction/values.tsv` | 87 | the per-character bank rows: pointers as written; each decoded row says `TABLE:<name>` |
| `extraction/auto_tables.tsv` | 57 | the bank gaps the extractor classified, with its entry guess (`gap_be23a`'s says `TABLE:bank_values`) |

Every integer is hex (`0x…`, `-0x…`) except `width`, a bit count. Strings are as written (a `ptr` stays `"0x27f548"`).
An absent key is `-`. Addresses are PRG offsets of the set the column names ([VSR-31]). The JSON objects' key order
is not carried, because it is not data; every list's order and the regions' order are, by row order. Each header
names the pin and the SHA-1 of `build_merged.sh` and the three records. The gameplay tables' headers also name the
two fact tables they compute addresses from.

**The three gameplay tables** (the maintainer's rulings, `SPEC.md` §0: *"Readable gameplay table (Recommended)"* for
the three long rows, and *"I lean yes since tables is what we decided and that data is valuable"* for the short
ones). Each record carries vs2 bank rows as raw bytes. They are decoded into named fields here, and each row names the vs2
address it was read from, `origins.vsav2 + (vsavj − origins.vsavj) + char × entry size`. That is the original
extractor's own `table_addr`, with `bank_map.toml`'s facts (`facts/origins.tsv`, `facts/table.tsv`).
- `jump_physics.tsv` (9 rows): `jump_params`, three jumps per tenant (`neutral`, `forward`, `back`) of `xv`, `xaccel`,
  `yv`, `gravity`. Each value is the engine's signed 16.16 long written as its exact decimal (`-0.01953125` is
  `0xFFFFFB00`). The layout is the original's, *"`PRG:0x0BDB7A` jump_params — id*0x30, THREE 0x10 rows
  (neutral/fwd/back jump) of (xv,xacc,yv,gravity)"*, whose consumer is *"the installer every seq-0600 starter bsr's
  (vsavj 0x27A34 / vs2 0x26C86)"* (its `docs/game/atlas/ram.md` lines 337–340). The field names are its
  `charmap_gen.py`'s. Units are not measured here.
- `cancel_windows.tsv` (90 rows): `byte2d_a` and `byte2d_b`, 30 bytes per tenant, one row per move index with
  `special` and `ex`. In the original's measurement (14z-194, #118 there, its `ram.md` lines 266–267), struct `+0x167` is
  *"loaded 0-1 f later from a per-character, per-move table (PRG:0x027EA2: PRG:0x0BE89A + char*30 + move; 10
  typical, 3/9 others), -1 per tick (PRG:0x0224DA): a special-cancel window opened with the normal"*, and `+0x168`
  is *"the same for EX: table PRG:0x0BEC5A (12 typical, 3/11 others)"*. So a value is a window in ticks. Which normal
  each move index is was not measured, there or here.

- `bank_values.tsv` (33 rows): each tenant's own short bank rows, one row per field, with `format` (`s16.16` as
  above, `u16`, `u8`) and the vs2 address. The fields:
  - `param32_a`: `fwd_walk_xv`, `back_walk_xv`, the original decoder's names. Its consumer is *"read id*8 from
    0x0BD87A at vsavj 0x0228E2/0x0271A8"*. Its notes on the `gap_bd8fa` slice (`bank_map.toml` line 210) record
    the reader, not the meaning. The original measured the meaning in play: Donovan's *"X-velocity word, 2.5 ->
    3.0"* at the first movement frame once his vs2 rows were ported (its `patch_index.md` line 159). The table reads
    3 for him.
  - `param32_b`: `long0`, `long1`, named by position. The original's decoder calls them walk velocities too. But
    its 14z-121 note says *"param32_b read id*8 from 0x0BE2FA at vsavj 0x026484 for chain a2:0x4C, the pursuit
    leap"* (`bank_map.toml` line 392), so what the two fields are is not measured.
  - `gap_be23a`: `min_air_dash_height`. Among the auto gaps it is a *"REAL per-char WORD table (14z-121): the MINIMUM
    AIR-DASH HEIGHT"*. In the original, *"Phobos's row 0x10 carries vs2's 24 (0x0018) in ours, Donovan's and
    Pyron's stay 0"* (`bank_map.toml` line 342). The table reads 24, 0 and 0.
  - `word132`, `word_pos_a`, `word_pos_b`, `word_y_off`, `word_range` (`u16`) and `byte15b` (`u8`): the field is
    `value`. Their names are the original's, and their meaning is not recorded there. The extractor's entry size
    (stride / 32: 2 bytes, 1 byte) is the only layout evidence.

**Two rows are not the tenant's: `rec8_a` and `rec8_b`.** The extractor reads every `rec8` row as 8 bytes at
`char*8`. The original's notes put both inside larger per-character records:
- `rec8_a` is *"SLICE of jump_params rows 0-5 (14z-121: jump_params is read id*0x30 + {0,0x10,0x20} from 0x0BDB7A
  at vsavj 0x027A76; no reader of this base)"* (line 245);
- `rec8_b` is *"the PURSUIT physics record pair (14z-121): read id*0x20 + (+0x0A ? 0x10 : 0) from 0x0BE3FA at vsavj
  0x026646 = four longs (xv, xacc, yv, yacc) x 2 variants per char"* (line 399).

So a tenant's `rec8_a`/`rec8_b` bytes are another character's data. For Donovan (`0x13*8 = 0x98`) they are char 3's
neutral-jump `yv`/`gravity` and char 4's second pursuit variant's `yv`/`yacc`. They stay as written in
`extraction/values.tsv`, never in a gameplay table that would call them the tenant's. What the original's build wrote
for them, and what the tenants' own rows hold, is the next paragraph (R-004; until then both were "not measured").

**What the build wrote for `rec8_a` and `rec8_b`, and the tenants' own rows (R-004, read statically; confirmed on the
built image in R-005).** In R-004 the original's merged build could not be rebuilt here (#4: it needed vhunt2), so
this was read from its generator and the reference dumps. R-005 rebuilt it (the build proof, above), and
`tools/rec8_writes.py --built` reads that build's own data view and ops. It confirms the reading:
- the six writes hold the records' values;
- of the build's 848 ops, three touch the table at `PRG:0x0BE3FA` (the `rec8_b` writes), each equal to vanilla;
- 0 bytes of that table differ from vanilla.
- **The write rule, quoted by a reader** from the original's `tools/gen_donovan_patch.py`: a value row's address is
  *"`return _int(t["vsavj"]) + slot * es, es`"* (line 1630), with *"`es = ... (t["stride"] // 32)`"* (line 1629). It
  is written by *"`poke_bytes(a, data, f"{v['table']}[{dst_slot:#x}] value")`"* (line 3677), with
  *"`p["dst_slot"] = tid`"* (line 134). The variant mirror is *"`t.get("mirror_variant", tid < 0x10)`"* (line 135).
  The skip set is empty when *"`port_param32 = true`"*, which all three manifests declare (donovan.toml:32,
  huitzil.toml:42, pyron.toml:72). The gap tables are *"GAP TABLES DISABLED (session 14w)"* (line 3685). The merged
  build runs *"`--profile cps2-wide-v1`"* (`build_merged.sh`:60), which puts Donovan at 0x13 (`roster.tsv`'s
  `id_by_profile`).
- **The six writes change nothing.** By that rule each tenant's 8 bytes land at the table's vsavj base + id*8
  (Donovan 0x13 at `PRG:0x0BDC12`/`PRG:0x0BE492`, Huitzil 0x10 at `PRG:0x0BDBFA`/`PRG:0x0BE47A`, Pyron 0x11 at
  `PRG:0x0BDC02`/`PRG:0x0BE482`). These sit inside veterans' rows. Each write equals vsavj's bytes already there.
- **The tenants' own rows are a veteran's copy.** No generic value write reaches the newcomers' own rows of the
  table at `PRG:0x0BE3FA` (row id*0x20): a rec8 row writes id*8, and the gap rows that slice the table are not
  written. No manifest row phase 0 tables writes into the table either; the one address in its range is a
  `capture_kf_leilei` source (that is a reading of the manifests, and absence is the weakest evidence, [VSR-52]).
  - In vsavj each tenant's row equals its base-half row: Donovan's equals row 3, Huitzil's row 0, Pyron's row 1.
  - vs2's row for each tenant differs from it.
- **Both games read the table by the raw id.** The one load of the table in each game (vsavj `PRG:0x026646`, vs2
  `PRG:0x0252DC`) takes its index from `+0x382`, the character id. It multiplies it by 0x20 and adds 0x10 when `+0x0A`
  is set.
  - No ported region references vs2's table: the ported code's bank refs point elsewhere (`extraction/refs.tsv`).
  - In vsavj the load is called from substate 0 of a state handler at `PRG:0x026670`. That substate sets `+0x38`. Its
    substate 2 compares against the per-id word at `PRG:0x0BE7FA` (the `word_y_off` row).
  - The state (`+0x04` = `0x02100600`) is entered from `PRG:0x02657A`, which picks the variant from a 32-entry table
    by a call to `PRG:0x014E8A`. It is also entered from `PRG:0x026600`, which picks it from bits of `+0x395`.

So a newcomer that enters that state takes Victor's, Bulleta's or Demitri's values for it, not vs2's own. Not
measured at R-004, and answered since (R-005, "The state is the DOLL's hop" below):
- which move or situation the state is: the doll's hop after Anakaris's Royal Judgement, not the pursuit (the
  original's "PURSUIT physics record pair" label does not hold);
- whether a newcomer reaches it: yes, all three, and each hops differently on the original's build;
- how the difference feels: not asked; the ruling made it moot.

Ruled (c) then (a) (`SPEC.md` §0, R-004), then (2026-10-20) port vs2's rows by the ground rule.

**The capture, R-005 (first pass): the pursuit is not that state, and nothing captured reaches it.** `tools/state_capture.py`
runs the original's own rigs on native vs2 and on its merged build (the R-005 build proof's pristine leg), on the
WIDE MAME (`docs/project/instruments.md`), and traces both fighters' `+0x04` every frame:
- **The newcomers' pursuits run in routine `0x00`, sequence `0x0E`**, on both games: Donovan's Foot Stab at all four
  strengths `0x02000E02`/`0x02000E04` (ES `0x02001002`/`0x02001004`), Huitzil's and Pyron's Sitting Attack likewise.
  The table's handler is not the pursuit. The original's label ("the PURSUIT physics record pair", and "the pursuit
  leap" for `param32_b`, read at `PRG:0x026484` in the same handler) does not hold for the pursuit these rigs perform.
- **`0x02100600` is a sub-state of fighter routine `0x10`** (scratch reading, addresses only): the fighter dispatch on
  `+0x05` at `PRG:0x02244E` sends routine `0x10` to `PRG:0x026258`, whose sequence table puts sequence 6 at
  `PRG:0x026670`. Sequence 0 places the fighter at the per-id height `PRG:0x0BE7FA` above its floor, sets a 30-frame
  timer and waits for one of three inputs; one of them enters `0x02100600`. Routine `0x10` is stored from outside its
  handler only at `PRG:0x026D9A` and `PRG:0x06FD34`. vs2 has the same layout (its stores at `PRG:0x025012`-`0x025F1E`).
- **Nothing captured enters routine `0x10`, on either game, for any fighter**: the six naming parts that hold a pursuit
  (96 events), seven victim parts (Victor's hits, knockdowns, throw, blocks and air hits on each newcomer, real
  picks), eight tech-roll legs (the roll runs in routine `0x02`, `0x020202xx`; P2 travels 120-152 px over frames
  3060-3150 on both games), and the 97 top-level replays of the original's corpus (without their gates' pokes). Over
  all of them the fighters' routines seen are `0x00`-`0x0E` and `0x12`: every routine but `0x10` (a measurer's
  histogram of the traces' `+0x04` high words). This is absence, the weakest evidence ([VSR-52]), but on the veterans as much as on
  the newcomers, so it says the rigs do not reach routine `0x10`, not that the newcomers cannot.
- In the 96 naming events, the newcomer's state sequence is identical on both legs, state and frame, in 85. The 11
  that differ are Dark Force (activation and moves in it; the original's ported-Dark-Force rulings) and Huitzil's
  Sitting Attack landing off a throw, which is the original's #179 (closed `not-ours`: the shared-wall push-apart
  follows vsavj's engine).

**How routine `0x10` is entered** (scratch reading, addresses only). The `0x06FD34` store is an effect object's own
sub-routine (it steps `+0x05` by `addq #2` over an effect animation set), not a fighter's. A fighter enters routine
`0x10` only from `PRG:0x026D9A`, reached from two places in the damage routine (`0x02`, handler `PRG:0x0237C6`), whose
sequence 2 dispatches on the reaction class `+0x140`:
- class `0x16` (`PRG:0x0254B8`): falling, the fighter is caught at the per-id height `PRG:0x0BE7FA` above its floor
  and, unless dead (`+0x11F`), enters routine `0x10`;
- class `0x36` (`PRG:0x025FAE`): after a `+0x26` countdown, `+0x156` takes a duration from a table by `+0x56`, then
  routine `0x10`.
Both classes are assigned together, `0x36` on the ground and `0x16` in the air (`+0x38`), by the damage routine's
sequence 0 (`PRG:0x023E58`/`0x023E8C`, and sub-state `0x12` at `PRG:0x02479C`/`0x0247AE` after a `+0x5C` countdown).
Routine `0x10` then counts `+0x156` down and, for 30 frames, takes one of three inputs. ~~The shape (a timed state
after a hit, shortened by input, death checked) suggests a stun~~ RETRACTED (R-005, the maintainer): neither game has
a universal stun. What replaces it, a further scratch reading (R-005 (7) in `STATE.md`): `PRG:0x023E58` is entry
`0x18` of sequence 0's dispatch on the victim's `+0x54` (`PRG:0x02385C`), and `PRG:0x023E8C` is the branch taken when
`+0x156` is already set, so the "ground/air by `+0x38`" pairing above is unconfirmed. `+0x54` is the attack record's
reaction byte `+0x17`, copied at the hit (`PRG:0x018438`). So the state follows an attack whose record says `0x18`.
Which moves those are was not read (a scan finds char `0x06`'s record `0x24` in both games, and unconfirmed high
indices for others); the next paragraph measured the one the maintainer named.

**The state is the DOLL's hop (R-005, measured).** The maintainer: Anakaris's "Ouke no Sabaki" fits (mizuumi's Royal
Judgement, j.236P: *"On successful hit this move will morph the opponent into their paper doll form"*). The rig kind
`doll` of `tools/state_capture.py`: P1 Anakaris (0x06) lands it, P2 holds a direction through the doll; native vs2
against the original's merged build, speed level pinned ([VSR-26]). Holding up or up-forward makes the doll hop, and
the hop is sequence 6 of routine `0x10`, `0x021006xx`; holding left or right walks it (sequence 4, scratch runs). So
the table at `PRG:0x0BE3FA` is each character's doll-hop physics (`+0x0A` picks the variant: 1 on every leg here). The
first hop, by a measurer from the report (`build/tmp/capture_r005_doll.report`, WIDE MAME `5b08cce7`, the build's
`vsavjw.zip` `29252167`):

| P2 | held | native vs2: frames, airborne, peak dy, end dx | original's build | first hops |
|---|---|---|---|---|
| Victor 0x03 (control) | U | 44, 36, 87, 0 | 44, 36, 87, 0 | identical |
| Victor 0x03 (control) | UR | 42, 34, 81, 87 | 42, 34, 81, 87 | identical |
| Donovan 0x13 | U | 43, 33, 76, 0 | 46, 36, 87, 0 | differ |
| Donovan 0x13 | UR | 43, 33, 78, 90 | 43, 34, 81, 87 | differ |
| Phobos 0x10 | U | 33, 23, 60, 0 | 42, 32, 76, 0 | differ |
| Phobos 0x10 | UR | 33, 23, 60, 69 | 42, 32, 78, 90 | differ |
| Pyron 0x11 | U | 41, 30, 76, 0 | 43, 32, 76, 0 | differ |
| Pyron 0x11 | UR | 41, 30, 78, 67 | 43, 32, 78, 90 | differ |

So every newcomer reaches the state, and its doll hops differently on the build. The control is identical, so the
difference is the newcomers' rows, not the instrument. On the build Donovan's first straight hop is Victor's frame for
frame (the report's dx,dy lists), as his row is Victor's. Ruled (`SPEC.md` §0, 2026-10-20): phase 1 ports vs2's
three rows (#6). Pixels are the traced RAM position words, not measured against the screen.

`tools/rec8_writes.py <export> <roms>` prints all of the above, with the SHA-1 of each file it read. Its gate is
`python3 tests/test_rec8_writes.py`, anchored on the reference dumps:
- R1: the 6 writes equal vsavj's bytes.
- R2: the 3 rows are base-half copies, and vs2's 3 rows differ.
- R3: one load per game, indexed from `+0x382`.

Its three controls (`value-flipped`, `row-unaliased`, `index-elsewhere`) fire, and a control mode FAILs. Measured
(R-004, a measurer): `rec8 writes equal to vsavj's bytes: 6 of 6`, with both readers indexed from `+0x382`.

**No ROM bytes** ([VSR-8]): the tables hold addresses, offsets, lengths, shifts, short discrete values and SHA-1s.
No cell but a `sha1` holds a run of 17 or more hex bytes, which the gate checks (E4). The three long rows are the
decoded tables above, and the short rows are written as numbers.

**Generated and gated.** `tools/extract_regions.py <export> <pin> <out>` writes all 16 tables and prints the SHA-1 of
every file it read. `render()` there is the inverse. The gate is `python3 tests/test_extraction_tables.py` (it needs
`../ROMS`):
- E1: the tables regenerate byte for byte.
- E2: they render back to each record, parse equal, and their headers name each record's SHA-1.
- E3: every gameplay value, re-encoded, equals the byte at its vs2 row in vsav2's data view. The address is computed
  in the gate from the fact tables, and each row's own address column must agree. vsav2.zip's members, the key
  included, have the SHA-1s the records read. The anchor is the reference dump, not the record ([VSR-51]).
- E4: no hex runs of 17 or more bytes.

Its seven controls are `perturbed-ref`, `dropped-scan`, `gravity-sign`, `windows-swapped`, `air-dash-zeroed`, `bytes-in-values` (E2 stays
green, so E4 is what catches bytes in the clear) and `wrong-row` (E3 alone, with the tables untouched). The phase-0
gate and the renderer skip the three gameplay tables by their `GENERATED by tools/extract_regions.py` header, and
`doll_hop.tsv` and `raw_id_census.tsv` by their `GENERATED by tools/doll_hop.py` and `GENERATED by
tools/raw_id_census.py` headers (R-006). Those headers are the only ways a table leaves `test_phase0_tables.py`'s G1,
so a phase-0 table given one of them would leave it too.

Measured at the extraction (R-004): 30,401 rows in 15 tables. E1–E4 pass:
- E1: 15 files, 0 differing.
- E2: 3 of 3 records render equal.
- E3: 189 values checked, 0 differing from vsav2's row; 27 inputs, 0 not in vsav2.zip.
- E4: 225,847 cells, 0 runs.

All six controls FIRED, and each control mode gives `VERDICT: FAIL`.

Measured at the short rows (R-004): 30,434 rows in 16 tables (`bank_values.tsv` 33). E1–E4 pass:
- E1: 16 files, 0 differing.
- E2: 3 of 3 records render equal.
- E3: 222 values checked, 0 differing from vsav2's row; 27 inputs, 0 not in vsav2.zip.
- E4: 226,045 cells, 0 runs.

All seven controls FIRED, and the new control's mode (`air-dash-zeroed`) gives `VERDICT: FAIL (E1, E2, E3)`.

## The doll's hop, vs2's rows (#6)

**What it holds.** `doll_hop.tsv` (6 rows) is each newcomer's two rows of the doll-hop table: vsavj `PRG:0x0BE3FA`,
vs2 `PRG:0x0D8598`, row id*0x20, variant `+0x0A` (0 or 1) at +0x10, four signed 16.16 longs `xv`, `xaccel`, `yv`,
`yaccel` (written as `jump_physics.tsv` writes them). They are vs2's rows, read from vs2's data view at the tenant's
vs2 char id (`extraction/runs.tsv`), and each row names its vs2 address. Ruled 2026-10-20 (`SPEC.md` §0): the
newcomers take vs2's rows. What the variants mean is not measured; the doll rig's legs all run variant 1 (above).

**Generated and gated.** `tools/doll_hop.py <export> <roms> [--write]` writes it and prints the SHA-1 of every file
it read. Its gate is `python3 tests/test_doll_hop_table.py`, anchored on the reference dumps:
- H1: the committed table equals the rows read now from vsav2, and its header names the dumps read.
- H2: each game has one reader of its table, indexed from `+0x382` (the raw id on both games).
- H3: each tenant's vs2 row differs from vsavj's row at the same id.

Its three controls (`value-flipped`, `index-elsewhere`, `rows-equal`) fire, each failing exactly its own check.

**The port's gate, `tests/test_doll_hop.py <build dir> <out dir>`.** It runs the `doll` rig of
`tools/state_capture.py` unchanged (8 parts, native vs2 against the build, WIDE MAME) and judges every hop's ordered
per-frame (dx, dy):
- K1: every leg traced, at least one hop, and P2's id in the state is the part's. A part failing it is VOID, never
  judged.
- K2: Victor's hops are identical on both legs (his row is vsavj's on both games: the instrument check).
- K3: each newcomer's hops are identical on both legs.

Start frames are reported, not asserted. Its controls perturb the recorded traces: `victor-moved` (K2),
`newcomer-moved` (K3), `hop-missing` (K1).

**Until phase 1 builds, the passing leg is `tools/doll_build.py`.** That is the build proof's rendered leg (the
original's merged build from these tables) with each tenant's rows appended to its rendered manifest as 8 `poke32`
`[[aux_poke]]` rows, at the table's vsavj base + id*0x20 + variant*0x10. The original's build freezes its op count
(848 in the leg's `tests/test_tenant_loop.sh`), so the leg's copy is raised by exactly the rows appended. After the
build the tool checks the built table against the rows and vanilla.

Measured (R-006, a measurer, from the run logs):
- **The build.** Three appends of 8 rows (Donovan `PRG:0x0BE65A`-`0x0BE67A`, Huitzil `PRG:0x0BE5FA`-`0x0BE61A`, Pyron
  `PRG:0x0BE61A`-`0x0BE63A`), op count 848 -> 872. *"build exit 0 in 154 s"*, every check of the original's build
  passing. *"built: table PRG:0x0BE3FA-0x0BE7FA, bytes differing from vanilla 19, from the expected rows 0"*.
  Its `vsavjw.zip` is `bdb58c14`.
- **The gate on the original's merged build** (`29252167`, the build proof's pristine leg): `VERDICT: FAIL (K3)`.
  K1 8 parts, 0 void; K2 2 of 2 identical; K3 0 of 6 identical. This is the defect, as measured in R-005.
- **The gate on the build with vs2's rows** (`bdb58c14`): `VERDICT: PASS`. K1 8 parts, 0 void; K2 2 of 2; K3 6 of
  6 identical, every hop of every part. On it the first straight hops are Donovan 43 frames, 33 airborne, peak 76;
  Phobos 33, 23, 60; Pyron 41, 30, 76. These are native vs2's, in the table above.
- **The controls.** All three FIRED on the passing build. On the original's build `newcomer-moved` is
  UNJUDGEABLE, because K3 already fails there. Each control's mode gives `VERDICT: FAIL` with its own check.

So for what the rig reaches (variant 1, holding U or UR), vs2's three rows are the whole difference in the doll's
hop: nothing else had to change for it. Variant 0 is ported from the same rows but no rig reaches it yet. The WIDE MAME
was `5b08cce7`. What phase 1 owes: its pipeline writes `doll_hop.tsv`, and this gate runs on its build.

## The raw-id census (#6)

**What it answers.** Which tables the engine reads by the raw character id `+0x382` give a newcomer its shell's row,
where vs2 has a row of its own. By the ground rule (`CLAUDE.md` [VSR-40]) those rows must be vs2's. A missing row has
no symptom to steer toward, so the list is made by enumerating ([VSR-186]). The doll table, measured in play (R-005,
R-006), is the anchor the static reading must reproduce ([VSR-187]).

**The bank map is not the engine's layout** (paid for in R-006). The original's `bank_map.toml` (`facts/table.tsv`)
slices the per-character bank into tables with guessed entry sizes. Compared by those slices, the doll table reads as
vs2's for all three newcomers: `rec8_b` takes 8 bytes per id, but the engine reads 0x20 per id, over `rec8_b` and
`gap_be4fa`–`gap_be77a`. So the census takes each table's base and row size from the code that reads it.

**How** (`tools/raw_id_census.py <export> <roms> [--built DIR] [--write]`, its header has the detail):
- every `move.b`/`move.w $382(An),Dn` in each game's opcode view;
- from each, the code forward to the indexed access the id reaches, following the register through copies and
  scaling, which gives the base and the row size;
- each vsavj table paired with its vs2 twin, by the bank's one shift inside the bank and elsewhere by aligning the two
  games' ordered read sites by shape;
- each table read in the view its access uses: a `(d8,PC,Xn)` read is a program-space fetch, which CPS-2 decrypts, so
  it is read in the opcode view, any other read in the data view ([VSR-87]);
- per newcomer: whether vsavj's row at the id is a copy of its base-half row (`shell`), and whether vs2's row at the
  id differs from vs2's own base-half row (`vs2_own`). A row to port has both.

`raw_id_census.tsv` (79 rows) holds the dumps' facts only. Its gate is `python3 tests/test_raw_id_census.py`:
- C1: the inventory regenerates;
- C2: the doll table is in it as measured;
- C3: both scans find their loads.

Its three controls (`table-edited`, `blind-scan`, `shift-off`) fire, each failing exactly its declared checks.

Measured (R-006, a measurer):
- **The scan.** 196 id loads in vsavj and 209 in vs2. In vsavj, 146 reach an indexed access, 36 of them with a base
  register set outside the code read. 79 tables are paired and 4 unpaired (`PRG:0x004DEC`, `PRG:0x03D664`,
  `PRG:0x049B30`, `PRG:0x04FFA8`).
- **To port** (from the dumps): *"rows 167 in tables 61; code-dispatch 5, code-value 74, pointer 77, value 11"*.
- **The original's merged build** (`--built`, its `verify_data.bin` `a6365f0d`): of the 237 newcomer rows, 75 are
  vs2's, 74 vanilla's and 88 rewritten. Of the 167 to port, *"left on vanilla's shell row 61 in tables 23;
  code-dispatch 3, code-value 54, pointer 1, value 3"*:

| table | kind, row | newcomers left on the shell's row |
|---|---|---|
| `PRG:0x0111F8` | code-value, 2 | Donovan, Huitzil, Pyron |
| `PRG:0x02ADEC` | code-dispatch, 2 | Donovan, Huitzil |
| `PRG:0x02B650` | code-dispatch, 2 | Donovan |
| `PRG:0x02E970` | code-value, 4 | Donovan, Huitzil, Pyron |
| `PRG:0x0331EA` | code-value, 2 | Donovan, Pyron |
| `PRG:0x0373CA` | code-value, 1 | Donovan, Huitzil, Pyron |
| `PRG:0x03A60A` | code-value, 4 | Donovan, Huitzil, Pyron |
| `PRG:0x0402BA` | code-value, 4 | Donovan, Huitzil, Pyron |
| `PRG:0x055344` | code-value, 4 | Donovan, Huitzil, Pyron |
| `PRG:0x05868A` | code-value, 2 | Donovan, Huitzil |
| `PRG:0x058700` | code-value, 4 | Donovan, Huitzil, Pyron |
| `PRG:0x0587A6` | code-value, 2 | Donovan, Huitzil |
| `PRG:0x058806` | code-value, 2 | Donovan, Huitzil, Pyron |
| `PRG:0x058AD8` | code-value, 4 | Donovan, Huitzil, Pyron |
| `PRG:0x0599CC` | code-value, 4 | Donovan, Huitzil, Pyron |
| `PRG:0x05B01E` | code-value, 4 | Donovan, Huitzil, Pyron |
| `PRG:0x06139C` | code-value, 4 | Donovan, Huitzil, Pyron |
| `PRG:0x067BC4` | code-value, 4 | Donovan, Huitzil, Pyron |
| `PRG:0x06D6F4` | code-value, 1 | Donovan, Huitzil, Pyron |
| `PRG:0x073ECA` | code-value, 1 | Donovan, Huitzil, Pyron |
| `PRG:0x076AB0` | code-value, 1 | Donovan, Huitzil, Pyron |
| `PRG:0x0BE3FA` | value, 0x20 | Donovan, Huitzil, Pyron (the doll's hop: vs2's rows tabled in `doll_hop.tsv`, R-006) |
| `PRG:0x0BF59A` | pointer, 4 | Huitzil |

**What the census does not say.**
- **It is static.** A row on this list is one a newcomer *reads* if it reaches the reading code. Whether it does in
  play, and whether a player could feel it, is measured per table, as the doll table was. Only the doll table is
  measured.
- **What each table holds is not read here.** Some of these tables may be cosmetic or single-player surfaces
  ([VSR-41]), and the original may route a newcomer around a reader by a thunk at a caller, which a check of the read
  site's own bytes does not see.
- **Pointer tables.** The pointed-to content is not compared, so "rewritten" means only "not vanilla's bytes".
- **Not reached by the scan:** id loads whose base register is set outside the code read (36), the 4 unpaired tables,
  reads through another field holding the id, and code that compares the id to a constant.
- **Two pairings disagree.** For 7 bank pointer tables (`PRG:0x0BD17A`–`0x0BD37A`, `PRG:0x0BF31A`, `PRG:0x0BF39A`)
  the site alignment names the next vs2 table, not the bank shift's (the `paired` column says so). All 7 are rewritten
  by the build.

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
