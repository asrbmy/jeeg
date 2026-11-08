# keywords: freelance rate, hourly rate, how much to charge, my hourly rate, rate calculator, consulting rate, charge per hour, day rate
# desc: Work out the hourly rate you need (freelance rate income 4000 expenses 800 hours 25 weeks off 6).
# category: money
# usage: freelance rate income <n> expenses <n> hours <n>
# rawargs: full
# patterns: \bfreelance\s+rate\b ;; \bhourly\s+rate\b ;; \bhow\s+much\s+(should\s+i\s+|to\s+)charge\b
# priority: 2
import re
from _lib import args_text, fail
t = args_text().lower().replace(",", "")
def grab(*names, default=None):
    for n in names:
        m = re.search(n + r"\D{0,15}?(\d+(?:\.\d+)?)", t)
        if m:
            return float(m.group(1))
    return default
inc = grab(r"income", r"want", r"target", r"salary", r"earn")
exp = grab(r"expenses?", r"costs?", r"overheads?", default=0.0)
hrs = grab(r"hours?", r"hrs", default=25.0)
off = grab(r"weeks?\s*off", r"holidays?", r"vacation", default=6.0)
tax = grab(r"tax", default=0.0)
if inc is None:
    fail("Usage: freelance rate income 4000 expenses 800 hours 25 weeks off 6 [tax 20]   (income = what you want to take home per month)")
if not (0 < hrs <= 80 and 0 <= off <= 40 and 0 <= tax < 80 and inc > 0 and exp >= 0):
    fail("Check the values: hours per week 1-80, weeks off 0-40, tax 0-79%.")
yearly = (inc / (1 - tax / 100) + exp) * 12
billable = hrs * (52 - off)
hourly = yearly / billable
print(f"To take home {inc:,.2f} a month" + (f" after {tax:g}% tax" if tax else "") + f" with {exp:,.2f} monthly costs:")
print(f"  Needed per year : {yearly:,.2f}")
print(f"  Billable hours  : {billable:,.0f} a year ({hrs:g} a week, {52 - off:g} weeks)")
print(f"  Hourly rate     : {hourly:,.2f}")
print(f"  Day rate (8 h)  : {hourly * 8:,.2f}")
print("  (Only billable hours count; admin, sales and learning time are the reason the rate looks high.)")
