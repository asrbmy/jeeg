# keywords: shopping, shopping list, add to shopping list, need to buy, add item
# desc: Add items to the shopping list (shopping add milk, eggs and bread)
# category: lists
# usage: shopping add <items>
# rawargs: yes
import re
from _lib import args_text, fail
from _store import load, save
items = [i.strip() for i in re.split(r",|\band\b|\n", args_text(), flags=re.I) if i.strip()]
if not items:
    fail("Usage: shopping add <item>, <item> ...")
cur = load("shopping.json", [])
added = []
for i in items:
    if i.lower() not in (c.lower() for c in cur):
        cur.append(i); added.append(i)
save("shopping.json", cur)
print(f"Added: {', '.join(added)}" if added else "Already on the list.")
