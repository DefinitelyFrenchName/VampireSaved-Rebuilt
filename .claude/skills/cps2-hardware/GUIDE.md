# CPS-2 hardware (level 1, game-independent) — the guide

The human rendition of `SKILL.md` in this directory: the same rules, the same
IDs, each followed by the INCIDENT that taught it. In the originating
project (`DefinitelyFrenchName/VampireSaved` at `6dee2be7`) it is **GENERATED** by
`tools/gen_skill_guide.py` from the documentation paragraph every rule is anchored
to. Here it is a CARRIED COPY, changed only where a rule was adapted (the same edit
as in `SKILL.md`), where a host name was removed and where ROM bytes were elided
([VSR-8]); it is regenerated once this repository has its own generator and anchors.
Origin: Project VAMPIRE SAVED — the full-roster Vampire Savior romhack on the real CPS-2 engine (FBNeo and MAME as instruments, a jtframe core on MiSTer). The incidents therefore name that project's game, builds,
gates, scripts, build directories and session tags (`14z-N`): they are that project's
HISTORY, quoted from its documents, not instructions for this repository, whose
implementation differs (`SPEC.md` §4); the RULES do not name them. The rule is the reminder,
the incident is the fact. IDs are stable and never reused; a gap means the
rule stayed at the origin's board-specific level.

**To use this skill elsewhere:** copy this directory (`SKILL.md` + `GUIDE.md`)
into `~/.claude/skills/cps2-hardware/`. Nothing in it depends on the origin tree.

## A.1 Bytes, views and the encryption window

**[CPH-1]** → lifted to level 0 as [MFI-43] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.

> **Incident** (`docs/platform/gotchas.md` › *CPS-2 ROM file byte order is NOT 68k logical order (paid: 2026-07-25, ~1h)*):
>
> The 16-bit words in the dumped program ROM files are stored **low-byte-first**.
> MAME's `cps2_decrypt` operates on the `uint16` values you get from reading the
> file little-endian (that's what the region layout gives it on a little-endian
> host), NOT on big-endian words. Interpreting the files big-endian and
> decrypting "works" (self-consistent, round-trips) but produces garbage that is
> deceptively half-right: byte-symmetric words like `0x0000` decrypt identically
> either way, and the 68k vector table alternates `0x00xx`/`0xxx00` words, so a
> spot check of the first bytes shows a plausible mix of matches. **Symptom to
> recognize:** a diff against a known-good image where "every other word
> matches" in vector/data areas.

**[CPH-2]** **The program zips store CODE encrypted; only DATA reads bypass the crypt.** Any static analysis of code — diffing against stock, disassembling, searching for an instruction pattern — uses the DECRYPTED opcode space, never the members. Data tables may be read raw from the members (with the `LOAD16_WORD_SWAP` byte order in mind).

> **Incident** (`docs/platform/gotchas.md` › *CPS-2 program zips store CODE encrypted — static byte reads of code are noise*):
>
> Paid for in session 14z-2 (an hour of "why does the ported region disassemble
> to garbage"). The romset zips (+ .key) hold ENCRYPTED opcodes; only DATA
> reads bypass the crypt. Any static analysis of code regions — diffing a
> build against vanilla, disassembling a ported routine, searching for an
> instruction pattern — must use the DECRYPTED opcode space:
> `tests/lua/dump_opcodes.lua` (MAME's own cps2crypt is the oracle), or the
> pipeline's `build/out/*_opcodes.bin`. Data tables MAY be read raw from the
> zip members (remember ROM_LOAD16_WORD_SWAP byte order). A "code" op in
> patch_prg re-encrypts; that's why plaintext jsr bytes are never found in
> the members.

**[CPH-3]** **PC-relative operand reads are PROGRAM-space and DECRYPTED; `(An)`-based reads are DATA-space and raw.** Pick the view by the READ MODE, not by where the table lives. Absolutizing a `(d16,PC,Dn)` read as `lea` + `(a0,dn)` reads CIPHERTEXT (an odd jump target, an address error at the first hit). Fix shape: hook an instruction BEFORE the pc-relative read and `rts` back into the untouched original.

> **Incident** (`docs/platform/gotchas.md` › *PC-relative reads are PROGRAM-space; (An)-based reads are DATA-space — absolutizing a pc-relative table read on CPS-2 reads CIPHERTEXT*):
>
> The 68000 classes `(d16,PC)`/`(d8,PC,Xn)` operand fetches as program
> references; CPS-2 decrypts program-space accesses in 0x000000-0x100000.
> A site_thunk that faithfully "reproduced" `move.w $185DA(pc,d0),d0` as
> `lea $185DA,a0; move.w (a0,d0),d0` read the encrypted bytes instead
> (data view table[6] = 0x53BF -> odd jmp target -> vec3 at the first KO
> hit; 14z-43). Corollary: a table read via `(pc,...)` lives in the
> OPCODES image; the same table read via `lea (pc)`+`(a0,...)` (the
> property table 0x28D00 pattern) lives in the DATA image — check the
> READ MODE, not the address, when choosing the view AND when relocating
> code. Fix pattern: hook an instruction BEFORE the pc-relative read and
> rts back into the untouched original (the reaction_hook "ghost-clean"
> topology).

**[CPH-4]** **Anything fetched through the opcode space must be written as CODE wherever it lands — instructions AND every pc-relatively-read table — because the cipher is address-aware**: inside the key range it re-encrypts so the CPU's decryption yields your bytes, outside it passes them through unchanged. `data` is right for An-relative and absolute reads only; embedded data inside a thunk body in crypt space must be `data` or a data read gets ciphertext. The trap has both directions.

> **Incident** (`docs/platform/gotchas.md` › *A pc-relatively-read table must be a `code` op at ANY address (14z-91)*):
>
> So the choice is decided by HOW THE BYTES ARE READ, not by where they
> land. Anything the 68000 fetches through AS_OPCODES — instructions, and
> every pc-relative table read (`movea.l (d8,PC,Dn.w)`, `move.w (d8,PC,Dn.w)`)
> — must be a `code` op wherever it goes. `data` is right for An-relative
> and absolute DATA reads only.

**[CPH-5]** **When a table's view is in doubt, DECODE BOTH VIEWS and keep the one whose targets land on real code/data** — a pc-rel WORD JUMP TABLE decodes only from the opcode view, a byte map only from the data view, and both live inside the encrypted range. The addressing mode alone is not sufficient for hand analysis; the wrong view produces plausible garbage.

> **Incident** (`docs/platform/gotchas.md` › *In-code pc-rel WORD JUMP TABLES read through the OPCODE view; byte/data tables through the DATA view — both live inside the encrypted range (14z-68)*):
>
> The effect byte map (vs2 0x27FD8) reads correctly ONLY from the data
> view (the standing GOTCHA). The seq-0x0E state-dispatch word table
> (vs2 0x5556C, `move.w (pc,d0.w)` consumed) reads correctly ONLY from
> the OPCODE view — its data-view bytes decode to garbage targets.
> Deciding "which view" by the read instruction's addressing mode is
> not sufficient; classify per table by DECODING BOTH VIEWS and taking
> the one whose targets land on real code/data. The extractor already
> does this right — the trap is for hand analysis, where the wrong
> view produces plausible-looking garbage that can send a whole
> session down a false trail.

**[CPH-6]** **Relocating a pc-relative DISPATCHER: carry a copy of its table INSIDE the thunk body** (emitted as code, so it re-encrypts with it) and keep reading it pc-relatively — never rewrite the read as an absolute data-view load. The cheap discriminator before trusting any table read: count ODD targets per view (38 of 80 odd in the data view = ciphertext).

> **Incident** (`docs/platform/gotchas.md` › *PC-relative reads are DECRYPTED reads on CPS-2 (paid: 2026-07-25, ~45min)*):
>
> INSTANCE, 14z-79 — RELOCATING a pc-relative dispatcher, not just its table.
> The (b') thunk had to reproduce vsavj's `move.w (6,PC,D0.w),D1 / jmp
> (2,PC,D1.w)` at `0x018460` from a thunk in hole_a, ~0xE4A48 away — far past
> the +/-127 an 8-bit pc-displacement reaches. The design of record (STATE
> 14z-78) therefore rewrote the read as `lea 0x018468,a0 / move.w (0,a0,d0.w),d1`
> — textbook second-rule territory, and it would have shipped: measured on the
> two views, **38 of the 80 legacy targets come out ODD in the data view** (all
> 80 are even in the opcode view), i.e. an address error on the hottest path in
> the game. Cheap discriminator, worth running on any table before trusting a
> read of it:

**[CPH-7]** **The encrypted range is INCLUSIVE of its upper word** — the limit test is `<=` on the word address in the emulators (and in the original's cipher, which matches them), so the word at the boundary byte is still encrypted and the first raw word sits one word above. Found by a test whose first draft asserted the opposite; write the test before trusting the behaviour.

> **Incident** (`docs/platform/gotchas.md` › *The CPS-2 encrypted range is INCLUSIVE of its upper word — 0x100001, not 0x100000 (measured 14z-59k)*):
>
> The project quotes vsavj's encrypted range as `PRG:0x000000-0x100000`
> ("first 1MB only"). The limit test is `<=` on the WORD address, in both our
> `Cipher.crypt_words_at` (`lo <= a <= hi`) and MAME's `cps2crypt.cpp`
> (`a >= lower_limit && a <= upper_limit`). So the word at byte `0x100000` is
> still ENCRYPTED and the first raw word is at `0x100002`.

**[CPH-8]** **Code above the encryption window is stored RAW, automatically and by the cipher's range-awareness** — which is what makes an extended program region viable for ported CODE. Locked in both directions (inside must transform and round-trip; outside must pass through byte-identical), and it FAILS the build rather than warning, because a silent failure turns ported code into executable garbage.

> **Incident** (`docs/platform/gotchas.md` › *Ported CODE above the encryption window is stored RAW, automatically*):
>
> `patch_prg.py` re-encrypts every `code`/`code_file` op unconditionally, so
> it looks like code placed above 1MB would be corrupted. It is not:
> `Cipher.crypt_words_at` is RANGE-AWARE and returns out-of-range words
> unchanged, matching how the CPU fetches them. That is what makes the CPS-2
> WIDE extension (`$400010-$600000`) viable as a home for ported CHARACTER
> code — Donovan's port alone is ~338 KiB and Huitzil/Pyron are comparable,
> so this property is load-bearing for the whole roster.

## A.2 Graphics: simms, tiles, identity

**[CPH-9]** **Gfx simms are NOT tile-contiguous**: a tile's 32 bytes are sixteen two-byte pairs at stride 4, the even/odd word streams of each 0x80000 block feeding decoded chunks 1 MB apart. Naive contiguous slicing still MATCHES on sibling comparisons (same wrong neighbours both sides), so a sibling calibration certifies a broken method. Verify any hardware-interleaved layout against the emulator's LOADER SOURCE before bulk analysis, and fact-lock it with a test.

> **Incident** (`docs/platform/gotchas.md` › *CPS-2 gfx simms are not tile-contiguous — naive slicing silently "works" on siblings only*):
>
> A 16x16 tile's 32 bytes within a simm are 16 two-byte PAIRS at stride 4
> (even/odd word streams of each 0x80000 block feed decoded chunks 1MB
> apart — see tools/gfx_tiles.py header for the exact mapping, derived
> from FBNeo Cps2LoadOne). Slicing contiguous 32-byte runs mixes bytes of
> tiles 1MB apart. The trap: same-index comparisons across sets STILL
> MATCH under wrong slicing (same wrong neighbors on both sides), so a
> sibling calibration (vsav2 vs vhunt2: 200K tiles "match") certifies a
> broken method; all cross-set content-addressed lookups then collapse to
> ~3% and look like "the art was re-encoded". Cost: half a session of
> false hypotheses (plane order, palette permutation). Rule: any binary
> structure with a hardware interleave gets its layout verified against
> the emulator's loader source BEFORE bulk analysis, and the layout
> understanding gets a fact-lock test (tests/test_gfx_tiles.sh).

**[CPH-10]** **Compose a tile address the way the hardware does — `code | ((y & 0x6000) << 3)` — BEFORE dumping it, and print the composition.** Dumping the code without its bank bits compared unrelated vanilla data and "exonerated" a broken band for a session. A null result from a dump is only as good as the address that produced it: give the instrument a band that MUST differ as its negative control.

> **Incident** (`docs/platform/gotchas.md` › *Dump a tile band WITH its bank bits, or you will exonerate the guilty*):
>
> (paid: 2026-08-05, 14z-60y/60z — one session spent on the wrong hypothesis)
> The sprite record's code word for Donovan's select portrait is `0xAD8F`,
> but its y-word selects bank 2, so the tile the hardware fetches is

**[CPH-11]** **Within each 8-pixel half of an OBJ tile row, plane bit `i` is pixel `7-i`; the transparent pen is 15, not 0; an OBJ entry at `(x, y)` lands at screen `(x - 64, y - 16)`.** A byte round-trip proves a codec self-consistent, not hardware-correct — verify any SYNTHESIZED tile at the RENDER layer against its intended bitmap (an asymmetric glyph is what caught a 14-session mirror).

> **Incident** (`docs/platform/gotchas.md` › *`gfx_tiles.decode` had every 8-pixel half MIRRORED, and nothing noticed for 14 sessions (14z-105)*):
>
> Within each 8-pixel half of a CPS-2 OBJ tile row, plane bit `i` is pixel
> `7-i`. `decode()` mapped bit `i` to pixel `i` from the day it was written,
> and its inverse (`encode`, new 14z-105) inherited that — the first tiles
> this project ever AUTHORED (the select-screen version glyphs) drew each
> half mirrored on the real OBJ path. Caught only because "M6" is not
> symmetric: a MAME snapshot pixel-compared against the intended bitmap
> showed the "6" scrambled while the near-symmetric "M" looked right.

**[CPH-12]** → lifted to level 0 as [MFI-44] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.

> **Incident** (`docs/platform/gotchas.md` › *A member carrying another member's PRISTINE bytes SHADOWS it — both emulators resolve a ROM entry by HASH before NAME*):
>
> So the name is the FALLBACK in both emulators, not the identity. A member's
> identity in a set is its HASH, and two files with the same bytes are the
> same member as far as the loader is concerned.

**[CPH-13]** → lifted to level 0 as [MFI-45] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.

> **Incident** (`docs/project/cps2_wide.md` › *The profile*):
>
> ```
> CPS-2 WIDE v1
>   PRG    : 6 MB    CPU $000000-$5FFFFF  ($000000-$0FFFFF encrypted, rest raw)
>                    reserved, never allocate: $400000-$40000F (CpsFrg regs)
>   GFX    : 48 MB   12 uniform 4 MB members (3 groups of 4)
>                    19-bit tile address via the CPS-2 Turbo rule (see below)
> QSOUND : 16 MB   4 uniform 4 MB members; since v1.2 (14z-86) the two
>            EXTENSION members vsw.21m/22m are CONTENT members (sentinel
>            CRCs 0xdec0de3a/3b — the old shared zero-fill CRC would
>            hash-shadow a content-bearing 21m onto the still-zero 22m).
>            The M5 voice batch packs absent vs2 sample windows there
>            (banks 0x80+; tools/build_qs_songs.py [voice_batch]).
>   Z80    : 256 KB unchanged in SIZE; since v1.1 (14z-86) the two driver
>            members are CONTENT members `vsw.z01/z02` (sentinel CRCs
>            0xdec0de38/39 in both descriptors, resolve by NAME) so builds
>            can carry authored M5 song rows (tools/build_qs_songs.py +
>            build/manifest/qs_songs.toml; gate tests/test_qs_songs.sh).
>            Stock names vm3.01/02 would hash-shadow to vsav.zip's
>            pristine members (the 14z-60z class). The canonical overlay
>            ships STOCK bytes; content builds patch free id rows + zero
>            runs only (vanilla-span identity gated). ~27 KB free measured.
>   Everything else: bit-identical stock CPS-2
> ```

## A.3 The OBJ sprite list

**[CPH-14]** **OBJ y-word bit 15 is the sprite-list TERMINATOR, not a spare bit** — set it on a sprite and every later sprite is dropped. Before treating any bit of a hardware structure as spare, find the code that CONSUMES the structure; a census of "which bits are set" cannot tell you which bits are load-bearing.

> **Incident** (`docs/platform/gotchas.md` › *OBJ y-word bit 15 is the sprite-list TERMINATOR, not a spare bit*):
>
> The plan for a 19th tile-address bit was "widen the OBJ mask 0x6000 ->
> 0xE000", i.e. use y-word bit 15. That bit ends the sprite list
> (`CpsObjGet`: `if (ps[1] & 0x8000) break;`), so setting it on a sprite
> would silently drop every sprite after it. Capcom's own CPS-2 Turbo hits
> this and promotes **bit 12** instead (`if (y & 0x1000) y |= 0x8000`)
> AFTER the terminator check. Two lessons: (a) the free bit is 12, with
> hardware precedent; (b) before treating any bit in a hardware structure
> as spare, find the code that CONSUMES the structure — a census of "which
> bits are set" cannot tell you which bits are load-bearing.

**[CPH-15]** **The CPS-2 Turbo rule is the precedent for a 19th tile-address bit: promote y bit 12 into bit 15 AFTER the terminator check, then take three bank bits** — measured never set on a live sprite in the stock game, with a control proving the probe was not blind. The bank bits are DATA (per-character bank tables and a few immediate setters), so a bank value carrying bit 12 flows through existing tables with no code change.

> **Incident** (`docs/project/cps2_wide.md` › *Correction A2 — the 19th bit is bit 12, not bit 15*):
>
> Capcom hit the same wall on CPS-2 Turbo and solved it by **promoting bit
> 12** into the address after the terminator check:

**[CPH-16]** **OBJ RAM is double-buffered and a dump spans BOTH pages plus several drawers' output.** Filtering entries to an expected code band showed a byte-perfect match while the screen showed garbage from entries OUTSIDE the filter. When a render contradicts an OBJ-level match, diff the FULL unfiltered entry set on both sides first.

> **Incident** (`docs/platform/gotchas.md` › *OBJ RAM dumps span BOTH pages — filter by code range and you will blame the wrong drawer*):
>
> A 4KB dump at 0x708000 contains multiple drawers' output (main walker,
> doubling/fade drawer, second page). Filtering entries to the expected
> code band showed a byte-perfect match while the SCREEN showed garbage:
> the garbage came from OTHER entries (raw unremapped codes) outside the
> filter. When a render contradicts an OBJ-level match, diff the FULL
> unfiltered entry set both sides first (14z-22 — found the un-walked
> record subset in minutes once unfiltered).

**[CPH-17]** **Walk a structure the way the hardware walks it — terminators, bounds, buffer selection — and separate sentinels from values.** A raw y-word census reported 841 "sprites" with bit 15 set: stale data past the terminator, never drawn. A tilemap's raw max code is always `0xFFFF` because unused cells hold that sentinel. A census that ignores the walker confidently answers a question nobody asked.

> **Incident** (`docs/project/gotchas.md` › *Censusing a structure without knowing its terminator counts garbage*):
>
> The first y-word census scanned all of OBJ RAM and reported 841 sprites
> with bit 15 set — "vanilla uses the bit, plan dead". Every one of them
> was stale data PAST the list terminator, never drawn. The same trap in
> the scroll3 tilemap: raw `maxcode` is always 0xFFFF because unused cells
> hold that sentinel, which reads as "legacy content reaches the address
> wrap" when nothing of the sort is happening. Walk structures the way the
> hardware walks them (respect terminators, bounds and buffer selection),
> and separate sentinels from real values, or the measurement will confi-
> dently answer a question you did not ask.

## A.4 QSound and the Z80 driver

**[CPH-18]** → lifted to level 0 as [MFI-46] (`mame-fbneo-instruments`); the anchored paragraph is unchanged.

> **Incident** (`docs/platform/gotchas.md` › *A member's REGION layout is not its FILE layout — and the Z80 driver's own address space is a THIRD thing (14z-86)*):
>
> MAME loads CPS2's `vm3.01` split (`ROM_LOAD` 0x8000 at region 0, then
> `ROM_CONTINUE` at region 0x10000; `vm3.02` at region 0x28000). A session of
> Z80-driver RE (14z-85d) assumed region==file above the fixed window and read
> every table at region-derived offsets: the id table "at FILE 0x11006", entry
> bytes [four ROM bytes elided, [VSR-8]], an "8-byte table @0x5219" — all plausible-looking bytes
> at WRONG offsets, and the garbage the wrong offsets produced for CODE was
> confidently explained as "KABUKI encryption" (the Z80 is plain; KABUKI is the
> CPS1-QSound generation). One read tap with DATA logging (qs_table_trace,
> SPANS over the banked window) collapsed the whole edifice in one run: the
> driver's 24-bit logical addresses are FLAT member-concat file offsets, full
> stop (flat = CPU + bank*0x4000 in the $8000 window; bank register hw-masked
> to 4 bits, MAME `qsound_banksw_w`).

**[CPH-19]** **A sample window must live in ONE HALF of its 64K bank** — the DSP compares the playback pointer against `end` SIGNED, so a window straddling `0x8000` collapses to its silent loop tail after the attack. Register- and content-level A/Bs were BLIND to it: keep one gate at the OUTPUT level (a WAV capture and a per-window band comparison) when porting content into a player you do not fully model.

> **Incident** (`docs/platform/gotchas.md` › *QSound sample windows must live in ONE HALF of their 64K bank — the DSP compares pointers SIGNED (14z-86)*):
>
> The M5 voice packer placed sample windows first-fit avoiding only 0x10000
> crossings. Four restored voices came out attack-then-silence: their windows
> straddled bank offset 0x8000, and the DL-1425 program compares the playback
> pointer against END in SIGNED 16-bit — start positive, end "negative" →
> the end condition holds at once and the voice collapses to its silent loop
> tail. Every NATIVE record respects the half-bank law (checked corpus-wide);
> the packer now packs at 0x8000 granularity and refuses >0x8000 windows.

**[CPH-20]** **A copied sample window must keep the SOURCE offset's BYTE PARITY** — the members are stored pre-swapped and both emulators byteswap pairs at load, so an odd→even move plays every byte pair exchanged: RMS preserved, high band doubled, "PC-speaker" harshness. File-level comparison is blind (the bytes are equal, the LANES differ); the output-level checker must flag BOTH directions of a band change.

> **Incident** (`docs/platform/gotchas.md` › *QSound packing law #2: the destination offset must keep the SOURCE offset's BYTE PARITY (14z-86)*):
>
> The voice batch still sounded "like PC-speaker synthesis in a DOS game"
> (maintainer, on BOTH emulators) after the half-bank fix. The mechanism:
> the QSound members are stored PRE-SWAPPED and both emulators byteswap
> 16-bit pairs at load — so the audio stream a sample yields depends on the
> byte LANE of its offset. A window copied from an even source offset to an
> odd destination (or vice versa) plays with every byte pair exchanged: RMS
> preserved, high band doubled, words recognizable but harsh. File-level
> content comparison is BLIND to it (the bytes are equal; the LANES differ),
> and so was the first WAV checker (it only flagged collapsed high band, not
> elevated — the maintainer's ear caught what the threshold passed; the
> checker now flags both directions). The packer keeps parity; the
> found-in-vsav path requires parity-matching hits.

**[CPH-21]** **A sample record's `end` offset PLAYS — copy the INCLUSIVE window**, provably (native windows end at `0xFFFF`, which an exclusive bound could not express). An exclusive copy leaves one foreign byte at every record's end; where the loop tail is silence, one byte turns the sustain into an impulse train — a "pure computer beep".

> **Incident** (`docs/platform/gotchas.md` › *QSound packing law #3: the record's `end` offset PLAYS — copy the inclusive window (14z-87b)*):
>
> The sword-plant "beep" (maintainer ear-confirmed against a byte-synthesized
> prediction): a sample record's `end` field is played/looped INCLUSIVE —
> proven by field width, since native windows end at 0xFFFF, which an
> exclusive bound could not express — but the voice-batch packer copied
> `q2[w0:w1]` EXCLUSIVE. Every packed sample's last played byte therefore
> held the NEXT blob's first byte. For a voice whose loop tail is silence,
> ONE foreign byte turns the sustained loop into an impulse train (13-sample
> period ≈ 1.85kHz — a "pure computer beep" to the ear, ~70ms to keyoff).
> Measured: exactly 3 of 57 packed records had a non-zero contaminated end
> byte — the others landed on 0x00 neighbors by luck, which is why the batch
> otherwise sounded normal and the WAV gate's per-window thresholds passed.
> rec#0x3C8 = Donovan voice 0x705 = fired at EVERY sword plant = the report.
> Enforced in tools/build_qs_songs.py (inclusive copy, all size math +1) and
> gated by test_qs_songs.sh's law-3 section (resolved inclusive window ==
> vs2's, per record, + a flipped-end-byte verdict control). The find-in-vsav
> path inherits the law automatically (the searched blob now includes the
> end byte).

**[CPH-22]** **A "pure synthetic beep" IS a tight-loop sample** (a few dozen saturated bytes looping); the hardware plays samples only. Rendering a record's window once mischaracterises its sound — render attack + loop repetitions, or better, DIFFERENCE a silence-probe build's audio against the reference build's and judge the difference signal, never envelope peaks at chosen frames.

> **Incident** (`docs/platform/gotchas.md` › *A QSound "pure synthetic beep" is a TIGHT-LOOP sample — and a raw-window render can never reproduce it (14z-87b)*):
>
> The hardware plays samples only; a clean pitched tone is a sample record
> whose loop region is a few dozen samples (vsavj record #0x3E: loop
> 0xFFF4-0xFFFF = 11 saturated bytes → ~1.17kHz pure tone at the driver
> rate). Two paid-for corollaries: (1) rendering a record's raw window
> start→end ONCE mischaracterizes its in-engine sound completely — the
> sustained tone lives in the loop, not the window; render attack + loop
> repetitions, or better, isolate the real sound by DIFFERENCING a
> silence-probe build's audio against the reference build's (the two runs
> are identical until the silenced id's first enqueue, so the difference IS
> the sound); (2) a silence-probe verdict must compare the DIFFERENCE
> SIGNAL, not envelope peaks at chosen frames — peak equality at two
> timestamps "refuted" the true beep source for half a session while the
> global diff showed audio removed at exactly the enqueue frame.

**[CPH-23]** **The loaders' shape rules bind the ROMSET, and each belongs to one implementation**: gfx members come in groups of four of equal size (the FBNeo loader consumes four at a time); QSound length stays a power of two because that is FBNeo's `rom_mask` rule — MAME's ceiling is a 24-bit device interface and the FPGA core has no mask at all; stock members are never resized or reordered, new capacity is APPENDED so legacy provenance stays trivially valid.

> **Incident** (`docs/project/cps2_wide.md` › *The profile*):
>
> Rules that are not negotiable, because the loaders depend on them:
> - GFX members come in groups of **4** and must all be the **same size**
>   (`cps.cpp` consumes 4 at a time; `nGfxMaxSize` mis-sizes otherwise).
> - QSound length must stay a **power of two** (`rom_mask = nCpsQSamLen - 1`).
>   **SCOPE, 14z-107 (4): this binds the ROMSET because it is FBNeo's loader
>   rule.** MAME's ceiling is a 24-bit `device_rom_interface`, and jtcps2 has
>   **no mask at all** on the sample path (`PCM_AW` is an address width;
>   `grep mask cores/cps15/hdl/jtcps15_sound.v` is empty), so MiSTer may PLACE
>   a non-power-of-two slice of the same 16 MB region — and must, because the
>   verbatim `.rom` overflows the 26-bit `ioctl_addr`. **What that width DOES
>   bind (measured 14z-107 (6)) is 8 MB PER SLOT** — jtframe's 8-bit slot
>   cannot be given `AW > SDRAMW = 23` at all — so the placed 8.9375 MB is two
>   slots in two SDRAM banks, not one wider slot. See
>   `docs/project/mister_map.md` §3, §5, §7.
> - Stock members are never resized or reordered — new capacity is appended,
>   so all legacy provenance stays trivially valid.

## A.5 The CPS-2 WIDE profile as a platform artifact

**[CPH-24]** **The WIDE profile is a NAMED, VERSIONED hardware shape** — program 6 MB (the first 1 MB encrypted, the rest raw), gfx 48 MB in three groups of four, QSound 16 MB, Z80 unchanged in size — implemented identically by every target, with the profile's own content-member rules (which members carry content, which sentinels) versioned with it.

> **Incident** (`docs/project/cps2_wide.md` › *CPS-2 WIDE — extended hardware profile (v1, RATIFIED — implemented in three emulators/cores)*):
>
> Vampire Savior with all 18 characters does not fit a stock CPS-2. One
> character costs ~338 KiB of program ROM and ~16-18K tiles; the stock free
> space is ~1 KiB of PRG and ~370 tiles. WIDE is the named, versioned
> hardware profile that makes the roster physically possible, implemented
> identically by every emulator target.

**[CPH-25]** **`$400000-$40000F` is reserved and never allocated**: the three implementations treat READS there differently (ROM-shadowed, readable registers, ROM under the wide decode), a divergence unobservable ONLY because nothing lives there. The reservation is load-bearing for cross-implementation agreement, not tidiness.

> **Incident** (`docs/project/cps2_wide.md` › *Two things MAME taught us that FBNeo did not*):
>
> 2. **`$400000-$40000F` behaves differently in the two emulators.** FBNeo's
>    `SekMapMemory(CpsRom, 0, nCpsRomLen-1)` read-shadows the CPS2 output
>    registers with ROM (writes still reach the handler); MAME keeps them
>    readable, because its base map re-declares them after the ROM range.
>    This is a genuine divergence and it is unobservable ONLY because the
>    profile reserves that window. **Never allocate there** — the reservation
>    is now load-bearing for dual-emulator agreement, not just tidiness.
>    **THIRD IMPLEMENTATION, 14z-107 (4): jtcps2 makes it a three-way
>    divergence.** `jtcps2_main.v:190` decodes `objcfg_cs` over the whole
>    `$400000-$4FFFFF` but qualifies it with `!RnW`, so today a READ there
>    asserts nothing; under the proposed 6 MB `rom_cs` it would return ROM.
>    The reservation is what keeps all three behaviours unobservable.
>    (`docs/project/mister_map.md` §8.)

**[CPH-26]** **Content authored into the extension is written RAW but laid out in FILE byte order** (logical words converted to file byte order — in the original, `words_to_file_bytes(words_from_logical_bytes(…))`), and the member's real CRC goes into the descriptor.

> **Incident** (`docs/project/cps2_wide.md` › *B4 prg: PASSED, with the control that made it meaningful*):
>
> Note for authors: everything above `PRG:0x0FFFFF` is outside the
> encryption window, so extension content is written RAW (no re-encryption)
> — but it must still be laid out in FILE byte order, i.e. converted with
> `cps2_decrypt.words_to_file_bytes(words_from_logical_bytes(...))`, and
> the member's real CRC must go into the descriptor.

**[CPH-27]** **Before widening anything, MEASURE that the stock game never touches the candidate space** — zero reads of the extension windows, the promote bit never set on a live sprite, no scroll code relying on the address wrap, free driver space — each with a control proving the probe was not blind. Widening is linear where the measurement says nothing reads it; the bit is free where the measurement says nothing sets it.

> **Incident** (`docs/project/cps2_wide.md` › *Phase A measurements (2026-08-03, vanilla vsavj, full legacy corpus)*):
>
> Instrument: `tests/audit_wide_phase_a.sh` (rerunnable; ground-truths itself
> before trusting any null result).

**[CPH-28]** **Inertness is not functionality.** Proving a widened path HARMLESS on stock content (bit-identical RAM and framebuffer) says nothing about whether it REACHES the new space; that needs a positive control — a legacy tile moved into the new bank with the bit set and observed to render from there, a data table relocated where pointing it at zero fill DOES diverge.

> **Incident** (`docs/project/cps2_wide.md` › *Phase B progress (proving the profile inert, one variable per build)*):
>
> **Inertness is not functionality.** B2 proves the 19-bit path is HARMLESS
> (vanilla never sets bit 12, so nothing changes). Proving it actually
> REACHES the new banks is B4's job, and B4 must include that positive
> control — a build where a legacy tile is moved into group C with bit 12
> set and is observed to render from there.

**[CPH-29]** **Every emulator change under the profile is governed**: bounded and declarative, profile-gated by a separate driver entry so the stock set and every other game are untouched by construction, subject to the emulator superset invariant (the patched binary on the stock set reproduces the frozen expectations bit for bit, as a battery gate), mirrored in a second implementation, ratified per profile version.

> **Incident** (`docs/project/cps2_wide.md` › *Governance (Rule 1 v2)*):
>
> Emulator changes are permitted only inside this profile, and each must be:
> bounded and declarative; **profile-gated** (a driver flag set by a new
> driver entry, so stock vsavj and every other CPS-2 game are untouched by
> construction); subject to the **emulator superset invariant** — the
> patched binary running stock unmodified vsavj must reproduce the frozen
> vanilla expectations bit-for-bit, enforced as a battery gate; mirrored in
> a second emulator where practical; and ratified per profile version.

**[CPH-30]** **The change budget is MEASURED, and an undercount is a retraction-class error.** The profile costs TWO gated blocks in the sprite drawer — the promote and its test-only positive control — and everything else is descriptor table data; a governance summary that said "one gated conditional" was corrected under retraction discipline, and the summary lines that still said it three sessions later were corrected again at 14z-114. Summary lines drift faster than the sections beneath them.

> **Incident** (`docs/project/cps2_wide.md` › *Emulator change budget (measured, not estimated)*):
>
> So the entire profile costs **two gated blocks** in emulation logic, both in
> `Cps2ObjDraw`, and everything else is table data. CORRECTED 14z-90 (GitHub
> issue #35): this line said "one gated conditional". The second block is the
> `CPS2_WIDE_CANARY` positive control, which `docs/project/patch_index.md`
> explicitly retains ("CPS2_WIDE_CANARY stays as the B4 positive control") — so
> it is deliberate and ratified, but it is not zero, and a governance summary
> that undercounts the change budget is the kind of claim this project's
> retraction discipline exists to catch. The canary is test-only and gated on
> the same `Cps2Wide` flag.
