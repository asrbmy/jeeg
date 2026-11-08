# keywords: chart csv, csv chart, graph csv, plot csv, bar chart csv, chart from csv, csv graph
# desc: Make a bar chart (HTML page) from a CSV: first text column vs first number column (chart csv sales.csv).
# category: files
# usage: chart csv <file.csv>
# rawargs: full
# patterns: \b(chart|graph|plot)\b.*\bcsv\b ;; \bcsv\b.*\b(chart|graph|plot)\b
# priority: 1
import csv, html
from pathlib import Path
from _lib import args_text, fail
from _files import path_arg, unique_path
t = args_text()
for junk in ("chart csv", "csv chart", "graph csv", "plot csv", "bar chart", "make a", "from"):
    t = t.replace(junk, " ")
words = t.split()
p = path_arg(" ".join(words))
if not p.is_file() or p.stat().st_size > 20 * 1024 * 1024:
    fail("Give a CSV file under 20 MB, e.g. chart csv sales.csv")
with open(p, encoding="utf-8-sig", newline="") as fh:
    rows = list(csv.reader(fh))
if len(rows) < 2:
    fail("The CSV needs a header row and at least one data row.")
head, body = rows[0], rows[1:2001]
def num(s):
    try:
        return float(s.replace(",", "").replace("$", "").replace("%", "").strip())
    except ValueError:
        return None
vcol = next((i for i in range(len(head)) if sum(num(r[i]) is not None for r in body if len(r) > i) >= max(1, len(body) // 2)), None)
if vcol is None:
    fail("No number column found.")
lcol = next((i for i in range(len(head)) if i != vcol), None)
pts = [((r[lcol] if lcol is not None and len(r) > lcol else str(n + 1)), num(r[vcol])) for n, r in enumerate(body) if len(r) > vcol and num(r[vcol]) is not None]
shown = pts[:40]
mx = max((v for _, v in shown), default=1) or 1
bars = []
for n, (lab, v) in enumerate(shown):
    wd = max(1.0, 100.0 * abs(v) / abs(mx))
    bars.append(f'<div class="r"><span class="l">{html.escape(lab[:28])}</span><span class="b" style="width:{wd:.1f}%"></span><span class="v">{v:,.2f}</span></div>')
page = ("<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>" + html.escape(p.name) + "</title>"
        "<style>body{font:15px system-ui,sans-serif;margin:24px auto;max-width:760px;padding:0 16px;color:#1f1e1d;background:#faf9f5}"
        "h1{font:600 22px Georgia,serif}.r{display:flex;align-items:center;gap:8px;margin:4px 0}.l{width:150px;flex:none;text-align:right;color:#555}"
        ".b{height:18px;background:#c96442;border-radius:3px;flex:none;max-width:50%}.v{color:#555;font-size:13px}p{color:#73726c}"
        "@media(prefers-color-scheme:dark){body{background:#262624;color:#f0eee6}.l,.v{color:#a09f97}.b{background:#d97757}}</style>"
        "<h1>" + html.escape(head[vcol]) + (" by " + html.escape(head[lcol]) if lcol is not None else "") + "</h1>"
        + "".join(bars) + "<p>" + f"{len(shown)} of {len(pts)} rows shown. Made on your computer; nothing was uploaded.</p>")
dest = unique_path(p.with_name(p.stem + "_chart.html"))
dest.write_text(page, encoding="utf-8")
print(f"Chart of '{head[vcol]}' ({len(shown)} bars) -> {dest}")
print("Open that file in your browser.")
