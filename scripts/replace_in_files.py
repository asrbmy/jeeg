# keywords: replace in files, replace text in files, bulk replace text, change text in many files, replace word in files
# desc: Find and replace text in all text files of a folder, with a backup (replace in files docs "old" with "new").
# category: files
# usage: replace in files <folder> "old" with "new" [preview]
# confirm: yes
# rawargs: full
# patterns: \breplace\s+in\s+files?\b ;; \bfind\s+and\s+replace\b.*\bfiles?\b
# priority: 1
import re, shutil, time
from pathlib import Path
from _lib import args_text, fail, data_dir
from _files import resolve_folder, walk_files
t = args_text()
preview = bool(re.search(r"\b(preview|dry-run|dryrun)\b", t, re.I))
t = re.sub(r"\s*\b(preview|dry-run|dryrun)\b\s*", " ", t, flags=re.I).strip()
m = re.search(r'replace\s+in\s+files?\s+(.+?)\s+(?:"([^"]+)"|\'([^\']+)\')\s+with\s+(?:"([^"]*)"|\'([^\']*)\')\s*$', t, re.I)
if not m:
    fail('Usage: replace in files <folder> "old text" with "new text"   (quotes needed; a backup is saved first)')
folder, old, new = resolve_folder(m.group(1)), m.group(2) or m.group(3), m.group(4) if m.group(4) is not None else m.group(5)
if not folder.is_dir():
    fail("Give a folder, e.g. replace in files docs \"colour\" with \"color\"")
if len(old) < 2:
    fail("The text to find must be at least 2 characters.")
TEXT = {".txt", ".md", ".py", ".js", ".ts", ".html", ".htm", ".css", ".json", ".csv", ".xml", ".yaml", ".yml", ".ini", ".cfg", ".toml", ".rst", ".tex", ".sh", ".bat", ".sql", ".log"}
hits = []
for f, st in walk_files(folder, seconds=20):
    p = Path(f)
    if p.is_symlink() or p.suffix.lower() not in TEXT or st.st_size > 2 * 1024 * 1024:     # never write through a link
        continue
    try:
        s = p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    n = s.count(old)
    if n:
        hits.append((p, n, s))
if not hits:
    print("Nothing found, so nothing changed.")
    raise SystemExit(0)
if len(hits) > 500:
    fail(f"{len(hits)} files match; narrow it down with a smaller folder.")
if preview:
    for p, n, s in hits:
        print(f"  {p.relative_to(folder)}: {n} place(s) would change")
    print(f"Preview: {sum(n for _, n, _ in hits)} place(s) in {len(hits)} file(s) would change. Nothing was changed.")
    raise SystemExit(0)
bk = data_dir() / "replace_backup" / time.strftime("%Y%m%d_%H%M%S")
total = 0
for p, n, s in hits:
    dst = bk / p.relative_to(folder)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dst)
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(s.replace(old, new))
    total += n
    print(f"  {p.relative_to(folder)}: {n} change(s)")
print(f"Replaced {total} place(s) in {len(hits)} file(s). Originals saved in {bk}")
