# keywords: gst, tax, vat, add gst, remove gst, gst inclusive, gst exclusive, cgst, sgst, igst, price with tax, excluding gst
# desc: GST add or remove (gst 1000 18, gst 1180 18 inclusive)
# category: money
# usage: gst <amount> [rate] [inclusive]
# rawargs: yes
import re
from _lib import args_text, fail
from _money import inr, numbers
t = args_text().lower()
incl = bool(re.search(r"\b(incl\w*|inclusive|remove|extract|reverse|including|with gst in)\b", t))
n = numbers(t.replace("%", " "))
if not n:
    fail("Usage: gst <amount> [rate%] [inclusive]   e.g. gst 1000 18   |   gst 1180 18 inclusive")
amt, rate = n[0], (n[1] if len(n) > 1 else 18.0)
if not (amt >= 0 and 0 <= rate <= 100):
    fail("Check the values.")
base = amt / (1 + rate / 100) if incl else amt
gst = base * rate / 100
print(f"{'Price includes' if incl else 'Add'} GST at {rate:g}%")
print(f"  Base price : {inr(base)}")
print(f"  GST        : {inr(gst)}   (CGST {inr(gst / 2)} + SGST {inr(gst / 2)})")
print(f"  Total      : {inr(base + gst)}")
