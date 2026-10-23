# keywords: shopping clear, clear shopping list, empty shopping list, clear groceries, reset shopping, start over
# desc: Clear the whole shopping list
# category: lists
# confirm: yes
from _store import save
save("shopping.json", [])
print("Shopping list cleared.")
