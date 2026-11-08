# keywords: severance, severance pay, end of service, gratuity, redundancy pay, termination pay, leaving bonus
# desc: Estimate severance or end-of-service pay (severance 5 years salary 4000 a month weeks 2)
# category: money
# usage: severance <years> years salary <amount> [a year] [weeks <n>]
# rawargs: yes
# patterns: \bseverance\b ;; \bend[\s-]of[\s-]service\b ;; \bgratuity\b ;; \bredundancy\s+pay\b
# priority: 2
import re
from _lib import args_text, fail
t = args_text().lower().replace(",", "")
def pick(pat):
    m = re.search(pat, t)
    return float(m.group(1)) if m else None
years = pick(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)")
sal = pick(r"(?:salary|pay|earn\w*)\D{0,6}(\d+(?:\.\d+)?)")
weeks = pick(r"(\d+(?:\.\d+)?)\s*weeks?") or pick(r"weeks?\D{0,4}(\d+(?:\.\d+)?)") or 2.0
if not years or not sal or years <= 0 or sal <= 0 or not 0 < weeks <= 52:
    fail("Usage: severance 5 years salary 4000 a month [weeks 2]\n"
         "  weeks = weeks of pay for each year of service (the rule in your country or contract; 2 is a common minimum).\n"
         "  Say 'a year' after the salary if it is yearly.")
yearly = bool(re.search(r"(?:salary|pay)\D{0,12}(?:a|per|/)\s*(?:year|yr|annum)", t))
weekly = (sal if yearly else sal * 12) / 52
amount = weekly * weeks * years
print(f"{years:g} years x {weeks:g} weeks of pay x {weekly:,.2f} a week")
print(f"Estimated severance: {amount:,.2f}  (about {amount / (weekly * 4.345):.1f} months of pay)")
print("A guide only. Real rules (caps, tax, notice pay) differ by country and contract; check yours.")
