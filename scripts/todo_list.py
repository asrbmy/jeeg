# keywords: todo list, show todos, my todos, pending, things to do, what do i have to do, to do list, my list, show tasks
# desc: Show your to-do list
# category: productivity
# priority: 1
import json
from _lib import args_text, data_dir
f = data_dir() / "todos.json"
items = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
show_all = "all" in args_text().lower().split()
rows = [i for i in items if show_all or not i["done"]]
if not rows:
    print("Nothing to do - your list is empty.")
for i in rows:
    print(f"  [{'x' if i['done'] else ' '}] {i['id']:>3}  {i['text']}")
print(f"({sum(not i['done'] for i in items)} open, {sum(i['done'] for i in items)} done)")
