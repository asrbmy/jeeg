# keywords: exif, strip exif, remove exif, remove metadata, photo metadata, remove location from photo, clean photo, privacy photo
# desc: Remove hidden location and camera data from a photo (strip exif photo.jpg). Needs Pillow.
# category: files
# usage: strip exif <photo>
# rawargs: full
# patterns: \bexif\b ;; \bremove\b.*\b(metadata|location)\b.*\b(photo|picture|image)\b
# priority: 1
from pathlib import Path
from _lib import args_text, fail
from _files import path_arg, unique_path
try:
    from PIL import Image
except ImportError:
    fail("This needs the Pillow library:  pip install Pillow")
t = args_text()
for junk in ("strip exif", "remove exif", "remove metadata", "remove location from", "clean photo", "privacy photo", "exif", "metadata", "from"):
    t = t.replace(junk, " ")
p = path_arg(t.strip())
if not p.is_file() or p.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}:
    fail("Give a photo: JPG, PNG, WebP or TIFF.")
Image.MAX_IMAGE_PIXELS = 120_000_000
with Image.open(p) as im:
    had = bool(getattr(im, "getexif", lambda: {})())
    gps = False
    try:
        gps = 34853 in im.getexif()
    except Exception:
        pass
    fmt = im.format
    im.load()
    clean = im.copy()
    clean.info = {}
    dest = unique_path(p.with_name(p.stem + "_clean" + p.suffix))
    clean.save(dest, format=fmt, quality=95) if fmt == "JPEG" else clean.save(dest, format=fmt)
print(f"Saved a copy without hidden data -> {dest}")
print("The original had camera/time data" + (" and a GPS location" if gps else "") + "." if had else "The original had no EXIF data.")
print("The original file was not changed.")
