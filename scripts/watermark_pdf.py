# keywords: watermark pdf, stamp pdf, add watermark, pdf watermark, mark pdf draft, confidential stamp
# desc: Stamp text across every PDF page (watermark pdf report.pdf CONFIDENTIAL) - needs: pip install pypdf
# category: media
# usage: watermark pdf <file> <text>
# rawargs: yes
# patterns: \bwatermark\b ;; \bstamp\s+(a\s+|the\s+)?pdf\b
# priority: 2
import io, math, re
from _lib import args_text, fail, need
from _files import path_arg, unique_path, tokens
raw = args_text()
m = re.search(r"([^\s\"']+\.pdf|\"[^\"]+\.pdf\"|'[^']+\.pdf')", raw, re.I)
if not m:
    fail("Usage: watermark pdf report.pdf CONFIDENTIAL")
name = m.group(1).strip("\"'")
text = re.sub(r"\b(watermark|stamp|add|pdf|mark|with|the|text)\b", " ", raw.replace(m.group(1), " "), flags=re.I).strip(" \"'") or "DRAFT"
text = "".join(c for c in text if 32 <= ord(c) < 127)[:40].strip() or "DRAFT"
need("pypdf")
from pypdf import PdfReader, PdfWriter
src = path_arg(name)
r = PdfReader(str(src))
if r.is_encrypted:
    fail(f"{src.name} is password protected.")
esc = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
def stamp(w, h):
    """A one-page PDF with big, light, diagonal text (hand-written, no extra libraries)."""
    diag = math.hypot(w, h)
    size = max(12, min(80, diag * 0.7 / max(1, len(text)) / 0.55))
    a = math.atan2(h, w)
    c, s = math.cos(a), math.sin(a)
    tw = len(text) * size * 0.55
    x, y = w / 2 - (tw / 2) * c + (size / 3) * s, h / 2 - (tw / 2) * s - (size / 3) * c
    content = f"q /G gs 0.55 0.55 0.55 rg BT /F1 {size:.1f} Tf {c:.4f} {s:.4f} {-s:.4f} {c:.4f} {x:.1f} {y:.1f} Tm ({esc}) Tj ET Q".encode("latin-1")
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w:.2f} {h:.2f}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> /ExtGState << /G 6 0 R >> >> >>".encode(),
            b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>", b"<< /Type /ExtGState /ca 0.28 >>"]
    out, offs = bytearray(b"%PDF-1.4\n"), []
    for i, o in enumerate(objs, 1):
        offs.append(len(out)); out += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    x0 = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode() + b"".join(f"{o:010d} 00000 n \n".encode() for o in offs)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{x0}\n%%EOF\n".encode()
    return PdfReader(io.BytesIO(bytes(out))).pages[0]
wr = PdfWriter()
for pg in r.pages:
    w_, h_ = float(pg.mediabox.width), float(pg.mediabox.height)
    pg.merge_page(stamp(w_, h_))
    wr.add_page(pg)
out = unique_path(src.with_name(f"{src.stem}-watermarked.pdf"))
with open(out, "wb") as f:
    wr.write(f)
print(f"Stamped '{text}' on {len(r.pages)} page(s) -> {out}")
