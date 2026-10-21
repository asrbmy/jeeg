# keywords: note, add note, take note, save note, remember, jot, write down, memo, new note
# desc: Save a quick note (note add call dentist at 5)
# category: productivity
# usage: add note <text>
import time
from _lib import args_text, data_dir, fail
text = args_text()
if not text:
    fail("Usage: add note <text>")
with open(data_dir() / "notes.txt", "a", encoding="utf-8") as f:
    f.write(f"{time.strftime('%Y-%m-%d %H:%M')}  {text}\n")
print("Note saved.")
