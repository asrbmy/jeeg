# keywords: images to pdf, photos to pdf, jpg to pdf, pictures to pdf, make pdf from images, combine images into pdf, scan to pdf
# desc: Combine pictures into one PDF (images to pdf <folder or files>)
# category: media
# usage: images to pdf <folder|files>
# rawargs: full
from _lib import args_text, fail, need
from _files import path_arg, tokens, unique_path
need("PIL", "pillow")
from PIL import Image
import re
t = re.sub(r"^\s*(?:(?:convert|make|combine|turn|put|save)\s+)?(?:(?:the|my|all)\s+)?(?:images?|photos?|pictures?|pics?|jpgs?|pngs?)\s+(?:in(?:to)?|to)\s+(?:a\s+)?pdf\s*(?:from|of)?\s*", "", args_text(), flags=re.I)
toks = tokens(t)
if not toks: fail("Usage: images to pdf <folder>   or   images to pdf a.jpg b.jpg c.png")
EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff"}
ps = [path_arg(x) for x in toks]
if len(ps) == 1 and ps[0].is_dir():
    base = ps[0]; ps = sorted((p for p in base.iterdir() if p.suffix.lower() in EXT), key=lambda p: p.name.lower())
    out = unique_path(base / (base.name + ".pdf"))
else:
    out = unique_path(ps[0].with_suffix(".pdf"))
ps = [p for p in ps if p.suffix.lower() in EXT]
if not ps: fail("No pictures found.")
if len(ps) > 300: fail("Too many pictures (limit 300).")
ims = []
for p in ps:
    im = Image.open(p)
    if im.mode != "RGB":
        im = im.convert("RGBA"); bg = Image.new("RGB", im.size, "white"); bg.paste(im, mask=im.split()[-1]); im = bg
    ims.append(im)
ims[0].save(out, "PDF", save_all=True, append_images=ims[1:])
print(f"{len(ims)} picture(s) -> {out}")
