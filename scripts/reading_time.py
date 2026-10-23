# keywords: reading time, how long to read, read time, minutes to read, word count and reading time, time to read, how long will it take to read, speaking time
# desc: How long a text file or PDF takes to read (reading time notes.txt)
# category: study
# usage: reading time <file>
# rawargs: yes
import re
from pathlib import Path
from _lib import args_text, fail
from _files import path_arg, is_text_file
t = re.sub(r"^\s*(?:(?:the|a)\s+)?(?:reading\s+)?(?:time\s+)?(?:of|for|to read)?\s*", "", args_text(), flags=re.I)
if not t.strip(): fail("Usage: reading time <file>   (text file or PDF)")
p = path_arg(t)
if p.suffix.lower() == ".pdf":
    try: from pypdf import PdfReader
    except ImportError: fail("PDF needs:  pip install pypdf")
    r = PdfReader(str(p))
    if r.is_encrypted: fail("That PDF is password protected.")
    text = "\n".join((pg.extract_text() or "") for pg in r.pages[:500])
elif is_text_file(p, 20 * 1024 * 1024):
    text = p.read_text(encoding="utf-8", errors="ignore")
else:
    fail("I can read text files and PDFs.")
words = len(re.findall(r"\b[\w'-]+\b", text))
if not words: fail("No readable words found (a scanned PDF has no text layer).")
fmt = lambda mins: f"{int(mins)} min {int(round((mins - int(mins)) * 60))} s" if mins >= 1 else f"{int(round(mins * 60))} s"
print(f"{p.name}: {words:,} words, {len(text):,} characters")
print(f"  Reading silently (200 words/min): {fmt(words / 200)}")
print(f"  Reading aloud (130 words/min):    {fmt(words / 130)}")
