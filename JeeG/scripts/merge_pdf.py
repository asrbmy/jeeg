# keywords: merge pdf, combine pdf, join pdf, pdf merge, append pdf, put pdfs together, merge pdfs
# desc: Join PDF files into one (merge pdf a.pdf b.pdf)
# category: media
# usage: merge pdf <file> <file> ...
# rawargs: yes
from _lib import args_text, fail, need
from _files import path_arg, tokens, unique_path
need("pypdf")
from pypdf import PdfWriter, PdfReader
ps = [path_arg(x) for x in tokens(args_text())]
if len(ps) < 2: fail('Usage: merge pdf a.pdf b.pdf [c.pdf ...]   (use "quotes" for names with spaces)')
out = unique_path(ps[0].with_name("merged.pdf"))
wr = PdfWriter(); pages = 0
for p in ps:
    r = PdfReader(str(p))
    if r.is_encrypted: fail(f"{p.name} is password protected.")
    for pg in r.pages: wr.add_page(pg); pages += 1
with open(out, "wb") as f: wr.write(f)
print(f"Merged {len(ps)} files ({pages} pages) -> {out}")
