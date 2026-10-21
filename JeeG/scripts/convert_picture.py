# keywords: convert image, image to jpg, png to jpg, jpg to png, webp to png, change image format, convert photo, convert picture, image format
# desc: Convert a picture to another format (convert image photo.png to jpg)
# category: media
# usage: convert image <file> to <format>
# rawargs: full
# patterns: \bconvert (an? )?(image|photo|picture|png|jpe?g|webp)\b ;; \b(png|jpe?g|webp|bmp|gif|tiff?) to (png|jpe?g|webp|bmp|gif|tiff?|pdf|ico)\b
import re
from _lib import args_text, fail, need
from _files import path_arg, split_on, unique_path
src_t, fmt = split_on(re.sub(r"^\s*(?:convert|change|turn|save)\s+(?:the\s+|an?\s+|my\s+)?(?:image|photo|picture|pic)?\s*", "", args_text(), flags=re.I), "to")
fmt = fmt.lower().strip(". ")
FM = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP", "bmp": "BMP", "gif": "GIF", "tiff": "TIFF", "tif": "TIFF", "pdf": "PDF", "ico": "ICO"}
if fmt not in FM: fail("Usage: convert image <file> to <jpg|png|webp|bmp|gif|tiff|pdf>")
need("PIL", "pillow")
from PIL import Image
p = path_arg(src_t)
im = Image.open(p)
if FM[fmt] in ("JPEG", "PDF", "BMP") and im.mode not in ("RGB", "L"):
    bg = Image.new("RGB", im.size, "white")
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA"); bg.paste(im, mask=im.split()[-1]); im = bg
    else: im = im.convert("RGB")
out = unique_path(p.with_suffix("." + ("jpg" if fmt == "jpeg" else fmt)))
im.save(out, FM[fmt])
print(f"Saved {out}")
