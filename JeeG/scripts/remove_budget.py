# keywords: remove budget, delete budget, clear budget, drop budget
# desc: Remove a category budget (remove budget food)
# category: money
# usage: remove budget <category>
# rawargs: yes
from _lib import args_text, fail
from _store import load, save
from _files import drop_tokens
c = drop_tokens(args_text().lower(), {"remove", "delete", "clear", "drop", "budget", "for", "the"}).strip()
b = load("budgets.json", {})
if c not in b: fail(f"No budget for '{c}'. See: budget report")
del b[c]; save("budgets.json", b); print(f"Removed the budget for {c}.")
