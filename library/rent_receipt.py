# keywords: rent receipt, hra receipt, rent receipts, make rent receipt, rent slip
# desc: Make monthly rent receipts for HRA as one printable page (rent receipt Asha Rao 15000 landlord Mohan Das from april 2026 for 12 months)
# category: money
# usage: rent receipt <tenant> <rent> landlord <name> [from <month year>] [for <n> months]
# rawargs: yes
import datetime
import html
import re
import sys
from pathlib import Path

t = " ".join(sys.argv[1:])
t = re.sub(r"^\s*(?:make|create|generate)?\s*(?:a\s+)?rent\s+receipts?\s*(?:for)?\s*", "", t, flags=re.I)
lm = re.search(r"\blandlord\s+(.+?)(?=\s+(?:from|for|address)\b|$)", t, re.I)
fm = re.search(r"\bfrom\s+([a-z]+)\s+(\d{4})", t, re.I)
nm = re.search(r"\bfor\s+(\d{1,2})\s+months?\b", t, re.I)
am = re.search(r"(?<![\w.])(\d[\d,]*)(?![\w])", t)
if not (lm and am):
    sys.exit("Usage: rent receipt <tenant> <rent> landlord <name> [from april 2026] [for 12 months]")
tenant = t[:am.start()].strip(" ,-")
if not tenant:
    sys.exit("Please give the tenant's name before the rent amount.")
rent = int(am.group(1).replace(",", ""))
landlord = lm.group(1).strip()
n = int(nm.group(1)) if nm else 12
months = {m.lower(): i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
today = datetime.date.today()
y, mo = today.year, today.month
if fm:
    mo = months.get(fm.group(1).lower()[:3], 0)
    y = int(fm.group(2))
    if not mo:
        sys.exit("I could not read the month. Example: from april 2026")
if not (1 <= n <= 12 and 0 < rent < 10_000_000):
    sys.exit("Rent must be a positive number and the count 1 to 12.")
e = html.escape
rows = []
for i in range(n):
    mm, yy = (mo - 1 + i) % 12 + 1, y + (mo - 1 + i) // 12
    last = (datetime.date(yy + (mm == 12), mm % 12 + 1, 1) - datetime.timedelta(days=1))
    rows.append(f"<section><h2>Rent receipt</h2><p>Received with thanks from <b>{e(tenant)}</b> the sum of <b>Rs. {rent:,}</b> "
                f"as rent for the month of <b>{last:%B %Y}</b>.</p><p>Date: {last:%d %B %Y}</p>"
                f"<p class=sig>Landlord: {e(landlord)}<br>Signature: ______________<br>Landlord PAN (needed if yearly rent is over Rs. 1,00,000): ____________</p></section>")
page = ("<!doctype html><meta charset=utf-8><title>Rent receipts</title><style>body{font:16px/1.6 system-ui,sans-serif;max-width:640px;margin:0 auto;padding:24px}"
        "section{border:1px solid #bbb;padding:24px;margin:24px 0;page-break-inside:avoid}h2{margin-top:0}.sig{margin-top:40px}</style>" + "".join(rows))
out_dir = next((Path.home() / d for d in ("Documents", "Desktop") if (Path.home() / d).is_dir()), Path.home()) / "JeeG-receipts"
out_dir.mkdir(exist_ok=True)
f = out_dir / f"rent-receipts-{re.sub(r'[^A-Za-z0-9]+', '-', tenant).strip('-')[:30]}-{y}-{mo:02d}.html"
f.write_text(page, encoding="utf-8")
print(f"Made {n} receipt(s) of Rs. {rent:,} for {tenant}. Open the file and print it (Ctrl+P) or save as PDF:\n{f}")
