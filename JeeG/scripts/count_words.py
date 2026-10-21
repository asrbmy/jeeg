# keywords: word count, count words, characters, lines, length, how many words, text statistics, wc
# desc: Count words, lines and characters in text or a file
# category: utility
# usage: count words <text|file>
from pathlib import Path
from _lib import args_text, fail
t = args_text()
if not t:
    fail("Usage: count words <text or file path>")
p = Path(t.strip('"\'')).expanduser()
if p.is_file():
    if p.stat().st_size > 50_000_000: fail("File is larger than 50 MB.")
    data = p.read_text(encoding="utf-8", errors="replace"); print(f"File: {p}")
else:
    data = t
print(f"Words: {len(data.split()):,}   Lines: {len(data.splitlines()) or 1:,}   Characters: {len(data):,}")
