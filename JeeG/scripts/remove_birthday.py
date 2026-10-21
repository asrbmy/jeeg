# keywords: remove birthday, delete birthday, forget birthday, remove anniversary
# desc: Delete a saved birthday
# category: birthdays
# usage: remove birthday <name>
# rawargs: yes
from _lib import args_text, fail
from _store import load, save
n = args_text().strip().lower()
b = load("birthdays.json", {})
if n not in b:
    fail("No birthday saved with exactly that name.")
del b[n]; save("birthdays.json", b); print(f"Removed {n.title()}.")
