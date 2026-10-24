# keywords: reading list, add book, books, book list, finished book, finished reading, read book, books to read, my books
# desc: Keep a list of books to read and finished (add book Atomic Habits, books, finished book atomic habits)
# category: personal
# usage: add book <title> | books | finished book <title> | remove book <title>
# rawargs: full
# patterns: \bread(ing)?\s+list\b ;; \badd\s+(a\s+)?book\b ;; \b(finished|completed)\s+(reading\s+)?(the\s+)?book\b ;; ^\s*books\s*$ ;; \bmy\s+books\b ;; \bbooks\s+to\s+read\b
# priority: 2
import datetime, re
from _lib import args_text, fail
from _store import load, save
t = args_text().strip()
books = load("books.json", [])
low = t.lower()
m = re.match(r"^\s*(?:i\s+)?(?:finished|completed|read)\s+(?:reading\s+)?(?:the\s+)?(?:book\s+)?(.+)$", t, re.I)
if m:
    key = m.group(1).lower().strip()
    hit = [b for b in books if key and (key in b["title"].lower() or b["title"].lower() in key)]
    if len(hit) != 1: fail("Say which book: " + (", ".join(b["title"] for b in books if not b.get("done")) or "(none on your list)"))
    hit[0]["done"] = datetime.date.today().isoformat(); save("books.json", books)
    print(f"Marked as finished: {hit[0]['title']}. Well done.")
    raise SystemExit(0)
m = re.match(r"^\s*(?:add|save|new)\s+(?:a\s+)?(?:book|to\s+(?:my\s+)?reading\s+list)\s*:?\s*(.+)$", t, re.I) or re.match(r"^\s*(?:add|save)\s+(.+?)\s+to\s+(?:my\s+)?(?:reading\s+list|books)\s*$", t, re.I)
if m:
    title = " ".join(m.group(1).split())[:80]
    if not title: fail("Usage: add book <title>")
    if any(b["title"].lower() == title.lower() for b in books): fail("That book is already on your list.")
    if len(books) >= 500: fail("The list is full (500 books).")
    books.append({"title": title, "added": datetime.date.today().isoformat(), "done": None}); save("books.json", books)
    print(f"Added: {title}. {sum(1 for b in books if not b.get('done'))} book(s) to read.")
    raise SystemExit(0)
m = re.match(r"^\s*(?:remove|delete)\s+(?:book\s+)?(.+)$", t, re.I)
if m:
    key = m.group(1).lower().strip()
    hit = [b for b in books if key in b["title"].lower()]
    if len(hit) != 1: fail("Say which book to remove.")
    books.remove(hit[0]); save("books.json", books); print(f"Removed {hit[0]['title']}."); raise SystemExit(0)
if not books: fail("Your list is empty. Example:  add book Atomic Habits")
todo = [b for b in books if not b.get("done")]
done = [b for b in books if b.get("done")]
print(f"To read ({len(todo)}):")
for b in todo: print(f"  [ ] {b['title']}")
if done:
    print(f"Finished ({len(done)}):")
    for b in sorted(done, key=lambda x: x["done"])[-8:]: print(f"  [x] {b['title']}  ({b['done']})")
