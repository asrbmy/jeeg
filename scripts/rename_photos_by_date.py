# keywords: rename photos, photos by date, rename pictures by date, date photos, photo names, rename images by date, organise photos by date, exif rename
# desc: Rename photos to their date taken, e.g. 2026-10-21_143005.jpg (preview first; add 'apply')
# category: files
# usage: rename photos by date <folder> [apply]
# rawargs: full
import datetime, os, re
from pathlib import Path
from _lib import args_text, fail
from _files import resolve_folder
apply = bool(re.search(r"\b(apply|go ahead|do it)\b", args_text(), re.I))
t = re.sub(r"^\s*(?:please\s+)?(?:rename\s+)?(?:(?:the|my)\s+)?(?:photos?|pictures?|images?|pics?)\s+by\s+date(?:\s+taken)?\s*(?:in|of|from)?\s*", "", args_text(), flags=re.I)
from _files import drop_tokens
t = drop_tokens(t, {"apply", "go", "ahead", "do", "it", "preview"})
folder = resolve_folder(t or "pictures")
EXT = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic"}
try:
    from PIL import Image
except ImportError:
    Image = None
def taken(p):
    if Image and p.suffix.lower() in {".jpg", ".jpeg", ".tif", ".tiff", ".png", ".webp"}:
        try:
            ex = Image.open(p).getexif()
            v = ex.get_ifd(0x8769).get(36867) or ex.get(306)
            if v: return datetime.datetime.strptime(str(v)[:19], "%Y:%m:%d %H:%M:%S"), "exif"
        except Exception: pass
    return datetime.datetime.fromtimestamp(p.stat().st_mtime), "file date"
files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in EXT and not p.name.startswith("."))
if not files: fail(f"No pictures in {folder}")
plan, used = [], {p.name.lower() for p in files}
final = set()
for p in files:
    dt, src = taken(p)
    base = f"{dt:%Y-%m-%d_%H%M%S}"; new = base + p.suffix.lower(); i = 1
    while new.lower() in final or (new.lower() in used and new.lower() != p.name.lower()):
        new = f"{base}_{i}{p.suffix.lower()}"; i += 1
    final.add(new.lower())
    if new != p.name: plan.append((p, folder / new, src))
if not plan: print("Nothing to rename."); raise SystemExit(0)
for a, b, src in plan[:40]: print(f"  {a.name}  ->  {b.name}   ({src})")
if len(plan) > 40: print(f"  ... and {len(plan) - 40} more")
if not Image: print("(Pillow is not installed, so file dates are used instead of the date taken: pip install pillow)")
if not apply: print(f"{len(plan)} file(s) would change. Add 'apply' to do it."); raise SystemExit(0)
tmp = []
for i, (a, b, _) in enumerate(plan):
    t1 = a.with_name(f".jg_tmp_{os.getpid()}_{i}"); os.rename(a, t1); tmp.append((t1, b))
for t1, b in tmp: os.rename(t1, b)
from _undo import record
record("rename photos", [(a, b) for a, b, _ in plan])
print(f"Renamed {len(plan)} file(s). Type  undo  to put the names back.")
