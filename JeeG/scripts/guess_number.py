# keywords: guess the number, guess number, number game, guessing game, play guess, higher or lower, number guessing
# desc: Play 'guess the number' (guess number, or guess number 1000)
# category: fun
# usage: guess number [max]
# rawargs: yes
import random, re
from _lib import args_text
m = re.search(r"\d+", args_text())
hi = max(10, min(int(m.group()), 1000000)) if m else 100
secret = random.SystemRandom().randint(1, hi)
import math
tries = max(5, math.ceil(math.log2(hi)) + 1)
print(f"I picked a number from 1 to {hi:,}. You have {tries} tries. (q to quit)")
for i in range(1, tries + 1):
    try: s = input(f"Guess {i}/{tries}: ").strip().lower()
    except (EOFError, KeyboardInterrupt): print(); break
    if s in ("q", "quit", "exit"): break
    if not re.fullmatch(r"\d+", s): print("  Type a whole number."); continue
    g = int(s)
    if g == secret: print(f"Correct! You got it in {i} tries."); break
    print("  higher" if g < secret else "  lower")
else:
    print(f"Out of tries. It was {secret}.")
