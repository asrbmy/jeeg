# keywords: pocket money, allowance split, kids allowance, save spend give, children money jars
# desc: Split a child's pocket money into save, spend and give jars (allowance split 500; allowance split 20 save 50 give 10)
# category: money
# usage: allowance split <amount> [save <%>] [give <%>]
# rawargs: yes
import re
import sys

t = " ".join(sys.argv[1:]).lower()
m = re.search(r"(\d+(?:\.\d+)?)", re.sub(r"(save|give|spend)\D{0,6}\d+(?:\.\d+)?\s*%?", " ", t))
if not m:
    sys.exit("Usage: allowance split 500   (optional: save 50 give 10 - percentages; the rest is for spending)")
amt = float(m.group(1))
def pct(w, d):
    x = re.search(w + r"\D{0,6}(\d+(?:\.\d+)?)", t)
    return float(x.group(1)) if x else d
save, give = pct("save", 40), pct("give", 10)
if save < 0 or give < 0 or save + give > 100 or amt <= 0:
    sys.exit("Percentages must add up to 100 or less.")
spend = 100 - save - give
print(f"Pocket money {amt:,.2f}:")
for name, p in (("Save", save), ("Spend", spend), ("Give", give)):
    print(f"  {name:<6} {p:>5.1f}%   {amt * p / 100:>10,.2f}")
print("Tip: three labelled jars make the idea real for a child.")
