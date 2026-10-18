# What was carried from the original, and how

The ledgers of the carry of 2026-10-18 (the original's session 14z-205, its #120): every rule of the original's eight
skills, and every section of its swarm rules, classed `keep` (carried unchanged), `adapt` (its lesson restated without
the original's implementation), `drop` (its subject was only the original's implementation, or `SPEC.md` §4 replaces it
by construction) or `flag` (kept, with a question for the maintainer), each with its reason. The last line of each file
counts them.

- `ledger_facts.tsv`: `mame-fbneo-instruments`, `cps2-hardware`, `cps2-emulation`, `vampire-savior-engine`
- `ledger_mister.tsv`: `mister-jtframe-core`, `mister-cps2-wide-core`, `mister-vampire-saved`
- `ledger_port.tsv`: `vampire-saved-port` (each `[VSP-N]` and the `[VSR-N]` it became)
- `ledger_claude_md.tsv`: `CLAUDE.md`'s rules [VSR-1]..[VSR-50], each with the rule, section or ruling of the original it
  comes from (kept out of `CLAUDE.md` by the maintainer's ruling of 2026-10-18)
- `ledger_swarm.tsv`: `.claude/agents/`, `docs/project/worker_spec.md`, `rule_checker.md`, `swarm.md`, `must_fire_contract.md`

Checked mechanically against the original at its commit `6dee2be7`: every original rule ID is in a ledger; every `keep`
rule of the facts and MiSTer skills is byte-identical to the original's line, and every `keep` rule of the port skill is
identical apart from its ID; `measurer.md` and `reader.md` are byte-identical and both rule-checker checklists are
sha1-identical; every quotation of a person in `CLAUDE.md` and `docs/project/` is found verbatim in the original. NOT
checked: whether each `adapt` and `drop` is right, which the agents that wrote them judged, rule by rule, and nobody has
reviewed since.
