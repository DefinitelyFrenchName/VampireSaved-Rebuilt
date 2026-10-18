"""test_metrics.py — the gate on tools/metrics.py, the session dashboard's figures (#3; docs/project/metrics/README.md).

Builds a synthetic session whose every figure is known by construction (build/tmp/test_metrics/: a main transcript
timed in whole minutes, one worker, a git repository with a remote branch, a tree with tables, tickets and STATE.md, a
run log), runs the tool on it as a process, and compares each figure, in both directions ([VSR-21]): a figure must
equal the expected value AND carry the expected class, and every expected ABSENT must be ABSENT, never a number.
  C1 TIME      span, working, tools, maintainer, unaccounted (and that they sum to the span); the harness cross-checks
  C2 TOKENS    the orchestrator's tokens once per message id; the harness's per-model totals; the workers' share
  C3 EVENTS    prompts, questions, tool calls by name, background launches, errors, guard refusals, unanswered
               requests, timed turns, thinking, workers by kind and their time
  C4 GIT       the session's commits (by key and by span), files, lines, areas, unpushed
  C5 TREE      phase 0 progress, the census, gates and ported gates, the inventory, tickets, decisions, rule-checker
  C6 RUNLOG    gate runs, last verdict, controls, control modes, minutes red
  C7 ACTIVITY  the ESTIMATED activity split
  C8 ABSENT    a session without a cost-state record, and one without a transcript, give ABSENT rows
  C9 SCHEMA    `metrics.py check` passes on the output, and fails on a known-bad row
  C10 SHARE    --share-pattern counts only the calls naming the pattern, as EXTRAPOLATED

CONTROLS ([VSR-22], docs/project/must_fire_contract.md):
  late-result      perturbed copy: the first Bash call's result 30 s later. C1, C7 must fail.
  usage-twice      shadow tool: usage kept per record instead of per message id. C2 must fail.
  ask-as-tool      shadow tool: AskUserQuestion timed as a tool. C1 must fail.
  absent-filled    shadow tool: a missing cost-state read as zeros. C8 must fail.
  rule-dropped     shadow tool: every row's rule blanked. C9 must fail.
Shadow tools are copies under build/tmp/ (the tracked tool is never written). A normal run runs each control and
reports it FIRED or DEAD; `--control <name>` makes the perturbed input the gate's input and the gate must FAIL.

Usage: python3 tests/test_metrics.py [--control NAME]
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import runlog  # noqa: E402

TOOL = os.path.join(ROOT, "tools", "metrics.py")
TMP = os.path.join(ROOT, "build", "tmp", "test_metrics")
BASE = 1767225600  # 2026-01-01T00:00:00Z: the fixture's minute 0
OPUS, SONNET = "claude-opus-5-5", "claude-sonnet-5-5"
SHADOWS = {
    "usage-twice": ('            usage[m["id"]] = (m.get("model") or "?", m["usage"])',
                    '            usage[r.get("uuid")] = (m.get("model") or "?", m["usage"])'),
    "ask-as-tool": ('        (ask if c["name"] == "AskUserQuestion" else tools).append((c["start"], c["end"]))',
                    '        tools.append((c["start"], c["end"]))'),
    "absent-filled": ('        cs = p["cost"]\n',
                      '        cs = p["cost"] or {"totalDuration": 0, "totalAPIDuration": 0, "totalToolDuration": 0,'
                      ' "totalCostUSD": 0, "modelUsage": {}}\n'),
    "rule-dropped": ("        rows.append(dict(zip(COLUMNS, (key, section, metric, label, value, unit, cls, source, "
                     "rule))))",
                     "        rows.append(dict(zip(COLUMNS, (key, section, metric, label, value, unit, cls, source, "
                     "''))))"),
}
CONTROLS = {"late-result": {"C1", "C7"}, "usage-twice": {"C2"}, "ask-as-tool": {"C1"}, "absent-filled": {"C8"},
            "rule-dropped": {"C9"}}

# (session, metric) -> (value as written, class); the fixture below is built to these numbers
D, M, E, X, A = "DERIVED", "MEASURED", "ESTIMATED", "EXTRAPOLATED", "ABSENT"
EXPECT = {
    "C1": {("R-900", "span_min"): ("203.0", D), ("R-900", "working_min"): ("19.0", D),
           ("R-900", "tools_min"): ("58.0", D), ("R-900", "maintainer_min"): ("120.0", D),
           ("R-900", "unaccounted_min"): ("6.0", D), ("R-900", "harness_duration_min"): ("210.0", M),
           ("R-900", "harness_api_min"): ("20.0", M), ("R-900", "harness_tool_min"): ("11.0", M),
           ("R-900", "working_vs_harness_pct"): ("-5.0", D), ("R-900", "tools_vs_harness_pct"): ("13.6", D),
           ("R-900", "cost_usd"): ("1.23", M)},
    "C2": {("R-900", "out_" + OPUS): ("350", M), ("R-900", "think_" + OPUS): ("40", M),
           ("R-900", "in_" + OPUS): ("6000", M), ("R-900", "harness_out_" + OPUS): ("400", M),
           ("R-900", "harness_out_" + SONNET): ("300", M), ("R-900", "worker_out"): ("350", D),
           ("R-900", "worker_out_share_pct"): ("50.0", D)},
    "C3": {("R-900", "prompts_typed"): ("1", M), ("R-900", "prompts_queued"): ("1", M), ("R-900", "asks"): ("1", M),
           ("R-900", "tool_calls"): ("5", M), ("R-900", "tool_Bash"): ("2", M), ("R-900", "tool_Write"): ("1", M),
           ("R-900", "tool_Agent"): ("1", M), ("R-900", "tool_AskUserQuestion"): ("1", M),
           ("R-900", "bg_launched"): ("1", M), ("R-900", "tool_errors"): ("1", M),
           ("R-900", "guard_refusals"): ("1", M), ("R-900", "requests_unanswered"): ("1", M),
           ("R-900", "turns_timed"): ("2", M), ("R-900", "turns_timed_min"): ("2.4", M),
           ("R-900", "thinking_min"): ("3.0", M), ("R-900", "workers"): ("1", M),
           ("R-900", "workers_measurer"): ("1", M), ("R-900", "worker_span_min"): ("7.0", D),
           ("R-900", "worker_working_min"): ("6.0", D), ("R-900", "transcript"): ("aaaaaaaa", M)},
    "C4": {("R-900", "commits"): ("3", D), ("R-900", "files"): ("6", D), ("R-900", "insertions"): ("6", D),
           ("R-900", "deletions"): ("0", D), ("R-900", "area_tools"): ("1", D),
           ("R-900", "area_docs/project"): ("3", D), ("R-900", "area_STATE.md"): ("1", D),
           ("R-900", "area_tests"): ("1", D), ("R-900", "unpushed"): ("2", M)},
    "C5": {("R-900", "tabled_gameplay"): ("3", M), ("R-900", "tabled_fact"): ("2", M),
           ("R-900", "tabled_code"): ("0", M), ("R-900", "census_gameplay"): ("236", M),
           ("R-900", "census_fact"): ("8520", M), ("R-900", "census_code"): ("30", M), ("R-900", "gates"): ("1", M),
           ("R-900", "gates_ported"): ("1", M), ("R-900", "gates_original"): ("3", M),
           ("R-900", "gates_original_E1"): ("2", M), ("R-900", "gates_original_T"): ("1", M),
           ("R-900", "tickets_open"): ("2", M), ("R-900", "decisions_pending"): ("2", M),
           ("R-900", "rule_checker_runs"): ("0", D)},
    "C6": {("R-900", "gate_runs"): ("4", D), ("R-900", "g1_runs"): ("3", D), ("R-900", "g1_verdict"): ("PASS", M),
           ("R-900", "g1_cases"): ("7", M), ("R-900", "g1_declared"): ("2", M), ("R-900", "g1_fired"): ("2", M),
           ("R-900", "g1_seconds"): ("60.0", M), ("R-900", "g1_modes"): ("1", D),
           ("R-900", "g1_modes_honoured"): ("1", D), ("R-900", "red_min"): ("10.0", D)},
    "C7": {("R-900", "act_records_min"): ("0.0", E), ("R-900", "act_verify_min"): ("16.5", E),
           ("R-900", "act_rework_min"): ("3.0", E), ("R-900", "act_author_min"): ("0.0", E),
           ("R-900", "act_measure_min"): ("3.0", E), ("R-900", "act_converse_min"): ("69.0", E)},
    "C8": {("R-901", "harness_duration_min"): ("", A), ("R-901", "harness_api_min"): ("", A),
           ("R-901", "harness_tool_min"): ("", A), ("R-901", "cost_usd"): ("", A), ("R-901", "worker_out"): ("", A),
           ("R-901", "worker_out_share_pct"): ("", A), ("R-901", "working_min"): ("2.0", D),
           ("R-901", "gate_runs"): ("", A), ("R-902", "transcript"): ("", A)},
    "C10": {("R-903", "working_min"): ("4.0", X), ("R-903", "tools_min"): ("1.0", X),
            ("R-903", "maintainer_min"): ("0.0", X), ("R-903", "calls_in_share"): ("1", E),
            ("R-903", "span_min"): ("203.0", D)},
}


def iso(minute):
    return "%s.000Z" % __import__("datetime").datetime.utcfromtimestamp(BASE + minute * 60).strftime("%Y-%m-%dT%H:%M:%S")


def transcript(late=0.0):
    """the main transcript of R-900: minute by minute, the buckets in the module's EXPECT"""
    recs, n = [], [0]

    def rec(minute, **kw):
        n[0] += 1
        r = {"uuid": "u%d" % n[0], "timestamp": iso(minute)}
        r.update(kw)
        recs.append(r)

    def usage(out, think=0):
        return {"output_tokens": out, "output_tokens_details": {"thinking_tokens": think}, "input_tokens": 10,
                "cache_creation_input_tokens": 100, "cache_read_input_tokens": 890}

    def asst(minute, req, mid, blocks, out=50, think=0, thinking_ms=0):
        rec(minute, type="assistant", requestRef=req, thinkingDurationMs=thinking_ms,
            message={"id": mid, "model": OPUS, "content": blocks, "usage": usage(out, think)})

    def use(uid, name, inp):
        return {"type": "tool_use", "id": uid, "name": name, "input": inp}

    def result(minute, uid, text="ok", error=False):
        rec(minute, type="user", message={"content": [{"type": "tool_result", "tool_use_id": uid, "content": text,
                                                       "is_error": error}]})

    rec(0, type="user", origin={"kind": "human"}, promptSource="typed", message={"content": "go"})
    rec(1, type="api-request", id="r1")
    asst(3, "r1", "m1", [{"type": "text", "text": "x"}], out=100, think=40, thinking_ms=120000)
    asst(5, "r1", "m1", [use("t1", "Bash", {"command": "python3 tests/test_x.py"})], out=100, think=40)
    result(15 + late, "t1")
    rec(16, type="api-request", id="r2")
    asst(20, "r2", "m2", [use("t2", "AskUserQuestion", {"questions": []})])
    result(80, "t2")
    rec(81, type="api-request", id="r3")
    asst(85, "r3", "m3", [use("t3", "Write", {"file_path": "tools/a.py", "content": ""}),
                          use("t4", "Bash", {"command": "rm ../x"})], thinking_ms=60000)
    result(86, "t3")
    result(86, "t4", "PreToolUse:Bash hook error: BLOCKED by guard_readonly: ../x is outside", error=True)
    rec(87, type="api-request", id="r4")
    asst(90, "r4", "m4", [{"type": "text", "text": "done"}])
    rec(90, type="system", subtype="turn_duration", durationMs=90000)
    rec(150, type="user", origin={"kind": "human"}, promptSource="queued", message={"content": "more"})
    rec(151, type="api-request", id="r5")
    asst(153, "r5", "m5", [use("t5", "Agent", {"subagent_type": "measurer", "run_in_background": True})])
    result(153.5, "t5")
    rec(200, type="user", origin={"kind": "peer", "name": "measurer"}, message={"content": "hand-back"})
    rec(201, type="api-request", id="r6")
    asst(203, "r6", "m6", [{"type": "text", "text": "ok"}])
    rec(203, type="api-request", id="r7")
    rec(203, type="system", subtype="turn_duration", durationMs=53000)
    recs.append({"type": "cost-state", "totalDuration": 12600000, "totalAPIDuration": 1200000,
                 "totalToolDuration": 660000, "totalCostUSD": 1.234,
                 "modelUsage": {OPUS: {"outputTokens": 400}, SONNET: {"outputTokens": 300}}})
    return recs


def write_jsonl(path, recs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")


def git(repo, *a, minute=None):
    env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")
    if minute is not None:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = "@%d +0000" % (BASE + minute * 60)
    subprocess.run(["git", "-C", repo, "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
                    "-c", "commit.gpgsign=false"] + list(a), check=True, capture_output=True, env=env)


def fixture(base, late=0.0):
    shutil.rmtree(base, ignore_errors=True)
    projects, repo, runs = (os.path.join(base, d) for d in ("projects", "repo", "runs"))
    main = os.path.join(projects, "aaaaaaaa-0000.jsonl")
    write_jsonl(main, transcript(late))
    worker = os.path.join(projects, "aaaaaaaa-0000", "subagents", "agent-w1")
    write_jsonl(worker + ".jsonl", [
        {"type": "user", "timestamp": iso(153), "message": {"content": "measure"}},
        {"type": "api-request", "id": "w1", "timestamp": iso(154)},
        {"type": "assistant", "requestRef": "w1", "timestamp": iso(160),
         "message": {"id": "wm1", "model": SONNET, "content": [], "usage": {"output_tokens": 16}}}])
    json.dump({"agentType": "measurer"}, open(worker + ".meta.json", "w"))
    write_jsonl(os.path.join(projects, "bbbbbbbb-0000.jsonl"), [
        {"type": "user", "timestamp": iso(1000), "origin": {"kind": "human"}, "promptSource": "typed",
         "message": {"content": "hi"}},
        {"type": "api-request", "id": "q1", "timestamp": iso(1001)},
        {"type": "assistant", "requestRef": "q1", "timestamp": iso(1003),
         "message": {"id": "n1", "model": OPUS, "content": [], "usage": {"output_tokens": 5}}}])
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")

    def put(rel, text, append=False):
        p = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a" if append else "w") as f:
            f.write(text)

    # before the span: the tree the session starts from (not the session's)
    put("STATE.md", "# STATE\n\n## Session R-900 — x. transcript `aaaaaaaa`.\n\n## Session R-901 — y. transcript "
        "`bbbbbbbb`.\n\n## Session R-902 — z, no transcript on record.\n\n## Decisions pending (human)\n\n1. a\n"
        "2. b\n\n## The next session starts with\n\n1. c\n")
    put("SPEC.md", "reads gameplay values 15 in tables of 236 (221 baked), facts 0 in tables\nand 541 derived of 8,520 "
        "(7,979 baked), code constants 30 baked.\n")
    put("docs/project/tables/roster.tsv", "# GENERATED\nmanifest\tkind\n" + "m\tk\n" * 3)
    put("docs/project/tables/facts/a.tsv", "# GENERATED\nmanifest\tkind\n" + "m\tk\n" * 2)
    put("docs/project/tables/facts/held.tsv", "# held\nm\tk\n")
    put("docs/tests_inventory.tsv", "# read\ngate\tfamily\tkind\ttier\tlane\tscope\tneeds\tclass\twhy\tcovers\n"
        "a\tf\tk\tt\tl\ts\tn\tE1\tw\tc\nb\tf\tk\tt\tl\ts\tn\tE1\tw\tc\nc\tf\tk\tt\tl\ts\tn\tT\tw\tc\n")
    put("docs/project/tickets.tsv", "# tickets\nnumber\tkind\tstatus\ttitle\n1\tbug\topen\ta\n2\tbug\tdone\tb\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Older work", minute=-100)
    put("tools/a.py", "a = 1\n")
    put("docs/project/x.md", "x\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Something in the span", minute=50)
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    put("STATE.md", "closing words\n", append=True)
    put("docs/project/tickets.tsv", "3\tevolution\topen\tc\n", append=True)
    put("tests/test_y.py", "Ported from the original's test_z.sh\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "R-900 close: in the span", minute=170)
    put("docs/project/y.md", "y\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "R-900: after the span, by its key", minute=500)
    os.makedirs(runs)

    def run(gate, mode, start, end, verdict, cases=7):
        return {"gate": gate, "mode": mode, "start": iso(start)[:19] + "Z", "end": iso(end)[:19] + "Z",
                "duration_s": (end - start) * 60.0, "head": "0" * 40, "dirty": False, "diff": "", "verdict": verdict,
                "failed": [], "cases": cases, "controls_declared": ["p", "q"], "controls_fired": ["p", "q"],
                "controls_dead": []}
    write_jsonl(os.path.join(runs, "runs.jsonl"), [
        run("g1", "normal", -50, -49, "FAIL"), run("g1", "normal", 20, 21, "FAIL"),
        run("g1", "normal", 31, 32, "PASS"), run("g1", "control:p", 40, 41, "FAIL"),
        run("g1", "normal", 60, 61, "PASS")])
    return projects, repo, runs


def collect(tool, projects, repo, runs, out):
    logs = []
    for key, extra in (("R-900", []), ("R-901", []), ("R-902", []),
                       ("R-903", ["--transcript", os.path.join(projects, "aaaaaaaa-0000.jsonl"),
                                  "--share-pattern", "tools/a.py"])):
        p = subprocess.run([sys.executable, tool, "collect", key, "--projects", projects, "--repo", repo, "--runs",
                            runs, "--out", out] + extra, capture_output=True, text=True)
        logs.append((key, p.returncode, (p.stdout + p.stderr).strip().splitlines()[-1:] if p.returncode else []))
    return logs


def checks(tool, late=0.0, name="normal"):
    base = os.path.join(TMP, name)
    projects, repo, runs = fixture(base, late)
    out = os.path.join(base, "figures.tsv")
    logs = collect(tool, projects, repo, runs, out)
    failed, figures = set(), []
    died = [(k, c, t) for k, c, t in logs if c]
    if died:
        figures.append("collect died: %s" % died)
        return set(EXPECT) | {"C9"}, figures
    got = {}
    for line in open(out):
        if line.startswith("#") or line.startswith("session\t"):
            continue
        f = line.rstrip("\n").split("\t")
        got[(f[0], f[2])] = (f[4], f[6])
    for check, want in EXPECT.items():
        wrong = ["%s %s: got %s, expected %s" % (k[0], k[1], got.get(k), v) for k, v in want.items() if got.get(k) != v]
        if check == "C1" and not wrong:
            parts = sum(float(got[("R-900", m)][0]) for m in ("working_min", "tools_min", "maintainer_min",
                                                             "unaccounted_min"))
            if abs(parts - float(got[("R-900", "span_min")][0])) > 0.05:
                wrong.append("the buckets sum to %.1f, the span is %s" % (parts, got[("R-900", "span_min")][0]))
        figures.append("%-4s %d figures, %d wrong%s" % (check, len(want), len(wrong), (": " + wrong[0]) if wrong else ""))
        if wrong:
            failed.add(check)
    # C9: the schema check passes on the output and fails on a known-bad row
    p = subprocess.run([sys.executable, tool, "check", out], capture_output=True, text=True)
    bad = os.path.join(base, "bad.tsv")
    shutil.copy(out, bad)
    with open(bad, "a") as f:
        f.write("R-999\ttime\tx\tx\t1.0\tmin\tDERIVED\tsomewhere\t\n")
    q = subprocess.run([sys.executable, tool, "check", bad], capture_output=True, text=True)
    figures.append("C9   check on the output: exit %d (%s); on a known-bad row: exit %d" % (
        p.returncode, p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "no output", q.returncode))
    if p.returncode != 0 or q.returncode != 1:
        failed.add("C9")
    return failed, figures


def shadow(name):
    d = os.path.join(TMP, "shadow_" + name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    src = open(TOOL).read()
    old, new = SHADOWS[name]
    if src.count(old) != 1:
        raise SystemExit("CONTROL %s: anchor line not found exactly once in tools/metrics.py" % name)
    path = os.path.join(d, "metrics.py")
    open(path, "w").write(src.replace(old, new))
    shutil.copy(os.path.join(ROOT, "tools", "runlog.py"), d)
    return path


def control(name):
    if name == "late-result":
        return checks(TOOL, late=0.5, name="control_" + name)
    return checks(shadow(name), name="control_" + name)


def main():
    args = sys.argv[1:]
    mode = ("control:" + args[1]) if args[:1] == ["--control"] and len(args) > 1 else "normal"
    run, fired, dead = runlog.Run("test_metrics", mode), [], []
    print("tool: %s" % TOOL)
    if args[:1] == ["--control"]:
        name = args[1] if len(args) > 1 else ""
        if name not in CONTROLS:
            print("REFUSED: no declared control named %r (declared: %s)" % (name, ", ".join(CONTROLS)))
            run.record("REFUSED", declared=list(CONTROLS))
            sys.exit(3)
        print("MODE: control %s (the perturbed input is the gate's input; the gate must FAIL)" % name)
        failed, figures = control(name)
    else:
        failed, figures = checks(TOOL)
        for name in CONTROLS:
            got, _ = control(name)
            if got == CONTROLS[name]:
                print("CONTROL FIRED: %s (failed %s, exactly as declared)" % (name, ",".join(sorted(got))))
                fired.append(name)
            else:
                print("CONTROL DEAD: %s (failed %s, declared %s)" % (name, ",".join(sorted(got)) or "nothing",
                                                                     ",".join(sorted(CONTROLS[name]))))
                dead.append(name)
                failed.add("control:" + name)
    for f in figures:
        print(f)
    verdict = "PASS" if not failed else "FAIL"
    print("VERDICT: %s%s" % (verdict, "" if not failed else " (" + ", ".join(sorted(failed)) + ")"))
    run.record(verdict, failed=failed, cases=sum(len(v) for v in EXPECT.values()) + 2, declared=list(CONTROLS),
               fired=fired, dead=dead)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
