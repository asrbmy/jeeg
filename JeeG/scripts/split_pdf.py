# keywords: split pdf, extract pages, pdf pages, split pages, pdf split, take pages from pdf, separate pdf pages
# desc: Split a PDF into pages, or pull out some pages (split pdf report.pdf pages 2-4)
# category: media
# usage: split pdf <file> [pages 2-4]
# rawargs: yes
import re
from _lib import args_text, fail, need
from _files import path_arg, unique_path
need("pypdf")
from pypdf import PdfWriter, PdfReader
t = args_text()
m = re.search(r"\bpages?\s+([\d,\- ]+)$", t, re.I)
spec = m.group(1).strip() if m else ""
p = path_arg(t[:m.start()] if m else t)
r = PdfReader(str(p))
if r.is_encrypted: fail("That PDF is password protected.")
n = len(r.pages)
if spec:
    want = []
    for part in re.split(r"[ ,]+", spec):
        if not part: continue
        a, _, b = part.partition("-")
        lo, hi = int(a), int(b or a)
        if lo < 1 or hi > n or lo > hi: fail(f"Pages must be between 1 and {n}.")
        want += range(lo, hi + 1)
    wr = PdfWriter()
    for i in want: wr.add_page(r.pages[i - 1])
    out = unique_path(p.with_name(f"{p.stem}_pages_{spec.replace(' ', '').replace(',', '_')}.pdf"))
    with open(out, "wb") as f: wr.write(f)
    print(f"{len(want)} page(s) -> {out}")
else:
    if n > 500: fail("That PDF has more than 500 pages; choose some with: split pdf file.pdf pages 1-10")
    folder = unique_path(p.with_name(p.stem + "_pages")); folder.mkdir()
    for i in range(n):
        wr = PdfWriter(); wr.add_page(r.pages[i])
        with open(folder / f"{p.stem}_{i + 1:03d}.pdf", "wb") as f: wr.write(f)
    print(f"{n} page(s) -> {folder}")
