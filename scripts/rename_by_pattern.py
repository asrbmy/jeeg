# keywords: rename pattern, rename as, rename with pattern, name template, rename using, pattern rename, rename files as
# desc: Rename files with a pattern, preview first (rename files in downloads as trip_{n}.{ext}; placeholders {name} {date} {n} {ext}; add 'apply' to do it)
# category: files
# usage: rename files in <folder> as <pattern> [apply]
# rawargs: full
# patterns: \brename\b.*\b(as|using|pattern)\b\s+\S*\{
# priority: 2
import datetime, re
from pathlib import Path
from _lib import args_text, fail
from _files import drop_tokens, resolve_folder
t = args_text()
apply = bool(re.search(r"\b(apply|go ahead|do it)\b", t, re.I))
t = re.sub(r"\b(apply|go ahead|do it|preview)\b", " ", t, flags=re.I)
m = re.search(r"\b(?:as|using|pattern|to)\s+(\S*\{\S*)", t, re.I)
if not m:
    fail("Usage: rename files in <folder> as <pattern>   e.g. rename files in trip as holiday_{n}.{ext}\n  placeholders: {name} (old name) {date} (modified date) {n} (001, 002 ...) {ext}\n  Add the word apply to really do it.")
pat = m.group(1).strip("\"'")
rest = t[:m.start()]
rest = drop_tokens(rest, {"please", "rename", "file", "files", "all", "in", "the", "my", "folder", "with", "a", "of"}).strip()
folder = resolve_folder(rest, default="Downloads")
if re.search(r"[\\/:*?\"<>|]", re.sub(r"\{(name|date|n|ext)\}", "", pat)) or ".." in pat:
    fail("The pattern can only contain a file name (no folders or special characters), plus {name} {date} {n} {ext}.")
if not re.fullmatch(r"(?:[^{}]|\{(?:name|date|n|ext)\})+", pat):
    fail("Unknown placeholder. Use only {name} {date} {n} {ext}.")
files = sorted((p for p in folder.iterdir() if p.is_file() and not p.name.startswith(".")), key=lambda p: (p.stat().st_mtime, p.name.lower()))
if not files:
    fail("No files in that folder.")
if len(files) > 5000:
    fail("Too many files (over 5000). Use a smaller folder.")
width = max(3, len(str(len(files))))
plan, used = [], set()
for i, p in enumerate(files, 1):
    new = pat.format(name=p.stem, date=datetime.date.fromtimestamp(p.stat().st_mtime).isoformat(), n=str(i).zfill(width), ext=p.suffix.lstrip("."))
    if "{ext}" not in m.group(1) and not Path(new).suffix and p.suffix:
        new += p.suffix
    new = new[:200].rstrip(". ")
    if new in used:
        fail(f"The pattern gives two files the same name ('{new}'). Add {{n}} to the pattern.")
    used.add(new)
    plan.append((p, p.with_name(new)))
plan = [(a, b) for a, b in plan if a.name != b.name]
clash = [b.name for a, b in plan if b.exists() and b not in [x for x, _ in plan]]
if clash:
    fail(f"'{clash[0]}' already exists in that folder. Nothing was renamed.")
if not plan:
    print("Nothing to rename; the names already match.")
    raise SystemExit(0)
for a, b in plan[:12]:
    print(f"  {a.name}  ->  {b.name}")
if len(plan) > 12:
    print(f"  ... and {len(plan) - 12} more")
if not apply:
    print(f"\nThis was a preview of {len(plan)} file(s). Run again with the word 'apply' to do it.")
    raise SystemExit(0)
tmp = []
for i, (a, b) in enumerate(plan):                  # two steps so swaps and overlaps never overwrite anything
    t1 = a.with_name(f".jeeg_tmp_{i}_{a.name}")
    a.rename(t1); tmp.append((t1, b, a))
done = []
for t1, b, a in tmp:
    t1.rename(b); done.append((a, b))
try:
    from _undo import record
    record(f"rename by pattern in {folder.name}", [(a, b) for a, b in done])
except Exception:
    pass
print(f"Renamed {len(done)} file(s). Say 'undo' to put them back.")
