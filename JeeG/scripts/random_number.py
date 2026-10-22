# keywords: random, number, random number, pick a number, between, lottery, rand
# desc: Random number (random number 1 to 50)
# category: utility
# usage: random number [min] [max]
# rawargs: yes
import random, re
from _lib import args_text, fail
nums = [int(x) for x in re.findall(r"-?\d+", args_text())]
lo, hi = (1, 100) if not nums else tuple(sorted((1, nums[0]))) if len(nums) == 1 else sorted(nums[:2])
if hi - lo > 10**12:
    fail("Range too large.")
print(random.SystemRandom().randint(lo, hi), f"  (between {lo} and {hi})")
