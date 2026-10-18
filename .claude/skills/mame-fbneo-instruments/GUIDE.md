# MAME and FBNeo as instruments (level 0, board-agnostic) — the guide

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
into `~/.claude/skills/mame-fbneo-instruments/`. Nothing in it depends on the origin tree.

## 0.1 MAME as an instrument: what a probe sees

**[MFI-1]** **Driver `logerror` lines need `-log`, not `-verbose`** — they land in `error.log` in the working directory. Where a driver logs its own decryption key or region setup, that line is the authoritative value for the set, ahead of any table you transcribed.

> **Incident** (`docs/platform/gotchas.md` › *MAME `logerror` output needs `-log`, not `-verbose` (paid: 2026-07-25)*):
>
> `-verbose` only shows OSD chatter. Driver `logerror()` lines (e.g. cps2's
> `cps2 decrypt <key0>,<key1>,<lower>,<upper>`) go to `error.log` in the
> working directory only when `-log` is passed. That line is the fastest way to
> get the authoritative key/range for a set.

**[MFI-2]** **A `-debug` run's frame_done counter counts the debugger's boot halt** (corrected 14z-196): the halt emits one `frame_done` with no emulated frame, so a script counting `frame_done` calls stages every input one frame early and its log diverges within frames; counted on the EMULATED clock (`screen:frame_number()` moving, the first call counted) a `-debug` run reproduces the non-debug log frame for frame (4 of 4 replays). Breakpoint STOPS can still move the game for some instruments — tie a breakpoint leg to a no-debugger reference. Checksum-exact gates run WITHOUT `-debug` unless their clock is the emulated one; a frozen expectation for a debug run is frozen FROM a debug run. In debugger expressions bare hex parses as a REGISTER — write `0x` prefixes.

> **Incident** (`docs/platform/gotchas.md` › *MAME `-debug` runs diverge from non-debug runs — through a frame_done counter that counts the debugger's boot halt, NOT the scheduler (paid: 2026-07-25, ~1.5h; CORRECTED 14z-196, GitHub #228)*):
>
> **CORRECTED 14z-196 (#228) — the mechanism below was wrong, the symptom right.** The debugger's
> initial halt emits ONE `frame_done` with no emulated frame (`tests/lua/clock_check.lua` measures it: `uiframes 1`
> on every crash-guard `-debug` run), so a script that counts `frame_done` calls as frames — `replay_guard.lua`'s
> authoritative mode — runs one frame ahead of emulated time from the start and stages every input one frame early.
> Count emulated frames instead (`screen:frame_number()` moving, the FIRST `frame_done` counted, as
> `tests/lua/dispatch_census.lua` and `tests/lua/pc_count.lua` do) and a `-debug` crash-guard run reproduces
> `replay.lua`'s checksum log on EVERY frame: 4 of 4 replays, full length — `01_attract_long` 7,320/7,320,
> `02_demitri_vs_cpu` 5,520/5,520, `03_two_player_vs` 5,320/5,320, `04_select_fuzz` 3,520/3,520, against 0 frames
> past frame 11 for the frame_done-counting guard (`build/agent196/t228/screenclock/`, `uiframe1/`). So `-debug` by
> itself does NOT perturb multi-CPU timing on these replays; the "finer scheduler timeslices" theory and the "NOT a
> lost frame at the initial debugger halt" elimination below are RETRACTED. What still holds: breakpoint … *(the paragraph continues in the origin doc)*

**[MFI-3]** **Every `-debug` watch configuration is its own TIMELINE** — two debug trace runs are not comparable to each other either. A run carries its own dumps so it can be attributed without a second run.

> **Incident** (`docs/platform/gotchas.md` › *MAME palette RAM ($90C000) takes Lua pokes for READBACK but not for RENDERING (14z-102)*):
>
> two -debug INSTRUMENT-grammar traps from the #103 close — both misread a measurement for a full round each (paid: 14z-98)
>
> **Every -debug watch configuration is its own TIMELINE, not just
> "different from non-debug".** Three trace_writes runs on the SAME rig
> with the SAME pokes — differing only in the WATCH argument — took three
> different match trajectories: one stalled at f3260, one drained the
> white bar to exactly 0 at ~f6957, one cycled round restarts through
> f8921. Reading run B's hit inventory against run A's state map produced
> "the kill commit never runs for Donovan" from a timeline that contained
> no Donovan death at all. The 14z-97b entry said "the -debug timeline is
> a different run"; the extension is that EACH -debug configuration is —
> two -debug runs are not comparable either. Remedy, now in the
> instrument: `trace_writes.lua` takes `DUMPS` (14z-98), so a trace run
> carries its own state anchors; interpret hits only against anchors from
> the SAME run. (Also worth knowing while reading its logs: the wpset
> stop PC is the instruction AFTER the access — the writer/reader is the
> instruction before the logged PC.)

**[MFI-4]** **Breakpoint logging is a SAMPLER, never an inventory**: the Lua pump drops hits (four draws logged where a write-watch proved five). A trace gives EXISTENCE evidence; coverage is closed structurally (record streams, pointer arrays), never from a trace.

> **Incident** (`docs/platform/gotchas.md` › *MAME breakpoint logging is a SAMPLER, not an inventory*):
>
> The Lua breakpoint pump (periodic callback resuming `debugger.
> execution_state`) drops hits: with six handler breakpoints live during
> frames 2596-2600, four record draws were logged while a write-watch
> proved at least five occurred (obj $FFBC00's draw never appeared).
> Runtime traces give EXISTENCE evidence ("this record IS drawn at bank
> 2"), never completeness ("these are ALL the records"). Any fix scoped
> from a trace must be closed structurally (record streams, pointer
> arrays) before it can claim coverage — the Anita-feet 54-record list
> came from the stream walk, not from the trace that found its first
> member.

**[MFI-5]** **A stopped CPU keeps emitting frames**: `frame_done` fires while the debugger holds, the script's frame counter inflates past emulated time, and replay INPUT keyed to it drifts. Every high-frequency breakpoint trace runs a silently desynced replay; use traces for rare events only, and DUMPS (no debugger) for anything frame-accurate.

> **Incident** (`docs/platform/gotchas.md` › *Debugger stops DESYNC replay frame counting*):
>
> While a Lua breakpoint/watchpoint holds the CPU, MAME keeps emitting
> video frames: `emu.register_frame_done` fires, the script's frame
> counter inflates past emulated time, and replay INPUT PLAYBACK (keyed
> by that counter) drifts — so every high-frequency breakpoint trace
> runs a silently desynced replay, and its logged frame numbers are not
> comparable to replay.lua frame numbers. (Symptom that exposed it: a
> bpset on a routine proven to run 40+ times logged one hit; a "window
> 2596-2600" trace saw a different game moment than the same frames'
> RAM dumps.) Use debugger traces only for EXISTENCE evidence at rare
> events; for anything frame-accurate or complete, use replay.lua DUMPS
> (exact, no debugger) and read state from RAM — companion-slot cursor
> fields survive at frame-done even when the live flag is clear.

**[MFI-6]** **Condition a breakpoint that drives replay input so it fires a HANDFUL of times per run**, or drive state via write taps (no stops). When a stop-based trace and a tap-based trace disagree about what frame N contains, believe the tap; cross-check any stop-based finding against a screen-identifying fact (an init PC, a known object base) before attributing it to a screen.

> **Incident** (`docs/platform/gotchas.md` › *Unconditioned breakpoints DESYNC replay input — the trace measures a screen the replay never left (14z-63)*):
>
> `obj_record_full_trace.lua` with breakpoints on the hot OBJ format
> handlers (thousands of stops per second) produced a trace whose frame
> counter said "select screen" while the machine was still in ATTRACT: the
> frame counter advances on `frame_done`, which keeps firing for UI frames
> while the CPU sits stopped, so scripted inputs land at the wrong EMULATED
> time and the replay silently never progresses. The symptom is coherent
> and misleading: a stable set of records cycling "at select frames" that
> are really the attract screen's menu objects ($FFB800 CUR 0x26810E, REC
> 0x269032 — the 0x07C428-inited attract chain). The conditioned
> `obj_record_bank_trace` run (2 stops total) in the same session showed
> the true select-entry facts.
> Rules:
> - A breakpoint instrument driving replay input is only trustworthy when
>   stops are RARE — condition the breakpoint (a0/a6 windows) so it fires
>   a handful of times per run, or drive state via write taps (no stops).
> - When a stop-based trace and a tap-based trace disagree about what
>   frame N contains, believe the tap — its frames are emulated frames.
> - Cross-check any stop-based finding against a screen-identifying fact
>   (an init PC, a known object base) before attributing it to a screen.
> FIXED 14z-197 (GitHub #228): `obj_record_full_trace.lua` counts emulated frames
> through `tests/lua/emu_clock.lua` — 26,132 UI frames skipped over 3,000 frames
> on the reference leg's game clock (`tests/test_emu_clock.sh` section 5). A stop
> can still move the game itself ([MFI-2]), so the rules above stand.

**[MFI-7]** **An ARMED breakpoint delays input application by a beat** whenever it stops inside the frame the replay layer was about to write — deterministic INPUT-VIOLATIONs that look like host keystrokes (the tell: the SAME frame on two legs). Arm forcing/probing breakpoints LAZILY, just before their window, and `bpclear` the moment they have served.

> **Incident** (`docs/platform/gotchas.md` › *An ARMED DEBUGGER BREAKPOINT skews the Lua harness's input application — deterministic INPUT-VIOLATIONs that look like host input (14z-110)*):
>
> Any MAME `-debug` breakpoint stop delays `emu.register_frame_done`'s input
> application by a beat when the stop lands inside the frame the replay layer
> was about to write — the input-integrity check then reads the PREVIOUS
> chord and flags INPUT-VIOLATION. The tell that it is NOT host input: the
> violation frame is DETERMINISTIC (two parallel legs flagged the SAME frame
> 2874, byte-identical live value). The eager first version of `GUARD_FORCE`
> paid for this: its breakpoint idled armed from boot, and a 14k-frame run
> collected 75 violations. THE RULE: a forcing/probing breakpoint is armed
> LAZILY (just before the window it serves) and cleared the moment it has
> served (parse the bp number from the debugger console and `bpclear` it).
> After the fix the same run shows ZERO violations. Crash-handler
> breakpoints are exempt in practice — they only stop when the run is
> already over.

**[MFI-8]** **A `wpset` watchpoint is SILENTLY BLIND to every pc-relative read** (served through the OPCODES space) — which is how most dispatch tables are read on a 68k. Watching a table the code jumps through? Use the opcodes space (`wposet`). Any "this is never read" needs a POSITIVE CONTROL with the same instrument on the same leg; silence and blindness are indistinguishable without one.

> **Incident** (`docs/platform/gotchas.md` › *A `wpset` watchpoint is SILENTLY BLIND to every pc-relative read on CPS-2 — jump/handler tables need the OPCODES space (14z-71)*):
>
> MAME's m68k serves pc-relative reads through `m68k_read_pcrelative_*`
> -> `m_readimm16` -> **AS_OPCODES**, not the program space. So a plain
> `wpset` on any table the engine indexes with `move.w (d16,pc,Dn),Dm` or
> `movea.l (d16,pc,Dn),An` — which is *most* dispatch tables in this
> engine — never fires, and the run reports **zero hits**.

**[MFI-9]** **Watchpoint LENGTH is parsed as HEX** (`10` = sixteen). A length a harness regex rejects kills the run before the replay starts and leaves an EMPTY trace — indistinguishable from a measurement of zero. Assert the run COMPLETED (its own end marker) before reading any count as a measurement.

> **Incident** (`docs/platform/gotchas.md` › *MAME parses a watchpoint LENGTH as HEX — and a length the harness regex rejects kills the run and prints a clean-looking zero (14z-71)*):
>
> `wpset addr,len,type` takes `len` in HEX, so `10` is sixteen bytes and
> ten bytes is `a`. `tests/lua/trace_writes.lua` matched the WATCH length
> with `%d+`, so any hex-lettered length failed the pattern, the `assert`
> killed the run **before the replay started**, and the trace file came out
> EMPTY. Downstream that is indistinguishable from a real measurement of
> zero accesses.

**[MFI-10]** **A boot-time RAM test writes EVERY byte of work RAM**, so a bare write count on any address reports phantom hits. Never assert on a raw count — discriminate by PC (derived from the build's own address map) or, weaker, by frame window. The failure is always a "count everything" default; the defence is a control or a discriminator, never a tuned threshold.

> **Incident** (`docs/platform/gotchas.md` › *The boot RAM test writes EVERY byte of work RAM — a bare write-count on any address reports phantom hits (14z-71)*):
>
> vsav's POST walks all of work RAM (frames ~5-72, PCs `0x000D34`-`0x000DDC`,
> plus per-venue clears out to ~f824). So a watchpoint on any RAM address
> returns a non-zero write count on a perfectly clean run.

**[MFI-11]** **A MAME watchpoint logs REGISTERS, not the value written**; reading "the value" off a register snapshot attributed a write to the wrong caller. A value-logging write tap with PC attribution (FBNeo carries one through a small frontend patch) answers "what went in" non-perturbingly; keep MAME's watchpoint for "which code ran". A 68k `move.l` appears as TWO word writes on both; a tap keyed on the entry base sees only the (zero) high word, and grepping for the full value finds nothing.

> **Incident** (`docs/platform/gotchas.md` › *A MAME watchpoint logs REGISTERS, not the VALUE WRITTEN — reading the value off a register snapshot attributed a write to the wrong caller (14z-76)*):
>
> `tests/lua/trace_writes.lua` logs `frame PC D0 D1 A0..A6` at each hit. It does
> **not** log the datum. On a `move.l a1,$30(a4)` it is tempting to read A1 as
> "the value written" — and that is right only if the sample came from the call
> you care about. In 14z-76 the win-quote installer was sampled on a *different*
> invocation in the same frame; A1 read `0x330F4C` while the field actually
> received `0x3311C2`. That mis-attribution sent the investigation looking for a
> second, non-existent installer, and produced a self-contradiction ("the field
> is read before anything writes it") that stood until the right instrument was
> used.

**[MFI-12]** **MAME Lua write taps are silently DROPPED when the driver re-installs its memory handlers** (some drivers do it right after boot) — a tap that logs boot writes only reads as "nobody writes this field". Re-install on the change notifier, GUARD the installer against its own notifier (unguarded it recurses until MAME segfaults with no Lua error), and assert on the instrument's own SUMMARY line, never the exit code — MAME can segfault at teardown after the log is written.

> **Incident** (`docs/platform/gotchas.md` › *MAME Lua write taps are silently dropped on handler re-install*):
>
> `space:install_write_tap` dies (no error) whenever anything re-installs
> handlers over the space — CPS-2 does this right after boot. Symptom: tap
> logs boot writes only, reads as "nobody writes this field," which is a
> WRONG conclusion. `tests/lua/tap_writes.lua` carries the fix (re-install
> via `add_change_notifier`); use it instead of hand-rolling taps. Taps are
> the right tool for hot fields (positions) where trace_writes.lua-style
> watchpoint stops would desync the replay. **And judge a tap run by the
> tap's own END line, never MAME's exit code** — paid on Linux 14z-188
> (WSL2): `test_select_wheel` and `test_don_immortal_native` went red
> on a MAME segfault at TEARDOWN after a complete log (`test_select_wheel`
> 12 of 12 runs under a 24-way parallel load, 0 of 4 at 5-way); both now
> read the END line or the dumps. Removing the superseded tap before
> re-installing (`read_tap.lua`'s pattern) cut the rate to 5 of 12 but did
> not remove it: the crash is not root-caused.

**[MFI-13]** **Write taps must be WORD-aligned** on a 16-bit bus (tap the containing word, filter on mask/offset; byte writes arrive replicated across the word), and **bucket taps by BYTE LANE**, not word offset — a word-bucketed tap read a word's low-byte lane as "never written" while the code under test wrote it every run. A freeness claim from a word-bucketed tap is not evidence.

> **Incident** (`docs/platform/gotchas.md` › *MAME write taps must be WORD-ALIGNED*):
>
> `install_write_tap` on `ff8403,1` dies with "start address has low bits
> set, did you mean ff8402?" — and it is a hard error that kills the script
> after a full boot. Tap the containing word (`ff8402,2`) and filter on the
> logged mask/offset. Byte writes arrive with the value replicated across
> the word (`data 00000303` for a byte `0x03`), so mask the low byte.

**[MFI-14]** **Lua READ taps observe nothing where memory is direct-mapped or served through cached pointers** — device ROM spaces, and on some drivers work RAM and program ROM alike (measure it with a positive control before relying on one). "Nobody reads this address" is never a conclusion a read tap can support there; use the debugger trace or static pointer archaeology, and remove a dead knob rather than document it.

> **Incident** (`docs/platform/gotchas.md` › *MAME Lua: WRITE taps fire, READ taps do not (14z-112, measured)*):
>
> `space:install_write_tap()` works and is what `tests/lua/inp_guard.lua` relies
> on (the #99 capture taps the game's own `$FF0000` exception store).
> **`space:install_read_tap()` never fires on this driver** — not for ROM and
> not for work RAM. Measured 14z-112 with a positive control: a tap on
> `RAM:$FF8400-$FF840F`, read every frame by the fighter code, produced ZERO
> events over a 3-frame window, exactly like a tap on a program-ROM record.
> Direct-mapped memory reads bypass taps; only handler-backed accesses would
> surface. So "nobody reads this address" is NEVER a conclusion a read tap can
> support here — use the debugger trace (`INP_DEBUG=1 TRACE_FROM=`) or static
> pointer archaeology instead. The knob was written for #112 and removed the
> same session rather than left documented-and-dead.

**[MFI-15]** **`-video none` STILL creates a window that can take focus, and host keystrokes are injected into the EMULATED controls.** Prevent (input providers `none`; `SDL_VIDEODRIVER=dummy` so no window exists) AND detect (assert every frame that the live controller bits are exactly what the script staged, fail the run on a violation) — mask to the bits the harness drives, because an input port can also carry a serial line (an EEPROM data bit) that legitimately toggles at boot.

> **Incident** (`docs/platform/gotchas.md` › *MAME's "-video none" STILL creates a window that can take focus — and host keystrokes are injected into the EMULATED controls*):
>
> (mechanism supplied by the maintainer, 2026-08-03; implicated in the two
> unexplained 14z-59 divergences)
> MAME has no true headless mode the way some emulators do. Even with
> `-video none` it creates a window, and that window can steal focus. Any
> key pressed while it has focus goes to MAME's default keyboard map, which
> covers **P1 directions, buttons 1-6, coins and start**. The harness runs on
> the maintainer's working laptop, so this is a live hazard, not a
> theoretical one — the machine gets used, focus gets grabbed back, and
> keystrokes land wherever they land.

**[MFI-16]** **`-aviwrite` is headless-capable but uncompressed** (gigabytes in minutes, and it slows the run past frame caps you believed in); record a WINDOW from Lua (`begin_recording` at a named frame, losslessly compressed), pass an ABSOLUTE output path (a relative one goes through snapshot-name substitution), and ground-truth the recorder before reading anything off it — a recorder that drops or blanks frames still produces a file that plays.

> **Incident** (`docs/platform/gotchas.md` › *MAME `-aviwrite` is headless-capable but uncompressed (14z-94)*):
>
> Recording from inside MAME is the right instrument for dating a visual
> event — the captured frames are EMULATED frames, so window frame k is
> replay frame START+k by construction, and the file is reproducible run to
> run. A host screen recorder gives neither.

**[MFI-17]** **Cross-driver framebuffer CHECKSUMS are NOT comparable** — thousands of "divergent" frames between two machine configs whose bitmaps are pixel-identical. A checksum stream is valid WITHIN one machine config; across drivers pixel-compare snapshots directly, or use the other emulator's exact framebuffer hash. A "divergent framebuffer" claim across drivers is untrustworthy until snapshot-verified.

> **Incident** (`docs/platform/gotchas.md` › *MAME cross-driver VIDEO_OUT checksums are NOT comparable (14z-62d)*):
>
> Comparing replay.lua VIDEO_OUT streams between the `vsav`/`vsavj` machine
> and the `vsavjw` (cps2wide) machine flags THOUSANDS of "divergent" frames
> whose actual bitmaps are pixel-identical — verified by decoding
> `video:snapshot()` PNGs at four frames inside "divergent" runs (raw
> IDAT equal) while work RAM was bit-identical and the OBJ lists matched
> entry-for-entry. The checksum evidently samples something the machine
> config perturbs (timing/sampling nuance), not the final picture. Rules:
> - VIDEO_OUT is valid WITHIN one machine config (its self-check, the
>   determinism gates, stock-vs-stock comparisons).
> - For cross-driver pixel comparison use FBNeo FBNEO_HVIDEO (proven exact
>   across vsavj/vsavjw in test_wide_render_content.sh) or pixel-compare
>   MAME snapshots directly.
> - A "divergent framebuffer" claim about a WIDE build measured with MAME
>   VIDEO_OUT against stock is UNTRUSTWORTHY until snapshot-verified.

**[MFI-18]** **A chained rompath makes MAME a LIAR about member identity**: a stale member resolves by hash to the PRISTINE twin in the reference set and renders perfectly while the other emulator loads the stale bytes. Assert member identity ON THE ZIP (CRC against pristine), never through rendering; for honest visuals of a patched set use a RESTRICTED rompath with no pristine twin reachable; when the two emulators disagree visually, suspect ROM RESOLUTION before emulation.

> **Incident** (`docs/platform/gotchas.md` › *A chained rompath makes MAME a LIAR about member identity (14z-62h)*):
>
> The same bug was invisible to every MAME-side measurement: with
> `MAME_ROMPATH="<build>;$ROMDIR"`, MAME resolved the stale (CRC-mismatched)
> group-B members by HASH to the PRISTINE copies in ROMDIR's vsav.zip and
> rendered Jedah perfectly — while FBNeo (name-resolution inside its overlay,
> where the build's vsav.zip replaces the reference by filename) loaded the
> stale bytes. The two instruments disagreed about WHICH ROM was running.
> Rules:
> - Member identity is asserted ON THE ZIP (CRC compare vs pristine), never
>   via rendering through a chained rompath.
> - For honest MAME visuals of a patched set, use a RESTRICTED rompath
>   (build zips + qsound_hle only) so no pristine twin is reachable.
> - When FBNeo and MAME disagree visually, suspect ROM RESOLUTION before
>   emulation — this is the third member-resolution trap (60z, the zero-CRC
>   collision, now this).

**[MFI-19]** **Palette RAM takes Lua pokes for READBACK but not for RENDERING** — a poked palette reads back changed and draws unchanged, because the renderer reads the device's decoded copy. A poke is not a render; verify at the picture.

> **Incident** (`docs/platform/gotchas.md` › *A probe PC that is not an instruction boundary measures NOTHING while looking green (14z-100)*):
>
> MAME palette RAM ($90C000) takes Lua pokes for READBACK but not for RENDERING (14z-102)
>
> Poking palette rows from a frame_done hook (POKES or space:write) lands
> in the bytes — a later DUMPS readback shows the poked values sticking —
> but the rendered frame never changes; only the GAME's own writes
> recolor. Two magenta-row controls proved it (poked row read back intact
> at the next frames, snapshot unchanged, while the DF seq's writes to the
> same row visibly recolor). Do not build a palette A/B on pokes: it is a
> dead instrument that passes its own readback liveness check. Use a probe
> BUILD (or poke the game's staging buffer, once its per-frame copy source
> is measured), and treat any poke-based "no visual change" as
> unmeasured.

**[MFI-20]** **MAME audits the whole board**: per-set key files and any SHARED device romset are required, and the audit lists the shared device as missing under EVERY dependent game (looks like mass failure); `-verifyroms` uses the ini's rompath unless `-rompath` is passed and can "fail" sets it never opened. "Works everywhere but fails MAME audit" is usually packaging, not dumps.

> **Incident** (`docs/platform/gotchas.md` › *Pre-seeded from the ROM-audit round (2026-07-25, before repo existed)*):
>
> - **MAME audits the whole board, not just the game:** FBNeo has decryption
>   keys compiled in and synthesizes QSound (HLE) without the DSP dump; modern
>   MAME requires per-set `.key` files AND the shared device romset
>   `qsound_hle.zip` (`dl-1425.bin` — one copy in the rompath serves every
>   QSound game, but the audit lists it as missing under *every* dependent
>   game, which looks like mass failure). A collection that "works everywhere
>   but fails MAME audit" is usually packaging/device ROMs, not bad dumps —
>   read the audit line items. Also: `-verifyroms` uses the rompath from
>   mame.ini unless `-rompath` is passed — it can "fail" sets it never opened.
> - **vhunt2r1 has no key of its own:** its MAME definition loads the parent's
>   `vhunt2.key` under that exact filename (identical board key across both
>   revisions, CRC 61306b20).
> - **Clone/parent split:** `vsavj` and `vhunt2r1` are clones; in split sets
>   their gfx/QSound ROMs live in the parent zips (`vsav.zip`, `vhunt2.zip`),
>   which must be present alongside.

## 0.2 Building MAME without changing the instrument

**[MFI-21]** **`git submodule add` stages the DEFAULT BRANCH, not the tag you check out afterwards**; the next `submodule update` silently restores it, and a reference built before and a patched build after compared two DIFFERENT emulator versions while reporting a green invariant. `git add` the submodule after the tag checkout; hard-code the pinned SHA in the build script and refuse anything else; compare `tag^{commit}`, not the annotated tag object.

> **Incident** (`docs/platform/gotchas.md` › *`git submodule add` stages the DEFAULT BRANCH, not the tag you check out*):
>
> leaves the SUPERPROJECT INDEX pointing at the default branch head — the
> `add` staged it before the checkout, and the checkout never re-staged.
> Everything looks right (`git -C emu/mame log -1` shows the tag's commit)
> until something runs `git submodule update`, which dutifully restores the
> INDEXED commit and silently moves the tree back to master.

**[MFI-22]** **GENie cannot handle a SPACE anywhere in the source path, and a symlink does not help** (`getcwd()` resolves through it). Build from an rsync'd space-free mirror, and ANCHOR the mirror's excludes with a leading slash — an unanchored directory pattern matches at ANY depth, and the one meant for the output tree also dropped the scripts' own directory of the same name, producing a missing-RULE error far from the cause.

> **Incident** (`docs/platform/gotchas.md` › *MAME's build system cannot handle a SPACE anywhere in the source path*):
>
> (paid: 2026-08-03, B5 — ~30 min)
> This repository lives under `.../Vampire Saved/...`. MAME's GENie build
> dies on that. `scripts/genie.lua:18` carries the escaping line
> **commented out upstream**, and `SOURCES=` builds shell out to
> `makedep.py` with `MAME_DIR` unquoted, so genie reports the useless
> `Error creating projects from specified source files` (the same command
> run by hand works fine — that is the tell).

**[MFI-23]** **The OSD is found ONLY through pkg-config** (`REGENIE=1` after installing it — detection is baked into generated project files, and the failure lands minutes in); **a `SOURCES=`-filtered build silently OMITS any driver missing from the driver list** — assert `-listfull <driver>` before trusting anything else, and the binary is named after the subtarget; **the driver list holds no inline comments** — add the bare name.

> **Incident** (`docs/platform/gotchas.md` › *MAME's OSD is a DIFFERENT ONE PER PLATFORM, and it is found ONLY through pkg-config*):
>
> (paid: same session, ~8 min of wasted compile)
> **WHICH OSD, measured from the pinned source** (`makefile`, "specify OSD
> layer"): `TARGETOS=macosx` -> `sdl3`, `linux` -> `sdl` (SDL2 + SDL2_ttf +
> fontconfig, `scripts/src/osd/sdl.lua`, plus the `qmake6` TOOL its config
> queries on every build — the 2026-09-13 entry), `windows` -> `windows`, the native OSD
> needing no SDL at all. The macOS requirement was written down as everyone's
> until 2026-09-12, when a Linux build died on a `fontconfig.pc` nothing had
> asked for and a WSL2 page was sending readers to compile SDL3 from source for
> nothing. ON macOS: `scripts/src/osd/sdl3.lua` decides between framework and library linkage
> by asking pkg-config. With pkg-config absent it silently picks framework
> linkage, and the build then dies **several minutes in** with
> `fatal error: 'SDL3/SDL.h' file not found`. Having the sdl3 library
> installed is not enough. Prerequisites are `brew install sdl3 pkgconf`,
> and after installing pkgconf the build needs `REGENIE=1` — the detection
> is baked into the generated project files.

**[MFI-24]** **Parity BEFORE the patch.** Swapping a binary changes the INSTRUMENT, not the subject: prove the UNPATCHED source build reproduces every frozen oracle log bit for bit first, and make that gate refuse to run against a binary that already knows the extended driver. Whether a filtered build changes emulation is not argued, it is measured.

> **Incident** (`docs/project/cps2_wide.md` › *From HANDOFF.md: «MAME from source — the oracle follows the profile»*):
>
> **Order is not optional.** `test_mame_parity.sh` proves the UNPATCHED
> source build reproduces every frozen oracle log bit-for-bit before the
> profile patch is allowed near it — swapping the binary changes the
> INSTRUMENT, and an instrument that moved invalidates every MAME finding
> since session 1. The gate refuses to run against a binary that knows
> `vsavjw`.

**[MFI-25]** **`git apply` inside another repository's working tree SILENTLY SKIPS the patch and exits 0** (`$HOME` was itself a repo; `--check` "passed" too). Use `patch -p1 -d <dir>` for out-of-tree trees, and never treat an exit code as evidence a patch landed: assert on the RESULT — a marker in the patched file, the feature in the built ARTIFACT, and the reference binary NOT having it.

> **Incident** (`docs/platform/gotchas.md` › *`git apply` SILENTLY SKIPS the patch when the target is inside another repo's working tree — and exits 0 (paid: 2026-08-03, B5)*):
>
> `tools/setup_mame.sh` builds from a mirror under `~/.cache/vampire-saved/`.
> On this machine **`$HOME` is itself a git repository**, so the mirror sits
> at prefix `.cache/vampire-saved/mame/` inside it. `git -C <mirror> apply
> 0002-cps2-wide-v1.patch` therefore read the diff's paths
> (`src/mame/capcom/cps2.cpp`) as **$HOME-repo-root-relative**, found them
> outside the current prefix, printed `Skipped patch 'src/...'` — and
> **returned 0**. `git apply --check` "passed" for the same reason.

## 0.3 FBNeo as an instrument

**[MFI-26]** **`make sdl2 SKIPDEPEND=1` is mandatory on a fresh clone, run TWICE there (the parallel first pass, with `-k`, stops on `burn.o` until the driver list is generated) — and it hides header AND driver edits**: after editing a driver, `touch` the source or the link silently reuses the old object and the emulator keeps the previous descriptor (a grown region that measures exactly like the stock one). Driver sources are not always valid UTF-8: edit them in byte mode.

> **Incident** (`docs/platform/gotchas.md` › *FBNeo fresh builds need `SKIPDEPEND=1` (paid: 2026-07-25)*):
>
> `make sdl2` on a fresh clone dies with `No rule to make target 'driverlist.h',
> needed by 'burn.d'` — the depend-generation path (DEPEND=1 default) wants the
> generated `driverlist.h` via a bare-name prerequisite that vpath can't resolve
> before the file exists. FBNeo's own CI never builds that path: every workflow
> passes `SKIPDEPEND=1`. Use `make sdl2 SKIPDEPEND=1 -j8`. (Consequence: no
> header-change tracking — after editing FBNeo headers, `make clean` or touch
> the affected .cpp files.) **AND RUN IT TWICE ON A FRESH TREE (measured
> 14z-149, the first release build from a clean worktree):** with
> `SKIPDEPEND=1 -j` the same message comes back for `burn.o` — its bare
> prerequisite `driverlist.h` is satisfiable only after the rule that GENERATES
> the list has run, and that rule depends on every driver object, so a parallel
> first pass schedules `burn.o` long before the list exists and stops (a serial
> `-j1` build compiles the drivers first and never sees it). The dev submodule
> never showed this because its list has existed since the first build. The
> recipe that works on any host: `make sdl2 SKIPDEPEND=1 -j8 -k` (everything but
> `burn.o` builds, the list included), then `make sdl2 SKIPDEPEND=1 -j8` (a
> no-op on a complete tree). `tools/build_release_emulators.sh` and the shipped
> EMULATOR.md recipe do exactly that.

**[MFI-27]** **The shared EEPROM breaks run-to-run determinism** — `$HOME` overrides do not sandbox the user config, every run shares one `.nv`, and the boot counter differs by one; runs shorter than the write-back look deterministic. Force the EEPROM/hiscore/cheat paths into the per-run sandbox. Found by the standard bug-report format applied to the emulator: per-frame dumps of two runs, first divergent frame + address.

> **Incident** (`docs/platform/gotchas.md` › *FBNeo shared EEPROM breaks run-to-run determinism (paid: 2026-07-25, ~45min)*):
>
> Symptom: consecutive scripted FBNeo runs of vsavj diverged from frame ~75 by
> exactly ONE work-RAM byte (`RAM:$FF0CC9`) whose value differed by 1 — the
> game's EEPROM bootup counter. Cause chain: (a) `$HOME` overrides do NOT
> sandbox FBNeo on macOS — the user config ini (loaded from the real
> `~/Library/Application Support/fbneo/`) carries absolute support paths;
> (b) `szAppEEPROMPath` then points every run at the same `vsavj.nv`, and the
> bootup counter increments per boot. Runs shorter than the EEPROM write-back
> looked deterministic, which disguised the cause. Fix: the harness forces
> `szAppEEPROMPath`/hiscore/cheat paths into the per-run sandbox cwd
> (`main.cpp`, harness-active branch). Debug method that found it: per-frame
> full work-RAM dumps from two runs, diffed → first divergent frame + address
> (the standard bug-report format works for emulator bugs too).

**[MFI-28]** **FBNeo matches a member by CRC FIRST, then by name; when NEITHER matches it loads 0xFF FILL and still prints `(OK)`.** A region reading 0xFF means "never arrived"; 0x00 means "loaded but empty". A `(OK)` line is not proof — and the more dangerous half is the hash-shadow ([MFI-44]).

> **Incident** (`docs/platform/gotchas.md` › *FBNeo matches zip members by CRC — a mismatch loads 0xFF FILL and still prints "(OK)"*):
>
> This is the single nastiest trap found in the WIDE work, and it
> CONTRADICTS an earlier note in this repo ("FBNeo verified to load
> CRC-changed patched zips (no descriptor change needed)"). That note is
> true only in the narrow sense that FBNeo does not refuse to RUN. What it
> actually does when a member's CRC does not match the descriptor is load
> **0xFF fill** for that member — while the log still prints
> `Loading graphics (name)... (OK)`.

**[MFI-29]** **The SDL frontend has NO `-rompath`; the flag is silently ignored** and the set reports as missing — reads as "my romset is wrong". Run FBNeo from a `roms/` overlay of symlinks (reference zips first, the build's zips over them), with ABSOLUTE link targets — the emulator resolves them from inside its sandbox, and a relative overlay is a directory of broken symlinks whose only symptom is a bare "DrvInit failed" in the sandbox log. Assert on the emulator's own load output (the driver banner and the per-member `(OK)` lines), never on the process starting.

> **Incident** (`docs/platform/gotchas.md` › *FBNeo's SDL frontend has NO `-rompath` — the flag is silently ignored*):
>
> (paid: 2026-08-05, 14z-60m — cost the maintainer several failed launches)
> `tools/run_wide.sh` launched FBNeo as
> `fbneo vsavjw -rompath "<build>;$ROMDIR"`. MAME supports `-rompath`; **FBNeo
> does not**. Rom paths live in `szAppRomPaths[]`, defaulting to
> `/usr/local/share/roms/` and **`roms/` relative to the CWD**
> (`src/burner/sdl/drv.cpp:6`), and are otherwise set from the config file.
> An unknown option is not rejected — FBNeo simply searches its configured
> paths, finds no `vsavjw.zip`, and reports the set as unavailable. The
> symptom therefore reads as "my romset is wrong" when the romset is fine.

**[MFI-30]** **Without the framebuffer knob the sprite path never runs** (`pBurnDraw` null → the object drawer is never called), so a probe in the sprite path prints nothing and reads as "my flag is not set"; and a harness that captures stdout+stderr into the sandbox log leaves the command's own output empty.

> **Incident** (`docs/platform/gotchas.md` › *FBNeo harness: no video means the sprite path never runs, and stdout is captured to the sandbox log*):
>
> Two ways to waste an hour while instrumenting FBNeo. (1) The harness only
> renders when `FBNEO_HVIDEO` is set; without it `pBurnDraw` is NULL and
> `Cps2ObjDraw` is never called, so a printf in the sprite path produces
> NOTHING — which reads exactly like "my feature flag is not being set".
> (2) `tools/run_replay_fbneo.sh` redirects the emulator's stdout+stderr to
> `<sandbox>/fbneo_replay.log`; grepping the command's own output finds
> nothing. That log is also where FBNeo prints its region sizes and
> per-member "Loading graphics (x)... (OK)" lines — the fastest way to
> confirm a descriptor change actually took effect.

**[MFI-31]** **A reference binary must differ from the build under test by EXACTLY ONE thing**, built from the same tree state with only the patch under test reverted. A reference build that merely SKIPPED applying the patch to a tree that already carried it compared the extension against itself — a vacuous pass on the one gate that justifies emulator changes at all. The reference build REVERTS; both builds and the gate assert the extension's marker in BOTH directions on the artifact.

> **Incident** (`docs/platform/gotchas.md` › *`WIDE=0 tools/setup_fbneo.sh` did not produce a clean reference — it only SKIPPED applying the profile patch, never reverted it*):
>
> (paid: 2026-08-03, B5b — the FBNeo emulator superset invariant may never
> have actually been tested)
> `setup_fbneo.sh` applies the CPS-2 WIDE patch to the submodule WORKING TREE
> and leaves it there. On the next invocation with `WIDE=0` the script took
> the "skip" branch, printed **"WIDE=0: harness-only build (reference binary
> for the superset invariant)"** — and built a binary that still **carried the
> profile**, because the tree had never been reverted.

**[MFI-32]** **Instrument extensions to a frontend are frontend-only and opt-in**: scripted input/output/frame count/dumps, a per-frame framebuffer checksum, gfx-buffer dumps, a value-logging write tap with PC attribution, frame-scheduled pokes, address-resolved dumps reaching OBJ/palette RAM — all inert when unset, so the patched emulator on stock content is the stock emulator by construction. That is the emulator-superset shape in the harness's own edition.

> **Incident** (`docs/project/operations.md` › *From HANDOFF.md: «What exists» — the tool catalogue*):
>
> | FBNeo | `emu/fbneo` submodule + `tools/setup_fbneo.sh` | built (SDL2); THREE patches, only TWO of which are ever in a DEVELOPMENT binary: `0001` harness (frontend-only: `-hinput/-hout/-hframes/-hdump`, plus `FBNEO_HVIDEO` framebuffer checksums, `FBNEO_HGFX` gfx-buffer dumps, and the B5b set — `FBNEO_HTAP` write tap with PC attribution, `FBNEO_HPOKE` frame-scheduled pokes, address-resolved dumps reaching OBJ/palette RAM) and `0002` the CPS-2 WIDE profile (driver descriptor + TWO gated blocks in `Cps2ObjDraw` — the promote and the canary control; "one gated core line" until 14z-114, corrected per 14z-90). **AND `0003` drop-sdl2-image, RELEASE-ONLY (ratified by the maintainer 2026-09-21):** `tools/build_release_emulators.sh` applies it and `setup_fbneo.sh` does NOT, so the dev binary you measure with still links SDL2_image. It stops FBNeo linking that library — whose only use is an optional per-game preview PNG in FBNeo's own game-browser menu, a path that already did nothing here — which removes 21 transitive image codecs: a shipped macOS bundle is **4 files instead of 24**, and the System Settings route should then cost 4 Gatekeeper approvals instead of 24 — INFERRED from MAME's measured 2-file/2-approval case, exercised at neither count (#144). Proven inert: 12,120 frames of `05_timeout_idle` with and without it are BIT-IDENTICAL in work RAM AND framebuffer. **CRC WARNING:** FBNeo matches zip members by CRC — a mismatched gfx/QSound member is silently replaced by 0xFF fill while still logging `(OK)` (docs/GOTCHAS.md) |

## 0.4 Two implementations: what transfers and what does not

**[MFI-33]** **Same inputs are NOT the same content across emulators**: a boot-phase offset of a few frames changes WHICH content runs near any transition — CPU-chosen opponents differ (a different attract-PRNG state at the coin), a menu press near an input-accept boundary joins on one and not the other, a match-start predicate flickers during intros. Dual-emulator replays script BOTH sides, keep presses ≥100 frames after the enabling transition and ≥10 from any boundary, and compare mapped fields at ANCHORS with a debounce — within-emulator oracles stay whole-RAM frame-exact.

> **Incident** (`docs/platform/gotchas.md` › *Cross-emulator replays: same inputs ≠ same content (paid: 2026-07-25, ~2h)*):
>
> The MAME↔FBNeo frame offset (a few frames at boot) does more than shift
> frame indices — near any screen transition it changes WHICH content runs.
> Three measured mechanisms, all found while validating `tools/compare_fields.py`:

**[MFI-34]** **Frame indices and object SLOTS do not transfer between emulators** — the allocator hands the same object a different slot on a different timeline, so a slot-keyed tap chases a different object and "survives" a crash the other emulator reproduces deterministically. Cross emulators by keying on CONTENT (the handler PC, the type byte); treat the frame-addressed emulator as the instrument when the finding is frame-addressed.

> **Incident** (`docs/platform/gotchas.md` › *FBNeo/MAME frame indices and object slots do not transfer — a slot-keyed tap chases a different object (14z-81)*):
>
> The merged Huitzil crash is deterministic on MAME at frame 2886, object
> `$FFB800`. (That frame is the crash guard's `frame_done` count, its clock until 14z-197 (#228 step 4), on a game
> that had diverged from the replay at frame 12. On emulated time, with the probe kept from stopping the CPU before it,
> the satellite's first anim walk on the healthy build is at frame 7962 — `tests/audit_merged_vec3.sh`.) An `FBNEO_HTAP` on that slot showed healthy writes on BOTH builds
> — and the merged build survived the whole 11,017-frame replay on FBNeo. Not
> a contradiction: the emulators traverse the same states on different frame
> indices (documented since session 2), the RAM state at pick time therefore
> differs, and the object ALLOCATOR hands the satellite a different slot — so
> the tap watched some other object, and the defect's observable moved. A tap
> or probe keyed on an OBJECT SLOT is only meaningful within one emulator's
> run; to cross emulators, key on content (the handler PC, the type byte),
> and treat MAME as the instrument when the finding is frame-addressed.

**[MFI-35]** **A RAM-checksum gate is structurally BLIND to the video path** — a rendering change produces byte-identical RAM whether it draws correctly or garbage. Before trusting a gate on a change, confirm its instrumentation EXECUTES the code path changed; give both harnesses an opt-in framebuffer checksum for exactly this, written to a separate file so no frozen RAM expectation moves.

> **Incident** (`docs/platform/gotchas.md` › *The FBNeo gate never rendered a pixel — RAM checksums are blind to video*):
>
> The FBNeo harness ran every frame with `pBurnDraw = NULL`. That is correct
> for speed and for a work-RAM oracle, but it means the emulator-side gate
> could not see the video path AT ALL: a change to sprite/tile rendering
> produces byte-identical RAM logs whether it works or draws garbage. This
> was discovered while trying to verify the CPS-2 WIDE 19-bit tile address,
> whose entire effect is in `cps_obj.cpp` — the gate would have "passed" it
> without ever executing the modified line. Fixed by an opt-in framebuffer
> checksum (`FBNEO_HVIDEO=<path>`, harness.cpp), now compared alongside RAM
> in tests/test_wide_profile.sh. General lesson: before trusting a gate on a
> change, confirm the gate's instrumentation actually EXECUTES the code path
> you changed.

**[MFI-36]** **Sound is invisible to every RAM and pixel gate** — it lives in a ring the gates mask as noise and in a second processor's pipeline they never look at. Any subsystem whose output leaves the main CPU's address space needs a DEDICATED detector; "the battery is green" says nothing about it.

> **Incident** (`docs/project/gotchas.md` › *Sound is invisible to every RAM and pixel gate — it needs its own*):
>
> The masked legacy gate, the field oracles and the pixel menu gates were
> ALL green while Donovan was completely silent, and equally green when a
> sound path was wired to vsavj's music-track id range (the round-2
> "214P plays music" bug). Sound state lives in a ring the gates mask as
> noise and in a Z80/QSound pipeline they never look at. tests/
> test_don_sound.sh exists because of this: it taps the ring, fails on
> any id in the music range, and freezes the per-replay id inventory.
> Any subsystem whose output leaves the 68k address space (sound today,
> anything sent to another processor tomorrow) needs a dedicated
> detector — "the battery is green" says nothing about it.

**[MFI-37]** **A value fed by allocation, RNG or sound state cannot be correlated ACROSS runs** — a write tap from run A compared with a read from run B produced a phantom "invisible write". Serialize read and write in ONE run with one instrument; run write watches UNWINDOWED first (the boot POST doubles as the liveness control); the observation window bounds the claim.

> **Incident** (`docs/platform/gotchas.md` › *A state-dependent value may not be correlated ACROSS runs — serialize read and write in ONE run (14z-87)*):
>
> The sword-plant "ding" hunt spent most of a session on a phantom
> "invisible write": a write tap on `$FF8782` said the last mid-match write
> was 0x06, a debugger bp said the dispatcher later READ 0x0C from that
> byte, both instruments were provably live — and no mechanism on either
> emulator can change RAM without a bus write. The resolution: **the value
> is a dynamic ALLOCATION result (the arcade ladder's opponent pick — read
> then as a "voice-class borrow", a reading RETRACTED 14z-188 — on a rig
> whose match never formed), and every run allocates differently** — measured 0x06/0x0C/0x09/0x00 across
> identical-input MAME runs and 0x04 on FBNeo. The write from run A was
> being compared with the read from run B. In one run with read AND write
> taps installed together (`tests/lua/read_tap.lua`), the write was 0x0C
> and the read was 0x0C: nothing was ever invisible.

**[MFI-38]** **A canary changes exactly ONE thing or it answers nothing.** When a ROM edit would also change game logic, change the EMULATOR under a test-only flag instead, so game state is identical by construction and only pixels can move; the cheap isolation is to run the modified program on the OTHER emulator, which lacks the feature entirely.

> **Incident** (`docs/platform/gotchas.md` › *A canary must change exactly ONE thing, or it cannot answer anything*):
>
> The first CPS-2 WIDE B4 canary tried to prove the new 19-bit gfx banks
> were reachable by remapping 15 characters' bank-table rows to the new
> banks and requiring pixel-identical output. It failed — and the failure
> was uninterpretable, because the same edit ALSO changed game logic (see
> `docs/project/cps2_wide.md` "B4" — the reference was in-file before this
> entry was re-filed here at 14z-118). Two variables moved at once, so neither "the emulator path is
> broken" nor "the game strips the bit" could be concluded. The isolation
> that DID work was cheap and should have come first: run the modified
> program under the OTHER emulator (which lacks the feature entirely) and
> diff — that immediately separated "game behaves differently" from
> "emulator renders differently". Design canaries so that exactly one
> subsystem can account for the result, and prefer changing the EMULATOR
> under a test-only flag over changing the ROM when the ROM change has
> side effects.

**[MFI-39]** **A relocation test with no negative control proves nothing** — "I moved X and nothing changed" was also true with X pointed at zero fill, because X was never read in those replays. Pair every such test with "I broke X and something changed".

> **Incident** (`docs/platform/gotchas.md` › *A relocation test with no negative control proves nothing*):
>
> The CPS-2 WIDE PRG canary relocated one character's sound table into the
> extension and came back RAM-identical — apparently proving the 68k could
> read above 4MB. It proved nothing: pointing the same table at ZERO FILL
> was *also* RAM-identical, because that row is never read in those
> replays. Any "I moved X and nothing changed, therefore X works" test must
> be paired with "I broke X and something changed". The fixed version
> relocated all 20 tables, where the zeros variant does diverge and the
> identical result is real evidence.

**[MFI-40]** **"Unknown system" is an EMULATOR problem, not a ROM problem** — renaming the zip to force a load is actively harmful (the wrong driver's descriptor loads the wrong regions and the failure moves downstream). Check the binary carries the driver first (`-listfull`, the banner string in the binary).

> **Incident** (`HANDOFF.md` › *If it still will not start, in order*):
>
> **"Unknown system: vsavjw" is an EMULATOR problem, not a ROM problem, and
> renaming `vsavjw.zip` to `vsavj.zip` to force it is actively harmful** — it
> boots under the stock 4MB descriptor with the sfx helper live and the sound
> pointer aimed at the CPS2 register window, re-creating the music bug while
> looking fine. See GOTCHAS.

**[MFI-41]** **What a machine migration puts at risk is only the frozen MAME expectations** (absolute values; every FBNeo gate written as a live A/B is machine-independent by construction), so the parity gate IS the migration gate — run it on the target before trusting anything, and if it fails do NOT re-freeze to make it green: that silently redefines the baseline every invariant rests on. CPU architecture should not matter for interpreted cores with endian-pinned checksums — an argument, not a measurement; the gate is the measurement.

> **Incident** (`docs/project/operations.md` › *Platform / migration notes (14z-59d)*):
>
> **What is actually at risk in a move: only the MAME expectations.**
> - `tests/expected/**` are ABSOLUTE frozen values, and they are **MAME-only**
>   — `run_suite.sh` drives MAME.
> - Every FBNeo gate (`test_wide_profile.sh`, `test_fbneo_replay_determinism.sh`,
>   the xemu gates) is a **live A/B comparison** and carries no frozen file,
>   so it is machine-independent by construction. Verified by inspection.
> - So `tests/test_mame_parity.sh` **is the migration gate**, and it covers
>   the entire exposure. Run it on the target before trusting anything. If it
>   fails, do NOT re-freeze to make it green — that silently redefines the
>   baseline the superset invariant rests on.

**[MFI-42]** **Two builds can share a PROGRAM fingerprint and differ in every graphics and sound member** (a shippable build and its legacy-only instrument, deliberately). The program fingerprint answers "which code"; "which build is this" is answered by hashing the WHOLE ARTIFACT, every member. Never pick a build by fingerprint or by mtime.

> **Incident** (`docs/platform/gotchas.md` › *TWO BUILDS CAN SHARE A PROGRAM FINGERPRINT — the merged build and its legacy-only instrument do, deliberately (paid: 14z-94)*):
>
> The maintainer asked to confirm which merged build to playtest, fearing they
> had tested the wrong one. They were right to ask, and the fingerprint would
> NOT have settled it:

## 0.5 ROM images and members, as the two emulators see them

**[MFI-43]** **ROM FILES in a word-swapped region are little-endian word pairs; IMAGES (opcode view, data view, emulator dumps) are the CPU's logical order, big-endian on a 68k.** Decrypting or diffing in the wrong order "works" (self-consistent, round-trips) and produces garbage that is deceptively half-right — byte-symmetric words survive either way. Symptom: a diff where "every other word matches" in vector/data areas. Pin the convention with an oracle against the emulator's own opcode space, and run it after touching any byte-order code.

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

**[MFI-44]** **Both emulators resolve a ROM member by HASH before NAME, so a member carrying another member's pristine bytes SHADOWS it — silently, as a "successful" load.** A member's identity in a set is its hash. Rules: no member may carry the pristine bytes of a member the build patched (audit the romset's identity in the build); byte-identical zero-fill PLACEHOLDERS are harmless; 0xFF fill is what you get when NOTHING matches, a wrong file's bytes when something else does.

> **Incident** (`docs/platform/gotchas.md` › *A member carrying another member's PRISTINE bytes SHADOWS it — both emulators resolve a ROM entry by HASH before NAME*):
>
> So the name is the FALLBACK in both emulators, not the identity. A member's
> identity in a set is its HASH, and two files with the same bytes are the
> same member as far as the loader is concerned.

**[MFI-45]** **Descriptor CRCs: FIXED-content members carry their real CRC; VARIABLE-content members carry SENTINELS and resolve by name** — and no two variable members may share a sentinel, because the shared zero-fill CRC hash-shadows a content-bearing member onto its still-zero sibling. Print the exact descriptor rows (name/size/CRC) from the tool that writes the members.

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

**[MFI-46]** **A member's REGION layout is not its FILE layout, and a sound CPU's own address space is a THIRD thing** (split `ROM_LOAD`/`ROM_CONTINUE`; a masked bank register in a window). Read the driver's load lines before deriving any file offset from an emulator address; log the DATA, not just the PC, when arbitrating a mapping; "it disassembles as garbage" is evidence of a wrong offset, not of encryption.

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
