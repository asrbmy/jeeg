# keywords: clear todos, clear done, remove completed, clean todo, delete done todos, tidy
# desc: Remove finished items from the to-do list
# category: productivity
import json
from _lib import data_dir
f = data_dir() / "todos.json"
items = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
keep = [i for i in items if not i["done"]]
f.write_text(json.dumps(keep, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Removed {len(items) - len(keep)} finished items; {len(keep)} left.")
