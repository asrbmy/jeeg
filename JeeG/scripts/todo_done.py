# keywords: todo done, done, finish, complete, completed, tick, mark done, check off, finished
# desc: Mark a to-do done (todo done 3, or part of its text)
# category: productivity
# usage: todo done <number|text>
import json, re
from _lib import args_text, data_dir, fail
q = args_text().strip()
f = data_dir() / "todos.json"
items = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
if not q:
    fail("Usage: todo done <number or words from the item>")
ids = {int(x) for x in re.findall(r"\d+", q)} if re.fullmatch(r"[\d\s,]+", q) else set()
hit = [i for i in items if not i["done"] and (i["id"] in ids or (not ids and q.lower() in i["text"].lower()))]
if not hit:
    fail("No matching open item. Use 'todo list' to see numbers.")
if len(hit) > 3 and not ids:
    fail(f"'{q}' matches {len(hit)} items; use the item numbers instead.")
for i in hit:
    i["done"] = True
    print(f"Done: #{i['id']} {i['text']}")
f.write_text(json.dumps(items, indent=1, ensure_ascii=False), encoding="utf-8")
