# Vampire Savior — the engine's laws (level 1 for the GAME: true with no port in mind) — the guide

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
into `~/.claude/skills/vampire-savior-engine/`. Nothing in it depends on the origin tree.

## C.1 Three siblings, one engine — the method

**[VSE-1]** **vsav, vsav2 and vhunt2 are three official builds of ONE engine, and their per-character / per-state tables are INDEX-ALIGNED.** Before free-form disassembly of a subsystem, read the same routine in the siblings: a REAL pointer differs between siblings by the host region's shift, an operand pair reads identical — the sibling diff is the pointer oracle, and it is what makes "port by diff" possible at all (`character_tables.md` "The full per-character table BANK").

> **Incident** (`docs/game/atlas/character_tables.md` › *The full per-character table BANK — layout identical in all three sets*):
>
> A contiguous bank of 32-entry tables, stride 0x80 between neighbors. Bank
> origin (= first dispatch table) per set — **all internal deltas are
> preserved across sets**, so any table found in vsavj is `origin + same
> delta` in the others (verified for bank[0], hitbox pair, +0x132 word
> table):

**[VSE-2]** **THE DEAD-ROW CLASS is the most common defect shape**: vsav ships table rows the newcomers need as a STUB (an `rts`, or a displacement pointing back into the table) or an ALIAS of a base-half row, and legacy never notices because legacy never indexes them. Signature: the ported character does something vanilla never does and the failure is TOTAL, with nothing upstream wrong. Recipe: find the table and index, read the SAME row in vs2/vh2, measure the row DEAD in vanilla with a positive control on a live row (opcodes-space watch, PC-filtered past the boot sweep), then the cheapest mechanism that reproduces vs2.

> **Incident** (`docs/game/engine_internals.md` › *THE DEAD-ROW CLASS — vsav ships table rows as STUBS or ALIASES where vs2/vh2 fill them (named 14z-74; SIX instances and counting)*):
>
> **The single most common defect shape in this port.** vsav and vs2 share an
> engine, and their per-character / per-state dispatch and data tables are
> index-aligned — but **vsav leaves rows the newcomers need either as a STUB
> (pointing at an `rts`, or at a displacement inside the table itself) or as an
> ALIAS of a base-half row.** Legacy never notices, because legacy never
> indexes those rows. A ported character indexes them immediately.

**[VSE-3]** **Sibling-COINCIDENT values are invisible to the diff, and the coincident vsavj address is usually a WRONG routine**: engine subroutines, engine tables, the global coordinate pool, A5 work-var displacements — every same-value pointer class found so far. Same value ≠ same meaning; any pointer INTO shared engine data needs a content match or a reconciliation, never a pass-through.

> **Incident** (`docs/game/gotchas.md` › *The sibling-coincidence gotcha, third strike: the global coordinate pool*):
>
> The companion-effect records' coordinate-list pointers aim at vs2's
> GLOBAL X/Y pool (0x30xxxx) — same-value in vs2 and vhunt2, so the
> sibling diff never flagged them, and the region ported with raw
> vs2-space cptrs. Latent since M2a: those effects read coordinates from
> unrelated vsavj bytes (masked by their art also being wrong). Every
> same-value pointer class found so far — engine subs (the sound farm),
> engine tables (the OBJ bank table), and now the coordinate pool — was
> invisible to the diff for the same reason. Rule stands: same-value !=
> same-meaning; any pointer INTO shared engine data needs a reconciliation
> row or a content-match, never a pass-through.

**[VSE-4]** **The A5 work-variable layouts differ between generations by a uniform shift** (the damage staging vars are one family): ported code writing engine work vars by displacement writes DEAD MEMORY on the host — no crash, no diff visibility, silently wrong behaviour (a zero-damage throw).

> **Incident** (`docs/game/gotchas.md` › *Same-value class #4: A5-relative work-var displacements*):
>
> The engines' A5 work-variable layouts differ (vsavj damage vars at
> -0x4BBE/BC/BA vs vs2 at -0x4B6C/6A/68 — a uniform -0x52 family shift).
> Ported code writing engine work vars by displacement writes DEAD MEMORY
> on vsavj — no crash, no diff visibility (vs2/vhunt2 share the layout),
> just silently-wrong behavior (the zero-damage throw). Any ported code
> that communicates with engine routines through A5 work vars needs its
> displacements reconciled like ROM refs. Sweep pattern: displacement
> words in the vs2 work-var bands inside ported code regions.

**[VSE-5]** **vsavj keeps byte-identical COPIES of engine code inside per-character families** (a character's private copy of the generic jump-seq head). A byte-for-byte twin found by search may be a DEAD copy: find the LIVE handler by TRACING the dispatch, never by byte search alone.

> **Incident** (`docs/game/gotchas.md` › *The content-twin trap: vsavj keeps byte-identical copies of engine code inside per-char families — hook the LIVE one, found by tracing*):
>
> Searching vsavj for the byte-for-byte twin of vs2's generic jump-seq
> head found 0x26A58 — which hooked cleanly and did NOTHING (0 probe
> hits): it is ANAKARIS's private copy of the handler, id-routed at
> 0x22A0E (`cmpi.b #6` at the head). The LIVE generic handler is reached
> through the class-02 stepper 0x225C4 (table 0x225EE, seq06 -> +0x420).
> Find live engine handlers by TRACING the actual dispatch (GUARD_TRACE
> on the acting frames), never by byte search alone — the engine
> duplicates handler code per character and the copies diff identical.

**[VSE-6]** **Engine-generation TUNING drifts inside structurally identical twins**: hit-freeze constants, the multi-hit re-hit gate byte vs2 added, motion-table definitions, the sprite-list handlers' one-byte code bias. A field-for-field twin can still differ behaviourally — A/B the ENGINE fields at event frames on both games, never only the ported bytes.

> **Incident** (`docs/game/gotchas.md` › *Hit-freeze constants are ENGINE-GENERATION tuning, not ported data — sibling-verified structure can still drift behaviorally*):
>
> The vsavj and vs2 victim-reaction handlers are structural twins
> (field-for-field), but the freeze constants inside them differ
> (attacker +0x5C: 0x0B vsavj vs 0x04 vs2; victim 0x18 vs 0x0C): vs2
> retuned the shared engine for its rapid multi-hits. Any ported move
> whose FEEL depends on engine-side constants (freeze, shake, gravity
> tables) can diverge with zero byte differences in the ported regions
> — A/B-measure the engine fields (tap the obj struct at event frames
> on both games), don't audit only the ported bytes. (14z-42: this one
> drift WAS both maintainer symptoms — hit count and animation speed.)

**[VSE-7]** **vs2 WIDENED index consumers vsav left narrow, and every such widening is a crash waiting for a ported index**: the effect byte map, the dispatch tables, the sub-state dispatchers (80 entries vs 84 — the renumber gap), the projectile hit-class map (64 vs 80), the throw-arc map, list type 12. Every TYPE/CLASS byte in ported data indexes SOME engine dispatch, and the engines RENUMBERED families between games.

> **Incident** (`docs/game/engine_internals.md` › *The projectile-pool HIT-CLASS map — a second type consumer, bounded at 64 (14z-82b)*):
>
> then `move.w (6,PC,D0.w),d1; jmp (2,PC,D1.w)` through per-dispatcher
> 8-word tables. vs2's sibling map (routine 0x19292, map 0x19298) has **80
> entries**: 0-58 byte-identical (vanilla's true domain — its type table
> has 59 rows), 59-63 divergent (vs2 gives Donovan's 61/62 classes
> 0x0E/0x04; vsavj zeros them), 64-79 the newcomer extension. So **any
> ported type >= 64 in the $FF94xx pool that lands a hit over-indexes
> vsavj's map** — map[64] = the following rts opcode's 0x4E — and takes a
> wild jump: the f7997 vec3, latent in frozen pyron-m2 (satellite type 64)
> and shared by Huitzil (68/72 in the same pool). Third instance of the
> "vs2 widened an index consumer" class (14z-26 property table, 14z-35
> dispatch table, 14z-79's 0x018460 window is the same family).

**[VSE-8]** **A PC on one leg does not name the same routine on the other — and SOME coincide anyway**, which is what makes it dangerous. Correspondence comes from the sibling map or a known region delta; leg-independent COUNTS (did it happen, how often) always transfer, addresses never do.

> **Incident** (`docs/game/engine_internals.md` › *The anim walker reads the sprite list from node+4 (measured 14z-70)*):
>
> **Method note, paid for this session: a PC logged on one leg does not
> name the same routine on the other — and SOME of them coincide anyway,
> which is what makes it dangerous.** The native leg is vsav2 and ours is
> vsavj-based: two different builds of the engine, which is the whole
> reason `tools/reconcile_batch.py` exists. In this one run:

## C.2 The per-character bank and the id space

**[VSE-9]** **The per-character bank is a contiguous run of 32-entry tables, stride `0x80`, index-aligned across all three sets** — any table found in one set is `origin + the same delta` in the others; the first 14 are CODE dispatch (one engine event each), the rest values, pointers and records (`character_tables.md`).

> **Incident** (`docs/game/atlas/character_tables.md` › *The full per-character table BANK — layout identical in all three sets*):
>
> Semantic skeleton (from disassembly of every vsavj consumer site):

**[VSE-10]** **The character id is 5-bit everywhere it is stored; the variant half `0x10-0x1F` has REAL storage in every layout-verified table (zero out-of-range rows), and vsavj fills it with COPIES.** The only architectural narrowing is a small enumerable set of consumer sites that FOLD to 4 bits — seven in vsavj, two in vsav2 (Capcom widened the rest). The folding count is PER-FIELD: derived fields carry their own folds (`id_space.md`).

> **Incident** (`docs/game/atlas/id_space.md` › *The character-id space — is the variant half architectural or conventional?*):
>
> **THE ANSWER: conventional.** The id is a 5-bit value everywhere it is
> stored and in every layout-verified table; vsavj simply fills the upper 16
> rows with copies. The only architectural narrowing is a small, enumerable
> set of *consumer sites* that mask the id to 4 bits — and vsav2, which ships
> three characters on variant ids, shows the fix is to widen those sites.

**[VSE-11]** **A register-dataflow walk cannot see a mask applied straight to a memory field** (`andi.b #$0f,$382(a4)` — the id-cycling selector): two independent walkers missed both such sites; scan for direct memory masks as their own class.

> **Incident** (`docs/game/atlas/id_space.md` › *2. Code — how wide is the id where it is consumed?*):
>
> Both walkers missed it because both keyed on *register* dataflow, and these
> instructions read-modify-write memory with no destination register. Found
> by disassembling the selector by hand. The lesson generalises: **a dataflow
> walk over registers cannot see a mask applied straight to a memory field**,
> and the tool now scans for that class separately (`direct_masks`).

**[VSE-12]** **Count a table's rows from the DATA view and the indexer's arithmetic, never from where the bytes stop looking familiar** — an aliased 32-row table read from the opcode image looks like 16 rows of noise. Paid twice (`anim_pairs`, the effect-palette table). And a variant row holding a value vanilla uses is what an ALIAS IS — the reason repointing it is safe, not a reason it is off-limits.

> **Incident** (`docs/game/gotchas.md` › *A VARIANT ALIAS ROW holds a value vanilla uses — that does not make the SLOT used, and reading it that way deferred a fix for two sessions (14z-76)*):
>
> Every 32-row per-character table in vsav aliases rows `0x10-0x1F` onto
> `0x00-0x0F`. So a tenant's row *always* contains a pointer vanilla also uses
> somewhere — that is the definition of an alias, and it is precisely the
> property that makes repointing the row superset-safe.

**[VSE-13]** **Reserved variant ids: `0x12` (the Gallon-variant path writes it as an immediate on the select screen) and `0x18` (Oboro Bishamon — vanilla's own variant dataset, compared against at four sites; its vanilla entry path is unlocated).** Free: `0x10`, `0x11`, `0x13` — the newcomers' native vs2 ids. Two unrelated tables (the id writers, the sprite-palette pointer rows) agreeing on the same two exceptions is why the set is trusted.

> **Incident** (`docs/game/atlas/id_space.md` › *RESERVED IDS — vanilla does use part of the variant half*):
>
> **Consequence for the roster.** The free-id set is smaller than "everything
> above `0x0F`":

**[VSE-14]** **No legacy gameplay path in the corpus writes a variant-half id** (union of all writers: `00 01 02 03 05 06 08 0A 0C 0E 0F`), which is what makes a character at a variant id superset-safe BY CONSTRUCTION — stated as "no replay HERE", never "vanilla cannot" (`0x12`/`0x18` exist).

> **Incident** (`docs/game/atlas/id_space.md` › *Which ids vanilla ever assigns (measured over the corpus)*):
>
> Union of ids written by any gameplay path:
> `00 01 02 03 05 06 08 0A 0C 0E 0F` — **not one value in `0x10-0x1F`.**

**[VSE-15]** **"Selectable" is not "fightable"**: the CPU opponent, the attract assignment and the challenger path write only P2's id, from an opponent ORDER LIST in work RAM with its own length, through a 32-bit used-mask; arcade-ladder membership is a separate work item from the wheel.

> **Incident** (`docs/game/atlas/id_space.md` › *The arcade-opponent path (a fourth roster work item)*):
>
> "Selectable" is not "fightable". Tapping the **P2** id field `RAM:$FF8B82`
> found three gameplay writers the P1 tap never sees:

**[VSE-16]** **Per-character table entries are PAIRS more often than they look**: a 16-character table of 8-byte (forward, back) pairs and a 32-character table of 4-byte values have identical spacing. Verify entry layout against vanilla CONTENT (alternating-sign longs are a pair signature) before registering any row — a wrong registration corrupted Felicia's walk-back at 1 px/frame for 19 playtest rounds.

> **Incident** (`docs/game/gotchas.md` › *Per-char table entries are PAIRS more often than you think*):
>
> param32_a/b (movement velocities) span 0x80 per 32 apparent slots and
> were registered as 4-byte rows; they are 16-char tables of 8-byte
> (forward, back) PAIRS. "Slot 0x0F × 4 bytes" = char 7's second long =
> FELICIA'S WALK-BACK — corrupted by Donovan's port since the table
> work landed, at 1px-drift scale that 19 playtest rounds never saw.
> Verify entry layout against vanilla CONTENT before registering any
> table: alternating sign longs (+,-,+,-) are a pair signature; a
> 16-char pair table and a 32-char value table have identical spacing.
> The 29_felicia_walljump oracle caught it the day it was frozen.

**[VSE-17]** **Match-init id normalisation folds `0x0B`/`0x1B` (the Shadow/Marionette slots) and, in vs2, maps both Oboro-class ids onto slot-8 CODE while keeping their own DATA rows** — vs2/vh2 carry five true variant datasets (three newcomers, two Oboros); vsavj carries one.

> **Incident** (`docs/game/atlas/character_tables.md` › *The other two variant datasets: two Oboro-class Bishamons*):
>
> Match-init ID normalization (vsav2 `PRG:0x01F5A0`, mirrored in vhunt2;
> vsavj has the 0x18 case only): IDs `0x18` AND `0x19` both remap to slot-8
> (Bishamon) *code* while keeping their own *data* rows — so VS2/VH2 carry
> two distinct Oboro-class datasets (0x18 ≈ vsavj's Oboro; 0x19 = a second
> flavor, vsav2/vhunt2-only). The five variant datasets in the siblings are
> therefore: **Huitzil 0x10, Pyron 0x11, Donovan 0x13, Oboro 0x18,
> Oboro-alt 0x19**.

## C.3 Objects, pools, type dispatch

**[VSE-18]** **Every secondary object is ticked by a per-frame POOL WALKER that dispatches on the TYPE byte at slot `+0x02` through a per-pool LONG table** — a type at or past the vanilla entry count is unreachable for vanilla objects BY CONSTRUCTION (the guarantee an authored type rests on), and the tables are read pc-relatively (opcode view). Three pools, three numbering spaces: the effect-piece pool (32 × `0x80`), the projectile pool (32 × `0x100`, with its own hit-class map bounded at 64), and a local pool walked by an embedded dispatcher (`ram.md` "Fighter + effect-pool fields").

> **Incident** (`docs/game/engine_internals.md` › *Object TYPE dispatch and the pool walker (decoded 14z-65, fully measured 14z-68d on the Huitzil effect arc)*):
>
> Every secondary object — companions, pods, effect pieces, the victory
> portrait drawer — is ticked from a per-frame walker that dispatches on
> a TYPE byte. This is the single most load-bearing shared mechanism for
> a ported character, and the one most likely to route a tenant's object
> into host code.

**[VSE-19]** **"Never dispatched in the corpus" is not "free"**: the corpus-observed free lists are 50 and 83 indices; a pool-attributed STATIC sweep from every allocator call site finds the true free lists are 1 and 6. A coverage artefact 40× the one that falsified the list-type-6 deadness claim.

> **Incident** (`docs/game/engine_internals.md` › *Object TYPE dispatch and the pool walker (decoded 14z-65, fully measured 14z-68d on the Huitzil effect arc)*):
>
> **Why not repoint tenant types onto "never dispatched" table entries?**
> Because the free lists are not free. `build/manifest/dispatch_census.toml`
> records 50 and 83 indices never observed across the legacy corpus, but a
> pool-attributed STATIC sweep (scanning forward from every call site of
> each pool's allocator — `0x16F8E` for `$FF9400`, `0x16FBA` for `$FFB800`)
> finds the true free lists are **1 index and 6**. The corpus touches 9 of
> 58 real spawn types at one site and 31 of 108 at the other. That is the
> same coverage artefact that falsified the list-type 6 deadness claim,
> about 40x larger — and it would have traded a guarantee (a vanilla object
> CANNOT carry a type >= the vanilla entry count) for an inference.

**[VSE-20]** **Row 8 of the big type table is the SHARED companion machine, and vs2 rewrote its own row 8** — a newcomer's companion carries type 8 on both games, so on the host it is ticked by the host's machine and plays host content. Base, stream, count and updater are ONE unit; swapping only a record base produces odd/negative indices.

> **Incident** (`docs/game/engine_internals.md` › *The shared-type trap, and `[[obj_hook_extra]]`*):
>
> Row 8 of the big table is the COMPANION machine — vsavj `0x606AC`,
> vs2 `0x6CAC0` — and **vs2 rewrote its own row 8**. So a tenant's
> companion/effect object, which carries type 0x08 on both games, is
> ticked by vsavj's machine and resolves vsavj's records. Symptom
> (14z-68): the object exists with correct fields and the right record
> offset, but plays host content.

**[VSE-21]** **Type stamps have TWO forms** — a header long `move.l #$01xxTTss,(A4)` and a byte stamp `move.b #type,(2,A4)` — and a census that knows one is blind to ~26 sites. The spawn idiom is alloc-fail test, `move.b #1,(A4)`, type at +2, owner/sub at +3.

> **Incident** (`docs/game/engine_internals.md` › *Per-tenant TYPE NUMBERS on multi-tenant builds (14z-82)*):
>
> The mechanism rests on a FROZEN census, `build/manifest/type_stamps.toml`
> (tools/audit_type_stamps.py; gate tests/test_type_stamp_census.sh):
> * **Stamp forms are TWO, not one**: `move.l #$01xxTTss,(A4)` header
>   stamps AND `move.b #type,(2,A4)` byte stamps — the spawn idiom is
>   `beq.s <alloc-fail>; move.b #1,(A4); type at +2; owner/sub at +3`.
>   The 14z-81b ad-hoc scan knew only the move.l form and was blind to
>   ~26 sites.
> * Type 117 has exactly ONE stamp (x088512+0x27CE); 116/119 are
>   x088512-only; 114 has ~25 sites across 8 per-tenant region names;
>   **type 120 has ZERO stamp sites in any ported span** (its only vs2
>   stamp 0x00B63C is unported) and keeps first-wins.
> * The 115→117 mid-frame type "morph" (14z-81c) is simply the 117 header
>   re-stamp running later in the same copy — stamps renumber together,
>   so the morph is timing-proof under renumbering.
> * NO code in any tenant's regions COMPARES or table-indexes the type
>   byte for this family (census passes 3/4 + the dynamic writer census
>   tests/audit_type_writes.sh) — the exposure is the walker alone.

**[VSE-22]** **vanilla never seeds the secondary-object pools during a normal match; vs2 always does.** An unseeded pool makes the allocator spin on an empty free list — a HANG with no exception, presenting as a WATCHDOG REBOOT. First place to look when a newcomer reboots the machine on its first special.

> **Incident** (`docs/game/engine_internals.md` › *Pool seeding and the `[[init_shim]]` (14z-65 — the watchdog class)*):
>
> **Vanilla vsavj never seeds the secondary-object pools during a normal
> match; vs2 always does.** Every newcomer's ecosystem allocates from
> those pools, so an unseeded pool means the allocator spins on an empty
> free list — and it **hangs without an exception**: no crash, no
> tripwire, just a watchdog reboot (measured symptom: handler entered,
> no fault, reset). If a new tenant reboots the machine on its first
> special move, look here first.

**[VSE-23]** **The two generations' allocators differ in semantics**: a RECYCLED slot keeps stale bytes under the new object's init unless cleared — a round-2-only bug, after the pool has cycled once. And update-queue class 7 exists in vs2 only (classes 0-6 on vsav): an unremapped registration leaves a stale node that dispatches a FREED slot two rounds later.

> **Incident** (`docs/game/engine_internals.md` › *Allocator wrappers and slot recycling (14z-65)*):
>
> vs2's allocators `0x15702` / `0x1572E` are wrapped (`alloc_wrap` in the
> tenant manifest) with an 0x80-byte clear: vs2's allocator semantics
> differ from vsavj's, and without the wrapper a RECYCLED slot keeps
> stale bytes under the new object's init — which surfaces as a
> round-2-only bug, after the pool has been through one cycle.

**[VSE-24]** **A shared engine routine may be reached by a ported character through a CLONE, not the vanilla copy** (the capture positioner's clone in a ported region): breakpoint the clone, not the engine twin, or measure zero hits on live code.

> **Incident** (`docs/game/engine_internals.md` › *The class-02 sequence system, per-char jump handlers, and the air system (session 14z-66, measured on the Huitzil port)*):
>
> … ab_victim.sh`): before the fix H's
>     row 0x10 aliased character 0's block, holding the victim −27px behind
>     vs native +74 in front; after porting H's own vs2 block `0x0C56AA` the
>     victim tracks native's exact keyframe sequence. **A ported tenant's
>     per-attacker `slot_ptr_table` rows are a REQUIRED port item — check
>     them for every new grappler/thrower.** NOTE for measurement: compare
>     `dx = p2x − p1x` (relative), never absolute victim-x — the ~21px
>     cross-emulator camera shift cancels only in the relative measure (an
>     absolute-x comparison stalled 14z-72 for a session). And a ported
>     tenant reaches this positioner through a CLONE of it (H's is `0xc9eb0`,
>     because `0x27282` fell inside region x026142), not the vanilla copy at
>     `0x2802e` — breakpoint the tenant's clone, not the engine twin.

## C.4 Animation, the drawer, graphics

**[VSE-25]** **Anim nodes are `0x18` bytes**: duration, flags (bit 7 = follow the LINK instead of advancing), the sprite-record pointer at +4, hitbox-family words, the script-op area, a per-node sfx byte. The walker writes the node pointer to `+0x1C`; a hit-freeze holds the node timer via `+0x5C`, so holds FLOAT across nodes — they are not data durations.

> **Incident** (`docs/game/engine_internals.md` › *Anim-script walker + hit-freeze / reaction subsystem (session 14z-42, measured)*):
>
> - **Node format (0x18 bytes):** +0 duration byte — loaded into
>   obj+0x20 as a countdown (`move.l (a0),$20(a6)` on node set;
>   decrement at vs2 0x271C4 `subq.b #1,$20(a6)`, ours 0xCE412); +1
>   flags (bit7 = follow the LINK at +0x18 instead of advancing
>   sequentially — loop-backs are links, e.g. the Lightning Sword loop
>   node 0x284A48 links +0x18 -> 0x284988); +4.l sprite-record ptr;
>   +8.w/+0xA hitbox-family words; +0x10.. the [cf14]..[0b] script-op
>   area; +0x16 byte nonzero -> per-node sfx (jsr 0x5122 on vs2 with
>   d1/d2/d3 from the per-char table 0xD95B8 — the call our
>   stubbed_sound row silences).
> - **Node write:** `move.l a0,$1c(a6)` at vs2 0x2713C. Two writes in
>   one frame = a zero/1-duration chain, normal.
> - **The walker's chain rules, read off vs2 `0x2713C..0x271F2` and LIVE-VERIFIED
>   14z-118** (`tests/test_anim_node_walk.sh`: Donovan on native vs2, 3,638/3,638
>   sampled node pointers on the decoded graph): node SELECT — `a0 = table +
>   word[table + 2*seq]` (the index-table words are offsets from the TABLE's own
>   base; tables a/a2/b at vs2 `0xD7018/0xD7098/0xD7118`, c `0xD7198`, proj
>   `0xD7218` = bank[0]−0x280/−0x200/−0x180/−0x100/−0x80; the START entrie … *(the paragraph continues in the origin doc)*

**[VSE-26]** **Anim NUMBERS: facing adds `0x300`; set-anim QUEUES a (number, params) into the command ring and the DISPLAY processor resolves number → record strip through per-character strip tables later** — patching bank fields or numbers at spawn changes nothing; only the display-side table selection does. Object `+0x18`/`+0x1A` are TILE-bank attributes, not anim selectors.

> **Incident** (`docs/game/gotchas.md` › *Anim numbers: facing adds 0x300; set-anim QUEUES, display resolves*):
>
> `jsr $4CE2`-family set-anim helpers add 0x300 to the anim number when the
> facing bit ($70) is set, then queue (number, params) into the command
> ring at a5-0x71F2 (writer 0x31DA). The number→record-strip resolution
> happens LATER in the display processor via per-char strip tables (the
> `movea.l #T,a0` site family from the overlay work) — so patching bank
> fields or numbers at spawn/first-tick does NOT change which strip is
> walked; only the display-side table selection does. Object +0x18/+0x1A
> (0x0000/0x4000/0x6000 | 0xE000) are TILE-bank attributes, not anim-table
> selectors.

**[VSE-27]** **The drawer**: object `+0x1C` → node → node+4 → the SPRITE LIST; the list's TYPE word (even, a byte-granular index) selects a handler from a table whose entry 0's offset IS its size — it cannot grow in place and cannot be relocated (`(d8,PC,Xn)`). vsav has six types, vs2 seven; type 12 (composite) does not exist in vsav and jumps off the table (`sprite_lists.md`).

> **Incident** (`docs/game/atlas/sprite_lists.md` › *The table length is SELF-ENCODING*):
>
> Handler code begins immediately after the last entry, so **entry 0's own
> offset is the table size**:

**[VSE-28]** **Types 4, 6 and 8 bias every emitted tile code by a GAME-SPECIFIC constant (vsav `+0x3800`, vs2 `+0x4200`) — one byte in an otherwise byte-identical routine.** Ported vs2 list data through vsav's handler addresses tiles `0x0A00` too low and draws whatever is there. "255/256 identical, the one difference must be a relocated address" is the trap.

> **Incident** (`docs/game/atlas/sprite_lists.md` › *4. THE GAME-SPECIFIC CONSTANTS (the trap)*):
>
> vsav and vsav2 do **not** interpret the same list data identically. Every
> emitted tile code is biased by a constant, and the constant differs:

**[VSE-29]** **Bank attribution is per-RECORD and per-LIST-TYPE, never per-character**: types 0/2/8 take the bank from the object's `+0x18`; type 4 COMPOSES its own (`ori.w #$2000`) and cannot be relocated by the record path. One effect legitimately draws from two gfx banks. "Real art from the wrong place — geometry right, content someone else's" is the signature (the sword/statue blink, the beam strip).

> **Incident** (`docs/game/engine_internals.md` › *Where the BANK comes from — and why it differs per list type*):
>
> The gfx bank lives in the OBJ y-word (bits 13-14, plus WIDE's bit 12). Two
> handlers source it two different ways, and this decides whether a
> tenant's art can be relocated at all:

**[VSE-30]** **Every list handler debits its declared budget from the frame's shared sprite budget and skips the WHOLE list when short** — effects vanish rather than degrade under pressure, and a changed budget word flips borderline skips on crowded frames into a one-byte work-RAM divergence. Replaced records keep the host's budget word.

> **Incident** (`docs/game/atlas/sprite_lists.md` › *2. The per-list budget*):
>
> Skipping is all-or-nothing per list, so budget pressure makes whole pieces
> of an effect vanish rather than degrade. `docs/game/gotchas.md` records the
> coupling between this budget word and a one-byte work-RAM divergence.

**[VSE-31]** **OBJ record formats differ in ENTRY STRIDE** (format 2: 4-byte `(tile, attr)` entries, count at +4; format 0: 2-byte tile-only entries, count at +2, one attr in the header) and **loop-count idioms differ per handler** (`subq` before `dbra` = count, else count+1). Decode EVERY handler's layout before writing a walker; every data-rewriting pass gets an output-side re-parse that must reproduce the source-side counts.

> **Incident** (`docs/game/gotchas.md` › *OBJ record formats differ in ENTRY STRIDE, not just header meaning*):
>
> Format 2 records: (tile.w, attr.w) 4-byte entries, count at +4. Format 0
> records: tile-only 2-BYTE entries, count at +2, a single attr in the
> header. A unified 4-byte walk "works" — the validation happens to pass —
> but remaps only every other tile of format-0 records. Symptom: sprites
> with ALTERNATING correct/garbage tiles (the character-select blink,
> playtest round 4, 2026-07-28). Rule: when a structure is
> format-dispatched (jump table), decode EVERY handler's field layout
> before writing a walker; two formats sharing a header shape is an
> assumption, not a fact.

**[VSE-32]** **Record walks that follow POINTERS miss OFFSET-COMPUTED records** (aux table + index×4): they ship with unremapped tile words and uncopied art. Tell: native and ported OBJ dumps showing IDENTICAL raw codes at the same pieces. Sweep every even offset in both walks with identical rules.

> **Incident** (`docs/game/gotchas.md` › *Record walks that follow POINTERS miss offset-computed records*):
>
> The electrocute X-ray overlays (and by implication other aux-chain
> display records) are located by arithmetic (aux table + index*4), not
> by any in-region pointer — a pointer-following walk never visits them,
> so they silently ship with UNREMAPPED tile words and UNCOPIED art. The
> tell in the data: NAT and POR OBJ dumps showing IDENTICAL raw code
> values at the same pieces (a ported record should differ by the remap
> delta). Fixed with a validated every-even-offset sweep in BOTH walks
> (obj_records + gen) — the sweep MUST use identical rules on source and
> output or the parity check trips on its own remapped values (band
> window widened to cover src+dst). Also: never run pixel probes in
> parallel with a running battery — three concurrent MAME instances
> flaked a replay timeline into a different attract phase; standalone
> reruns are the only trustworthy probe results.

**[VSE-33]** **A multi-tile sprite walks `tile = base + row*0x10 + ((base + col) & 0x0F)` — the column wraps within the base's row of 16**: expand `w×h` from every base in any inventory, and any relocation must be 16-ALIGNED. Dumps report the BASE code only.

> **Incident** (`docs/game/atlas/sprite_lists.md` › *5. Multi-tile sprites*):
>
> — the column index **wraps within the base's row of 16**. Two consequences:
> any tile-inventory work must expand `w×h` from the base (a base-only census
> is how the 214+P ground explosion kept drawing a solid block), and any
> relocation of such art must be **16-aligned** or the wrap breaks.

**[VSE-34]** **The per-character OBJ bank word is NOT display-only** — changing a row perturbs GAME STATE (work RAM diverges at frame 890 on an emulator with no extended-bank support). Treat it as behaviour-bearing.

> **Incident** (`docs/game/gotchas.md` › *The per-char OBJ bank word is NOT a display-only attribute*):
>
> The per-character OBJ bank table (`PRG:0x282D4`, opcode/decrypted view,
> 0x18 word rows of 0x0000/0x2000/0x4000/0x6000) looks like a pure
> "which gfx bank do this character's tiles live in" display attribute. It
> is not: changing a row perturbs GAME STATE. Measured — the same modified
> program run under MAME, which has no extended-bank support whatsoever,
> diverges in work RAM at frame 890 (FBNeo diverges at 894 on the same
> replay). So the word is read on some logic path as well as the sprite
> path. Anything that repoints a character's tile bank must expect, and
> account for, a behavioural change — it is not a cosmetic edit.

**[VSE-35]** **A character's band is NOT free once the character is replaced** — system content references tiles inside per-character bands (the VS-fade curtain columns). Audit actual vanilla references into a target window; and the electric-hit DARKEN extends the list into never-rewritten TAIL buckets, trusting long-ago content — a screen that leaves non-dark pieces there garbles it, a change that empties them removes it.

> **Incident** (`docs/game/gotchas.md` › *"This char's band is free once the char is replaced" — NO: bands hold SYSTEM-REFERENCED tiles too*):
>
> The session-14 tile placement assumed Jedah's OBJ band (0xAD80-0xEEBB)
> was writable once Donovan replaced him. FALSE: vanilla system content
> references tiles inside per-char bands — measured: the VS-fade curtain
> columns draw code 0xC625 (soft smoke art in vanilla, Donovan body
> chunks on the build), displayed during electric holds. Any future tile
> placement must AUDIT actual vanilla references into the target window
> (not just "whose band is it"), and the round-27/28/29 garble odyssey is
> the cost of skipping that audit: five wrong models (stale buckets,
> phantom clear, script order, phase artifacts, missing darken) before
> the vanilla CONTROL RUN — always run the vanilla control FIRST when a
> visual differs; it would have ended this in one session.

**[VSE-36]** **OBJ RAM diffing traps**: entries relocate between frames ("who writes offset X" is per-frame only), stale entries past the terminator render again when a composition extends the list, and 32-bit OBJ writes must be logged as longs or the code word hides in the untruncated half. Effect windows can be ~10 frames — sample ODD frames too, and check the list extent includes the buckets at the sampled frame.

> **Incident** (`docs/game/gotchas.md` › *OBJ-RAM diffing: entries move every frame, stale tails linger, dumps and taps CAN legitimately disagree*):
>
> Three traps from the Victor-shock investigation (session 14z-6):
> (1) sprite-list entries relocate between frames — "who writes offset X"
> is only meaningful frame-by-frame, and content seen at X may have been
> written there thousands of frames ago (the c625 curtain column was an
> intro-time leftover exposed mid-match by a longer list);
> (2) the region past the active terminator holds STALE entries that
> render again the moment a composition extends the list — garble that
> looks like bad tiles can be perfectly-good OLD entries;
> (3) tap_writes originally logged data as %04x — 32-bit moves (the
> common way OBJ entries are written) truncated to the LOW word, hiding
> the code word entirely (fixed: %08x). Grep for a 16-bit value must
> account for it appearing in either half of a long write.

**[VSE-37]** **To identify what an effect draws, diff the OBJ list before vs during, then join the two legs by TILE CONTENT — never by tile index, and never per-frame across legs that drift in phase.** A "constant delta" between two dense code sets is a statistical artefact until content confirms it (`+0xA220` matched 41/88 by chance); and "a uniform delta means arithmetic, not garbage — check the ART before calling it wrong" (the child shadow's band was correct, its core was the empty tile).

> **Incident** (`docs/game/engine_internals.md` › *Joining two legs' art by CONTENT (measured 14z-70e)*):
>
> **Method, promoted:** to identify what an effect draws, diff the OBJ list
> before vs during, then join the two legs by TILE CONTENT — never by tile
> index, and never per-frame across legs that can drift in phase.

**[VSE-38]** **THE ANCHOR METHOD for "this effect does not draw"**: start from the data the effect is FORCED to read (its sprite list), read-watch it on the native leg (the registers hand you the emitter PC, the object, the owner, the OBJ target), watch the ported twin, and walk one link back at a time on BOTH legs. Self-correcting: an anchor never read on our leg IS the finding. Before attributing a symptom to any code, put an execution breakpoint on it and confirm it runs — co-location is not causation.

> **Incident** (`docs/game/engine_internals.md` › *THE ANCHOR METHOD — how to attribute any "this effect does not draw" (14z-70, maintainer-endorsed; use this FIRST)*):
>
> Do not start from object layout, pool slots, or which region the machine
> lives in. Start from the **data the effect is forced to read**, and let
> the registers hand you the object:

**[VSE-39]** **Grouping by SYMPTOM sends the search after a single root that may not exist**: the four "effect does not draw" members shared three causes (a stub class row, a missing list type, a code bias) and one stood apart (an uncopied inventory). Test a symptom grouping member by member, cheapest first.

> **Incident** (`docs/game/engine_internals.md` › *The beam / effect family — four members, three stacked causes (closed 14z-71)*):
>
> > **All four are closed, and NO TWO SHARED A CAUSE.** The family was
> > grouped in 14z-69 as "one root — one port covers it". That was RIGHT for
> > three of the four, and the exception is the interesting part:
> > the **214 explosion** was an uncopied tile inventory; the **beam** and
> > the **ES big beam** were a stub effect-class row + a missing sprite-list
> > type + a per-game code bias; and the **grab lightning** shares the
> > beam's first cause — the dead effect-class row 16 (maintainer A/B:
> > hui17 none, hui18 yes, and hui18 differs by exactly that repoint). So
> > three of the four DID share a root; only the explosion stood apart.
> > Grouping by SYMPTOM
> > ("this effect does not draw") sent the search after a single root that
> > did not exist.

## C.5 Combat: damage, the judge, reactions, capture

**[VSE-40]** **Two parallel damage APPLIERS (fighter-hit stager, object-hit applier called by 54/78 per-hit reaction handlers) feed one scaler chain**: attack class × attacker stat table (byte-identical across games), the damage-level config, a random spice pass, a minimum floor of 1 and cap `0x7F`, then defender table → combo tables → low-HP rally → a 2D final map. Class-2 rows cap at 2 by DESIGN — small-tick beams are 1-2 HP on both games. Staging goes through A5 work vars (the generation-shifted family, [VSE-4]).

> **Incident** (`docs/game/engine_internals.md` › *The DAMAGE pipeline: two appliers, one scaler chain (14z-85e/85f, measured on Phobos' FINAL GUARDIAN; twins verified in both engines)*):
>
> **Two parallel damage APPLIERS feed one staging protocol** (all
> addresses vsavj; vs2 twins in parentheses, verified instruction-
> parallel):

**[VSE-41]** **THE ROUND JUDGE KILLS ON THE SIGN OF WHITE HP (`+0x52`), never `+0x50`** — both appliers subtract from both words and white sits at or below hp, so white crosses zero first; a state with `hp < 0` and `white >= 0` is UNJUDGEABLE and the round never ends until an engine failsafe (~8,000 frames). No legacy path produces it; a ported init that writes `+0x50` directly can. The phase machine is a jump-table CURSOR; several outer modes each own one — do not conflate their handlers (`ram.md` `+0x52`).

> **Incident** (`docs/game/engine_internals.md` › *THE ROUND JUDGE: death is the SIGN OF WHITE HP, and the phase machine that consumes it (14z-98, measured end to end on #103)*):
>
> **Why testing white alone is sound (the invariant):** both appliers
> subtract the staged damage from BOTH words (`0x18AB0`: real from
> `$FF3442`, white gets real + the `$FF3444` extra), and white sits AT
> OR BELOW hp, so white crosses zero first. The death decision runs on
> white right after the subtract (`0x18A42-0x18A66`): `< 0` -> the KILL
> COMMIT `0x18A7C` (`hp := -1, white := -1`, death flag `+0x11F := 1`);
> `0 < white <= $138(a1)` -> the near-death commit `0x18B12` (also sets
> `+0x11F/+0x117`, writes `+0x54` from attack byte `$17(a3)`). Measured
> live on an arcade KO: applier writes hp 17->6 / white 15->**-3**, then
> `0x2980A/0x29810` write both `-1` in the same frame. The no-kill
> attack flags are `$8(a3)/$9(a3)` bit 7 (clamp real/white at the floor
> instead of killing).

**[VSE-42]** **The victim's reaction class byte (`+0x54`, from the hit record) indexes a pc-relative word jump table that vsav ends EARLIER than vs2's** — a vs2-extended class over-indexes into code. vs2's table carries ALIASES (the remap licence: vsav's electric-shake entry is a structural twin of vs2's extended handler minus one exemption). Handlers end in the property byte map → the common install.

> **Incident** (`docs/game/engine_internals.md` › *The DAMAGE pipeline: two appliers, one scaler chain (14z-85e/85f, measured on Phobos' FINAL GUARDIAN; twins verified in both engines)*):
>
> **The victim-side REACTION CLASS dispatch (14z-85g(2), measured):**
> after the appliers, the victim's reaction is chosen at `PRG:0x2384E`:
> `move.b (0x54,a6),d0; add.w d0,d0; move.w (0x2385C,pc,d0.w),d1;
> jmp (pc,d1)` — the class byte (copied from the hit record, byte **+0x17**
> of the 0x20-stride hitbox/hitbox_proj records — see "Hitboxes and attack
> records"; the shipped Huitzil rows at `hitbox_proj +0x17D/+0x19D` are
> +0x17 of projectile records 5 and 6)
> indexes a PC-relative
> word jump table. vs2's twin (dispatch 0x2237A, table 0x22388) has
> 0x54 entries; **vsavj's table ends earlier — any vs2-extended class
> (0x4E+) over-indexes into code bytes** (the Donovan 421P/column class,
> 14z-33/34; the trap dome's class 0x52, 14z-85g(2)). vs2's table
> carries ALIASES (0x52 ≡ 0x06 ≡ 0x38 → the shock install 0x22656),
> which is the remap licence: vsavj entry[0x06] = the native
> electric-shake 0x23AC8, a structural twin of vs2's 0x52 handler minus
> the attacker-freeze exemption (vs2 skips the attacker's 0x0B when the
> "attacker" is a mine). The handlers end in property[class] (the
> 0x28D00/0x27FD8 byte map — property 0x0F = electric) → the common
> install (vsavj 0x27EC0 ↔ vs2 0x27114). Atlas rows: victim `+0x54`
> class, `+0x5C` freeze, `+0x07` seq sub-state (4 = shock), attacker
> link `+0x32`.

**[VSE-43]** **In the hit-spark spawner `a1` is the VICTIM and `a6` the attacker**; a thunk gating on `$382(a1)` gates on the victim and never fires. Multi-hit dedup keys on the hit id vs the victim's recent-hit ring; the combo counter is incremented by REACTION handlers, not the appliers.

> **Incident** (`docs/game/gotchas.md` › *In the engine hit-spark spawner, a1 is the VICTIM, a6 the attacker*):
>
> The shared spark spawner (vsavj 0x18EFC, vs2 0x178C2 twin) reads the
> attack record via a3 and checks `$54(a1)`/`$382(a1)` — but a1 is the
> DEFENDER (reaction-side remaps; vs2's char specials 6/0x10/0x11 there are
> victim-specific spark handling). The attacker is a6. A thunk gating "is
> the attacker Donovan" on `$382(a1)` silently gates on the victim and
> never fires (cost a build-and-measure round; measured live: a1=ff8800
> victim, a6=ff8400 attacker, bp at the spawn-mark thunk).

**[VSE-44]** **Capture: ONE anim node of the ATTACKER supplies both the victim's position keyframe and its pose index; the index is per VICTIM and its convention is SHARED between engines** (Bulleta 12/12, Victor 6/6 on both). The keyframe block is per-ATTACKER, and its first 32 words are a per-VICTIM offset table indexed UNMASKED — every vsavj block aliases its variant half onto the base half (fourteen by offset, two by materialised copy), so a variant-id victim takes the base character's keyframes AND record index: "half right, half a knocked-down sprite, very horizontal". Compare `dx = p2x − p1x`, never absolute x — the cross-emulator camera shift cancels only in the relative measure.

> **Incident** (`docs/game/engine_internals.md` › *THE CAPTURE-POSE INSTALLER (14z-99, measured on Victor's 6+HP grab)*):
>
> So **the first 32 words of every attacker's keyframe block are a
> per-victim offset table, indexed by the victim's char id UNMASKED** — and
> in vsavj **all sixteen blocks alias their variant half onto the base half**:
> fourteen by OFFSET (rows `0x10-0x1F` are word-copies of `0x00-0x0F`) and
> two — Zabel `0x04` and the special slot `0x0B` — by MATERIALIZATION (32
> distinct offsets whose variant sub-block CONTENT byte-copies the base
> sub-blocks, 15/16 rows; row `0x1F` is the known exception in both). A
> tenant victim therefore lands in the base
> character's capture sub-block and takes BOTH its position keyframes and
> its record index, which is precisely the "half right, half a knocked-down
> sprite, very horizontal" the field reported.

**[VSE-45]** **Throw arcs: the launch row comes from `table2[map1[2*subidx + d0] * 16]` writing xv/yv/xacc/gravity (16.16); vs2's `map1` carries five entries past vsavj's** — a newcomer index reads past the map into the next table and lands on a regular arc ("both grabs look identical"). Both tables are jammed in place; prefix/rows are byte-identical across games, so a full-table clone reads identical values for vanilla.

> **Incident** (`docs/game/engine_internals.md` › *Throw / physics-arc tables (14z-67, measured on the command grab)*):
>
> **vs2's `map1` carries FIVE entries past vsavj's end** (indexes
> 0x4A-0x53 -> rows 0x32-0x36; the 63214 command-grab arcs are rows
> 0x33/0x34, yv 16.0 and 20.0). On vsavj a newcomer's index reads PAST
> map1 into table2's bytes and lands on a regular-arc row — symptom:
> "both grabs look identical / the victim does not leave the screen".

**[VSE-46]** **The command-input system**: per-character eval handlers call MOTION HELPERS (`lea <steps>(pc); bra <tracker>`), tracker dispatchers of several KINDS (motion / charge / button-sequence) that are twins ACROSS engines with only the TABLES differing; the step tables are read DATA-space (the pc-relative `lea` only computes the address). vs2 RETUNED some motion tables (63214 fused vs split final step) — reconcile helpers by table content + dispatcher kind, never code similarity.

> **Incident** (`docs/game/engine_internals.md` › *Command-input / motion-tracker subsystem (session 14z-48, measured both engines)*):
>
> … nce-and-
>   continue same frame, bits B/F = diagonal-leniency classes).
>   Completion returns d0=1 to the char handler, which stamps the
>   matched command id at obj+0x106 (+0x105 = trigger latch); the
>   trigger dispatcher (0x21BFC / table 0xD7398[char]) then runs the
>   move-start.
> - **Dispatcher kinds:** several dispatcher entries exist per engine
>   (vs2 0x292A4/0x2938A/0x29422..., vsavj 0x29F4A/0x2A030/0x2A0C8/
>   0x2A128/0x2A1B4/0x2A2EA/0x2A42E) — motion vs charge vs
>   button-sequence families. The state machines of corresponding
>   kinds are proper twins ACROSS engines; only the TABLES differ.
> - **Engine-generation retune (the 14z-48 trap):** VS2 changed some
>   motion TABLE definitions vs vsavj — e.g. 63214: vsavj
>   [1,5,4,16] (final step dir+flag fused) vs vs2 [1,5,4,6,12]
>   (final step split; extra required entry) — an input-leniency
>   retune. vsavj's own HC tables serve the vanilla cast (Morrigan/
>   Lilith/Bulleta...; verified by caller scan). Ported newcomers
>   should carry vs2's exact tables via farm_port rows (vs2 input
>   feel); reconciliation of helper families MUST match by table
>   content + dispatcher kind, never code similarity (GOTCHAS).

**[VSE-47]** **A scripted motion input is NOT the move you named** — the input buffer FOLDS leading directions, a special's button must OVERLAP the final direction frames or nothing fires, and "AUTO" is AUTO-GUARD (a handicap; the human still attacks), not autoplay. Identify moves by measured EFFECTS, never by the script's input name; prove a menu selection with a snapshot.

> **Incident** (`docs/game/gotchas.md` › *vsav's AUTO is AUTO-GUARD (a handicap), NOT autoplay — and the victory portrait screen belongs to the 2P flow only (14z-99)*):
>
> **AUTO does not play the character.** The mode menu's AUTO row arms
> auto-blocking; the human still supplies every attack. Measured: an idle
> AUTO character auto-guards and deals ZERO hits over 8,000+ frames while
> the CPU chips it down (and auto-guard does not stop throws, so an idle
> AUTO character still loses). A rig that selects AUTO and then idles is a
> LOSING rig, not an autoplay rig. Prove the selection with a menu
> snapshot (the cursor lands on the gold AUTO row) before concluding
> anything about "AUTO behavior".

## C.6 The select screen, ids on screen, venue assets

**[VSE-48]** **Cell index IS character id**: the navigation routine commits the TABLE-B destination byte to BOTH the cursor cell and the id field with NO mask and NO validity check — an `0xFF` in a live row becomes id `0xFF` and indexes ~1 KB past every table. Vanilla's idiom for "no move" is SELF-REFERENCE; a generator emitting `0xFF` for empty sectors passed its own validator (`select_screen.md`).

> **Incident** (`docs/game/gotchas.md` › *An 0xFF inside a LIVE select-wheel row is committed as character id 0xFF*):
>
> (caught before shipping, 2026-08-05, 14z-60o)
> The navigation routine reads TABLE B and stores the byte with **no validity
> check**:

**[VSE-49]** **TABLE B is 32 rows and the index is unmasked, so variant-half cells are addressable by construction** — vs2's table IS the roster swap (the three vacated base cells are exactly the three characters vs2 dropped). The adjacency is HAND-TUNED: geometry reproduces at best 100/128 transitions, so new cells are AUTHORED and measured, never generated. TABLE A's nibble labelling is symmetric and needs an external fact (two recorded cursor paths) to pin `bit0=R bit1=L bit2=D bit3=U`.

> **Incident** (`docs/game/atlas/select_screen.md` › *The adjacency is HAND-TUNED — do not generate it from geometry*):
>
> So ~22% of Capcom's entries are deliberate hand choices that no simple rule
> predicts. **Adding cells means AUTHORING their rows and the neighbouring
> edits, then verifying** — `tools/select_wheel.py` checks the result
> (targets live, graph connected, nothing orphaned) and
> `tests/test_select_wheel.sh` measures it in the emulator. A generated table
> would be plausibly wrong in a way only playtesting would catch.

**[VSE-50]** **The hovered cell's UI pieces come from per-piece RECORD-POINTER arrays, 32 rows per player, P2 at `+0x80` — NOT `+0x40`, which is the variant half and only looked like P2 because it aliases.** The wheel itself is ONE static record drawn by ONE object with ONE bank word (per-entry banks are impossible); it cannot grow in place (another record follows; the coordinate list nests in the global pool) and has exactly one referrer.

> **Incident** (`docs/game/atlas/select_screen.md` › *The RECORD-POINTER array — what the hovered cell displays (14z-61)*):
>
> **This corrects an earlier reading.** `docs/game/engine_internals.md` recorded
> the P2 arrays as "+0x40 copies pointing at the same records", from a
> differential cursor dump. `+0x40` is the **variant half** (16 rows × 4
> bytes), which aliases the base half and therefore looks identical from a P2
> dump. The real player offset is `+0x80`, and the two halves are different
> things.

**[VSE-51]** **Venue-asset numerology lies**: palette index ≠ character id (the 3×3 pal-07 cell is Gallon's, not Jedah's); identify cells by MEASURING the cursor ring and colour-rendering candidate art with its live row. Cell POSITIONS cannot be read statically (drawing order ≠ cell order).

> **Incident** (`docs/game/gotchas.md` › *Venue-asset numerology: palette index ≠ character id; identify cells by MEASURING the cursor, not by suggestive constants*):
>
> The select wheel's big 3x3 cell uses pal row 07, and Jedah's vsavj
> char id is 0x07 — so it "obviously" was Jedah's medallion. It's
> GALLON's (pal indices in the wheel record are display rows; vs2's
> appended trio proves the point — Donovan's icon rides vs2 pal row
> 05, Anakaris' row). First 14z-49 attempt shipped Donovan's face
> onto Gallon's cell (with an attr+coord retune on top). The correct
> cell (Jedah's, 0xB526 at 236,57) was found in minutes once measured
> properly: (a) center the CURSOR RING's pal-1e pieces over the cell
> boxes, (b) color-render candidate cell art with its live palette
> row and eyeball it against known faces. Both checks are one dump +
> one render; do them BEFORE writing any manifest row that targets a
> "per-char" venue asset. (Bonus in the same family: vs2's gold
> "Donovan" icon guess was actually Huitzil — a color render against
> the character's design settles it instantly.)

**[VSE-52]** **There is no such thing as a free palette row on a venue screen**: venue PHASES rewrite rows on a ~15 s timer (grey over grey — invisible to sampling), fades READ BACK palette RAM to compute steps (re-asserting rows diverges their step counters in work RAM permanently), and the store tail has ~30 enumerated entry points. Prove a row free against the screen's WHOLE lifetime with a write tap, in every player configuration.

> **Incident** (`docs/game/gotchas.md` › *There is no such thing as a free palette row on a venue screen (14z-63)*):
>
> Three progressively-wrong "free row" proofs, each paid for:
> 1. "No OBJ references it" (sweeps over 3 replays) — missed that the
>    select VENUE PHASES write rows on a ~15 s timer: the accent march
>    claims the figure-family rows {0x15,0x16,0x17} (and P2's
>    {0x18,0x19,0x1A}) mid-screen. A row that held only a grey ramp all
>    session was being rewritten grey-over-grey — invisible to content
>    sampling AND to a single-frame poke-probe.
> 2. Per-frame re-assertion of stolen rows measured CLEAN on stress
>    replays but broke the legacy oracle in a subtle way: the fade system
>    READS BACK palette RAM to compute steps, so re-asserted values
>    diverge its step counters ($FF0E94/A4/B4/C4) on every transition —
>    permanently, invisibly, in work RAM.
> 3. Retargeting the writer at "the" dest computation missed: the store
>    tail (0x2AD50) has ~30 ENUMERATED entry points, many with
>    precomputed dests (bsr triplets writing base+1..3 with a1 carried).
>    Enumerate ALL branches into a routine before claiming a choke point.
> Rules:
> - Prove a row free against the SCREEN'S WHOLE LIFETIME (the timer-forced
>   maximum), with a WRITE TAP, in every player configuration — content
>   stability over samples proves nothing when writers rewrite same-values.
> - Palette RAM is not write-only to the engine: fades read it back.
>   Anything that rewrites it behind the engine's back perturbs work RAM.
> - The clean lever for venue-written rows is the VENUE JOB DATA (the
>   14z-15 script family), not the shared uploader code.

**[VSE-53]** **Palette rows `0x10+` belong to the P2 CHARACTER**: attribute a row with a ROSTER-VARIED control (a different P2), not a same-roster one — every probe with P2=Victor "matched native" because both games upload Victor identically, and a data port that "stilled the statue" deadened Victor's glow in every match (a superset violation that shipped). ROM→palette-RAM writes never transit work RAM, so the masked legacy gate is BLIND to palette edits; each needs its own static guard.

> **Incident** (`docs/game/gotchas.md` › *Palette rows 0x10+ belong to the P2 CHARACTER — attribute rows with a roster-varied control, not a same-roster control*):
>
> The 14z-18 "statue rows 0x10/0x11" attribution was wrong twice over:
> every probe match used P2=Victor, so rows 0x10/0x11 "matching native
> vs2" proved only that both games upload VICTOR identically — and the
> "statue accent family" 0x39B040 was Victor's own glow data. The
> data_port that "stilled the statue" actually deadened Victor's glow in
> every match including pure-legacy (superset violation, shipped in
> fa89812, reverted 14z-19). Two rules paid for: (1) before attributing
> a palette row/data block to a new-char object, run the VANILLA control
> (P1=Jedah cell picks vanilla Jedah with the same replay — one run
> showed the identical row-0x10 alternation) AND a control with a
> DIFFERENT P2; (2) ROM->palette-RAM writes never transit work RAM, so
> the masked legacy gate is BLIND to palette-data edits — every palette
> data_port needs its own static byte guard (test_don_accent.sh
> pattern).

**[VSE-54]** **"Slot-indexed cell" does not mean "slot-exclusive data"**: cell pokes are RAM-visible (menu objects store chain anchors in work RAM — any legacy cursor visiting the slot changes stored pointers), record budget words are globally coupled ([VSE-30]), and coordinate lists are read by OTHER screens on legacy paths (the win screen reads the "hover P2" coord list in matches with no such character). Every replaced byte range needs a legacy-read proof, run after EVERY replacement.

> **Incident** (`docs/game/gotchas.md` › *"Slot-indexed cell" does not mean "slot-exclusive data" — three surgery traps*):
>
> The select/splash record surgery tripped the masked legacy gate three
> times, each root-caused to the byte (session 14g):
> 1. CELL POKES are RAM-visible: menu objects store chain anchors in work
>    RAM; repointing a cell can change stored pointer values on any
>    legacy replay whose cursor VISITS the slot. In-place record
>    replacement only.
> 2. RECORD BUDGET WORDS are globally coupled: the OBJ emitter debits
>    each record's budget from the shared frame budget (d7); a changed
>    budget flips borderline skip decisions on crowded frames (one-byte
>    $FF811B divergence, 04_select_fuzz). Replaced records must keep the
>    HOST's budget word.
> 3. Coordinate lists can be read by OTHER SCREENS on legacy paths: the
>    win screen reads the "hover P2" record's coord list (PC 0x8C6E2)
>    in matches with no slot-0x0F character at all (322-frame position
>    divergence in 05_timeout_idle). Every byte range you replace needs
>    a legacy-read proof — the masked legacy gate IS that proof; run it
>    after every record replaced, not at the end of a batch.

**[VSE-55]** **The per-character strip zone INTERLEAVES the shared music-sequence pool**, read by the sound streamer through computed addressing that watchpoint sampling cannot see — apparent gaps are not evidence of deadness; the only space proven dead is what only a slot-0x0F in-match path can reach.

> **Incident** (`docs/game/gotchas.md` › *The per-char strip zone interleaves the SHARED MUSIC POOL*):
>
> Placing ported data into apparent "gaps" of Jedah's strip/stream area
> (0x267112-0x271CE8) broke legacy replays with sound-driver RAM deltas
> (02_demitri masked diverged at 891/1726; $FF00xx/$FF04xx/$FF06xx state,
> a fabricated stub materializing at $FF001A): the area interleaves the
> music-sequence pool that the sound streamer reads on every path, via
> computed addressing that A-register watchpoint sampling cannot see.
> Watchpoint-based "read maps" are lossy in exactly this blind spot —
> apparent gaps are not evidence of deadness. The only space PROVEN dead
> in this build is what only a slot-0x0F in-match path can reach: Jedah's
> own anim area (streams 0x248D5C-0x25004E, records 0x25570C-0x2601EC,
> attributed via vanilla-demo cursor sampling) — placement there was
> 02-masked-clean full-length.

**[VSE-56]** **The attract INTRO CUTSCENE is Jedah**: his per-character display sites execute on every legacy replay ~frame 888, and the same sites are reached in every match by shared display flows — a static repoint of "his" code is a legacy break (a hung Demitri match). Gate a site's alternate load on match-active AND a participating id.

> **Incident** (`docs/game/gotchas.md` › *The attract INTRO CUTSCENE is Jedah — per-char display sites are legacy surface*):
>
> VSAV's attract opening is Jedah's resurrection cutscene: his per-char
> display code (the strip-table `movea.l #T,a0` sites) executes on every
> legacy replay ~frame 888, long before the frozen-4278 demo divergence.
> A static repoint of those sites is therefore a legacy break even though
> the code "belongs to" Jedah. And the sites are additionally reached in
> EVERY match by shared display flows (statically poking them hung a
> Demitri match at 1857 — checksum log froze, the hang signature).
> Working pattern (session 14q, proven 02-masked-clean full-length):
> replace the 6-byte `movea.l #T,a0` with a 6-byte `jsr thunk`; the thunk
> selects vanilla vs ported T on `$FF8004.l == 0x40000` (match active)
> AND a slot-0x0F participant (`$FF8782`/`$FF8B82` char id). Legacy
> matches and the cutscene take the vanilla load byte-exactly; only
> slot-0x0F matches (always Donovan, including the attract demo) see the
> ported tables.

**[VSE-57]** **Per-slot presentation assets split three ways** (`venue_assets.md`): sprite palettes are a 32-row pointer table with an unmasked, 32-bounded consumer (one row to repoint); the select/VS palette blocks are reached through a DERIVED work var folded to 4 bits (a fold the id census cannot see) — dormant in every flow 14z-64 measured, but the arcade next-stage screen shows its signature (#100: Donovan named Victor), never reached by a rig; the HUD mugshot/name tables are 32-row aliased and unmasked (pure row work). Confirm what occupies a pool index before writing a block into a dense pool.

> **Incident** (`docs/game/atlas/venue_assets.md` › *Per-slot presentation assets — what a tenant on a variant id inherits*):
>
> **Summary: the in-match sprite palettes are clean; the select/VS-screen
> palettes are not.** The first is a 32-row pointer table with an unmasked
> consumer — repoint one row and done. The second is folded to 4 bits, so a
> tenant at `0x13` shows Victor's colours there until it is widened. That is
> cosmetic, and matches the maintainer's standing bar (imperfect art
> acceptable, mechanical soundness not).

**[VSE-58]** **The win screen draws from THREE independent per-winner tables — position (CODE words, pc-relative), palette (a pool + a per-character remap byte table read through the OPCODE view, with a 5×row MARKER in each row's last word as the self-check), and the portrait record — and the WIN QUOTE is a fourth, separate system with NO absolute pointers**: a 2D winner×loser lookup of 16-bit bank-relative offsets and pc-relative byte tables, whose first-level table's variant half is exactly aliased (every variant winner shows the base character's line). The screen shows after wins in BOTH 1P and 2P flows; rigs must end inputs at the KO and sample densely between the settle and the map screen.

> **Incident** (`docs/game/engine_internals.md` › *The WIN-QUOTE TEXT SYSTEM — fully decoded (14z-76)*):
>
> Three sessions attempted this by repointing per-character POINTER arrays.
> None of them could ever have worked: **the quote system contains no absolute
> pointers to repoint.** It is a 2D winner-x-loser lookup built entirely from
> 16-bit relative offsets and pc-relative byte tables.

**[VSE-59]** **The arcade ladder is a PAIR per rung — "fight this class, at this stage" — from two parallel 36-row tables copied into work RAM at `row = character id << 6 + venue byte`, scanned by ONE index across both until a class is free in the SOUND-STATE-FED in-use mask** (the run-to-run lottery). The venue byte is a plain byte offset, so an even value mid-group shifts the window across groups (deterministic steering, 12/12); an ODD value faults the pick itself. The stage index is not a caption — three readers act on it, and one past the family walks into the terminator.

> **Incident** (`docs/game/engine_internals.md` › *The ARCADE LADDER: who you fight next, and where (14z-94, measured on the #92 crash; decoded end to end and confirmed on screen)*):
>
> **Two parallel 36-row tables drive it.** `PRG:0x00B268` (table A) holds
> candidate CLASSES; `PRG:0x00BB68` (table B) holds the STAGE for each. Each
> row is 8 groups of 8 bytes; a row is one character's ladder and a group is
> one rung.

**[VSE-60]** **The stage-banner family is addressed from an ANCHOR that is the family's first row, not the pointer table's base** — both games number `v=0` at their own first row, so the twelve shared stages are identical at identical values and a port owes no renumber; assuming the table base invents a "+8" that does not exist.

> **Incident** (`docs/game/engine_internals.md` › *The ARCADE LADDER: who you fight next, and where (14z-94, measured on the #92 crash; decoded end to end and confirmed on screen)*):
>
> **The banner family is a run of fmt-4 glyph records**, addressed from an
> ANCHOR that is the family's first row, not the pointer table's base:

## C.7 Sound

**[VSE-61]** **The 68k side is id-only**: game code queues 16-byte entries into a ring, a per-frame pump sends ids to the sound board, and NO sample knowledge exists on the 68k. Per-node sfx: node byte +0x16 → a dispatcher that plays `row[class][node]` from per-character RECORD arrays (32 rows, variant half aliased; entry `id, alt_id, p4, p5, d3`); **id 0 is the engine's own SILENCE path**; arrays are indexed, never bounded — a replaced slot's array is both wrong AND too short.

> **Incident** (`docs/game/engine_internals.md` › *Sound subsystem: the QSound command path (session 14z-51, measured)*):
>
> - **68k side is id-only.** Game code queues `{id.l, d2.l, d3.l, pad}`
>   16-byte entries into a ring at `RAM:$FF0E0E` (0x100 entries), write
>   index word at `RAM:$FF1E0E` (enqueue routine PRG:0x31EA, a5=FF8000
>   with negative displacements). A per-frame pump transmits pending ids
>   to the sound board as 16-byte port packets (`0x618000-0x61801E`,
>   id hi/lo at +0/+2; keepalive at 0x619FFC). No sample knowledge on
>   the 68k side at all.
> - **The sound driver is a Z80** (`vm3.01/02`, 256KB banked; vs2 twins
>   `vs2.01/02`). Family-shared code head (identical to 0xD85), then
>   per-game data. It drives the QSound chip via the classic triplet
>   interface at Z80 `0xD800`→ no: **`0xD000/D001/D002`** (data hi, data
>   lo, reg#).
> - **QSound chip regs:** voice v params at reg v*8+k — k=1 start addr,
>   2 pitch, 3 phase (0x8000 = KEY-ON marker), 4 loop, 5 end, 6 vol;
>   **bank for voice v is written at reg ((v-1)&15)*8** (the +1 hardware
>   quirk). Sample address = (bank&0x7F)<<16 | start, into the 8MB
>   11m+12m image.
> - **Instrument (promoted): tests/lua/qs_sweep.lua** — replay-driven
>   venue + ring-poke id sweeps + chip-write log; parse with
>   tools/qs_analyze.py (key-on extraction with last-known reg
>   tracking). Sweeps run in TEST MODE (silent; ring index rests at
>   0x70 in both games at f1050 on replay 06). 12-frame windows
>   misattribute delayed-attack sfx — re-probe suspects with 45-frame
>   spacing.

**[VSE-62]** **`+0x382` is the character id, and on the 1P CPU flow the ARCADE LADDER writes the CPU side's next opponent there BEFORE it loads, over any forced pick**: a rig that pokes an id and lets the select screen time out into a CPU game fights whoever the ladder drew, and reads the drawn id back. Identify the loaded character by the hitbox base `+0x60` (`ram.md` `+0x382`). The 14z-87 "voice-class borrow" — a voice class reassigned mid-match — was this pick misread, and is RETRACTED.

> **Incident** (`docs/game/gotchas.md` › *+0x382 is the character id, and the 1P arcade ladder writes the CPU side's before it loads — a forced pick there does not survive a CPU flow*):
>
> The forced-pick pokes write the char id there, the TCRF cheat writes 0x18
> there, and audit_id_writers censuses it; the value held when the fighter
> loads decides the character. On the 1P CPU flow the ARCADE LADDER's pick
> (`jsr $AE7C` from `PRG:0x020704`, store at `PRG:0x0AEF6`) writes the CPU
> side's NEXT OPPONENT there before that fighter loads, overwriting any
> forced pick — so a rig that pokes an id and then lets the select screen
> time out into a CPU game fights whoever the ladder drew, and a read of
> `+0x382` names the drawn character, not the poked one. Identify the loaded
> character by the hitbox base `+0x60`. Paid for twice: 14z-87 read the
> drawn ids (0x06/0x0C/0x09/0x00 on a rig meant to be "Donovan P1", rig 90,
> which never formed its match — 14z-87b) as a VOICE CLASS the engine
> "borrows" mid-match, and the reading survived 14z-94's decoding of the
> same routine as the ladder until 14z-188 (#195) measured the store's
> timing and the load. RETRACTED with it: "a tenant's engine-voice events
> play a vanilla character's flavor". Mechanism: engine_internals "The
> ARCADE LADDER" and "The per-node sfx row is the fighter's OWN".

**[VSE-63]** **A SECOND voice family lives in the sound KERNEL**: four per-class word tables (one per voice event, a 16-entry base + a 16-entry variant copy directly after, read through the OPCODE view — they sit inside the crypt window), the event suffix literal in each id's low nibble. Silence can be the AUTHORED sound (vs2 voices the robot's hurt events with free id rows). The firing PATTERN is engine-side and victim-data-fed; the identity is the table's.

> **Incident** (`docs/game/engine_internals.md` › *The KERNEL per-class voice tables — a SECOND voice family in the sound kernel, not the 0x0BF41A record path (measured 14z-96)*):
>
> Distinct from BOTH per-node record dispatch (0x0BF41A) and the voice
> borrow: the sound KERNEL (the low-PRG region around the enqueue
> `0x31EE` / save-restore `$330E/$3306` / helper `$4CE2`) carries **four
> per-class voice-id word tables**, one per voice EVENT, each as a
> 16-entry base table + a 16-entry VARIANT table directly after it
> (reads go through the OPCODE view — the tables sit inside the crypt
> window and the data view shows ciphertext at the same offsets):

**[VSE-64]** **The `+0x300` id alias is the FACING bit and natively selects a per-facing TWIN SONG that differs only in CHANNEL ALLOCATION** — an alias is a channel choice, not sound content.

> **Incident** (`docs/game/engine_internals.md` › *The Z80 command dispatch, the note-table array, the dead type-C song class and the alias bit (measured 14z-86, the voice batch)*):
>
> … s use it): header byte0 = 0x80|voice → a FLAT
>   11-byte one-shot format parsed at 0x0311: [80|voice][priority]
>   [→ix+06][→ix+05][→ix+09][→ix+08][pitch via 0x34F1][sample# BE →
>   ix+2F/2E][b9,b10 → ix+14/15 pitch base]. **Proven EXECUTABLE by
>   authored probe** (14z-86: a hand-crafted row keyed the exact record
>   with the same keyon tuple as the multi-track version). Kept as a
>   capability reserve — the batch shipped verbatim multi songs instead.
>   Related: the note-on resolver at 0x0D0A treats ix+$2F bit7 as a
>   dual-mode switch (set = (table,entry) indirection, clear = RAW
>   sample number).
> - **The +0x300 id alias is the FACING bit** (`btst #0,$70(a6)` — the
>   same helper idiom id_space.md documents as facing) and natively
>   selects a per-facing TWIN SONG: measured over the 81 scoped voice
>   pairs, 74 differ ONLY in the channel-slot word, 6 are identical, 1
>   other — the alias is CHANNEL ALLOCATION, not sound content. The
>   voice batch skips it for the authored range 0x58-0xA6 (a range-gated
>   thunk clone of the helper at PRG:0x5FFF00) because only 38 free
>   (base, base+0x300) row pairs exist against 79 voices; kept vanilla
>   ids keep vanilla aliasing through the thunk's else-branch. Deviation
>   surface: simultaneous same-voice triggers share a channel (restart)
>   instead of layering on two.
> - **Song extents**: songs are stored contiguously; a song's length =
>   the gap to the next song start (sorted id-table addresses). Verified
>   batch-wide: no track stream overruns its extent.
> - The keyon-window disciplines: qs_sweep IDLIST mode takes STEP (the
>   12-frame default is attack-window-blind), qs_analyze takes the
>   window as its 3rd arg, and per-id window attribution is VENUE-FLAKY
>   for delayed keyons — batch A/Bs compare WHOLE-RUN (voice, length,
>   content) multisets instead (tools/check_qs_voice_batch.py; a
>   signature ours-only whose content exists in vs2's library is a
>   priority-suppressed track echo, measured moving with injection
>   timing).

**[VSE-65]** **The Z80 driver is NOT encrypted, and its 24-bit logical addresses are FLAT member-concat file offsets** (fixed region below `$8000`, banked window above, bank hardware-masked to 4 bits). Everything derives from a fixed-ROM anchor block: id table (4 B per id, a 24-bit song address, `addr-hi == 0` = a FREE no-op row — so a song below the first bank boundary is UNREACHABLE), sample-record table (8 B: bank, start, loop, end, transpose — the bank field is a full byte), the note-table pointer ARRAY selected by stream command `1F` with an UNBOUNDED byte (vs2 has one more slot: its VOICE table). The id space WRAPS mod the table size; "`0x700+` = music" is a 68k-side convention only.

> **Incident** (`docs/game/engine_internals.md` › *The QSound Z80 driver: id table, songs, streams, sample records (measured 14z-86, reader-traced on live vsavj, id 0x119)*):
>
> **The Z80 is NOT encrypted** (RETRACTS 14z-85d "KABUKI-encrypted").
> Proven three ways: file bytes at PC 0x1E82 and 0x0271 equal the traced
> instructions verbatim, and MAME's cps2 config maps AS_OPCODES only for
> the 68k. KABUKI is the CPS1-QSound generation. Static disassembly of
> the member works directly (`dasm <f>,<off>,<len>,1,:audiocpu` in the
> MAME debugger — the device is the FIFTH param; fourth is a bool, and a
> device in slot four fails silently). The "garbage" that suggested
> encryption was the wrong-offset reads above.

**[VSE-66]** **Stream grammar**: bytes `< 0x20` dispatch through a 32-entry pointer table (`08 n` = SAMPLE SELECT through the note table; `16` = a signed 16-bit stream JUMP; `17` = end-of-track, no operand; `1F n` = note-table select); `>= 0x20` are wait/sustain events. The two games' interpreters are byte-identical but for two envelope-base immediates — the licence for verbatim stream copies. A third one-shot song class exists, executable, and is dead code in both games. Songs are stored contiguously (length = gap to the next start).

> **Incident** (`docs/game/engine_internals.md` › *The Z80 command dispatch, the note-table array, the dead type-C song class and the alias bit (measured 14z-86, the voice batch)*):
>
> - **The real command dispatch**: the fetch loop at 0x1166 reads a
>   byte; ≥0x20 RETURNS to the tick path (a WAIT/sustain event); <0x20
>   dispatches via the pointer table at **0x1186** (32 × 2B). Operand counts (both games, byte-identical
>   interpreters): 00-03 zero-op flag toggles (ix+$04 bits), 04/05 two
>   ops, 06-11 one op, 12-15 zero (read track state not stream), **16 =
>   16-bit signed STREAM JUMP** (loops), **17 = end-of-track, no
>   operand** (the "17 30" reading of 14z-86 morning was the end marker
>   plus the NEXT song's priority byte), 18 pan/level, 19 volume, 1A-1E
>   one op (xlates 0x38F1/0x39F1/0x37F1 etc.), **1F = note-table select**.
> - **cmd 1F indexes the pointer array at $3B04 with an UNBOUNDED byte**
>   — vsavj has SEVEN slots (0x3B12…0x455A), **vs2 has EIGHT: slot 7 is
>   its VOICE note table**, which is why every voice song runs `1F 07`
>   and why vsavj cannot resolve them natively. No phantom index (7-255,
>   the out-of-array reads land in table data) yields a pointer into
>   authorable space — measured exhaustively. The port's answer:
>   RELOCATE table 0 byte-identically (repoint the $3B04 word) and write
>   the vacated word at the old table-0 base as the 8th slot pointer →
>   an authored voice table in the fixed-ROM free run. … *(the paragraph continues in the origin doc)*

**[VSE-67]** **For the shared sfx library the two games use IDENTICAL ids keying the SAME sample content** (relocated in the image); a 0x7xx id's faithfulness is a property of its sample CONTENT, not its number — content-search the host's image before declaring a sound absent. Key-on attribution windows are venue-flaky for delayed keyons: compare WHOLE-RUN (voice, length, content) multisets, and a 12-frame window is attack-window-blind.

> **Incident** (`docs/game/engine_internals.md` › *The shared sfx library uses IDENTICAL ids in both games (the id-space sweep, `docs/project/m5/keyons_*.json`)*):
>
> Sweeping ids 0x000-0x7FF on both games (2048 pokes each): 1613 vsavj /
> 1370 vs2 ids key voices. **For the shared sfx library the two games
> use IDENTICAL ids** — vs2 0x136/0x137/0x13d/0x142/0x146/0x112/0x156/
> 0x157/0x158/0x15a/0x18b/0x18d/0x299/0x2d4 all exist on vsavj as the
> SAME id keying the SAME sample content (relocated in the image;
> content-verified). (The 214P/214K music bug was root-caused 14z-52 — STATE_HISTORY "M5 phase
> 1: music bug root-caused".)
> vs2-ONLY samples (absent from vsav's 8MB — Donovan voice/new sfx):
> ids 0x71d, 0x73e, 0x753, 0x754, 0x755, 0x756 (+0x14a and 0x173 are
> same-id-different-content — vsavj reuses those ids for other sounds).
> 0x747 keys nothing in either probe so far (needs params or longer
> window). Sample ROMs are FULL (no blank 64K blocks), which is why the WIDE profile
> carries a 16 MB QSound region (`../project/cps2_wide.md`) and the M5 voice
> batch (14z-86, "The QSound Z80 driver" below) is authored into it.

## C.8 Modes, servants, exceptions

**[VSE-68]** **DARK FORCE COSTS ONE BANKED STOCK (`+0x109`)**; with an empty meter the P+K pair is DOWNGRADED to a single button (`+0x107` = `0xFF/0xFE`) and `seq 0x0A` is that downgrade, NOT Dark Force. Every DF measurement for three sessions was of a match that never entered the mode. The match-level DF flag is `$FF802E` — derived by dumping all of work RAM at five phases on both games and keeping only bytes that are off/off/on/on/off with identical values; every "DF flag" inferred from the fighter block by inspection was set by JUMPING (`ram.md`, gotchas "A MODE-gated symptom").

> **Incident** (`docs/game/gotchas.md` › *A MODE-gated symptom needs the MODE PROVEN ENTERED — pressing the input is not entering it (14z-69, cost this session twice)*):
>
> Dark Force costs one banked stock. With an empty meter the P+K pair is
> DOWNGRADED to a single button and the match continues normally: the
> tells are `+0x109` (banked stock) staying 0 and `+0x107` reading
> 0xFF/0xFE. **`seq 0x0A` is that downgrade.** Every DF measurement from
> 14z-66 through 14z-68 was taken on replay 82, which has no stock — so
> none of them were of Dark Force, including a gate that asserted "DF
> activates, expires, re-activates" and the claim that DF mechanics are
> already native-correct.

**[VSE-69]** **The two engines run DIFFERENT Dark Force systems, and P+K selects a different one on each**: vs2's P+K is Dark Force POWER (two stocks, no startup invincibility, a global buff; seq 0x16 cleared the same frame), vsav's is Dark Force CHANGE (one stock, the per-character handler dispatched on seq 0x16: the startup window and the form). vs2 did NOT drop the newcomers' Change handlers — their vs2 EX moves (the "personal" Dark Force) still reach them through vs2's own Change entry, at a fixed longer period — so a newcomer's Dark Force is compared against its vs2 EX move, never against vs2's P+K (Huitzil's flight mode IS Ray of Doom). Palette sequences are ANIMATION DATA driven node by node through a global id-indexed row table whose two games are NOT row-aligned (uniform +8 shift from a point), resolved by an API reachable only through the channel machine's program-byte dispatch.

> **Incident** (`docs/game/engine_internals.md` › *The two engines run DIFFERENT Dark Force systems (traced 14z-69c)*):
>
> The two engines run DIFFERENT Dark Force systems, and the tenant is
> caught between them. P+K selects vs2's Dark Force POWER and vsav's Dark Force CHANGE; the
> newcomers' Change handlers stay reachable in vs2 through their EX moves (measured
> 14z-168 — "Dark Force POWER, Dark Force CHANGE, and the newcomers' personal Dark
> Force" below), so a newcomer's Dark Force is compared against its vs2 EX move.

**[VSE-70]** **Which DF palette-seq ids belong to whom cannot be derived from the per-character routine table** (rows sharing one routine request different ids; at least some arrive by another path) — it was MEASURED per character on vanilla with the DF flag asserted; Anakaris never entered DF and his block is INFERRED from the seventh hardcoded base. "No character requests id N" does not make row N free: establish what the bytes ARE. The resolver's reachable window is bounded by its own arithmetic.

> **Incident** (`docs/game/engine_internals.md` › *THE DARK FORCE PALETTE-SEQUENCE BLOCKS — measured census (14z-79b)*):
>
> **WHY THIS CANNOT BE DERIVED FROM TABLE `0x02A8A4`.** The obvious model — row
> per character, each pointing at a routine with one hardcoded base — is WRONG.
> Rows `0x02-0x07`, `0x09`, `0x0D-0x0F` all hold `0x0040` and reach the SAME
> routine at `0x02a8e4`, yet `0x04` requests `0x44-0x47` and `0x02/0x03/0x05/0x07`
> request nothing. That routine is conditional (`cmp.b (0x14f,a6),d0 / bne.w
> 0x030ee8`) and at least some ids arrive by another path entirely. A static
> reading of the table produces a confident and wrong map.

**[VSE-71]** **Shadow/reflection SERVANTS (a class-`0x0C` trio per player) mirror the owner's animation by reading each node's +0xC word (low 13 bits) into SHARED tables of fixed row space** — an out-of-range seq over-indexes into sequence data. The tables are the same size in both games (+2 entries), and capture supers put a VANILLA victim's servant through attacker-supplied seq ids — a clamp must be UNGATED by character. The servant path takes zero hits while a companion's shadow draws: the companion's shadow is the piece family, not this path.

> **Incident** (`docs/game/engine_internals.md` › *Shadow / reflection servants (14z-66; premise CORRECTED 14z-68f)*):
>
> Per-player shadow servants (class-0x0C trio, vanilla spawner
> `0x489DE`+) mirror their owner's animation by reading each anim NODE's
> `+0xC` word (low 13 bits = a seq id) into SHARED tables:
> - installer vsavj `0x823E2` / `0x823F2` -> table `0x2083BC` or
>   `0x2087CA` (chosen on `+0x38`), stored to `+0x40(a6)`;
> - the walk re-reads on seq CHANGE only (`cmp.w $50(a6),d0; beq`) and
>   jumps the walker at `0x8245C`.

**[VSE-72]** **THE LEAPING PURSUIT is vsav's own** (U + any button on a knocked-down opponent): the command registers during the FALL and the first flat frames only, is button-independent, and aims at the victim's position at INPUT time; corner pushback shoving the attacker off is vanilla; the auto-wake races the flight time.

> **Incident** (`docs/game/engine_internals.md` › *THE LEAPING PURSUIT ATTACK (measured 14z-104, maintainer-confirmed mechanic)*):
>
> vsav retains Night Warriors' pursuit: with the opponent knocked down,
> U + any single P/K leaps onto them (ES variant on two buttons, meter).
> Measured on the merged build's legacy pairings (= vanilla by the
> superset invariant), rig `tests/replays/judge/03_down_attack.rpl`:

**[VSE-73]** **The game installs REAL handlers on every 68k exception vector**: each writes its identity to `$FF0000.w` (vector − 2), saves D0-A6 ascending from `$FF0018` and SP at `$FF0054`, then SOFT-boots — the abbreviated white check list and the NAME SCREEN. The gold full RAM test is the cold/watchdog path. So on bare hardware the reboot STYLE is the first instrument, and the register block is a free post-mortem — written only if the handler RUNS (a frozen machine leaves it stale).

> **Incident** (`docs/game/engine_internals.md` › *CPU exceptions and the soft-reset path (14z-109)*):
>
> The game installs REAL handlers on every 68k exception vector (`vec2` bus
> error through `vec11` line-F; handler ladder at `PRG:0xC0-0x14E`). Each
> handler:

**[VSE-74]** **The object-script state dispatchers (three siblings, 80-entry tables, ~0x17 distinct handlers in ONE pool, guard-chain fall-through) read the next-state index from the DATA NODE's +0x17 with NO bounds check** — an out-of-range byte reads whatever words follow, and the first odd "offset" faults the `jmp` (vec3) into a clean name-screen reboot with zero corruption beforehand: a data-side bad byte presents as a "flaky reset". The walker runs with A1 = one fighter and A3 = a node that can live in the OPPONENT's data — a bad node in X's data is triggered by X's opponent, whoever that is. D1 is dead on ENTRY to every handler and live afterwards (downstream `bsr` chain) — reproduce the displaced instruction's ENTIRE effect.

> **Incident** (`docs/game/engine_internals.md` › *The object-script state dispatcher at `PRG:0x018508` (14z-109)*):
>
> The offset table holds **80 entries** (`0x018510 + 80*2 = 0x0185B0`; valid
> indices `0x00-0x4F`), aliasing onto ~0x17 distinct handlers
> (`0x018694-0x01877c`; several write follow-up states into `(0x54,A1)`).
> **CORRECTED 14z-110: this section originally said "~0x26 states", conflating
> the ~0x26 distinct HANDLERS with the 80-entry TABLE. The crash is a TABLE
> overrun, so the table size is what matters.** This is one of THREE sibling
> dispatchers that read `(0x17,A3)` — see "The SUB-STATE DISPATCHER FAMILY at
> 0x018460": `0x018460`/`0x018508`/`0x0185D2`, all 80-entry, reached by
> guard-chain fall-through. **vs2's twin tables (`0x016D34`/`0x016DE4`/
> `0x016EB6`) have 84 entries** — so the RENUMBER GAP is exactly `0x50-0x53`:
> valid in vs2, out of range in vsavj. **There is NO bounds check on the node
> byte.** An index past the table reads whatever words follow; the first odd
> fetched "offset" faults the `jmp` with a vec3 address error, which the
> exception path above converts into a clean name-screen reboot — i.e. a
> data-side bad byte presents as a "flaky reset" with zero corruption
> beforehand. (#99 = node `0x3FB899` in Donovan's block carries vs2 state
> `0x51`; census tool `tools/audit_fsm_census.py`.)

**[VSE-75]** **CPU AI: four per-class tables of script starts, 32 longs each — 16 classes THEN THE SAME 16 REPEATED (Capcom's aliasing guard)** — so a variant class silently plays `id & 0x0F`'s AI; the interpreter is 15 nested dispatchers on a command byte, and the jump command's generic handler has 10 sub-states where a private one may have 5. CPU-side only; 2P never reads them.

> **Incident** (`docs/game/engine_internals.md` › *The CPU AI action-script system (14z-111, measured on the #99 capture)*):
>
> - **Tables.** Four per-class tables of script-start pointers, 32 longs each:
>   entries 0-15 = the 16 classes, **entries 16-31 = the same 16 repeated**
>   (Capcom's aliasing guard for ids with bit 4 set — Oboro Bishamon 0x18
>   legitimately aliases Bishamon 0x08). Consumers: `0x2CCB6` (table 0,
>   indexed by `+0x205`, writes `+0x210` and `+0x224`), `0x2CCF2` / `0x2CD40` /
>   `0x2CD9C` (tables 1-3: `+0x382<<2` row, then `jsr 0x14E8A` (RNG) `andi #$1F`
>   `+ (0x20A,a6)` picks one of 32 starts inside the row's block; write
>   `+0x214/+0x218/+0x21C`). CPU-side only (14z-98 trace); 2P never reads them.
>   *(Precised 14z-189 from the disassembly: tables 1 and 2 are two-level —
>   `move.w (a0,$205.w)` selects a sub-block, then the RNG byte (`andi #$1F`
>   `+ $20A`) indexes a byte table whose value picks a word at `+0x60`; table
>   3 (`0x2CD9C`) is NOT RNG-picked — it indexes the row's word table by
>   `$22B(a6)`. Every offset is `lea (a0,d1.w)`, i.e. SIGNED.)*
> - **The tenants' blocks are complete at the first level (14z-189, #129's
>   first question).** The three placed blocks are byte-identical to vs2's
>   (`x100000@huitzil` `0xE3C`, `x100e3c@pyron` `0xC8E`, `x101aca` `0x10CE`
>   bytes: 0 … *(the paragraph continues in the origin doc)*

## C.9 Rigs the game itself sabotages

**[VSE-76]** **A MODE-gated symptom needs the MODE PROVEN ENTERED** — assert the state (the flag, the resource consumed), never the input; take the screenshot early (DF has its own backgrounds and a cyan TIME bar); a negative result about a symptom the maintainer has SEEN is a bug in the rig until proven otherwise ("I could not reach the state", never "it does not reproduce"); and a negative result about a rig belongs to the replay that produced it.

> **Incident** (`docs/game/gotchas.md` › *A MODE-gated symptom needs the MODE PROVEN ENTERED — pressing the input is not entering it (14z-69, cost this session twice)*):
>
> Rules that fall out of this, in the order they would have saved time:
> 1. **Assert the state, not the input.** A rig that presses the button
>    proves nothing; a rig that measures the mode flag and the resource
>    it consumed cannot silently drift out of the state under test.
> 2. **Take the screenshot early.** The visual signature (background,
>    TIME bar) was decisive and free, and it is exactly what the
>    "verify at the RENDER layer" entry above already told us to do.
> 3. **A negative result about a symptom the maintainer has SEEN is a
>    bug in the rig until proven otherwise.** Report it as "I could not
>    reach the state", not as "it does not reproduce".
> 4. A negative result about a RIG belongs to the replay that produced
>    it: "the poke does not force him on vsav2" came from replay 61,
>    whose timing is authored for OUR wheel, and it blocked the native
>    leg for two sessions. Re-run it with a script whose timing is not
>    the thing under suspicion.

**[VSE-77]** **Sample a state-gated effect at the moment it gates on** — DF afterimages appear only while MOVING; the maintainer's repro steps ("move around, especially when air dashing") encode the gating and are worth asking for BEFORE measuring.

> **Incident** (`docs/game/gotchas.md` › *Sampling a STATE-gated effect at the wrong moment reads as "not reproduced" (14z-68u)*):
>
> The Dark Force afterimage/recolour was written up as "not reproduced
> on the current build" after measuring sprite counts and palette RAM
> across replay 82 at f3050-3250 — with DF verifiably ACTIVE (seq 0x0A
> confirmed). The effect is gated on the character MOVING, and that
> replay's walk is at f3300-3400. Every measurement was correct and the
> conclusion was wrong.
> Two habits: (1) when a symptom is reported for a MODE, enumerate what
> the mode gates on — active vs moving vs attacking — and sample each,
> not just "during the mode"; (2) a maintainer's repro steps ("move
> around, especially when air dashing") encode exactly that gating and
> are worth asking for BEFORE measuring, not after a negative result.

**[VSE-78]** **A WATCHDOG REBOOT masquerades as a clean "nothing happened"**: guard clean, no tripwire, structs zeroed — and the snapshot shows the boot splash. Zeroed structs at late frames are not a non-load verdict until a snapshot rules out the boot screen; a crash guard catches exceptions and tripwires, not hangs.

> **Incident** (`docs/game/gotchas.md` › *A WATCHDOG REBOOT masquerades as a clean "nothing happened" (14z-65)*):
>
> The forced-boot probe at id 0x10 on the stage-4 ladder build reported:
> guard clean, no tripwire, P1 struct zeroed at f3600 — reading like the
> char-load path politely declining. The SNAPSHOTS say otherwise: f2200
> select screen, f2900 black garbled transition, f3400 THE QSOUND BOOT
> SPLASH. The init path HANGS (no exception — nothing for the guard),
> the game stops kicking the CPS-2 watchdog, and the MACHINE RESETS; the
> "zeroed struct" is fresh-boot state.
> Rules:
> - Zeroed work-RAM structs + a clean guard at late frames is NOT a
>   non-load verdict until a snapshot rules out the boot screen.
> - The crash guard catches exceptions and tripwires, not hangs; hang
>   hunting needs GUARD_PC_LOG over the ONSET window (before the reboot),
>   GUARD_BREAK on the handler entry, or GUARD_TRACE under -debug.
> - The probe's "load ZEROS" verdict has been renamed accordingly
>   (WEDGED-or-REBOOTED); force_pick_probe now also snapshots.

**[VSE-79]** **A 1P-arcade rig is silently pinned to the ARCADE DRAW**: any timing change re-rolls its opponent and stage ([VSE-59]); a 1P-vs-CPU replay is NOT cross-leg comparable (different opponents, different stages on the two games) — author a 2P twin with both sides scripted before comparing legs.

> **Incident** (`docs/game/engine_internals.md` › *Rig facts (measured 14z-70/70b)*):
>
> **READ THIS FIRST — replay 83 is NOT cross-leg comparable.** It is a
> 1P-vs-CPU script (`sys=C1`, `sys=S1`, no C2/S2), and the two games pick a
> DIFFERENT CPU opponent and a DIFFERENT stage: at f3436 native is on the
> village stage against one character and ours is on a different stage
> against Felicia, with no explosion on screen at all. Any "ours draws
> tiles native never draws" conclusion from a frame-matched sprite diff on
> this replay is measuring two different matches. One was computed this
> session (101 our codes vs native's, zero overlap) and DISCARDED. Identify
> the effect on ONE leg by position and timing, or author a 2P replay.

**[VSE-80]** **Post-match surfaces**: coarse sampling after a round end lands on the MAP/tally screens that come AFTER the win screen; buttons pressed past the KO press THROUGH the victory surfaces. End inputs at the KO; sample densely between the settle and the next screen.

> **Incident** (`docs/game/gotchas.md` › *vsav's AUTO is AUTO-GUARD (a handicap), NOT autoplay — and the victory portrait screen belongs to the 2P flow only (14z-99)*):
>
> **The victory portrait screen shows after match wins in BOTH 1P-vs-COM
> and 2P** (field-confirmed by the maintainer and rig-reproduced 14z-99;
> the corner carries PRESS START in the 1P flavor and the loser's
> CONTINUE countdown in 2P). TWO RIG TRAPS hid it for a whole arc, both
> mine and both corrected by the maintainer:
> 1. **Coarse sampling after the round end lands on the MAP/tally screens
>    that come AFTER the win screen** — "the screen you check after the
>    round end is ALWAYS the map screen that comes after the win screen"
>    (maintainer, verbatim). Two flows were published as "never shows the
>    win screen" off exactly this: the 1P KO win and the legacy 2P win.
>    Sample the window BETWEEN the KO settle and the next screen, densely.
> 2. **Buttons pressed past the KO skip (or cut short) the victory
>    surfaces.** A mash that runs past the match-winning KO presses
>    through the win screen — measured: the same 1P KO win shows the
>    portrait screen for >=900f with inputs ended at the KO, and no
>    portrait screen at 200f sampling with the mash running. END REPLAY
>    INPUTS AT THE KO when the post-match surfaces are the subject.
> Also: in the replay-61 skeleton the 2P mode menu is up at ~f1950 (the
> "~f2800" the 14z-98 (8) notes carried is an IN-MATCH frame of this
> skeleton, not the menu).

**[VSE-81]** **Per-character timing is per-character**: reach, knockdown arcs, down windows and wake timing all differ, so a fixed-frame rig verified on one character whiffs on another; and the "static state" a classifier declares frozen is only as honest as its field tuple — diff a WIDE slice at distant times first.

> **Incident** (`docs/game/engine_internals.md` › *THE LEAPING PURSUIT ATTACK (measured 14z-104, maintainer-confirmed mechanic)*):
>
> … ictim's knockdown
>   FALL and the first frames of lying flat; a later input during the
>   flat period is ignored (a sweep victim lies only ~20-45 frames — the
>   window is genuinely brief, as players know it).
> - **Button-independent:** U1/U2/U4/U6 produce the identical leap
>   (seq 0x0E) — the strength choice is cosmetic for the standard
>   pursuit, per the universal-command design.
> - **Aim is captured at INPUT time:** the leap targets the victim's
>   position when the command registered, not at landing (measured with
>   a mid-flight victim-position poke: the arc still aimed at the
>   pre-poke spot).
> - **Per-character arcs** (tenants run their PORTED vs2 content):
>   Demitri 33-34f to y=100; Donovan 27f to y=102; Phobos 42f to y=88;
>   Pyron 39f to y=88.
> - **Corner behavior:** a pursuit at a cornered victim peaks directly
>   over the body, then the wall pushbox shoves the attacker off during
>   the descent and the strike lands beside them — measured on the
>   all-legacy control, i.e. vanilla behavior, not a port artifact.
>   **That is vsavj's rule, and vs2's differs** (14z-184, GitHub #179):
>   when both fighters land clamped at the same wall, vsavj pushes P1 out
>   and vs2 pushes P2 out — "THE PUSH-APART AT A SHARED WALL" below.
> - **The connect race:** with a sweep or throw knockdown, the victim's
>   auto-wake and the pursuit's flight time run neck-and-neck (a Victor
>   dummy woke at ~+22-45f; every rig geometry tried landed 1-10 frames
>   late or beside the body). Connecting cleanly likely needs a longer
>   knockdown than these rigs produce — carried as the pursuit-connect
>   refinement in docs/project/coverage_matrix.md. **A knockdown that does
>   connect (14z-184, #174):** Donovan's ES pursuit off **Sword Grapple
>   (63214+HP)**, pressed at +104 or +112 after the grapple's in … *(the paragraph continues in the origin doc)*

**[VSE-82]** **Player-struct bytes `$42-$45` are SHARED SCRATCH across phases** (select override state at select; unrelated ramps in match): qualify any claim about them by PHASE, or read the in-struct version of the displacement-collision trap.

> **Incident** (`docs/game/atlas/select_screen.md` › *THE RANDOM CELL `0x0B` — the cycling draw, decoded (14z-116)*):
>
> > **Caution: `$42-$45` on the player struct are SHARED SCRATCH.** The same
> > bytes are reused by in-match code for unrelated purposes — `0x0273E6`
> > writes a stepped ramp (`00 08 10 … F8`), `0x02F6D4` writes `0x28`,
> > `0x031132`/`0x03113E` write `0x80`/`0xFB`. A value of `0x28` in `$45`
> > would be outside the 5-bit id space entirely, and is harmless only
> > because the confirm path runs during SELECT, not during a match. Any
> > claim about these bytes has to be qualified by phase — reading them
> > without that qualifier is the in-struct version of the
> > displacement-collision trap.

**[VSE-83]** **The attract demo runs REAL characters** (a Jedah vs Victor demo from ~frame 4278 of the long attract), so a change to a demo-featured character legitimately alters the attract from that frame — correct superset behaviour, and expectations for it are build-dependent (`ram.md` "Attract-mode demo roster"; the full demo roster is still a TODO).

> **Incident** (`docs/game/atlas/ram.md` › *Attract-mode demo roster (superset-invariant note)*):
>
> The attract sequence includes CPU demo matches that feature real characters.
> Verified: `01_attract_long` (7200-frame attract, zero input) runs a **Jedah
> (id 0x0F) vs Victor** demo starting at **frame ~4278**. Consequence for
> patched builds: any change to a character that appears in an attract demo
> will alter that attract from the demo's start frame — this is *correct*
> superset behavior (the attract "involves" the modified character), not a
> violation. The auto-detecting regression runner must treat attract
> expectations as build-fingerprint-dependent when a demo-featured slot is
> modified. **The full attract-demo roster — MEASURED 14z-118, static + dynamic,
> gate `tests/test_attract_roster.sh`:** the assigner `PRG:0x005BEA` reads the
> demo counter `RAM:$FF1E2A` (`a5-0x61D6`), masks `#$e`, doubles, and reads an
> 8-entry x 4-byte table at `PRG:0x005C08` (P1 id, P2 id, venue.w) into the
> two id fields (`+0x382` of each player struct) and the venue word `$FF8100`. The eight, in order: Jedah `0F` v Victor `03`
> (venue `0x10`); Gallon `02` v Bulleta `00` (`0x0C`); Q-Bee `0C` v Bishamon `08`
> (`0x08`); Lilith `0E` v Zabel `04` (`0x04`); Anakaris `06` v Sasquatch `0A`
> (`0x02`); Demitri `01` v Morrigan `05` (`0x00`); Aulbath `09` v Felicia `07`
> (`0x0A`); Lei-Lei `0D` v Anakaris `06` (`0x06`). Every base id appears once per column; **no variant-half
> id can ever be featured**, so a tenant at `0x10-0x1F` never changes attract
> (dynamic: 40,000 vanilla attract frames, all eight seen in table order ~3,470
> frames apart, counter stepping by 2 and wrapping at 16 —
> `build/attract_roster_trace_14z118.log`). The "demo-featured slot" caveat
> above therefore applies only to a build that modifies a BASE id's data.)

**[VSE-84]** **A cross-game comparison needs a matched play mode and a pinned RNG** — vsav2 defaults P1 to TURBO where vsavj defaults to NORMAL (the speed level `$FF8116` decides the extra logic passes), and the two games' RNG states (`$FF80D4-D5`) differ while the RNG picks which fighter updates first on every pass. Pin both on both legs and prove from each leg's dump that the pins held; then hit counts, damage AND video-frame durations are comparable. Unpinned, counts follow each game's own draws and frame durations follow the two modes — which is what "the host engine ticks slower" had measured (retracted 14z-158). (Regional variants are a different question entirely: `vsav` and `vsavj` have no mechanical differences, so a measured one means suspect the instrument.)

> **Incident** (`docs/game/gotchas.md` › *THE ENGINE DOES NOT RUN ONE TICK PER VIDEO FRAME — a `frame_done` trace CANNOT count animation frames (paid: 14z-125b, measured)*):
>
> A CROSS-GAME COMPARISON NEEDS A MATCHED PLAY MODE AND A PINNED RNG — vsav2 defaults P1 to TURBO where vsavj defaults to NORMAL, and the two games' RNG states differ (paid: 14z-127 as "the engines tick at different rates"; corrected 14z-158, GitHub #135, #142)
>
> **The rule.** vsav2 and vsavj run the same pass decider and the same speed-level pattern table,
> but at character confirm vsav2 sets P1's play mode to TURBO (speed level `RAM:$FF8116` = 8) and
> vsavj to NORMAL (level 6), and on every measured frame their RNG states (`RAM:$FF80D4-D5`) differ
> — while the RNG picks which fighter updates first on every pass. So a replay that never touches
> the play-mode menu compares TURBO with NORMAL, on different draws. **Pin both, on both legs**:
> poke `$FF8116` and `$FF80D4-D5` every frame and prove from each leg's own dump that the pokes
> held. Pinned, Donovan's 421+P matches native in hit count, damage and every hit frame at all four
> strengths, no mash and at the ceiling, at levels 6 and 8, and the vanilla Victor freeze drains in
> the same number of frames on both games. Unpinned, hit counts follow each game's own draws (MP
> with no mash at level 6: 4 hits native, 5 ours — #142, closed invalid) and video-frame durations
> follow the two modes' rates. Mechanism: `engine_internals.md`, the play-mode and RNG paragraphs;
> gate: `tests/test_don_immortal_native.sh` (ruled 2026-09-15).

**[VSE-85]** **Demonstrate saturation, never assume it** — a mash that presses one frame and releases one frame leaves a DEAD frame and is HALF the achievable rate; alternating two buttons EVERY frame is the ceiling. Below the ceiling two legs sit at different points of the SAME response curve (a different play mode or RNG draw on the two legs changes presses-counted-per-check, [VSE-84]), which manufactures differences that vanish at the top: Donovan's 421+P read "never extends LP, over-extends HP/ES by two" at half rate and equal-at-three-of-four at the ceiling — and equal at all four once the play mode and the RNG were pinned (14z-158). Before calling any input rate maximal, RAISE IT and show the result does not move, and keep that as a live control so the assertions cannot go vacuous.

> **Incident** (`docs/game/gotchas.md` › *A REPLAY DOES NOT TRANSFER BETWEEN REGIONAL SETS EITHER — `vsav`'s match starts ~200+ frames after `vsavj`'s (paid: 14z-127)*):
>
> A "MASH" THAT PRESSES ONE FRAME AND RELEASES ONE FRAME IS HALF THE CEILING — and a saturation claim measured below the ceiling manufactures a difference (paid: 14z-127)
>
> `+0x126` is a NEW-PRESS mask, so a recipe must release between taps
> (the entry above). The obvious next step — press for 1 frame, release for 1,
> alternating two buttons — looks maximal and is **not**: the release frame is
> dead. **Alternating two buttons EVERY frame makes every frame a new press**,
> because the previous button is released as the next is pressed. That is double
> the rate, and it is the real ceiling.
