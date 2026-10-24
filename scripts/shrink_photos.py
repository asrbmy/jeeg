# keywords: compress pictures, compress photos, compress images, shrink photos, reduce photo size, make photos smaller, bulk resize, batch compress
# desc: Make every picture in a folder smaller into a new 'compressed' folder; originals untouched (compress pictures downloads, compress pictures trip quality 60 width 1600; needs pip install pillow)
# category: media
# usage: compress pictures <folder> [quality 60] [width 1600]
# rawargs: yes
# patterns: \b(compress|shrink|reduce)\b.*\b(pictures|photos|images|pics)\b ;; \bbulk\s+resize\b
# priority: 1
import re
from pathlib import Path
from _lib import args_text, fail, human, need
from _files import drop_tokens, resolve_folder, unique_path
t = args_text()
q = re.search(r"\bquality\s+(\d+)", t, re.I); wd = re.search(r"\b(?:width|max|wide)\s+(\d+)", t, re.I)
t = re.sub(r"\b(?:quality|width|max|wide)\s+\d+", " ", t, flags=re.I)
t = drop_tokens(t, {"please", "compress", "shrink", "reduce", "bulk", "batch", "resize", "make", "all", "my", "the", "picture", "pictures", "photo", "photos", "image", "images", "pic", "pics", "smaller", "in", "of", "size"})
quality, width = int(q.group(1)) if q else 75, int(wd.group(1)) if wd else 2000
if not (10 <= quality <= 95 and 200 <= width <= 12000):
    fail("Quality must be 10-95 and width 200-12000.")
folder = resolve_folder(t.strip(), default="Pictures")
need("PIL", "pillow")
from PIL import Image
files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
if not files:
    fail(f"No pictures (jpg, png, webp) found in {folder}.")
if len(files) > 2000:
    fail("That folder has over 2000 pictures; pick a smaller folder.")
out = folder / "compressed"
out.mkdir(exist_ok=True)
before = after = done = 0
for p in files:
    try:
        with Image.open(p) as im:
            im.load()
            if im.width > width:
                im = im.resize((width, max(1, round(im.height * width / im.width))), Image.LANCZOS)
            dest = unique_path(out / p.name)
            if p.suffix.lower() in (".jpg", ".jpeg"):
                im.convert("RGB").save(dest, "JPEG", quality=quality, optimize=True)
            elif p.suffix.lower() == ".webp":
                im.save(dest, "WEBP", quality=quality)
            else:
                im.save(dest, "PNG", optimize=True)
        before += p.stat().st_size; after += dest.stat().st_size; done += 1
    except Exception:
        print(f"  skipped {p.name}")
print(f"Compressed {done} picture(s): {human(before)} -> {human(after)} (saved {human(max(0, before - after))}).")
print(f"New files are in {out}. Your originals were not changed.")
