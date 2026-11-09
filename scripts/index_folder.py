# keywords: index folder, build index, search index build, index my files, index documents, index status, update index, remove index, full text index
# desc: Build a searchable index of a folder's text files, notes and Word documents (index folder docs; index status; index update; index remove docs). Nothing leaves your computer.
# category: files
# usage: index folder <folder> | index status | index update | index remove <folder>
# rawargs: full
# patterns: ^\s*index\s+(folder|status|update|remove|my|docs|documents|files|list|delete|forget|refresh)\b ;; ^\s*(build|make)\s+(a\s+)?(search\s+)?index\b
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
from _files import resolve_folder
t = args_text().strip()
low = t.lower()
low = re.sub(r"^(?:index|build index of|build an index of)\s*", "", low).strip()
low = re.sub(r"^(?:folder|my files|files)\b\s*", "", low).strip()
t2 = re.sub(r"^\s*(?:index|build index of)\b\s*(?:folder\b\s*)?", "", t, flags=re.I).strip().strip('"\'')
con = connect()
cur = con.cursor()
def status():
    rows = cur.execute("SELECT folder, COUNT(*), COALESCE(SUM(size),0), MAX(mtime) FROM files GROUP BY folder ORDER BY folder").fetchall()
    if not rows:
        print("Nothing is indexed yet. Try:  index folder Documents"); return
    for f, n, sz, _ in rows:
        print(f"  {f}   {n:,} files, {human(sz)} of text")
    print(f"Index file: {DB} ({human(DB.stat().st_size)}). Search it with:  search index <words>")
if low in {"status", "list", ""} and not t2.strip("."):
    status(); raise SystemExit(0)
if low == "status" or low == "list":
    status(); raise SystemExit(0)
if low.startswith("remove") or low.startswith("delete") or low.startswith("forget"):
    target = re.sub(r"^(?:remove|delete|forget)\s+(?:folder\s+)?", "", t2 if t2 else low, flags=re.I).strip()
    if target.lower() in {"all", "everything"}:
        ids = [r[0] for r in cur.execute("SELECT id FROM files")]
        folder = "all folders"
    else:
        folder = str(resolve_folder(target))
        ids = [r[0] for r in cur.execute("SELECT id FROM files WHERE folder = ?", (folder,))]
    for i in ids:
        cur.execute("DELETE FROM docs WHERE rowid = ?", (i,)); cur.execute("DELETE FROM files WHERE id = ?", (i,))
    con.commit()
    print(f"Removed {len(ids):,} file(s) of {folder} from the index (your files were not touched).")
    raise SystemExit(0)
if low.startswith("update") or low.startswith("refresh"):
    folders = [r[0] for r in cur.execute("SELECT DISTINCT folder FROM files")]
    if not folders:
        fail("Nothing is indexed yet. Try:  index folder Documents")
else:
    target = t2.strip()
    if not target:
        fail("Usage: index folder <folder>   (also: index status, index update, index remove <folder>)")
    f = resolve_folder(target)
    if not f.is_dir():
        fail("That folder was not found.")
    folders = [str(f)]
added = changed = removed = skipped = 0
started = time.time()
for folder in folders:
    base = Path(folder)
    if not base.is_dir():
        continue
    seen = set()
    count = 0
    for root, dirs, files in os.walk(base, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".") and not os.path.islink(os.path.join(root, d))]
        for fn in files:
            p = Path(root, fn)
            if p.suffix.lower() not in TEXT or SECRET.search(fn):
                continue
            try:
                if p.is_symlink():
                    continue
                st = p.stat()
            except OSError:
                continue
            if st.st_size > (20 * 1024 * 1024 if p.suffix.lower() == ".docx" else MAX_FILE):
                skipped += 1; continue
            count += 1
            if count > MAX_FILES:
                break
            key = str(p)
            seen.add(key)
            row = cur.execute("SELECT id, mtime, size FROM files WHERE path = ?", (key,)).fetchone()
            if row and abs(row[1] - st.st_mtime) < 1e-6 and row[2] == st.st_size:
                continue
            try:
                body = read_text(p)[:MAX_FILE]
            except (OSError, zipfile.BadZipFile, KeyError, ValueError):
                skipped += 1; continue
            if not body.strip():
                continue
            if row:
                cur.execute("UPDATE files SET mtime = ?, size = ? WHERE id = ?", (st.st_mtime, st.st_size, row[0]))
                cur.execute("DELETE FROM docs WHERE rowid = ?", (row[0],))
                cur.execute("INSERT INTO docs(rowid, body) VALUES (?, ?)", (row[0], body))
                changed += 1
            else:
                cur.execute("INSERT INTO files(path, folder, mtime, size) VALUES (?, ?, ?, ?)", (key, folder, st.st_mtime, st.st_size))
                cur.execute("INSERT INTO docs(rowid, body) VALUES (?, ?)", (cur.lastrowid, body))
                added += 1
            if time.time() - started > 120:
                break
        if count > MAX_FILES or time.time() - started > 120:
            break
    for i, path in cur.execute("SELECT id, path FROM files WHERE folder = ?", (folder,)).fetchall():
        if path not in seen and not (count > MAX_FILES or time.time() - started > 120):
            cur.execute("DELETE FROM docs WHERE rowid = ?", (i,)); cur.execute("DELETE FROM files WHERE id = ?", (i,)); removed += 1
    con.commit()
    if count > MAX_FILES:
        print(f"Stopped at {MAX_FILES:,} files in {folder}; index a smaller folder for the rest.")
    if time.time() - started > 120:
        print("Stopped after 2 minutes; run  index update  to continue.")
total = cur.execute("SELECT COUNT(*) FROM files").fetchone()[0]
print(f"Indexed {', '.join(folders)}: {added:,} new, {changed:,} changed, {removed:,} gone, {skipped:,} skipped. {total:,} files in the index.")
print("Search it with:  search index <words>.  Files that look like secrets (.env, keys, passwords) are never indexed.")
