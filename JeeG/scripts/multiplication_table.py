# keywords: multiplication table, times table, table of, maths table, tables, print table, multiply table, pahada
# desc: Print a multiplication table (table of 7, multiplication table 12 up to 20)
# category: fun
# usage: multiplication table <n> [up to <m>]
# rawargs: yes
import re
from _lib import args_text, fail
t = args_text().lower()
nums = [int(x) for x in re.findall(r"\d+", t)]
if not nums: fail("Usage: multiplication table <number> [up to <n>]   e.g. table of 7 up to 20")
n = nums[0]; upto = nums[1] if len(nums) > 1 else 10
if n > 10 ** 9 or not 1 <= upto <= 100: fail("Use a number up to 1,000,000,000 and 'up to' between 1 and 100.")
for i in range(1, upto + 1): print(f"{n} x {i:>{len(str(upto))}} = {n * i:,}")
