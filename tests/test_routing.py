#!/usr/bin/env python3
"""Routing regression test. Each line of phrases.txt:  phrase => script_name [| expected args]
Use 'none' for 'must not match anything' and 'menu' for 'must be ambiguous'."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import jeeg as tr  # noqa: E402

entries = tr.load_index(tr.script_dirs([]), rebuild=True)
bad = total = 0
for ln in (ROOT / "tests" / "phrases.txt").read_text(encoding="utf-8").splitlines():
    ln = ln.strip()
    if not ln or ln.startswith("#"):
        continue
    phrase, want = [x.strip() for x in ln.split("=>")]
    want_args = None
    if "|" in want:
        want, a = [x.strip() for x in want.split("|", 1)]
        want_args = a
    st, hit = tr.resolve(phrase, entries)
    if st == "ok":
        got, got_args = hit[1]["name"], " ".join(hit[2])
    else:
        got, got_args = ("menu" if st == "ambiguous" else "none"), ""
    total += 1
    ok = got == want and (want_args is None or got_args == want_args)
    if not ok:
        bad += 1
        extra = f" args={got_args!r}" if want_args is not None else ""
        names = ""
        if st == "ambiguous":
            names = " [" + ", ".join(h[1]["name"] for h in hit[:4]) + "]"
        print(f"FAIL  {phrase!r}: expected {want}{(' | ' + want_args) if want_args is not None else ''}, got {got}{extra}{names}")
print(f"routing: {total - bad}/{total} passed")

# ---- multi-task lines: which scripts would run, in order (dry run)
import contextlib, io, re  # noqa: E402
sbad = stotal = 0
sf = ROOT / "tests" / "splits.txt"
for ln in (sf.read_text(encoding="utf-8").splitlines() if sf.exists() else []):
    ln = ln.strip()
    if not ln or ln.startswith("#"):
        continue
    phrase, want = [x.strip() for x in ln.split("=>")]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        tr.run_query(phrase, entries, {"yes": True, "dry": True, "timeout": None})
    got = ",".join(re.findall(r"scripts[/\\]([a-z0-9_]+)\.py", buf.getvalue())) or "none"
    stotal += 1
    if got != want:
        sbad += 1
        print(f"FAIL  split {phrase!r}: expected {want}, got {got}")
print(f"multi-task: {stotal - sbad}/{stotal} passed")
sys.exit(1 if (bad or sbad) else 0)
