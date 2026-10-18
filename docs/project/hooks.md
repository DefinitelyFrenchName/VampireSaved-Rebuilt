# THE HOOKS — the deterministic guards wired into this repository's Claude Code sessions

**What this document is.** The record of every hook this repository installs: what it blocks, why, what it cannot see,
the gate that proves it, and how it is changed. The rule is `CLAUDE.md` [VSR-49] (deterministic hooks hard-block; the
enforcement protects itself); the structure it follows is `docs/project/swarm.md` §4. One hook so far.

## The read-only guard (`.claude/hooks/guard_readonly.py`, installed 2026-10-18)

**Why.** The maintainer's ruling of 2026-10-18 (`SPEC.md` §0): `../ROMS`, `../Images`, `../Videos` and `../community`
are read-only sources of truth, and *"like anything above the working directory, must only be accessed read-only"*
(`CLAUDE.md` [VSR-8], §7). Asked whether to add a hook so the rule is enforced rather than written: *"Please add the
hook"*.

**What it blocks.** A `PreToolUse` hook on `Write`, `Edit`, `MultiEdit`, `NotebookEdit` and `Bash`, for the session and
every subagent. A call is refused (exit 2, the reason on stderr) when it would write:
- **outside the working tree**, except the session scratchpad (`/private/tmp/claude-<uid>/`), this project's memory
  directory (`~/.claude/projects/<project>/memory/`) and the `/dev` sinks;
- **the edit-locked paths**: `.claude/settings.json`, `.claude/settings.local.json` and `.claude/hooks/`; a recursive
  operation (`rm -r`, `mv`, `chmod -R`) on a directory that contains one is refused too.

Reading is never refused. The file tools are judged exactly, by their resolved path (symlinks resolved). `Bash` is judged
by what its words show: redirection targets; the operands of the commands that write (`rm`, `mv`, `cp`'s destination,
`touch`, `mkdir`, `chmod`, `tee`, `sed -i`, `dd of=`, `curl -o`, `unzip`/`tar`/`7z` extraction targets, `find -delete`
and `-exec`, `xargs` fed from a read-only path, `git -C` and git's tree-rewriting subcommands); `cd` moves across `&&`,
`;` and newlines; `$( )` and backticks; `bash -c` and shell heredocs, parsed as shell; and inline code (`python3 -c`,
heredoc scripts), refused when ONE line both calls a write API and names a read-only path.

**What it cannot see** (each a known gap, not a licence):
- what a program decides at run time: a script file run with a read-only path as its argument (`python3 tools/x.py
  ../ROMS/vsavj.zip`) is allowed, because reading its input is the normal case ([VSR-10]); the script itself must
  not write there;
- inline code that names the path on one line and writes it on another (`p = '../ROMS/a'` then `open(p, 'w')`);
- variables other than `$HOME`, `$PWD` and `$CLAUDE_PROJECT_DIR`, and paths assembled at run time;
- a symlink created earlier in the same command and written through later;
- git subcommands that rewrite the tree without naming a locked path (`git reset --hard`, `git stash`);
- anything not launched through a tool call (the hooks see only tool calls, `swarm.md` §4).

**Its failure mode.** The hook fails closed: a crash on a call whose input names a read-only path blocks it, and the
settings mark the hook `onFailure: block`. A crash on any other call lets it through.

**The gate.** `python3 tests/test_readonly_guard.py` feeds the hook synthetic payloads (nothing runs, nothing is
written) and checks each verdict in both directions ([VSR-21]): writes outside the tree and to the locked paths must
be blocked, and reads of the four sources plus writes in the tree, the scratchpad and the memory directory must be
allowed. Its two declared controls ([VSR-22]) are shadow tools under a throwaway root: `disarmed`, which strips the
block exit, and `lock-stripped`, which empties the lock list. Each must break exactly the cases it targets. A normal
run reports each FIRED or DEAD, and `--control <name>` runs the gate on the shadow, where it must FAIL. Measured at
install: 59 cases (39 block, 20 allow), `VERDICT: PASS`, both controls FIRED, both control modes `VERDICT: FAIL`, and
a replay of the installing session's 31 calls in which only its own two edits of the hook were refused.

**How it changes.** Only the maintainer edits the hook and its settings ([VSR-49], the edit lock); hooks bind Claude,
not the maintainer's own editor or shell. A session that needs a change proposes it as a proven file outside the
locked paths (with the gate run against it) and the maintainer applies it.
