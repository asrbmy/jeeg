# keywords: todo, to do, add todo, new task, add task, remember to, task list, add item
# desc: Add a to-do item (add todo buy milk)
# category: productivity
# usage: add todo <text>
import json, time
from _lib import args_text, data_dir, fail
text = args_text()
if not text:
    fail("Usage: add todo <what to do>")
f = data_dir() / "todos.json"
items = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
n = max([i["id"] for i in items], default=0) + 1
items.append({"id": n, "text": text, "done": False, "created": time.strftime("%Y-%m-%d %H:%M")})
f.write_text(json.dumps(items, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Added #{n}: {text}")
