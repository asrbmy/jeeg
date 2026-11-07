# keywords: hra, hra exemption, house rent allowance, hra calculator, rent exemption
# desc: HRA tax exemption (hra basic 50000 hra 20000 rent 18000 metro)
# category: money
# usage: hra basic <amt> hra <amt> rent <amt> [metro]
# rawargs: full
# patterns: \bhra\b ;; \bhouse\s+rent\s+allowance\b
# priority: 2
import re
from _lib import args_text, fail
from _money import inr
t = re.sub(r"^\s*(?:hra|house rent allowance)\s*(?:exemption|calculator)?", " ", args_text().lower().replace(",", ""))
def pick(word):
    m = re.search(word + r"\D{0,12}?(\d+(?:\.\d+)?)", t)
    return float(m.group(1)) if m else None
basic, hra, rent = pick(r"basic(?:\s+salary)?"), pick(r"\bhra"), pick(r"rent")
if not (basic and hra and rent):
    fail("Usage: hra basic 50000 hra 20000 rent 18000 metro   (monthly amounts; say 'metro' for Delhi, Mumbai, Kolkata, Chennai)")
metro = bool(re.search(r"\bmetro\b|delhi|mumbai|kolkata|chennai", t)) and "non" not in t
parts = [("Actual HRA received", hra), ("Rent paid minus 10% of basic", max(0, rent - basic * .10)),
         (f"{50 if metro else 40}% of basic", basic * (.5 if metro else .4))]
ex = min(v for _, v in parts)
for n, v in parts:
    print(f"  {n:<30} {inr(v)}")
print(f"Exempt HRA: {inr(ex)} a month ({inr(ex * 12)} a year). Taxable HRA: {inr((hra - ex) * 12)} a year.")
print("(Old regime only. Basic means basic + DA. Rent above 1 lakh a year needs your landlord's PAN.)")
