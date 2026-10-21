# keywords: remove bill, delete bill, cancel bill, forget bill, stop bill reminder
# desc: Delete a saved bill (remove bill electricity)
# category: money
# usage: remove bill <name>
# rawargs: yes
# patterns: ^\s*(please\s+)?(remove|delete|cancel|forget|stop)\s+(the\s+|my\s+)?bill\b
import re
from _lib import args_text, fail
from _store import load, save
n = " ".join(re.sub(r"\b(remove|delete|bill|the|forget)\b", " ", args_text(), flags=re.I).split()).lower()
b = load("bills.json", {})
if n not in b: fail("No such bill. Saved: " + (", ".join(b) or "none"))
del b[n]; save("bills.json", b)
print(f"Removed '{n}'.")
