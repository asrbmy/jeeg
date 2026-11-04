# keywords: study plan, study planner, plan my study, exam plan, revision plan, study schedule hours
# desc: Plan study hours per day (study plan 5 subjects 20 days 6 hours)
# category: study
# usage: study plan <n> subjects <n> days <n> hours
# rawargs: yes
# patterns: \bstudy\s+(plan|planner|schedule)\b ;; \b(revision|exam)\s+plan\b
# priority: 2
import re
from _lib import args_text, fail
t = args_text().lower()
def pick(pat):
    m = re.search(pat, t)
    return float(m.group(1)) if m else None
subj, days, hrs = pick(r"(\d+(?:\.\d+)?)\s*subjects?"), pick(r"(\d+(?:\.\d+)?)\s*days?"), pick(r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|h)\b")
if not (subj and days and hrs) or min(subj, days, hrs) <= 0 or hrs > 24:
    fail("Usage: study plan 5 subjects 20 days 6 hours   (hours = study time per day)")
rev = max(1, round(days * 0.2))
learn = days - rev
total = days * hrs
per = total / subj
print(f"{subj:g} subjects, {days:g} days, {hrs:g} h a day = {total:g} hours in all ({per:.1f} h per subject)")
print(f"  First {learn:g} days: learn new topics, about {hrs * learn / subj:.1f} h on each subject")
print(f"  Last {rev:g} days: revision and past papers only")
print(f"  Each day: about {hrs / min(subj, 3):.1f} h blocks, 3 subjects at most, with a 10 minute break every hour.")
