# keywords: shopping remove, remove from shopping, bought, got it, cross off, shopping done, delete item, remove item
# desc: Cross an item off (shopping remove 2, or shopping remove milk)
# category: lists
# usage: shopping remove <n|name>
# rawargs: yes
import re
from _lib import args_text, fail
from _store import load, save
q = args_text().strip().lower()
items = load("shopping.json", [])
if not q:
    fail("Usage: shopping remove <number or name>")
if q.isdigit() and 1 <= int(q) <= len(items):
    gone = items.pop(int(q) - 1)
else:
    hits = [i for i in items if q in i.lower()]
    if len(hits) != 1:
        fail("No unique match. Use the number from 'shopping list'.")
    items.remove(hits[0]); gone = hits[0]
save("shopping.json", items)
print(f"Removed: {gone}")
