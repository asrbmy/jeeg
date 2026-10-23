# keywords: dice, roll, die, d6, d20, roll dice, ludo
# desc: Roll dice (roll dice, roll 2d6, roll d20)
# category: utility
# usage: roll <n>d<sides>
# rawargs: yes
import random, re
from _lib import args_text, fail
t = args_text().lower()
m = re.search(r"(\d*)\s*d\s*(\d+)", t)
if m:
    count, sides = int(m.group(1) or 1), int(m.group(2))
else:
    n = re.search(r"\d+", t)
    count, sides = (int(n.group()) if n else 1), 6
if not (1 <= count <= 100 and 2 <= sides <= 1000):
    fail("Use 1-100 dice with 2-1000 sides, e.g. roll 2d6")
r = [random.SystemRandom().randint(1, sides) for _ in range(count)]
print(f"{count}d{sides}: {r}" + (f"  total {sum(r)}" if count > 1 else ""))
