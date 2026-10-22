# keywords: remove countdown, delete countdown, clear countdown, stop countdown
# desc: Delete a countdown (remove countdown exam)
# category: reminders
# usage: remove countdown <event>
# rawargs: yes
from _lib import args_text, fail
from _store import load, save
from _files import drop_tokens
n = drop_tokens(args_text().lower(), {"remove", "delete", "clear", "stop", "countdown", "the"}).strip()
c = load("countdowns.json", [])
k = [x for x in c if x["name"] != n]
if len(k) == len(c): fail(f"No countdown named '{n}'. See: show countdowns")
save("countdowns.json", k); print(f"Removed {n}.")
