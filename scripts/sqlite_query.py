# keywords: sqlite, query database, database tables, sql query, read database, open database, db file, select from
# desc: Look inside a SQLite database file, read-only (database tables shop.db, query database shop.db select * from sales limit 5)
# category: data
# usage: database tables <file.db> | query database <file.db> <select ...>
# rawargs: full
# patterns: \b(?:query|open|read|look\s+(?:in|inside))\s+(?:the\s+)?(?:sqlite\s+)?(?:database|db)\b ;; \bdatabase\s+(?:tables|schema)\b ;; \bsqlite\s+(?:query|select|tables)\b
# priority: 4
import os, re, sqlite3
from pathlib import Path
from _lib import args_text, fail, safe_is_file

t = args_text().strip()
m = re.match(r"^(?:query|open|read|look\s+(?:in|inside))?\s*(?:the\s+)?(?:sqlite\s+)?(?:database|db)?\s*(tables|schema)?\s*(?:of\s+|in\s+)?(\"[^\"]+\"|'[^']+'|\S+\.(?:db|sqlite3?|sqlite))\s*(.*)$", t, re.I | re.S)
if not m:
    fail("Try:  database tables shop.db     or     query database shop.db select * from sales limit 5")
what, path, sql = (m.group(1) or "").lower(), m.group(2).strip("\"'"), m.group(3).strip().rstrip(";")
p = Path(os.path.expanduser(path))
if not safe_is_file(p):
    fail(f"No file named {path} here.")
with open(p, "rb") as f:
    if f.read(16) != b"SQLite format 3\x00":
        fail("That is not a SQLite database file.")
sql = re.sub(r"^(?:run|show|query|select\s+rows)\s+", "", sql, flags=re.I) if sql and not sql.lower().startswith("select") else sql
con = sqlite3.connect("file:" + p.resolve().as_posix().replace("?", "%3f").replace("#", "%23") + "?mode=ro", uri=True, timeout=5)


def deny(action, a1, a2, db, src):                      # only reading is allowed, whatever the SQL says
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
    if action == sqlite3.SQLITE_PRAGMA and (a1 or "").lower() in {"table_info", "table_xinfo"}:      # the column list, read-only
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY


con.set_authorizer(deny)
try:
    if what in {"tables", "schema"} or not sql:
        rows = con.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
        if not rows:
            print("The database has no tables.")
        for name, typ in rows:
            quoted = '"' + name.replace('"', '""') + '"'
            n = ""
            if typ == "table":
                try:
                    n = "  (%d rows)" % con.execute("SELECT COUNT(*) FROM " + quoted).fetchone()[0]
                except sqlite3.Error:
                    pass
            cols = [c[1] for c in con.execute("PRAGMA table_info(" + quoted + ")")]
            print("%s%s: %s" % (name, n, ", ".join(cols)))
        raise SystemExit(0)
    if not re.match(r"^\s*(select|with)\b", sql, re.I):
        fail("Only reading is allowed: start with SELECT.")
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description or []]
    rows = cur.fetchmany(201)
except sqlite3.Error as ex:
    fail(f"The database said: {ex}")
more = len(rows) > 200
rows = rows[:200]
cells = [[("" if v is None else str(v))[:40] for v in r] for r in rows]
w = [max([len(c)] + [len(r[i]) for r in cells]) for i, c in enumerate(cols)]
print("  ".join(c.ljust(w[i]) for i, c in enumerate(cols)))
print("  ".join("-" * x for x in w))
for r in cells:
    print("  ".join(v.ljust(w[i]) for i, v in enumerate(r)))
print(f"{len(rows)} row(s)" + ("  (stopped at 200; add LIMIT to choose)" if more else ""))
