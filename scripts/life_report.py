# keywords: life report, visual report, report page, my month chart, habit heatmap, spending chart, progress page, dashboard of my life
# desc: A visual page of your month: spending bars, habit heat-map, water, sleep, to-dos (life report, life report last month, life report year)
# category: productivity
# usage: life report [last month | year]
# rawargs: yes
# patterns: \blife\s+report\b ;; \b(visual|chart|graph)\s+(report|page)\b ;; \bhabit\s+heat\s*map\b
# priority: 2
import csv, datetime, html, re
from collections import Counter
from _lib import args_text, data_dir, fail, open_path, output_dir
from _money import inr
from _store import load, period
t = args_text().lower()
start, end, label = period(re.sub(r"\b(life|report|visual|page|chart|my|show|make|me|a|the)\b", " ", t))
today = datetime.date.today()
d = data_dir()
e = html.escape
def inside(s):
    try: x = datetime.date.fromisoformat(str(s)[:10])
    except ValueError: return False
    return (start is None or x >= start) and (end is None or x <= end)
# spending
cat, daily, n = Counter(), Counter(), 0
f = d / "expenses.csv"
if f.exists():
    with open(f, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if inside(r.get("date", "")):
                try: a = float(r.get("amount") or 0)
                except ValueError: continue
                cat[r.get("category", "misc") or "misc"] += a; daily[r["date"][:10]] += a; n += 1
total = sum(cat.values())
bars = "".join(f"<div class=row><span>{e(c)}</span><i style='width:{max(2, 100 * v / max(cat.values())):.0f}%'></i><b>{inr(v)}</b></div>" for c, v in cat.most_common(10)) or "<p class=m>No spending recorded in this period.</p>"
# habits: last 12 weeks heat map
habits = load("habits.json", {})
days = [today - datetime.timedelta(days=i) for i in range(83, -1, -1)]
heat = ""
for name, ds in sorted(habits.items()):
    s = set(ds)
    cells = "".join(f"<u class='{'on' if x.isoformat() in s else ''}' title='{x:%d %b}'></u>" for x in days)
    heat += f"<div class=h><span>{e(name)}</span><div class=g>{cells}</div></div>"
heat = heat or "<p class=m>No habits yet. Try: habit done gym</p>"
# water and sleep
def series(fn, key_skip="_"):
    data = {k: v for k, v in load(fn, {}).items() if not k.startswith(key_skip) and inside(k)}
    return sorted(data.items())
water, sleep = series("water.json"), series("sleep.json")
def spark(items, top):
    if not items: return "<p class=m>Nothing logged in this period.</p>"
    mx = max(top, max(v for _, v in items))
    return "<div class=sp>" + "".join(f"<u style='height:{max(3, 100 * v / mx):.0f}%' title='{k}: {v:g}'></u>" for k, v in items[-40:]) + "</div>"
wavg = f"{sum(v for _, v in water) / len(water):,.0f} ml a day" if water else ""
savg = f"{sum(v for _, v in sleep) / len(sleep):.1f} h a night" if sleep else ""
todos = load("todos.json", [])
done_n, open_n = sum(1 for x in todos if x.get("done")), sum(1 for x in todos if not x.get("done"))
jn = 0
jf = d / "journal.txt"
if jf.exists():
    jn = sum(1 for ln in jf.read_text(encoding="utf-8", errors="replace").splitlines() if inside(ln[:10]))
page = f"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Life report</title><style>
:root{{--bg:#faf9f5;--fg:#1f1e1d;--m:#73726c;--c:#fff;--l:#e8e6dc;--a:#c96442;--s:#ebe9df}}
@media(prefers-color-scheme:dark){{:root{{--bg:#262624;--fg:#f0eee6;--m:#a09f97;--c:#30302e;--l:#444441;--a:#d97757;--s:#3a3a37}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}}main{{max-width:760px;margin:0 auto;padding:32px 16px}}
h1{{font:600 28px Georgia,serif;margin:0}}h2{{font-size:16px;margin:0 0 12px}}.m{{color:var(--m)}}
section{{background:var(--c);border:1px solid var(--l);border-radius:14px;padding:18px;margin-top:16px}}
.row{{display:grid;grid-template-columns:110px 1fr auto;gap:10px;align-items:center;margin:6px 0}}.row i{{height:12px;background:var(--a);border-radius:6px}}.row b{{font-weight:500;min-width:90px;text-align:right}}
.h{{display:flex;gap:12px;align-items:center;margin:8px 0}}.h span{{width:90px;flex:none}}.g{{display:grid;grid-template-columns:repeat(28,1fr);gap:3px;flex:1}}
.g u{{aspect-ratio:1;background:var(--s);border-radius:3px}}.g u.on{{background:var(--a)}}
.sp{{display:flex;align-items:flex-end;gap:3px;height:70px}}.sp u{{flex:1;max-width:28px;background:var(--a);border-radius:3px 3px 0 0;opacity:.85}}
.k{{display:flex;gap:24px;flex-wrap:wrap}}.k div b{{display:block;font-size:22px}}</style><main>
<h1>Life report</h1><p class=m>{e(label)} &middot; made on your computer, nothing was sent anywhere</p>
<section><h2>Spending: {inr(total)} in {n} item(s)</h2>{bars}</section>
<section><h2>Habits, last 12 weeks</h2>{heat}</section>
<section><h2>Water {('&middot; ' + wavg) if wavg else ''}</h2>{spark(water, 2500)}</section>
<section><h2>Sleep {('&middot; ' + savg) if savg else ''}</h2>{spark(sleep, 9)}</section>
<section class=k><div><b>{open_n}</b>to-dos open</div><div><b>{done_n}</b>to-dos done</div><div><b>{jn}</b>journal entries</div></section></main>"""
out = output_dir("JeeG-reports")
fn = out / f"life-report-{today.isoformat()}.html"
fn.write_text(page, encoding="utf-8")
print(f"Life report for {label}: spending {inr(total)}, {len(habits)} habit(s), {open_n} open to-do(s).")
print(f"Saved: {fn}")
try:
    open_path(fn)
except SystemExit:
    pass
