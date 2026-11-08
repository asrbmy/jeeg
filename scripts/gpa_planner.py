# keywords: gpa planner, target gpa, gpa needed, required gpa, raise my gpa, what gpa do i need, cgpa target
# desc: What you must score next to reach a target GPA (gpa planner current 3.2 credits 90 target 3.4 next 30)
# category: study
# usage: gpa planner current <gpa> credits <done> target <gpa> next <credits> [scale 10]
# rawargs: yes
# patterns: \bgpa\s+planner\b ;; \b(target|required|needed)\s+(c?gpa)\b ;; \bwhat\s+(c?gpa|score|grade)\s+do\s+i\s+need\b ;; \braise\s+my\s+c?gpa\b
# priority: 3
import re
from _lib import args_text, fail
t = args_text().lower()
def pick(pat):
    m = re.search(pat, t)
    return float(m.group(1)) if m else None
cur = pick(r"(?:current|now|so far|have)\D{0,8}(\d+(?:\.\d+)?)")
done = pick(r"(?:credits?|hours?|subjects?|semesters?)\D{0,6}(\d+(?:\.\d+)?)") or pick(r"(\d+(?:\.\d+)?)\s*(?:credits?|hours?|subjects?|semesters?)\s*(?:done|completed|so far)")
target = pick(r"(?:target|want|goal|reach|get)\D{0,8}(\d+(?:\.\d+)?)")
nxt = pick(r"(?:next|remaining|left|more)\D{0,8}(\d+(?:\.\d+)?)")
scale = pick(r"(?:scale|out of|/)\s*(\d+(?:\.\d+)?)") or (10.0 if (target or 0) > 4.5 or (cur or 0) > 4.5 else 4.0)
if None in (cur, done, target, nxt) or min(done, nxt) <= 0 or not (0 <= cur <= scale and 0 < target <= scale):
    fail("Usage: gpa planner current 3.2 credits 90 target 3.5 next 30   (add 'scale 10' for a 10-point system)\n"
         "  current = your GPA now, credits = credits done so far, next = credits still to take.")
need = (target * (done + nxt) - cur * done) / nxt
print(f"Now {cur:g} over {done:g} credits. To finish on {target:g} after {nxt:g} more credits (scale {scale:g}):")
if need > scale:
    print(f"  You would need {need:.2f}, which is above the maximum of {scale:g}. Not possible in {nxt:g} credits.")
    best = (cur * done + scale * nxt) / (done + nxt)
    print(f"  The best you can reach is {best:.2f}. To hit {target:g} you need about {max(0, (target * done - cur * done) / (scale - target)):.0f} more credits at the maximum.")
elif need <= 0:
    print(f"  You will stay above {target:g} whatever you score.")
else:
    print(f"  You need an average of {need:.2f} in those {nxt:g} credits ({need / scale * 100:.0f}% of the maximum).")
