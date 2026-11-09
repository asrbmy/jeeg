# keywords: contact sheet, photo grid, thumbnail sheet, photo overview, picture overview, thumbnails of folder
# desc: Make one picture with small thumbnails of every photo in a folder (contact sheet <folder>). Needs Pillow.
# category: files
# usage: contact sheet <folder>
# rawargs: full
# patterns: \bcontact\s+sheet\b ;; \b(thumbnail|photo)\s+(grid|sheet)\b
# priority: 2
from pathlib import Path
from _lib import args_text, fail
from _files import path_arg, unique_path
try:
    from PIL import Image, ImageDraw
except ImportError:
    fail("This needs the Pillow library:  pip install Pillow")
t = args_text()
for junk in ("make a", "make", "create", "contact sheet", "thumbnail sheet", "thumbnail grid", "photo grid", "photo sheet", "photo overview", "picture overview", "thumbnails of", "of folder", "for", "of"):
    t = t.replace(junk, " ")
folder = path_arg(t.strip() or ".")
if not folder.is_dir():
    fail("Give a folder that has photos, for example:  contact sheet ~/Pictures/trip")
Image.MAX_IMAGE_PIXELS = 120_000_000
files = sorted(p for p in folder.iterdir() if p.is_file() and not p.is_symlink() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"})
if not files:
    fail("No photos found in that folder.")
MAX = 120
shown = files[:MAX]
cols, cell, label = 5, 220, 18
rows = (len(shown) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell, rows * (cell + label)), "white")
d = ImageDraw.Draw(sheet)
done = 0
for i, p in enumerate(shown):
    try:
        if p.stat().st_size > 60 * 1024 * 1024:
            continue
        with Image.open(p) as im:
            im.draft("RGB", (cell * 2, cell * 2))
            im = im.convert("RGB")
            im.thumbnail((cell - 8, cell - 8))
            x, y = (i % cols) * cell, (i // cols) * (cell + label)
            sheet.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
            d.text((x + 4, y + cell), p.name[:34], fill="black")
            done += 1
    except Exception:
        continue
if not done:
    fail("None of the photos could be read.")
dest = unique_path(folder / "contact_sheet.jpg")
sheet.save(dest, quality=85)
print(f"Made {dest} with {done} photos." + (f" (Only the first {MAX} of {len(files)} are shown.)" if len(files) > MAX else ""))
