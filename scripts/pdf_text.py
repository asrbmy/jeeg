# keywords: pdf text, pdf to text, extract text from pdf, read pdf, text from pdf, convert pdf to text, pdf to txt
# desc: Pull the text out of a PDF into a .txt file (pdf to text report.pdf, pdf to text report.pdf pages 2-4; needs pip install pypdf)
# category: files
# usage: pdf to text <file.pdf> [pages 2-4]
# rawargs: full
# patterns: \bpdf\s+(to|into)\s+(text|txt)\b ;; \b(text|words)\s+(from|out of)\s+(a\s+|the\s+|my\s+)?pdf\b ;; \bextract\s+text\b.*\bpdf\b ;; \btext\s+(from|in|of)\s+\S+\.pdf\b
# priority: 1
import re
from _lib import args_text, fail, need
from _files import path_arg, unique_path
t = args_text()
pg = re.search(r"\bpages?\s+(\d+)(?:\s*-\s*(\d+))?", t, re.I)
t = re.sub(r"\bpages?\s+\d+(?:\s*-\s*\d+)?", " ", t, flags=re.I)
t = re.sub(r"^\s*(?:please\s+)?(?:(?:convert|extract|get|read|pull|make)\b\s*)?(?:the\s+)?(?:text\b\s*)?(?:(?:from|out\s+of)\b\s*)?(?:(?:a|the)\b\s*)?(?:pdf\b(?![\w./-])\s*)?(?:to\b\s*)?(?:(?:text|txt)\b(?![\w./-])\s*)?(?:(?:from|of|in)\b\s*)?", "", t, flags=re.I).strip()
if not t:
    fail("Usage: pdf to text <file.pdf> [pages 2-4]")
src = path_arg(t)
if src.suffix.lower() != ".pdf":
    fail("That is not a .pdf file.")
need("pypdf")
from pypdf import PdfReader
try:
    r = PdfReader(str(src))
    if r.is_encrypted:
        fail("This PDF is password-protected.")
    n = len(r.pages)
    a, b = (int(pg.group(1)), int(pg.group(2) or pg.group(1))) if pg else (1, n)
    if not (1 <= a <= b <= n):
        fail(f"This PDF has {n} page(s). Choose pages between 1 and {n}.")
    parts = [(r.pages[i].extract_text() or "") for i in range(a - 1, b)]
except SystemExit:
    raise
except Exception as ex:
    fail(f"Could not read that PDF: {type(ex).__name__}")
text = "\n\n".join(f"--- page {a + i} ---\n{p.strip()}" for i, p in enumerate(parts))
if not "".join(parts).strip():
    fail("No text found. It is probably a scanned PDF (pictures of pages); it needs text recognition (OCR).")
out = unique_path(src.with_suffix(".txt"))
out.write_text(text, encoding="utf-8")
print(f"Wrote {len(text):,} characters from {b - a + 1} page(s): {out}")
