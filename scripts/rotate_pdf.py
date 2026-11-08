# keywords: rotate pdf, turn pdf, pdf rotate, flip pdf pages, sideways pdf, fix pdf orientation
# desc: Rotate PDF pages (rotate pdf scan.pdf 90; rotate pdf scan.pdf 180 pages 1-3) - needs: pip install pypdf
# category: media
# usage: rotate pdf <file> [90|180|270|left] [pages 1-3]
# rawargs: yes
# patterns: \brotate\s+(a\s+|the\s+)?pdf\b ;; \bpdf\s+rotate\b ;; \bturn\s+(a\s+|the\s+)?pdf\b
# priority: 2
import re
from _lib import args_text, fail, need
from _files import path_arg, unique_path, tokens
t = args_text()
pr = re.search(r"pages?\s+(\d+)(?:\s*-\s*(\d+))?", t, re.I)
if pr:
    t = t[:pr.start()] + t[pr.end():]
ang = 90
am = re.search(r"(?<![\w.])(-?\d{2,3})(?![\w.])\s*(?:deg\w*)?", re.sub(r"\.pdf\b", "", t, flags=re.I))
if am:
    ang = int(am.group(1))
    t = t.replace(am.group(0), " ", 1)
if re.search(r"\b(left|anticlockwise|counter)\b", t, re.I):
    ang = -abs(ang)
if ang % 90:
    fail("Rotate by 90, 180 or 270 degrees (or -90 for left).")
need("pypdf")
from pypdf import PdfReader, PdfWriter
names = [x for x in tokens(t) if x.lower().endswith(".pdf")] or [x for x in tokens(t) if x.lower() not in {"rotate", "pdf", "left", "right", "degrees", "by"}][:1]
if not names:
    fail("Usage: rotate pdf scan.pdf 90 [pages 1-3]")
src = path_arg(names[0])
r = PdfReader(str(src))
if r.is_encrypted:
    fail(f"{src.name} is password protected.")
n = len(r.pages)
lo, hi = (int(pr.group(1)), int(pr.group(2) or pr.group(1))) if pr else (1, n)
if not 1 <= lo <= hi <= n:
    fail(f"{src.name} has {n} pages; choose pages between 1 and {n}.")
wr = PdfWriter()
for i, pg in enumerate(r.pages, 1):
    if lo <= i <= hi:
        pg.rotate(ang)
    wr.add_page(pg)
out = unique_path(src.with_name(f"{src.stem}-rotated.pdf"))
with open(out, "wb") as f:
    wr.write(f)
print(f"Rotated pages {lo}-{hi} by {ang % 360} degrees -> {out}")
