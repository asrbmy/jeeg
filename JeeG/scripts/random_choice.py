# keywords: choose, pick, decide, choice, random choice, either, help me decide, which one
# desc: Pick one option at random (random choice pizza, burger, pasta)
# category: utility
# usage: random choice a, b, c
# rawargs: yes
import random, re
from _lib import args_text, fail
t = re.sub(r"^(between|from|of|out of)\s+", "", args_text().strip(), flags=re.I)
opts = [o.strip() for o in re.split(r",|\s+or\s+|\s*/\s*|\s*\|\s*", t) if o.strip()]
if len(opts) < 2:
    fail("Give at least two options separated by commas or 'or', e.g. random choice pizza, burger, pasta")
print("->", random.SystemRandom().choice(opts))
