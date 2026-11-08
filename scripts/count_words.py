# keywords: word count, count words, characters, lines, length, how many words, text statistics, wc
# desc: Count words, lines and characters in text or a file
# category: utility
# usage: count words <text|file>
# stdin: yes
from pathlib import Path
from _lib import args_or_stdin, fail, safe_is_file
t = args_or_stdin()
if not t:
    fail("Usage: count words <text or file path>")
p = Path(t.strip('"\'')[:1000]).expanduser() if len(t) < 1000 else Path('.nofile')
if safe_is_file(p):
    if p.stat().st_size > 50_000_000: fail("File is larger than 50 MB.")
    data = p.read_text(encoding="utf-8", errors="replace"); print(f"File: {p}")
else:
    data = t
print(f"Words: {len(data.split()):,}   Lines: {len(data.splitlines()) or 1:,}   Characters: {len(data):,}")
