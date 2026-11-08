# keywords: compress pdf, shrink pdf, reduce pdf size, pdf smaller, pdf too big, optimize pdf, make pdf lighter
# desc: Make a PDF smaller (compress pdf big.pdf) - needs: pip install pypdf (Pillow shrinks pictures too)
# category: media
# usage: compress pdf <file>
# rawargs: yes
# patterns: \b(compress|shrink|reduce|optimi[sz]e)\s+(the\s+|a\s+|my\s+)?(size\s+of\s+)?(a\s+)?pdf\b ;; \bpdf\s+(too\s+big|smaller)\b ;; \bmake\s+(a\s+|the\s+)?pdf\s+smaller\b
# priority: 2
import io
from _lib import args_text, fail, need, human
from _files import path_arg, unique_path, tokens
names = [x for x in tokens(args_text()) if x.lower() not in {"compress", "pdf", "shrink", "reduce", "size", "of", "the", "smaller", "make", "a"}]
if not names:
    fail("Usage: compress pdf big.pdf")
need("pypdf")
from pypdf import PdfReader, PdfWriter
src = path_arg(names[0])
r = PdfReader(str(src))
if r.is_encrypted:
    fail(f"{src.name} is password protected.")
wr = PdfWriter()
for pg in r.pages:
    wr.add_page(pg)
shrunk = 0
have_pil = True
try:
    from PIL import Image
    for pg in wr.pages:
        for img in pg.images:                      # re-save pictures as medium quality JPEG when that is smaller
            try:
                pil = img.image
                if pil is None or pil.width * pil.height < 200_000:
                    continue
                buf = io.BytesIO()
                pil.convert("RGB").save(buf, "JPEG", quality=60, optimize=True)
                if len(buf.getvalue()) < len(img.data) * 0.9:
                    img.replace(Image.open(io.BytesIO(buf.getvalue())), quality=60)
                    shrunk += 1
            except Exception:
                continue
except ImportError:
    have_pil = False
for pg in wr.pages:
    pg.compress_content_streams()
try:
    wr.compress_identical_objects(remove_identicals=True, remove_orphans=True)
except Exception:
    pass
out = unique_path(src.with_name(f"{src.stem}-small.pdf"))
with open(out, "wb") as f:
    wr.write(f)
a, b = src.stat().st_size, out.stat().st_size
if b >= a:
    out.unlink()
    print(f"{src.name} is already as small as JeeG can make it ({human(a)}). No new file made.")
else:
    print(f"{human(a)} -> {human(b)}  ({(1 - b / a) * 100:.0f}% smaller" + (f", {shrunk} picture(s) re-compressed" if shrunk else "") + f")\nSaved: {out}")
if not have_pil:
    print("Tip: pip install Pillow lets JeeG shrink pictures inside the PDF too.")
