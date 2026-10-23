# keywords: add bill, bill reminder, monthly bill, due date bill, remember bill, recurring bill, save bill
# desc: Remember a monthly bill's due day (add bill electricity 15 1200)
# category: money
# usage: add bill <name> <day> [amount]
# rawargs: yes
import re
from _lib import args_text, fail
from _store import load, save
t = re.sub(r"\b(add|bill|save|remember|due|on|the|of|rs|rent|reminder)\b(?=.*\d)", lambda m: m.group(0) if m.group(0) == "rent" else " ", args_text(), flags=re.I)
nums = re.findall(r"\d+(?:\.\d+)?", t)
if not nums: fail("Usage: add bill <name> <day of month> [amount]    e.g. add bill electricity 15 1200")
if not abs(float(nums[0])) < 1e6: fail("The day of the month must be between 1 and 31.")
day = int(float(nums[0]))
if not 1 <= day <= 31: fail("The day of the month must be between 1 and 31.")
amount = float(nums[1].replace(",", "")) if len(nums) > 1 else None
name = " ".join(re.sub(r"\d+(?:\.\d+)?(?:st|nd|rd|th)?", " ", t).split()).lower()
if re.search(r"(?<![\w])-\d", t): fail("Negative numbers are not allowed here.")
if not re.search(r"[a-z]", name): fail("Give the bill a name too: add bill electricity 15 1200")
if amount is not None and amount > 1e10: fail("That amount is too large.")
if not name: fail("Give the bill a name, e.g. add bill electricity 15")
b = load("bills.json", {})
b[name] = {"day": day, "amount": amount}
save("bills.json", b)
print(f"Saved bill '{name}': due on day {day} of every month" + (f", about Rs {amount:,.0f}" if amount else "") + ".  See them with: upcoming bills")
