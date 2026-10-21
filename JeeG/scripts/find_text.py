# keywords: find text, search in files, grep, find in files, search inside files, text in files, search contents, which file contains, files containing
# desc: Search inside text files for a phrase (find text invoice in documents)
# category: files
# usage: find text <words> in <folder>
# rawargs: full
# patterns: \bfind text\b ;; \b(find|search|look)\b.*\b(in|inside) (the )?(files|text files)\b ;; \bgrep\b ;; \bfiles? containing\b ;; \bwhich files? (contain|has|have)\b
import os, re
from pathlib import Path
from _lib import args_text, fail
from _files import resolve_folder, walk_files, is_text_file, split_on
t = re.sub(r"^\s*(?:(?:find|search|grep)\s+)?(?:text\s+)?(?:(?:in|inside)\s+(?:the\s+)?files?\s+)?(?:for\s+)?", "", args_text(), flags=re.I)
q = re.search(r'"([^"]+)"', t)
if q:
    needle, rest = q.group(1), (t[:q.start()] + " " + t[q.end():])
    folder = resolve_folder(re.sub(r"\b(in|inside|under|within)\b", " ", rest, flags=re.I).strip())
else:
    needle, where = split_on(t, "in")
    folder = resolve_folder(where)
needle = needle.strip()
if not needle: fail('Usage: find text <words> in <folder>   (use "quotes" for exact text)')
low = needle.lower(); hits = scanned = 0
for path, st in walk_files(folder, seconds=25):
    if st.st_size > 5 * 1024 * 1024 or not is_text_file(path): continue
    scanned += 1
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            for n, line in enumerate(f, 1):
                if low in line.lower():
                    hits += 1
                    if hits <= 40: print(f"{os.path.relpath(path, folder)}:{n}: {line.strip()[:110]}")
    except OSError:
        continue
print(f"{hits} match(es) for '{needle}' in {scanned} text files under {folder}." + (" (showing first 40)" if hits > 40 else ""))
