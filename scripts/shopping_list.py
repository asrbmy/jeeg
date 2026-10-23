# keywords: show shopping list, shopping list, grocery list, what to buy, my groceries, show groceries, list shopping
# desc: Show the shopping list
# category: lists
# priority: 1
from _store import load
items = load("shopping.json", [])
print("\n".join(f"  {n:>2}. {i}" for n, i in enumerate(items, 1)) if items else "Your shopping list is empty.")
