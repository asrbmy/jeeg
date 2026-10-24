# keywords: invoice, make invoice, create invoice, bill customer, gst invoice, tax invoice, generate invoice
# desc: Make a simple GST invoice page (invoice Ravi Traders: 3 pens at 10, 2 books at 150 gst 18)
# category: money
# usage: invoice <customer>: <qty> <item> at <rate>, ... [gst 18]
# rawargs: full
# patterns: \b(make|create|generate|write|new)\s+(an?\s+)?(gst\s+|tax\s+)?invoice\b ;; ^\s*(gst\s+|tax\s+)?invoice\b
# priority: 1
import datetime, html, re
from _lib import args_text, fail, open_path, output_dir
from _money import inr
from _store import load, save
t = args_text()
m = re.match(r"^\s*(?:please\s+)?(?:(?:make|create|generate|write|new)\s+)?(?:an?\s+)?(?:gst\s+|tax\s+)?(?:invoice|bill)\s*(?:for|to)?\s*(.*)$", t, re.I | re.S)
t = (m.group(1) if m else t).strip()
s = re.match(r"^(?:seller|from|my business|business)\s+(.+)$", t, re.I)
if s:
    save("invoice_seller.json", {"name": s.group(1).strip()[:80]})
    print(f"Invoices will now show: {s.group(1).strip()[:80]}")
    raise SystemExit(0)
if ":" not in t:
    fail("Usage: invoice <customer>: <qty> <item> at <rate>, <qty> <item> at <rate> [gst 18]\n"
         "  e.g. invoice Ravi Traders: 3 pens at 10, 2 books at 150 gst 18\n  Set your shop name once:  invoice seller Sharma Stationers")
cust, items = (x.strip() for x in t.split(":", 1))
gm = re.search(r"\bgst\b\s*(\d+(?:\.\d+)?)?\s*%?", items, re.I)
rate = 0.0
if gm:
    rate = float(gm.group(1) or 18)
    items = items[:gm.start()] + items[gm.end():]
if not cust or not (0 <= rate <= 100):
    fail("Give a customer name before the colon, and a GST rate between 0 and 100.")
rows = []
for part in re.split(r"\s*(?:,\s+|;|\band\b)\s*", items.strip(" ,;")):
    if not part.strip():
        continue
    p = re.match(r"^(\d+(?:\.\d+)?)\s+(.+?)\s+(?:at|@|x|for|rs\.?|inr)\s*(\d[\d,]*(?:\.\d+)?)\s*(?:each)?$", part.strip(), re.I)
    if not p:
        fail(f"Could not read '{part.strip()}'. Write items like: 3 pens at 10")
    q, name, price = float(p.group(1)), p.group(2).strip()[:60], float(p.group(3).replace(",", ""))
    if q <= 0 or price < 0 or q > 1e6 or price > 1e9:
        fail(f"Check the numbers in '{part.strip()}'.")
    rows.append((name, q, price))
if not rows or len(rows) > 50:
    fail("Add between 1 and 50 items.")
seller = load("invoice_seller.json", {}).get("name", "Your business name")
n = load("invoice_counter.json", {"n": 0})["n"] + 1
save("invoice_counter.json", {"n": n})
no = f"INV-{n:04d}"
sub = sum(q * p for _, q, p in rows)
gst = sub * rate / 100
e = html.escape
body = "".join(f"<tr><td>{e(nm)}</td><td class=r>{q:g}</td><td class=r>{inr(p)}</td><td class=r>{inr(q * p)}</td></tr>" for nm, q, p in rows)
tax = (f"<tr><td colspan=3 class=r>GST {rate:g}% (CGST {rate / 2:g}% + SGST {rate / 2:g}%)</td><td class=r>{inr(gst)}</td></tr>" if rate else "")
page = f"""<!doctype html><meta charset=utf-8><title>{no}</title><style>
body{{font:15px system-ui,sans-serif;max-width:680px;margin:40px auto;padding:0 16px;color:#222}}h1{{font-size:22px;margin:0}}
table{{width:100%;border-collapse:collapse;margin-top:20px}}th,td{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}.r{{text-align:right}}
.tot td{{font-weight:700;border-top:2px solid #222}}.m{{color:#666}}@media print{{body{{margin:0}}}}</style>
<h1>{e(seller)}</h1><p class=m>Invoice {no} &middot; {datetime.date.today():%d %b %Y}</p><p>Bill to: <b>{e(cust)}</b></p>
<table><tr><th>Item</th><th class=r>Qty</th><th class=r>Rate</th><th class=r>Amount</th></tr>{body}
<tr><td colspan=3 class=r>Subtotal</td><td class=r>{inr(sub)}</td></tr>{tax}
<tr class=tot><td colspan=3 class=r>Total (INR)</td><td class=r>{inr(sub + gst)}</td></tr></table>
<p class=m>Computer generated. Print this page (Ctrl+P) to save it as a PDF.</p>"""
out = output_dir("JeeG-invoices")
f = out / f"{no}-{re.sub(r'[^A-Za-z0-9]+', '-', cust).strip('-')[:30] or 'customer'}.html"
f.write_text(page, encoding="utf-8")
print(f"{no} for {cust}: total {inr(sub + gst)}" + (f" (GST {inr(gst)} included)" if rate else ""))
print(f"Saved: {f}")
try:
    open_path(f)
except SystemExit:
    pass
