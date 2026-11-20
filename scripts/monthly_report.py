# keywords: monthly report, month report, money report, month summary page, report page, finance report
# desc: Make a one-page report of this month (spending, budgets, recurring costs, mileage, 80C) you can open or print to PDF (monthly report)
# category: money
# usage: monthly report [YYYY-MM]
# rawargs: full
# patterns: ^\s*(monthly|month)\s+report\b
# priority: 4
import csv, datetime, html, re
from _lib import args_text, data_dir, fail, output_dir, open_path
from _store import load
from _money import inr
m = re.search(r"\b(20\d\d)-(0[1-9]|1[0-2])\b", args_text())
mo = m.group(0) if m else datetime.date.today().strftime("%Y-%m")
spent, rows = {}, 0
f = data_dir() / "expenses.csv"
if f.exists():
    for r in csv.DictReader(open(f, encoding="utf-8")):
        try:
            if r["date"].startswith(mo):
                spent[r["category"]] = spent.get(r["category"], 0) + float(r["amount"]); rows += 1
        except (KeyError, ValueError):
            pass
bud = load("budgets.json", {})
rec = load("recurring.json", [])
mil = load("mileage.json", {"rate": 0, "trips": []})
t80 = load("tax80c.json", {})
km = sum(x["km"] for x in mil["trips"] if x["date"].startswith(mo))
e = html.escape
def table(head, body):
    return "<table><tr>" + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr>" + "".join("<tr>" + "".join(f"<td>{e(str(c))}</td>" for c in r) + "</tr>" for r in body) + "</table>"
parts = [f"<h1>JeeG report for {mo}</h1><p class=n>Made on your computer from your own records. Nothing was sent anywhere.</p>"]
tot = sum(spent.values())
parts.append(f"<h2>Spending</h2><p>{rows} entries, total <b>{e(inr(tot))}</b>.</p>")
if spent:
    parts.append(table(["Category", "Spent", "Budget", "Used"], [(c, inr(v), inr(bud[c]) if c in bud else "-", f"{int(100 * v / bud[c])}%" if bud.get(c) else "-") for c, v in sorted(spent.items(), key=lambda x: -x[1])]))
if rec:
    parts.append("<h2>Recurring costs</h2>" + table(["Name", "Amount", "Category"], [(r["name"], inr(r["amount"]), r["category"]) for r in rec]) + f"<p>Per month {e(inr(sum(r['amount'] for r in rec)))}.</p>")
if km:
    parts.append(f"<h2>Mileage</h2><p>{km:g} km" + (f", claim {e(inr(km * mil['rate']))} at {e(inr(mil['rate']))}/km" if mil.get("rate") else "") + ".</p>")
if t80:
    parts.append("<h2>Section 80C</h2>" + table(["What", "Amount"], [(k, inr(v)) for k, v in sorted(t80.items(), key=lambda x: -x[1])]) + f"<p>Total {e(inr(sum(t80.values())))} of {e(inr(150000))}.</p>")
if not spent and not rec and not km and not t80:
    fail(f"There is nothing recorded for {mo} yet.")
css = "body{font:15px system-ui,sans-serif;max-width:720px;margin:2rem auto;padding:0 1rem;color:#222}table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid #ddd;padding:6px 8px;text-align:left}th{background:#f4f4f4}.n{color:#666}@media print{body{margin:0}}"
p = output_dir("JeeG reports") / f"report-{mo}.html"
p.write_text(f"<!doctype html><meta charset=utf-8><title>JeeG report {mo}</title><style>{css}</style>" + "".join(parts), encoding="utf-8")
print(f"Made {p}. Open it in your browser; use Print > Save as PDF for a PDF.")
