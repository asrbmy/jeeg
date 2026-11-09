# keywords: index lookup, indexed files, fulltext, full text search, inside files, file contents lookup
# desc: Search the text inside your indexed files, best matches first, with a snippet (search index invoice march).
# category: files
# usage: search index <words>
# rawargs: full
# patterns: ^\s*search\s+(my\s+)?(the\s+)?index(ed)?\b ;; ^\s*(search|find)\s+(inside|in)\s+(my\s+)?(indexed\s+)?(files|documents|docs)\s+for\b ;; \bfull\s*text\s+search\b ;; ^\s*index\s+(search|find)\b
# priority: 2
import os, re, sqlite3, time, zipfile
from pathlib import Path
from _lib import data_dir, fail, human
DB = data_dir() / "search_index.db"
TEXT = {".txt", ".md", ".markdown", ".rst", ".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".htm", ".css", ".json", ".csv", ".tsv", ".xml",
        ".yaml", ".yml", ".ini", ".cfg", ".toml", ".tex", ".sh", ".bat", ".ps1", ".sql", ".log", ".java", ".c", ".h", ".cpp", ".go", ".rs", ".rb", ".php", ".docx"}
SKIP_DIRS = {".git", ".svn", ".hg", "node_modules", "__pycache__", ".venv", "venv", "env", ".idea", ".vscode", "dist", "build", "site-packages", ".cache", ".ssh", ".gnupg", ".aws"}
SECRET = re.compile(r"(^\.env|\.pem$|\.key$|\.p12$|\.pfx$|\.kdbx$|^id_(rsa|dsa|ecdsa|ed25519)|secret|password|passwd|token|credential|\.netrc$|\.npmrc$|\.pypirc$)", re.I)
MAX_FILE = 2 * 1024 * 1024
MAX_FILES = 20000
def connect():
    con = sqlite3.connect(str(DB))
    try:
        con.execute("CREATE TABLE IF NOT EXISTS files(id INTEGER PRIMARY KEY, path TEXT UNIQUE, folder TEXT, mtime REAL, size INTEGER)")
        con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS docs USING fts5(body, tokenize='unicode61 remove_diacritics 2')")
    except sqlite3.OperationalError:
        con.close()
        fail("This Python's SQLite has no full-text search (FTS5), so the search index cannot be used here.")
    try:
        os.chmod(DB, 0o600)
    except OSError:
        pass
    return con
def docx_text(p):
    with zipfile.ZipFile(p) as z:
        info = z.getinfo("word/document.xml")
        if info.file_size > 20 * 1024 * 1024:
            return ""
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    return re.sub(r"<[^>]+>", "", xml)
def read_text(p):
    if p.suffix.lower() == ".docx":
        return docx_text(p)
    raw = p.read_bytes()
    if b"\x00" in raw[:4096]:
        return ""
    s = raw.decode("utf-8", "replace")
    if p.suffix.lower() in {".html", ".htm", ".xml"}:
        s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
        s = re.sub(r"<[^>]+>", " ", s)
    return s

from _lib import args_text
t = args_text()
t = re.sub(r"^\s*(?:search|find|look)\s+(?:in\s+|inside\s+|through\s+)?(?:my\s+)?(?:the\s+)?(?:index(?:ed)?(?:\s+files)?|indexed\s+files|documents|files|docs)?\s*(?:for)?\s*", "", t, flags=re.I)
t = re.sub(r"^\s*index\s+(?:search|find)\s*", "", t, flags=re.I)
words = [w_ for w_ in re.findall(r"[^\W_]{2,}", t.lower(), re.U)][:8]
if not words:
    fail("Usage: search index <words>   (index a folder first:  index folder Documents)")
if not DB.exists():
    fail("Nothing is indexed yet. Try:  index folder Documents")
con = connect()
q = " ".join('"' + w_ + '"' for w_ in words[:-1]) + (" " if len(words) > 1 else "") + '"' + words[-1] + '"*'
try:
    rows = con.execute("SELECT f.path, snippet(docs, 0, '[', ']', ' ... ', 14), bm25(docs) AS r FROM docs JOIN files f ON f.id = docs.rowid "
                       "WHERE docs MATCH ? ORDER BY r LIMIT 10", (q,)).fetchall()
except sqlite3.OperationalError:
    fail("I could not search for that. Use plain words.")
if not rows:
    n = con.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    print(f"No matches for: {' '.join(words)}   ({n:,} files indexed; run  index update  if files changed)")
    raise SystemExit(0)
print(f"{len(rows)} best match(es) for: {' '.join(words)}")
for path, snip, _ in rows:
    snip = re.sub(r"\s+", " ", snip).strip()
    print(f"\n  {path}\n    {snip[:200]}")
