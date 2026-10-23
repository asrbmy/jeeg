# keywords: tip, tip calculator, calculate tip, how much tip, service charge, bill with tip, tip percentage, gratuity
# desc: Work out a tip and split the bill (tip 1200 10%, tip 2450 12% split 4)
# category: money
# usage: tip <bill> [percent%] [split <people>]
# rawargs: yes
# patterns: ^\s*(please\s+)?(calculate\s+|work out\s+|add\s+)?(a\s+)?(tip|gratuity)\b
import re
from _lib import args_text, fail
from _money import inr
t = args_text().lower().replace(",", "")
sp = re.search(r"(?:split|among|between|by|for)\s+(\d+)", t)
n = int(sp.group(1)) if sp else 1
t2 = t.replace(sp.group(0), " ") if sp else t
pc = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent|pc)", t2)
t3 = t2.replace(pc.group(0), " ") if pc else t2
amt = re.search(r"\d+(?:\.\d+)?", t3)
if not amt: fail("Usage: tip <bill> [percent %] [split <people>]    e.g. tip 1200 10%   or   tip 2450 12% split 4")
bill, pcv = float(amt.group()), float(pc.group(1)) if pc else 10.0
if not (0 < bill < 1e9 and 0 <= pcv <= 100 and 1 <= n <= 1000): fail("Those numbers look wrong.")
tip = bill * pcv / 100
print(f"Bill {inr(bill)} + tip {pcv:g}% ({inr(tip)}) = total {inr(bill + tip)}")
if n > 1: print(f"Split {n} ways: {inr((bill + tip) / n)} each")
