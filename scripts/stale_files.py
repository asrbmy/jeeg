# keywords: stale files, old files, free up space, files not used, unused files, space hogs, not touched, clean up space, unused big files
# desc: Find big files you have not touched for a long time (old large files 100 mb 1 year in downloads)
# category: files
# usage: old large files [size] [age] [folder]
# rawargs: yes
# patterns: \bold\b.*\b(large|big)\b.*\bfiles?\b ;; \b(large|big)\b.*\bold\b.*\bfiles?\b ;; \bstale files?\b ;; \bfree up space\b
import re, time
from _lib import args_text, human
from _files import resolve_folder, walk_files
t = args_text()
sz = re.search(r"(\d+(?:\.\d+)?)\s*(kb|mb|gb)\b", t, re.I)
mb = float(sz.group(1)) * {"kb": 1 / 1024, "mb": 1, "gb": 1024}[sz.group(2).lower()] if sz else 100.0
ag = re.search(r"(\d+)\s*(day|week|month|year)s?\b", t, re.I)
days = int(ag.group(1)) * {"day": 1, "week": 7, "month": 30, "year": 365}[ag.group(2).lower()] if ag else 180
from _files import drop_tokens
t2 = re.sub(r"(\d+(?:\.\d+)?)\s*(kb|mb|gb|days?|weeks?|months?|years?)\b", " ", t, flags=re.I)
t2 = drop_tokens(t2, {"old", "large", "big", "file", "files", "older", "than", "in", "over", "bigger", "not", "touched", "for", "stale", "unused", "find", "show"})
folder = resolve_folder(t2.strip() or "downloads")
cut = time.time() - days * 86400
rows = [(st.st_size, st.st_mtime, p) for p, st in walk_files(folder, seconds=30) if st.st_size >= mb * 1048576 and st.st_mtime < cut]
rows.sort(reverse=True)
for s_, mt, p in rows[:30]: print(f"  {human(s_):>9}   {(time.time() - mt) / 86400:>5.0f} days   {p}")
print(f"{len(rows)} file(s) over {mb:g} MB and older than {days} days in {folder}; total {human(sum(r[0] for r in rows))}. Nothing was changed.")
