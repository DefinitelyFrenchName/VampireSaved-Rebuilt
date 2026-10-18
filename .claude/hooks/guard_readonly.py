"""guard_readonly.py — the PreToolUse hook that keeps everything outside the working tree read-only (docs/project/hooks.md).

The maintainer's ruling of 2026-10-18 (SPEC.md §0, CLAUDE.md [VSR-8], §7): ../ROMS, ../Images, ../Videos and ../community
are read-only sources of truth and, "like anything above the working directory, must only be accessed read-only". This
hook refuses a tool call that would write outside the working tree, and (the edit lock of [VSR-49]) one that would write
the hook itself or the settings that wire it. Exit 2 with the reason on stderr is Claude Code's block.

Allowed outside the tree: the session scratchpad (/private/tmp/claude-<uid>/), this project's memory directory, and the
/dev sinks. Write, Edit, MultiEdit and NotebookEdit are judged exactly by their path. Bash is judged by what its words
show: redirection targets, the operands of the commands that write, and `cd` moves; what a program decides to write
at run time cannot be seen (the gaps are listed in docs/project/hooks.md).

Python, stdlib only ([VSR-11]): a stdin-JSON filter that needs a shell tokenizer (shlex) and no build step.
Usage (by Claude Code): python3 .claude/hooks/guard_readonly.py < hook-input.json
"""
import json
import os
import re
import shlex
import sys

LOCKED = (".claude/settings.json", ".claude/settings.local.json", ".claude/hooks")

WRITE_ALL = {"rm", "rmdir", "touch", "mkdir", "chmod", "chown", "chgrp", "chflags", "xattr", "truncate", "shred",
             "unlink", "tee", "mv", "setfile", "mkfifo", "srm", "trash"}
WRITE_LAST = {"cp", "rsync", "install", "ln", "ditto", "scp"}
IN_PLACE = {"sed", "gsed", "perl", "ruby"}
INTERPRETERS = {"python", "python3", "perl", "ruby", "node", "osascript", "bash", "sh", "zsh"}
WRAPPERS = {"sudo", "command", "env", "nohup", "time", "nice", "exec", "builtin"}
GIT_TREE = {"checkout", "restore", "rm", "mv", "clean"}
GIT_READ = {"status", "log", "show", "diff", "ls-files", "rev-parse", "cat-file", "grep", "blame", "describe",
            "ls-tree", "shortlog", "archive", "name-rev", "for-each-ref", "show-ref", "count-objects"}
# read only in these forms: `config` with a reading flag, `branch`/`remote` listing; anything else of theirs writes
GIT_READ_IF = {"config": {"--get", "--get-all", "--get-regexp", "--list", "-l", "--show-origin"},
               "branch": {"--list", "-l", "-a", "-r", "-v", "-vv", "--show-current", "--contains"},
               "remote": {"-v", "show", "get-url"}}
WRITE_API = re.compile(r"open\([^)]*,\s*(mode\s*=\s*)?['\"][rbt]*[wax+]|write_text|write_bytes|"
                       r"\bos\.(remove|unlink|rename|replace|rmdir|removedirs|makedirs|mkdir|chmod|truncate|symlink|"
                       r"link|utime)\b|\bshutil\.|\.(unlink|rename|mkdir|touch|chmod|symlink_to|hardlink_to)\(|"
                       r"\bfs\.(write|append|rm|unlink|mkdir|rename|copy|cp)|\bFile\.(write|delete|rename)")
REDIR = re.compile(r"^[0-9]*(>|>>|&>|&>>|>\||>&)$")


def project_root():
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    return os.path.realpath(root)


ROOT = project_root()
HOME = os.path.expanduser("~")
ALLOWED = (
    os.path.realpath("/private/tmp/claude-%d" % os.getuid()),
    os.path.realpath(os.path.join(HOME, ".claude", "projects", ROOT.replace("/", "-"), "memory")),
)
SINKS = ("/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty", "/dev/fd/")


def expand(word, cwd):
    """~, $HOME, $PWD and $CLAUDE_PROJECT_DIR expanded; any other variable is left for unresolvable() to see."""
    for var, value in (("${HOME}", HOME), ("$HOME", HOME), ("${CLAUDE_PROJECT_DIR}", ROOT),
                       ("$CLAUDE_PROJECT_DIR", ROOT), ("${PWD}", cwd), ("$PWD", cwd)):
        word = word.replace(var, value)
    return os.path.expanduser(word)


def resolve(path, cwd):
    """The real absolute path a write would land on: known variables expanded, globs cut at their first wildcard,
    symlinks resolved through the deepest existing ancestor."""
    path = expand(path, cwd)
    cut = re.search(r"[*?\[]", path)
    if cut:
        path = os.path.dirname(path[:cut.start()] + "x")
    full = os.path.normpath(os.path.join(cwd, path))
    head, tail = full, ""
    while head and not os.path.exists(head):
        head, part = os.path.split(head)
        tail = os.path.join(part, tail) if tail else part
        if head == "/":
            break
    real = os.path.realpath(head)
    return os.path.normpath(os.path.join(real, tail)) if tail else real


def under(path, base):
    return path == base or path.startswith(base.rstrip("/") + "/")


def refusal(path, recursive=False):
    """Why a write to this resolved path is refused, or None. A recursive operation (rm -r, mv, chmod -R) is also
    refused on a directory that CONTAINS a locked path."""
    if path.startswith(SINKS):
        return None
    if not under(path, ROOT):
        if any(under(path, a) for a in ALLOWED):
            return None
        return "%s is outside the working tree, which is read-only (CLAUDE.md [VSR-8])" % path
    for rel in LOCKED:
        locked = os.path.join(ROOT, rel)
        if under(path, locked) or (recursive and under(locked, path)):
            return "%s is edit-locked: the hooks and their settings are the maintainer's (CLAUDE.md [VSR-49])" % path
    return None


def unresolvable(word):
    return "$" in word or "`" in word


def check_paths(words, cwd, recursive=False):
    out = []
    for w in words:
        if not w or unresolvable(expand(w, cwd)):
            continue
        why = refusal(resolve(w, cwd), recursive)
        if why:
            out.append(why)
    return out


def operands(args):
    return [a for a in args if a and not a.startswith("-")]


def mentions_protected(text, cwd):
    for tok in re.findall(r"[~/.$A-Za-z0-9_{}][^\s'\"();|&<>]*", text):
        if "/" in tok or tok.startswith("~") or tok.startswith(".."):
            if not unresolvable(expand(tok, cwd)) and refusal(resolve(tok, cwd)):
                return True
    return False


def check_segment(words, cwd, whole):
    """(reasons, new cwd) for one simple command."""
    assigned = {}
    while words and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]) or os.path.basename(words[0]) in WRAPPERS):
        if "=" in words[0] and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]):
            key, _, value = words[0].partition("=")
            assigned[key] = value
        words = words[1:]
        while words and words[0].startswith("-"):
            words = words[1:]
    if not words:
        return [], cwd
    cmd, args = os.path.basename(words[0]), words[1:]
    if cmd in ("cd", "pushd"):
        target = operands(args)
        if target and not unresolvable(expand(target[0], cwd)):
            return [], resolve(target[0], cwd)
        return [], os.path.expanduser("~") if not target else cwd
    recursive = any(re.match(r"^-[A-Za-z]*[rR]", a) for a in args) or cmd in ("mv", "rm", "rmdir")
    if cmd in WRITE_ALL:
        return check_paths(operands(args), cwd, recursive), cwd
    if cmd in WRITE_LAST:
        ops = operands(args)
        reasons = check_paths(ops[-1:], cwd, recursive)
        return reasons, cwd
    if cmd in IN_PLACE and any(a.startswith("-i") or a == "--in-place" for a in args):
        return check_paths(operands(args), cwd), cwd
    if cmd == "dd":
        return check_paths([a[3:] for a in args if a.startswith("of=")], cwd), cwd
    if cmd in ("curl", "wget"):
        dests = [args[i + 1] for i, a in enumerate(args[:-1]) if a in ("-o", "--output", "-O", "-P",
                                                                       "--directory-prefix", "--output-document")]
        return check_paths(dests, cwd), cwd
    if cmd == "unzip":
        if any(a in ("-l", "-v", "-t", "-p", "-Z", "-z") for a in args):
            return [], cwd
        if "-d" in args and args.index("-d") + 1 < len(args):
            return check_paths([args[args.index("-d") + 1]], cwd), cwd
        return check_paths(["."], cwd), cwd
    if cmd in ("zip", "7z", "7za"):
        if cmd == "zip":
            return check_paths(operands(args)[:1], cwd), cwd
        outs = [a[2:] for a in args if a.startswith("-o")]
        return check_paths(outs or (["."] if args and args[0] in ("x", "e") else []), cwd), cwd
    if cmd in ("tar", "bsdtar", "gtar"):
        modes = (args[0].lstrip("-") if args else "")
        dest = [args[i + 1] for i, a in enumerate(args[:-1]) if a in ("-C", "--directory")]
        archive = [args[i + 1] for i, a in enumerate(args[:-1]) if a == "-f" or (a.startswith("-") and
                                                                                    a.endswith("f") and "-" in a)]
        if "x" in modes:
            return check_paths(dest or ["."], cwd, True), cwd
        if any(m in modes for m in "cru"):
            return check_paths(archive, cwd), cwd
        return [], cwd
    if cmd == "find":
        start = [a for a in args if not a.startswith("-") and a not in ("!", "(", ")")][:1] or ["."]
        reasons = []
        if "-delete" in args:
            reasons += check_paths(start, cwd, True)
        for i, a in enumerate(args):
            if a in ("-exec", "-execdir", "-ok", "-okdir"):
                sub = []
                for b in args[i + 1:]:
                    if b in (";", "+", "\\;"):
                        break
                    sub.append(start[0] if b == "{}" else b)
                reasons += check_segment(sub, cwd, whole)[0]
        return reasons, cwd
    if cmd == "xargs":
        rest = [a for a in args if not a.startswith("-")]
        if rest and os.path.basename(rest[0]) in WRITE_ALL | WRITE_LAST and mentions_protected(whole, cwd):
            return ["xargs runs %s on paths read from a pipeline that names a read-only path" % rest[0]], cwd
        return check_segment(rest, cwd, whole)[0] if rest else [], cwd
    if cmd == "git":
        # where git acts: -C moves its directory; --git-dir/--work-tree and GIT_DIR/GIT_WORK_TREE name the
        # repository and tree it writes, whatever the directory (R-001, ticket #1)
        gcwd, places, i = cwd, [], 0
        for var in ("GIT_DIR", "GIT_WORK_TREE"):
            if var in assigned:
                places.append(assigned[var])
        while i < len(args) and args[i].startswith("-"):
            a = args[i]
            if a in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") and i + 1 < len(args):
                if a == "-C":
                    gcwd = resolve(args[i + 1], gcwd)
                elif a in ("--git-dir", "--work-tree"):
                    places.append(args[i + 1])
                i += 1
            elif a.startswith("--git-dir=") or a.startswith("--work-tree="):
                places.append(a.split("=", 1)[1])
            i += 1
        sub = args[i] if i < len(args) else ""
        rest = args[i + 1:]
        if sub == "archive":
            outs = [rest[j + 1] for j, a in enumerate(rest[:-1]) if a in ("-o", "--output")]
            outs += [a.split("=", 1)[1] for a in rest if a.startswith("--output=")]
            return check_paths(outs, cwd), cwd
        if sub in GIT_READ or (sub in GIT_READ_IF and (any(a in GIT_READ_IF[sub] for a in rest) or
                                                         (sub in ("branch", "remote") and not rest))):
            return [], cwd
        for where in [gcwd] + [resolve(expand(pl, gcwd), gcwd) for pl in places
                               if not unresolvable(expand(pl, gcwd))]:
            if refusal(where):
                return ["git %s would act on %s: %s" % (sub, where, refusal(where))], cwd
        if sub == "clone":
            ops = operands(args[i + 1:])
            return check_paths(ops[1:2], cwd), cwd
        if sub in GIT_TREE:
            return check_paths(operands(args[i + 1:]), gcwd), cwd
        return [], cwd
    if cmd in INTERPRETERS:
        for i, a in enumerate(args[:-1]):
            if a == "-c" and cmd in ("bash", "sh", "zsh"):
                return check_bash(args[i + 1], cwd), cwd
            if a in ("-c", "-e") and writes_protected(args[i + 1], cwd):
                return ["inline %s code writes and names a read-only path on one line" % cmd], cwd
    return [], cwd


def writes_protected(code, cwd):
    """Inline code is refused when ONE line both calls a write API and names a read-only path: a script that writes
    in the tree and merely mentions ../ROMS elsewhere (a document's text, a read) passes."""
    return any(WRITE_API.search(line) and mentions_protected(line, cwd) for line in code.split("\n"))


def split_heredocs(command):
    """The command without its heredoc bodies, and (the line that opened it, the body) for each body."""
    bodies, kept, lines, i = [], [], command.split("\n"), 0
    while i < len(lines):
        kept.append(lines[i])
        marks = re.findall(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?", lines[i])
        i += 1
        for mark in marks:
            body = []
            while i < len(lines) and lines[i].strip() != mark:
                body.append(lines[i])
                i += 1
            i += 1
            bodies.append((kept[-1], "\n".join(body)))
    return "\n".join(kept), bodies


def check_bash(command, cwd):
    reasons = []
    shell, bodies = split_heredocs(command)
    for head, body in bodies:
        if re.search(r"(^|[\s;&|(])(bash|sh|zsh)(\s+-[a-z]+)*\s*(-s\s*)?<<", head):
            reasons += check_bash(body, cwd)
        elif writes_protected(body, cwd):
            reasons.append("a heredoc script writes and names a read-only path on one line")
    for inner in re.findall(r"\$\(([^()]*)\)|`([^`]*)`", shell):
        reasons += check_bash(inner[0] or inner[1], cwd)
    try:
        lex = shlex.shlex(shell.replace("\\\n", " ").replace("\n", " ; "), posix=True, punctuation_chars=";&|<>()")
        lex.whitespace_split = True
        lex.commenters = ""
        tokens = list(lex)
    except ValueError:
        return reasons + (["an unparseable command names a read-only path"] if mentions_protected(shell, cwd)
                          else [])
    segment, k = [], 0
    while k <= len(tokens):
        tok = tokens[k] if k < len(tokens) else ";"
        if tok.endswith("&") and tok.startswith(">") and k + 1 < len(tokens) and tokens[k + 1].isdigit():
            k += 2
            continue
        if REDIR.match(tok):
            if k + 1 < len(tokens):
                reasons += check_paths([tokens[k + 1]], cwd)
            k += 2
            continue
        if tok in ("<", "<<", "<<<", "<&", "<>"):
            k += 2
            continue
        if tok in (";", "&&", "||", "|", "&", "|&", "(", ")", "\n", ";;"):
            found, cwd = check_segment(segment, cwd, shell)
            reasons += found
            segment = []
        else:
            segment.append(tok)
        k += 1
    return reasons


def judge(payload):
    tool = payload.get("tool_name", "")
    inp = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or os.getcwd()
    if tool == "Bash":
        return check_bash(inp.get("command", ""), cwd)
    path = inp.get("file_path") or inp.get("notebook_path")
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit") and path:
        why = refusal(resolve(path, cwd))
        return [why] if why else []
    return []


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
        text = json.dumps(payload.get("tool_input"))
        reasons = judge(payload)
    except Exception as exc:  # fail closed on a crash only when the call names a read-only path
        text = locals().get("text", raw)
        reasons = ["the guard crashed (%s) on a call that names a read-only path" % exc] \
            if mentions_protected(text, os.getcwd()) else []
    if reasons:
        print("BLOCKED by guard_readonly: " + "; ".join(sorted(set(reasons))), file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
