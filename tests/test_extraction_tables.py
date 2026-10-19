"""test_extraction_tables.py — the gate on the extraction tables and the two gameplay tables decoded from them
(tools/extract_regions.py; docs/project/tables/README.md "The extraction tables"; #4).

Needs an export of the original at the tables' pin, and the reference dumps (ROMDIR, read only) for E3.
  E1 FRESH     tools/extract_regions.py, run anew from the export, writes files byte-identical to the committed tables
  E2 WHOLE     the committed tables render back to each tenant's regions.json, parse equal (objects' key order aside,
               every list's order kept), and their `read:` headers name each record's SHA-1
  E3 ANCHORED  every jump_physics and cancel_windows row, re-encoded, equals the bytes at its vs2 row in vsav2's data
               view, at an address computed here from bank_map.toml's facts and the record's char (and the row's own
               vs2 column says the same address); vsav2.zip's members have the SHA-1s the records read
  E4 NO-ROM    no cell of the tables but a `sha1` holds a run of 17 or more hex bytes ([VSR-8])

CONTROLS ([VSR-22]):
  perturbed-ref     a copy of refs.tsv with one target moved by 2: E1 and E2 must fail
  dropped-scan      a copy of code_scan.tsv with one row deleted: E1 and E2 must fail
  gravity-sign      a copy of jump_physics.tsv with Donovan's neutral gravity negated: E1, E2 and E3 must fail
  windows-swapped   a copy of cancel_windows.tsv with Pyron's special and EX columns swapped: E1, E2 and E3 must fail
  bytes-in-values   a copy of values.tsv with Donovan's jump_params bytes written back in the clear: E1 and E4 must
                    fail (E2 passes: the record is still whole, which is why E4 exists)
  wrong-row         the tables untouched, E3 reads the next character's row: E3 alone must fail
A normal run runs each control and reports it FIRED or DEAD; `--control <name>` makes the perturbed input the gate's
and the gate must reach its own FAIL.

Usage: python3 tests/test_extraction_tables.py [--romdir DIR] [--export DIR] [--control NAME]
       (ROMDIR default: ../ROMS beside this repository; export default: build/export_<pin>)
"""
import filecmp
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from decimal import Decimal

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import extract_regions  # noqa: E402
import runlog  # noqa: E402
from test_phase0_tables import read_table  # noqa: E402

TABLES = os.path.join(ROOT, "docs", "project", "tables")
FILES = ["extraction/%s.tsv" % n for n in extract_regions.COLUMNS
         if n not in ("jump_physics", "cancel_windows")] + ["jump_physics.tsv", "cancel_windows.tsv"]
CONTROLS = {"perturbed-ref": {"E1", "E2"}, "dropped-scan": {"E1", "E2"}, "gravity-sign": {"E1", "E2", "E3"},
            "windows-swapped": {"E1", "E2", "E3"}, "bytes-in-values": {"E1", "E4"}, "wrong-row": {"E3"}}
HEX_RUN = re.compile(r"[0-9a-fA-F]{34,}")


def rows_of(tables, name):
    return extract_regions.read_rows(os.path.join(tables, name))


def vs2_rows():
    """{table: (vs2 address of row 0, entry size)}, read here from the fact tables (bank_map.toml's origins and its
    table rows), not from the tool."""
    facts = {}
    for name in ("origins", "table"):
        for r in read_table(os.path.join(TABLES, "facts", name + ".tsv"))[2]:
            if r[0] == "bank_map.toml" and r[3] in ("vsavj", "vsav2", "stride", "span"):
                facts[(r[2], r[3])] = int(r[4], 16)
    shift = facts[("#1", "vsav2")] - facts[("#1", "vsavj")]
    return {"jump_params": (facts[("jump_params", "vsavj")] + shift, facts[("jump_params", "stride")] // 32),
            "byte2d_a": (facts[("byte2d_a", "vsavj")] + shift, facts[("byte2d_a", "span")] // 32),
            "byte2d_b": (facts[("byte2d_b", "vsavj")] + shift, facts[("byte2d_b", "span")] // 32)}


def fixed16(text):
    v = Decimal(text) * 65536
    return int(v).to_bytes(4, "big", signed=True) if v == v.to_integral_value() else b"?"


def checks(tmp, tables, export, data, romdir, row_bump=0):
    failed, figures = set(), []
    fresh = os.path.join(tmp, "fresh")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "extract_regions.py"), export,
                        read_table(os.path.join(TABLES, "roster.tsv"))[0], fresh], capture_output=True, text=True)
    differ = [f for f in FILES if p.returncode or not filecmp.cmp(os.path.join(fresh, f), os.path.join(tables, f),
                                                                   shallow=False)]
    figures.append("E1 tool exit %d, files %d, differing %d%s" % (p.returncode, len(FILES), len(differ),
                                                                   (": " + differ[0]) if differ else ""))
    if p.returncode or differ:
        failed.add("E1")

    recs, _ = extract_regions.records(export)
    rendered = extract_regions.render(tables)
    read = dict(rows_of(tables, FILES[0])[0])
    bad = []
    for tenant, rel in recs:
        raw = open(os.path.join(export, rel), "rb").read()
        if rendered.get(tenant) != json.loads(raw):
            bad.append(tenant)
        if read.get(rel) != hashlib.sha1(raw).hexdigest()[:12]:
            bad.append(tenant + " (read header)")
    n = sum(len(rows_of(tables, f)[1]) for f in FILES)
    figures.append("E2 tenants %d, rendered equal %d, table rows %d%s" % (
        len(recs), len(recs) - len(bad), n, (": " + bad[0]) if bad else ""))
    if bad:
        failed.add("E2")

    at, char = vs2_rows(), {r["tenant"]: int(r["char"], 16) + row_bump
                            for r in rows_of(tables, "extraction/runs.tsv")[1]}
    checked, wrong = 0, []
    for r in rows_of(tables, "jump_physics.tsv")[1]:
        base, size = at["jump_params"]
        addr = base + char[r["tenant"]] * size + extract_regions.JUMPS.index(r["jump"]) * 16
        want = b"".join(fixed16(r[f]) for f in extract_regions.JUMP_FIELDS)
        checked += 1
        if data[addr:addr + 16] != want or r["vs2_row"] != "PRG:0x%06X" % addr:
            wrong.append("%s %s jump" % (r["tenant"], r["jump"]))
    for r in rows_of(tables, "cancel_windows.tsv")[1]:
        for col, table in (("special", "byte2d_a"), ("ex", "byte2d_b")):
            base, size = at[table]
            addr = base + char[r["tenant"]] * size + int(r["move"])
            checked += 1
            if data[addr] != int(r[col]) or r["vs2_" + col] != "PRG:0x%06X" % addr:
                wrong.append("%s move %s %s" % (r["tenant"], r["move"], col))
    with zipfile.ZipFile(os.path.join(romdir, "vsav2.zip")) as z:
        members = {i.filename: hashlib.sha1(z.read(i)).hexdigest() for i in z.infolist()}
    inputs = rows_of(tables, "extraction/inputs.tsv")[1]
    unmatched = [r["file"] for r in inputs if members.get(r["file"]) != r["sha1"]]
    figures.append("E3 gameplay values checked %d, differing from vsav2's row %d; record inputs %d, not in vsav2.zip %d"
                   "%s" % (checked, len(wrong), len(inputs), len(unmatched),
                           (": " + (wrong + unmatched)[0]) if wrong or unmatched else ""))
    if wrong or unmatched or not checked:
        failed.add("E3")

    cells, runs = 0, []
    for f in FILES:
        for r in rows_of(tables, f)[1]:
            for k, v in r.items():
                cells += 1
                if k != "sha1" and HEX_RUN.search(v):
                    runs.append("%s %s" % (f, k))
    figures.append("E4 cells %d, holding a run of 17+ hex bytes %d%s" % (cells, len(runs),
                                                                         (": " + runs[0]) if runs else ""))
    if runs:
        failed.add("E4")
    return failed, figures


def edit(tables, name, change):
    path = os.path.join(tables, name)
    lines = open(path).read().split("\n")
    header = next(i for i, l in enumerate(lines) if l and not l.startswith("#"))
    cols = lines[header].split("\t")
    out = lines[:header + 1]
    for line in lines[header + 1:]:
        if not line:
            out.append(line)
            continue
        row = dict(zip(cols, line.split("\t")))
        row = change(row)
        if row is not None:
            out.append("\t".join(row[c] for c in cols))
    open(path, "w").write("\n".join(out))


def perturb(name, tables, export):
    once = {"done": False}

    def first(pred, fn):
        def change(row):
            if not once["done"] and pred(row):
                once["done"] = True
                return fn(row)
            return row
        return change
    if name == "perturbed-ref":
        edit(tables, "extraction/refs.tsv", first(lambda r: True, lambda r: dict(r, target=hex(int(r["target"], 16) + 2))))
    elif name == "dropped-scan":
        edit(tables, "extraction/code_scan.tsv", first(lambda r: True, lambda r: None))
    elif name == "gravity-sign":
        edit(tables, "jump_physics.tsv", first(lambda r: r["tenant"] == "donovan" and r["jump"] == "neutral",
                                               lambda r: dict(r, gravity=str(-Decimal(r["gravity"])))))
    elif name == "windows-swapped":
        edit(tables, "cancel_windows.tsv", lambda r: dict(r, special=r["ex"], ex=r["special"])
             if r["tenant"] == "pyron" else r)
    elif name == "bytes-in-values":
        recs, _ = extract_regions.records(export)
        doc = json.load(open(os.path.join(export, dict(recs)["donovan"])))
        clear = next(x["value"] for x in doc["values"] if x["table"] == "jump_params")
        edit(tables, "extraction/values.tsv", first(lambda r: r["tenant"] == "donovan" and r["table"] == "jump_params",
                                                    lambda r: dict(r, value=clear)))


def run_case(name, export, data, romdir):
    tmp = tempfile.mkdtemp(prefix="test_extraction_tables.", dir=os.path.join(ROOT, "build", "tmp"))
    try:
        tables = os.path.join(tmp, "tables")
        for f in FILES:
            os.makedirs(os.path.dirname(os.path.join(tables, f)), exist_ok=True)
            shutil.copyfile(os.path.join(TABLES, f), os.path.join(tables, f))
        perturb(name, tables, export)
        return checks(tmp, tables, export, data, romdir, row_bump=1 if name == "wrong-row" else 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def vsav2_data(export, romdir):
    """vsav2's data view (what a data read sees), by the original's cps2_decrypt.py, into a scratch made here."""
    tmp = tempfile.mkdtemp(prefix="test_extraction_tables.vsav2.", dir=os.path.join(ROOT, "build", "tmp"))
    try:
        z = os.path.join(romdir, "vsav2.zip")
        print("read vsav2.zip sha1 %s" % hashlib.sha1(open(z, "rb").read()).hexdigest())
        subprocess.run([sys.executable, os.path.join(export, "tools", "cps2_decrypt.py"), z,
                        os.path.join(tmp, "op.bin"), "--data-out", os.path.join(tmp, "data.bin")],
                       check=True, capture_output=True)
        data = open(os.path.join(tmp, "data.bin"), "rb").read()
        print("image vsav2 data view sha1 %s" % hashlib.sha1(data).hexdigest())
        return data
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    args = sys.argv[1:]
    opts = {}
    for flag in ("--romdir", "--export", "--control"):
        if flag in args:
            i = args.index(flag)
            opts[flag] = args[i + 1] if i + 1 < len(args) else ""
            args = args[:i] + args[i + 2:]
    romdir = os.path.realpath(opts.get("--romdir") or os.path.join(ROOT, "..", "ROMS"))
    pin = read_table(os.path.join(TABLES, "roster.tsv"))[0]
    export = os.path.realpath(opts.get("--export") or os.path.join(ROOT, "build", "export_" + pin))
    os.makedirs(os.path.join(ROOT, "build", "tmp"), exist_ok=True)
    control = opts.get("--control")
    run = runlog.Run("test_extraction_tables", "control:" + control if control else "normal")
    print("romdir: %s\nexport: %s" % (romdir, export))
    fired, dead = [], []
    if control is not None and control not in CONTROLS:
        print("REFUSED: no declared control named %r (declared: %s)" % (control, ", ".join(CONTROLS)))
        run.record("REFUSED", declared=list(CONTROLS))
        sys.exit(3)
    data = vsav2_data(export, romdir)
    if control is not None:
        print("MODE: control %s (the perturbed input is the gate's; the gate must FAIL)" % control)
        failed, figures = run_case(control, export, data, romdir)
    else:
        failed, figures = run_case("normal", export, data, romdir)
        for name, want in CONTROLS.items():
            got, _ = run_case(name, export, data, romdir)
            if got == want:
                print("CONTROL FIRED: %s (failed %s, exactly as declared)" % (name, ",".join(sorted(got))))
                fired.append(name)
            else:
                print("CONTROL DEAD: %s (failed %s, declared %s)" % (name, ",".join(sorted(got)) or "nothing",
                                                                     ",".join(sorted(want))))
                dead.append(name)
                failed.add("control:" + name)
    for f in figures:
        print(f)
    print("VERDICT: %s" % ("PASS" if not failed else "FAIL (" + ", ".join(sorted(failed)) + ")"))
    run.record("PASS" if not failed else "FAIL", failed=failed, declared=list(CONTROLS), fired=fired, dead=dead)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
