# keywords: clean copied text, copied links, copied table to csv, strip formatting, plain text from copy
# desc: Work on what you copied (clipboard clean, clipboard links, clipboard csv, clipboard sort, clipboard count)
# category: clipboard
# usage: clipboard clean | links | csv | sort | count
# rawargs: full
# patterns: ^\s*clipboard\s+(clean|plain|links|urls|csv|table|sort|count|trim)\b
# priority: 4
import csv, io, re
from _lib import args_text, fail, output_dir
from _sys import clip_get, clip_set
t = re.sub(r"^\s*clipboard\s*", "", args_text(), flags=re.I).strip().lower()
txt = clip_get() or ""
if not txt.strip():
    fail("The clipboard is empty or is not text.")
if len(txt) > 5_000_000:
    fail("The clipboard text is too large.")
if t in {"clean", "plain", "trim"}:
    new = "\n".join(re.sub(r"[ \t ]+", " ", ln).strip() for ln in txt.replace("\r\n", "\n").split("\n"))
    new = re.sub(r"\n{3,}", "\n\n", new).strip()
    new = new.translate({0x2018: "'", 0x2019: "'", 0x201c: '"', 0x201d: '"', 0x2013: "-", 0x2014: "-", 0x200b: None})
    clip_set(new)
    print(f"Cleaned (extra spaces, blank lines, curly quotes). {len(txt)} -> {len(new)} characters, back on the clipboard.")
elif t in {"links", "urls"}:
    links = list(dict.fromkeys(re.findall(r"https?://[^\s<>\"')\]]+", txt)))
    if not links:
        fail("No links found in what you copied.")
    for x in links[:100]:
        print("  " + x.rstrip(".,;"))
    print(f"{len(links)} link(s).")
elif t in {"csv", "table"}:
    lines = [ln for ln in txt.replace("\r\n", "\n").split("\n") if ln.strip()]
    sep = "\t" if any("\t" in ln for ln in lines) else None
    rows = [ln.split("\t") if sep else re.split(r"\s{2,}", ln.strip()) for ln in lines]
    if max(len(r) for r in rows) < 2:
        fail("That does not look like a table (columns separated by tabs or 2+ spaces).")
    buf = io.StringIO(); csv.writer(buf).writerows([[c.strip() for c in r] for r in rows])
    import time
    p = output_dir("JeeG clipboard") / f"table-{time.strftime('%Y%m%d-%H%M%S')}.csv"
    p.write_text(buf.getvalue(), encoding="utf-8", newline="")
    print(f"Saved {len(rows)} row(s) as {p}")
elif t == "sort":
    lines = [ln for ln in txt.replace("\r\n", "\n").split("\n")]
    new = "\n".join(sorted(lines, key=str.lower)); clip_set(new); print(f"Sorted {len(lines)} line(s); back on the clipboard.")
elif t == "count":
    print(f"{len(txt.split())} words, {len(txt)} characters, {len(txt.splitlines())} lines.")
else:
    fail("Say: clipboard clean | links | csv | sort | count")
