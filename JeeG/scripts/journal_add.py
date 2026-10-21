# keywords: journal, diary, dear diary, log my day, write journal, daily log, journal entry, add journal
# desc: Add a dated diary entry (journal had a great day)
# category: journal
# usage: journal add <text>
# rawargs: yes
import time
from _lib import args_text, data_dir, fail
t = args_text()
if not t:
    fail("Usage: journal add <what happened>")
with open(data_dir() / "journal.txt", "a", encoding="utf-8") as f:
    f.write(f"{time.strftime('%Y-%m-%d %H:%M')}  {t}\n")
print("Saved to your journal.")
