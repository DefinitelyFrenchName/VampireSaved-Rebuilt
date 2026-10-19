# THE INSTRUMENTS — the emulators this repository builds to measure with

**What this document is.** The reference record of every emulator binary this repository builds as an instrument:
its pinned source, how it is built, what proves it measures what the original's frozen expectations were measured
with, and the gotchas paid for. The rule is `CLAUDE.md` [VSR-9] (built from pinned, recorded sources, the reference
binary first; an instrument is never moved without re-proving what it measures); the facts about the emulators are
the `mame-fbneo-instruments` skill ([MFI-NN]). A profile patch ([VSR-2]) is recorded here only once the maintainer
ratifies it for this repository; its spec has one copy, in its own document.

## MAME, the reference build (R-005)

**The pin.** Commit `27a8d9e85b58058965907d1d8a7a92f8ed039348`, tag `mame0288`: the original's gitlink `emu/mame` at
`bf92acd2` and the `PINNED` of its `tools/setup_mame.sh`. MAME 0.288 is the version of the Homebrew binary that froze
the original's vanilla oracle logs (the header of its `tests/test_mame_parity.sh`).

**The build.** `python3 tools/setup_mame.py build/emu/mame-ref [--source URL_OR_PATH]`:
- fetches the pinned commit into a bare repository and refuses any other commit;
- extracts its tree with `git archive` (no working copy, so nothing can be dirty);
- builds the CPS-2 subtarget as the original does: `make SUBTARGET=cps2 SOURCES=src/mame/capcom/cps2.cpp NOWERROR=1
  REGENIE=1`;
- asserts on the binary, not the exit code: it knows `vsavj` and does not know `vsavjw`;
- records the pin, the make line, the toolchain and the binary's SHA-1 in `build/emu/mame-ref/build.json`.

No profile patch is applied. The original builds the same tree twice, with and without the WIDE patch; this
repository has only the reference so far.

**The build of R-005** (macOS, Apple clang 21.0.0, SDL3 3.4.12, pkgconf 3.0.5; source fetched from the original's
local submodule, read-only, its commit checked against the pin): `build/emu/mame-ref/mame/cps2`, SHA-1
`ec1ebce91920e0a73e90eb91733ffd7edd6ec1cd`, `-version` *"0.288 (unknown)"*. 1.6 GB on disk with its objects.

**The proof: `tests/test_mame_reference.py`.** A class F gate (`SPEC.md` §5.1): it runs the original's own
`tests/test_mame_parity.sh`, unchanged, in the export, with this binary as its source build and Homebrew's `mame`
(SHA-1 `0526f872…`, 0.288) as its reference. Its checks:
- M1 identity: the binary is the one `build.json` recorded, at the pin, with no `vsavjw`;
- M2 parity: the original's verdict is PASS; every frozen row (section 1, the vanilla `vsavj` logs; 1b, the reference
  binary's frozen logs of the other replays) reproduced twice; every replay frozen nowhere (sections 2 and 3) identical
  on both binaries, none skipped; and the original's in-gate control fired.
Controls: `other-binary` (M1 on Homebrew's binary) and `wrong-hash` (the original's own mode). Result: see
"R-005's runs" below.

**R-005's runs** (a measurer read the logs and the run log):
- normal, first run: FAIL on M2 alone; the original's verdict was PASS (the gotcha below);
- normal: `VERDICT: PASS`, 393.9 s. *"M2 sections 1/1b replays 24/65, rows ok 89; A/B sections 2/3 replays 8/0,
  identical 8; rows failed 0, sections skipped 0"*; the original's *"PASS: MAME parity."*; both controls FIRED,
  `wrong-hash` in the original's own words (*"103_tenant_2pwin_auto's real log (8604a925…) passes against its frozen
  hash and fails against the hash with one digit changed"*);
- `--control wrong-hash`: `VERDICT: FAIL (M2)`, the 65 perturbed rows failed, the 24 vanilla logs still ok;
- `--control other-binary`: `VERDICT: FAIL (M1)`, Homebrew's SHA-1 is not `build.json`'s.

So the binary built here from the pin is, on every replay the original froze or can A/B, the instrument that froze
the original's MAME expectations. It is not yet proven on the WIDE set (`vsavjw`), which it cannot run.

## Gotchas paid for

- **The original's parity header says every replay is frozen; at `bf92acd2` eight are not** (`118_chain`,
  `118_input_sweep`, `118_sel_b1`..`b6`), so its section 2 runs them as a direct A/B against the reference binary.
  M2 was first written from the header and failed a PASSing run on its "A/B sections empty" clause. It now requires
  every A/B row identical and none skipped; without a reference binary those rows SKIP and the gate fails.
- **`tests/expected/vsavj/` holds 32 entries, not 32 frozen logs**: 24 `.sha1` files of replays that exist, three
  `.skip` files and five directories. Count the gate's own section header, not the directory.
