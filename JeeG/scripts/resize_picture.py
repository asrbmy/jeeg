# keywords: resize image, resize photo, resize picture, shrink image, make image smaller, scale image, image width, reduce image size
# desc: Resize a picture (resize image photo.jpg to 800 wide, or 50%)
# category: media
# usage: resize image <file> to <width>
# rawargs: full
import re
from _lib import args_text, fail, need
from _files import path_arg, split_on, unique_path
src_t, size = split_on(re.sub(r"^\s*(?:resize|shrink|scale|make)\s+(?:the\s+|an?\s+|my\s+)?(?:image|photo|picture|pic)?\s*", "", args_text(), flags=re.I), "to")
if not size: fail("Usage: resize image <file> to <width>   (800, 800x600 or 50%)   e.g. resize image photo.jpg to 800")
need("PIL", "pillow")
from PIL import Image
p = path_arg(src_t)
im = Image.open(p)
w0, h0 = im.size
s = size.lower().replace("pixels", "").replace("px", "").replace("wide", "").strip()
if (m := re.fullmatch(r"(\d+(?:\.\d+)?)\s*%", s)): f = float(m.group(1)) / 100; w1, h1 = round(w0 * f), round(h0 * f)
elif (m := re.fullmatch(r"(\d+)\s*[x*by ]+\s*(\d+)", s)): w1, h1 = int(m.group(1)), int(m.group(2))
elif (m := re.fullmatch(r"(\d+)", s)): w1 = int(m.group(1)); h1 = round(h0 * w1 / w0)
else: fail("Size must look like 800, 800x600 or 50%")
if not (1 <= w1 <= 20000 and 1 <= h1 <= 20000): fail("That size is out of range.")
out = unique_path(p.with_name(f"{p.stem}_{w1}x{h1}{p.suffix}"))
im.resize((w1, h1), Image.LANCZOS).save(out)
print(f"{p.name} {w0}x{h0} -> {out.name} {w1}x{h1}")
