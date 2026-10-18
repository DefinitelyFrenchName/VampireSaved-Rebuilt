"""test_readonly_guard.py — the gate on .claude/hooks/guard_readonly.py (docs/project/hooks.md).

Feeds the hook synthetic PreToolUse payloads and checks each verdict against ground truth in BOTH directions
([VSR-21]): writes outside the working tree and writes to the edit-locked hook files must be BLOCKED (exit 2); reads
of the read-only sources and writes inside the tree, the scratchpad and the memory directory must be ALLOWED (exit 0).
Nothing is written anywhere: every case is a payload, never a command that runs.

CONTROLS ([VSR-22], docs/project/must_fire_contract.md), each a shadow tool built under a throwaway root (the tracked
hook is never written):
  disarmed       shadow tool: the hook with its block exit stripped. Every BLOCK case must then fail, which proves the
                 gate sees the hook's exit status and not something else.
  lock-stripped  shadow tool: the hook with its edit-lock list emptied. The lock cases must then fail, which proves
                 the lock cases test the lock and not the outside-the-tree rule.
A normal run runs each control and reports it FIRED or DEAD; `--control <name>` makes the shadow the gate's input and
the gate must reach its own FAIL.

--hook <path> runs the gate on another copy of the hook (a proposed change, which the maintainer installs; the
installed hook is edit-locked): the default is the installed one.

Usage: python3 tests/test_readonly_guard.py [--hook <path>] [--control disarmed|lock-stripped]
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
HOOK = os.path.join(ROOT, ".claude", "hooks", "guard_readonly.py")
PARENT = os.path.dirname(ROOT)
SCRATCH = os.path.realpath("/private/tmp/claude-%d" % os.getuid())
MEMORY = os.path.join(os.path.expanduser("~"), ".claude", "projects", ROOT.replace("/", "-"), "memory")

CONTROLS = {
    "disarmed": ("        sys.exit(2)\n", "        pass\n"),
    "lock-stripped": ('LOCKED = (".claude/settings.json", ".claude/settings.local.json", ".claude/hooks")\n',
                      "LOCKED = ()\n"),
}


def w(path):
    return ("Write", {"file_path": path, "content": "x"})


def e(path):
    return ("Edit", {"file_path": path, "old_string": "a", "new_string": "b"})


def b(cmd):
    return ("Bash", {"command": cmd})


# (name, call, expected, kind) — kind "lock" marks the cases the lock-stripped control must break.
CASES = [
    # outside the tree: the four sources of truth and beyond
    ("write-roms", w(PARENT + "/ROMS/new.zip"), "block", "out"),
    ("edit-community", e(PARENT + "/community/Vampire Savior_Anakaris - Mizuumi Wiki.html"), "block", "out"),
    ("write-images-relative", w(ROOT + "/../Images/x.png"), "block", "out"),
    ("notebook-videos", ("NotebookEdit", {"notebook_path": PARENT + "/Videos/n.ipynb", "new_source": ""}), "block",
     "out"),
    ("write-home", w(os.path.expanduser("~/Desktop/x.txt")), "block", "out"),
    ("bash-rm", b("rm ../ROMS/vsav.zip"), "block", "out"),
    ("bash-rm-rf-parent", b("rm -rf .."), "block", "out"),
    ("bash-redirect", b("echo x > ../Videos/a.txt"), "block", "out"),
    ("bash-append-abs", b("echo x >> %s/Images/a.txt" % PARENT), "block", "out"),
    ("bash-redirect-fd", b("ls 2> ../community/err.txt"), "block", "out"),
    ("bash-cd-touch", b("cd ../ROMS && touch y"), "block", "out"),
    ("bash-cd-newline", b("cd ../ROMS\nunzip vsav.zip"), "block", "out"),
    ("bash-cp-into", b("cp docs/x.tsv ../Images/"), "block", "out"),
    ("bash-mv-out-of", b("mv ../ROMS/vsav.zip ."), "block", "out"),
    ("bash-sed-inplace", b("sed -i '' s/a/b/ ../community/f.html"), "block", "out"),
    ("bash-unzip-d", b("unzip ../ROMS/vsav.zip -d ../ROMS/x"), "block", "out"),
    ("bash-find-delete", b("find ../Images -name '*.JPG' -delete"), "block", "out"),
    ("bash-find-exec-rm", b("find ../Images -name x -exec rm {} \\;"), "block", "out"),
    ("bash-tar-x-C", b("tar -xf a.tar -C ../Videos"), "block", "out"),
    ("bash-dd-of", b("dd if=/dev/zero of=../ROMS/z bs=1 count=1"), "block", "out"),
    ("bash-curl-o", b("curl -o ../Images/x.png https://example.com/x.png"), "block", "out"),
    ("bash-xargs-rm", b("ls ../ROMS/*.zip | xargs rm"), "block", "out"),
    ("bash-tee", b("echo x | tee ../community/t.txt"), "block", "out"),
    ("bash-chmod", b("chmod -R a-w ../ROMS"), "block", "out"),
    ("bash-git-C-init", b("git -C ../ROMS init"), "block", "out"),
    ("bash-subshell", b("x=$(rm ../ROMS/vsav.zip)"), "block", "out"),
    ("bash-sh-c", b("bash -c 'rm ../ROMS/vsav.zip'"), "block", "out"),
    ("bash-python-c", b("python3 -c \"open('../ROMS/a', 'w').write('x')\""), "block", "out"),
    ("bash-heredoc-write", b("python3 - <<'EOF'\nimport pathlib\npathlib.Path('../community/x').write_text('y')\n"
                             "EOF"), "block", "out"),
    ("bash-home-var", b("rm -rf $HOME/Desktop/x"), "block", "out"),
    # the git forms of ticket #1: where git acts is -C, --git-dir/--work-tree and GIT_DIR/GIT_WORK_TREE
    ("git-work-tree-checkout", b("git --git-dir=../ROMS/.git --work-tree=../ROMS checkout ."), "block", "out"),
    ("git-work-tree-split", b("git --work-tree ../community checkout -- ."), "block", "out"),
    ("git-env-git-dir", b("GIT_DIR=../ROMS/.git git reset --hard"), "block", "out"),
    ("git-env-work-tree", b("GIT_WORK_TREE=../Images git checkout -- ."), "block", "out"),
    ("git-dash-c-hides-sub", b("git -c core.quotepath=off -C ../ROMS checkout ."), "block", "out"),
    ("git-fetch-original", b("git -C ../ROMS fetch origin"), "block", "out"),
    ("git-config-set", b("git -C ../ROMS config user.name x"), "block", "out"),
    ("git-branch-create", b("git -C ../ROMS branch scratch"), "block", "out"),
    ("git-archive-out", b("git -C ../ROMS archive -o ../ROMS/x.tar HEAD"), "block", "out"),
    ("bash-heredoc-shell", b("bash <<'EOF'\nrm ../ROMS/vsav.zip\nEOF"), "block", "out"),
    ("bash-heredoc-var-line", b("python3 - <<'EOF'\np = '../ROMS/a'; open(p, 'w')\nEOF"), "block", "out"),
    # the edit lock
    ("lock-write-settings", w(ROOT + "/.claude/settings.json"), "block", "lock"),
    ("lock-edit-hook", e(HOOK), "block", "lock"),
    ("lock-redirect-settings", b("echo '{}' > .claude/settings.json"), "block", "lock"),
    ("lock-rm-hooks-dir", b("rm -rf .claude/hooks"), "block", "lock"),
    ("lock-rm-claude-dir", b("rm -rf .claude"), "block", "lock"),
    ("lock-git-checkout", b("git checkout -- .claude/hooks/guard_readonly.py"), "block", "lock"),
    ("lock-sed-hook", b("sed -i '' s/2/0/ .claude/hooks/guard_readonly.py"), "block", "lock"),
    # allowed: reads of the sources, writes in the tree, the scratchpad, the memory directory
    ("read-ls", b("ls -la ../ROMS ../Images ../Videos ../community"), "allow", "ok"),
    ("read-unzip-l", b("unzip -l ../ROMS/vsav.zip"), "allow", "ok"),
    ("read-unzip-p", b("unzip -p ../ROMS/vsavj.zip member | shasum"), "allow", "ok"),
    ("read-sha-to-tree", b("shasum ../ROMS/*.zip > docs/roms.sha1"), "allow", "ok"),
    ("read-tool-arg", b("python3 tools/x.py ../ROMS/vsavj.zip out.tsv 2>/dev/null"), "allow", "ok"),
    ("read-find", b("find ../Images -name '*.JPG' -exec shasum {} +"), "allow", "ok"),
    ("read-heredoc", b("python3 - ../ROMS/vsav.zip <<'EOF'\nimport sys, zipfile\n"
                       "print(zipfile.ZipFile(sys.argv[1]).namelist())\nEOF"), "allow", "ok"),
    ("read-cp-to-scratch", b("cp ../Images/P1-Pyron_P2-Jedah.JPG %s/x.jpg" % SCRATCH), "allow", "ok"),
    ("read-git-C-status", b("git -C ../ROMS status"), "allow", "ok"),
    ("read-git-C-archive", b("git -C ../ROMS archive HEAD | tar -t"), "allow", "ok"),
    ("read-git-archive-scratch", b("git -C ../ROMS archive -o %s/o.tar HEAD" % SCRATCH), "allow", "ok"),
    ("read-git-C-config-get", b("git -C ../ROMS config --get remote.origin.url"), "allow", "ok"),
    ("read-git-C-branch-list", b("git -C ../ROMS branch -a"), "allow", "ok"),
    ("read-git-dir-log", b("git --git-dir=../ROMS/.git log -1"), "allow", "ok"),
    ("tree-write", w(ROOT + "/docs/project/hooks.md"), "allow", "ok"),
    ("tree-redirect", b("echo x > docs/x.txt 2>&1"), "allow", "ok"),
    ("tree-rm", b("rm -rf build/tmp"), "allow", "ok"),
    ("tree-cd-back", b("cd ../ROMS && cd ../VampireSaved-Rebuilt && touch y"), "allow", "ok"),
    ("tree-git", b("git add -A && git commit -q -m x && git push -q origin main"), "allow", "ok"),
    ("tree-claude-skill", e(ROOT + "/.claude/skills/vampire-saved-port/SKILL.md"), "allow", "ok"),
    ("scratch-write", w(SCRATCH + "/sub/notes.txt"), "allow", "ok"),
    ("memory-write", w(MEMORY + "/MEMORY.md"), "allow", "ok"),
    ("devnull", b("ls ../ROMS > /dev/null"), "allow", "ok"),
    ("tree-heredoc-mentions", b("python3 - <<'EOF'\nimport pathlib\ntext = 'the sets are in ../ROMS and $HOME'\n"
                                "pathlib.Path('docs/x.md').write_text(text)\nEOF"), "allow", "ok"),
    ("tree-heredoc-reads-roms", b("python3 - <<'EOF'\nimport zipfile\nn = zipfile.ZipFile('../ROMS/vsav.zip').namelist()\n"
                                  "open('docs/names.txt', 'w').write(str(n))\nEOF"), "allow", "ok"),
]


def run(hook, call):
    tool, tool_input = call
    payload = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input, "cwd": ROOT}
    env = dict(os.environ, CLAUDE_PROJECT_DIR=ROOT)
    p = subprocess.run([sys.executable, hook], input=json.dumps(payload), capture_output=True, text=True, env=env,
                       timeout=30)
    return {2: "block", 0: "allow"}.get(p.returncode, "error(%d: %s)" % (p.returncode, p.stderr.strip()[:200]))


def shadow(name, root):
    """The control's perturbation, written once: a copy of the hook with one line replaced, under `root`."""
    old, new = CONTROLS[name]
    src = open(HOOK).read()
    if src.count(old) != 1:
        raise SystemExit("CONTROL %s: anchor line not found exactly once in the hook" % name)
    path = os.path.join(root, "guard_%s.py" % name.replace("-", "_"))
    with open(path, "w") as f:
        f.write(src.replace(old, new))
    return path


def check(hook, log=True):
    failures = []
    for name, call, expected, _kind in CASES:
        got = run(hook, call)
        if got != expected:
            failures.append((name, expected, got))
        if log:
            print("%-4s %-24s expected %-5s got %s" % ("ok" if got == expected else "FAIL", name, expected, got))
    return failures


def main():
    global HOOK
    args = sys.argv[1:]
    if args[:1] == ["--hook"]:
        HOOK = os.path.realpath(args[1])
        args = args[2:]
    with tempfile.TemporaryDirectory(dir=SCRATCH if os.path.isdir(SCRATCH) else None) as tmp:
        if args[:1] == ["--control"]:
            name = args[1] if len(args) > 1 else ""
            if name not in CONTROLS:
                print("REFUSED: no declared control named %r (declared: %s)" % (name, ", ".join(CONTROLS)))
                sys.exit(3)
            print("MODE: control %s (the shadow tool is the gate's input; the gate must FAIL)" % name)
            failures = check(shadow(name, tmp))
        else:
            print("hook: %s" % HOOK)
            failures = check(HOOK)
            blocks = sum(1 for c in CASES if c[2] == "block")
            print("cases: %d (%d block, %d allow)" % (len(CASES), blocks, len(CASES) - blocks))
            for name in CONTROLS:
                broken = {n for n, _, _ in check(shadow(name, tmp), log=False)}
                want = {c[0] for c in CASES if c[2] == "block" and (name == "disarmed" or c[3] == "lock")}
                if broken == want:
                    print("CONTROL FIRED: %s (%d cases failed, exactly the %d it must break)" % (
                        name, len(broken), len(want)))
                else:
                    print("CONTROL DEAD: %s (failed %d, expected exactly %d; differing: %s)" % (
                        name, len(broken), len(want), sorted(broken ^ want)[:8]))
                    failures.append(("control:" + name, "fired", "dead"))
    print("VERDICT: %s (%d failing)" % ("PASS" if not failures else "FAIL", len(failures)))
    sys.exit(0 if not failures else 1)


if __name__ == "__main__":
    main()
