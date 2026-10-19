# THE INSTRUMENTS — the emulators this repository builds to measure with

**What this document is.** The reference record of every emulator binary this repository builds as an instrument:
its pinned source, how it is built, what proves it measures what the original's frozen expectations were measured
with, and the gotchas paid for. The rule is `CLAUDE.md` [VSR-9] (built from pinned, recorded sources, the reference
binary first; an instrument is never moved without re-proving what it measures); the facts about the emulators are
the `mame-fbneo-instruments` skill ([MFI-NN]). A profile patch ([VSR-2]) is recorded here only once the maintainer
ratifies it for this repository; its spec has one copy, in its own document.

**Where things stand (R-005).** Two MAME binaries from the one pin: the reference (no patch), proven the instrument
that froze the original's MAME expectations, and the CPS-2 WIDE v1.2 profile (ratified 2026-10-19, `SPEC.md` §0;
spec `docs/project/cps2_wide.md`), proven inert on stock content and reaching its appended banks. No FBNeo yet.

## MAME, the reference build (R-005)

**The pin.** Commit `27a8d9e85b58058965907d1d8a7a92f8ed039348`, tag `mame0288`: the original's gitlink `emu/mame` at
`bf92acd2` and the `PINNED` of its `tools/setup_mame.sh`. MAME 0.288 is the version of the Homebrew binary that froze
the original's vanilla oracle logs (the header of its `tests/test_mame_parity.sh`).

**The build.** `python3 tools/setup_mame.py build/emu/mame-ref [--profile none] [--source URL_OR_PATH]`:
- fetches the pinned commit into a bare repository and refuses any other commit;
- extracts its tree with `git archive` (no working copy, so nothing can be dirty);
- builds the CPS-2 subtarget as the original does: `make SUBTARGET=cps2 SOURCES=src/mame/capcom/cps2.cpp NOWERROR=1
  REGENIE=1`;
- asserts on the binary, not the exit code: it knows `vsavj` and does not know `vsavjw`;
- records the pin, the make line, the toolchain and the binary's SHA-1 in `build/emu/mame-ref/build.json`.

No profile patch is applied; the WIDE binary is the same tree plus the patch, in its own directory (below).

**The binaries of R-005** (macOS, Apple clang 21.0.0, SDL3 3.4.12, pkgconf 3.0.5; source fetched from the original's
local submodule, read-only, its commit checked against the pin; `-version` *"0.288 (unknown)"*; 1.6 GB on disk each
with its objects): `build/emu/mame-ref/mame/cps2`, first SHA-1 `ec1ebce91920e0a73e90eb91733ffd7edd6ec1cd`, proven;
relinked three times (the first gotcha below), now `f17f851cefe58dfa1f181a724560913cee14cda8`, proven again.

**The proof: `tests/test_mame_reference.py`.** A class F gate (`SPEC.md` §5.1): it runs the original's own
`tests/test_mame_parity.sh`, unchanged, in the export, with this binary as its source build and Homebrew's `mame`
(SHA-1 `0526f872…`, 0.288) as its reference. Its checks:
- M1 identity: the binary is the one `build.json` recorded, at the pin, with no `vsavjw`;
- M2 parity: the original's verdict is PASS; every frozen row (section 1, the vanilla `vsavj` logs; 1b, the reference
  binary's frozen logs of the other replays) reproduced twice; every replay frozen nowhere (sections 2 and 3) identical
  on both binaries, none skipped; and the original's in-gate control fired.
Controls: `other-binary` (M1 on Homebrew's binary) and `wrong-hash` (the original's own mode). Result: see
"R-005's runs" below.

**R-005's runs** (a measurer read the logs and the run log), on `ec1ebce9`:
- normal, first run: FAIL on M2 alone; the original's verdict was PASS (the gotcha below);
- normal: `VERDICT: PASS`, 393.9 s. *"M2 sections 1/1b replays 24/65, rows ok 89; A/B sections 2/3 replays 8/0,
  identical 8; rows failed 0, sections skipped 0"*; the original's *"PASS: MAME parity."*; both controls FIRED,
  `wrong-hash` in the original's own words (*"103_tenant_2pwin_auto's real log (8604a925…) passes against its frozen
  hash and fails against the hash with one digit changed"*);
- `--control wrong-hash`: `VERDICT: FAIL (M2)`, the 65 perturbed rows failed, the 24 vanilla logs still ok;
- `--control other-binary`: `VERDICT: FAIL (M1)`, Homebrew's SHA-1 is not `build.json`'s.

On `f17f851c`, after the relinks: `VERDICT: PASS`, the same M2 figures (24/65, 89 ok; 8/0, 8 identical), both controls
FIRED.

So the binary built here from the pin is, on every replay the original froze or can A/B, the instrument that froze
the original's MAME expectations. It cannot run the WIDE set (`vsavjw`); that is the WIDE binary's.

## MAME, the CPS-2 WIDE v1.2 profile (R-005)

**The build.** `python3 tools/setup_mame.py build/emu/mame-wide --profile wide`: the same pinned tree with
`emu/mame-patches/0002-cps2-wide-v1.patch` (the original's, byte for byte: git blob `587e0353`, SHA-1 `1d13c9d8…`)
applied by patch(1), its markers asserted in the tree (`cps2wide` in cps2.cpp, the row `vsavjw` in mame.lst) and the
binary asserted to know `vsavjw`. `build.json` records the profile and the patch's SHA-1. R-005's binary:
`build/emu/mame-wide/mame/cps2`, SHA-1 `5b08cce7d3231921ad2bab68ed872aafa23ec133`.

**The romsets it runs** (built in the export by the original's `tools/build_wide_romset.py`, the commands of
`docs/project/cps2_wide.md` "From HANDOFF.md"; outside git, never distributed, [VSR-8]):
- `build/wide0/rompath`, the shippable overlay (`--qsound 2 --gfx 4 --prg 4`, appended members zero-filled);
- `build/wide_canary/rompath`, the B4 canary (`--gfx-copy-group-b`), kept apart: its group C carries group B's CRCs
  and would hash-shadow a patched group B ([MFI-44]).

**The proof: `tests/test_mame_wide.py`.** A class F gate: the original's own `tests/test_mame_wide.sh`, unchanged, with
both binaries and both romsets, over its 12-replay legacy corpus, each comparison on work RAM AND framebuffer:
section 1 the emulator superset invariant (stock vsavj, reference binary against WIDE binary), section 2 inertness
(WIDE set against stock set, same binary), section 3 the B4 canary (`CPS2_WIDE_CANARY=1`, sprites of banks 2/3 drawn
from banks 4/5). Checks: W1 identity (both build records, both SHA-1s, `vsavjw` known by the WIDE binary only), W2 the
original's PASS with every section `ok` on all 12, none failed or skipped. Controls:
- `ref-as-wide`: W1 with the reference in the WIDE binary's place, must fail;
- `canary-unreached`: a perturbed copy of the original's gate whose canary run reads the shippable overlay (group C
  zero-filled) instead of the canary set; section 3 must FAIL on the framebuffer ([MFI-39]). A normal run fires it on
  one replay (`02_demitri_vs_cpu`).

**R-005's runs:**
- normal, first run (2,165.7 s): the original *"PASS: CPS-2 WIDE profile gate (MAME) … over 12 replays"*; sections
  1, 2 and 3 each `ok 12, failed 0`; both controls FIRED (*"02_demitri_vs_cpu: sections 1 and 2 ok, section 3 FAIL on
  the framebuffer alone"*); the wrapper's verdict FAIL on W2 from its own corpus count (the gotcha below);
- `--control canary-unreached` (1,417.7 s): FAIL (W2), section 3 *"ok 1, failed 11"*, sections 1 and 2 ok 12. The one
  replay left `ok` is `06_test_mode` (a measurer read the log), which draws no bank-2/3 sprite;
- `--control ref-as-wide`: FAIL (W1).
The superset invariant and inertness hold on RAM and pixels, and the 19-bit tile address reaches the appended banks.

## Gotchas paid for

- **A relink moves the instrument, even from the same objects** (R-005, macOS, Apple clang 21). The original's make
  line carries `REGENIE=1`, which regenerates the project files on every run, recompiles two files (`formats/all.cpp`,
  the driver list) and relinks. Re-running the build on the proven reference binary changed its SHA-1 (`ec1ebce9` →
  `84f17729`), and one more relink changed it again (→ `67a75d09`). Between the last two (a Mach-O section compare, the
  scratch script not kept): `__TEXT,__text`, every data section and the indirect symbol table equal; the UUID and the
  stub sections differ, one stub reading the neighbouring GOT slot (`#0xa08` against `#0xa10`). Whether that is
  behaviour-neutral was not measured; the rule does not need it, since a binary with a new SHA-1 is proven again.
  `tools/setup_mame.py` now never rebuilds a binary whose recorded SHA-1 still matches, and prints `INSTRUMENT MOVED`
  (keeping the old SHA-1 in `build.json`) when a build changes it.

- **The original's WIDE corpus list continues its lines with a backslash**: `CORPUS="${*:-01_attract_long … \`.
  Splitting that default on whitespace counts 14 replays, two of them `\`, and W2 failed a PASSing run against 14.
  The count now drops the continuation tokens and reads 12, which agrees with the original's own *"over 12
  replays"*.
- **The original's parity header says every replay is frozen; at `bf92acd2` eight are not** (`118_chain`,
  `118_input_sweep`, `118_sel_b1`..`b6`), so its section 2 runs them as a direct A/B against the reference binary.
  M2 was first written from the header and failed a PASSing run on its "A/B sections empty" clause. It now requires
  every A/B row identical and none skipped; without a reference binary those rows SKIP and the gate fails.
- **`tests/expected/vsavj/` holds 32 entries, not 32 frozen logs**: 24 `.sha1` files of replays that exist, three
  `.skip` files and five directories. Count the gate's own section header, not the directory.
