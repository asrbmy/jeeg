# keywords: pdf to png, pdf to jpg, render pdf pages, pdf screenshot, save pdf pages
# desc: Save each PDF page as a picture (pdf to images report.pdf; pdf to images report.pdf 200 dpi) - needs: pip install pypdfium2 Pillow
# category: media
# usage: pdf to images <file> [jpg] [<n> dpi]
# rawargs: yes
# patterns: \bpdf\s+(to|into|as)\s+(images?|pictures?|png|jpe?g|photos?)\b ;; \bsave\s+pdf\s+pages\b ;; \bconvert\s+(a\s+|the\s+)?pdf\s+to\s+(an?\s+)?(image|picture|png|jpe?g)\b
# priority: 2
import re
from _lib import args_text, fail, need
from _files import path_arg, unique_path, tokens
raw = args_text()
dm = re.search(r"(\d{2,3})\s*dpi", raw, re.I)
dpi = int(dm.group(1)) if dm else 150
raw = raw.replace(dm.group(0), " ") if dm else raw
fmt = "jpg" if re.search(r"\b(jpg|jpeg)\b", raw, re.I) else "png"
names = [x for x in tokens(raw) if x.lower().endswith(".pdf")]
if not names:
    fail("Usage: pdf to images report.pdf [jpg] [200 dpi]")
if not 50 <= dpi <= 400:
    fail("Choose a resolution between 50 and 400 dpi.")
need("pypdfium2")
need("PIL", "Pillow")
import pypdfium2 as pdfium
src = path_arg(names[0])
try:
    doc = pdfium.PdfDocument(str(src))
except Exception:
    fail(f"Could not open {src.name}. Is it a PDF, and is it free of a password?")
n = len(doc)
if n > 300:
    fail(f"{src.name} has {n} pages; this makes at most 300 pictures at a time.")
out = unique_path(src.with_name(f"{src.stem}-pages"))
out.mkdir()
for i in range(n):
    img = doc[i].render(scale=dpi / 72).to_pil()
    if fmt == "jpg":
        img = img.convert("RGB")
    img.save(out / f"page-{i + 1:03d}.{fmt}")
print(f"Saved {n} page(s) as {fmt.upper()} at {dpi} dpi -> {out}")
