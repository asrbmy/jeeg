# keywords: show journal, read journal, my journal, past entries, diary entries, journal history, search journal
# desc: Read your journal (last 7 days; or a number of days, or a word to search)
# category: journal
# usage: journal show [days|word]
# rawargs: yes
import datetime, re
from _lib import args_text, data_dir
f = data_dir() / "journal.txt"
lines = f.read_text(encoding="utf-8").splitlines() if f.exists() else []
q = args_text().strip().lower()
m = re.fullmatch(r"(?:last\s+)?(\d+)(?:\s*days?)?", q)
if m or not q:
    cut = (datetime.date.today() - datetime.timedelta(days=min(int(m.group(1)), 36500) if m else 7)).isoformat()
    lines = [l for l in lines if l[:10] >= cut]
else:
    lines = [l for l in lines if q in l.lower()]
print("\n".join(lines[-60:]) if lines else "No journal entries found.")
