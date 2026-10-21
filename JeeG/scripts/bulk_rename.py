# keywords: bulk rename, batch rename, rename files, rename all files, mass rename, rename many files, add prefix, add suffix, number files
# desc: Rename many files at once, with a preview first (bulk rename downloads replace img with photo)
# category: files
# usage: bulk rename <folder> replace <old> with <new>
# rawargs: yes
import os, re
from pathlib import Path
from _lib import args_text, fail
from _files import resolve_folder
t = args_text()
apply = bool(re.search(r"\b(apply|go ahead|do it)\b", t, re.I))
t = re.sub(r"\b(apply|go ahead|do it|preview)\b", " ", t, flags=re.I).strip()
m = re.search(r"\b(replace|prefix|suffix|number|numbered|lowercase|uppercase|underscores|spaces)\b", t, re.I)
if not m:
    fail("Usage: bulk rename <folder> replace <old> with <new>\n"
         "       bulk rename <folder> prefix <text> | suffix <text> | number <base> | lowercase | uppercase | underscores\n"
         "It only previews. Add the word 'apply' at the end to really rename.")
op, rest = m.group(1).lower(), t[m.end():].strip()
folder = resolve_folder(t[:m.start()].strip())
files = sorted(p for p in folder.iterdir() if p.is_file() and not p.name.startswith("."))
if not files: fail(f"No files in {folder}")
plan = []
for i, p in enumerate(files, 1):
    stem, ext = p.stem, p.suffix
    if op == "replace":
        mm = re.fullmatch(r"(.+?)\s+with\s+(.*)", rest, re.I)
        if not mm: fail("Usage: bulk rename <folder> replace <old> with <new>")
        new = stem.replace(mm.group(1).strip("\"'"), mm.group(2).strip("\"'")) + ext
    elif op == "prefix": new = rest + p.name
    elif op == "suffix": new = stem + rest + ext
    elif op in ("number", "numbered"):
        new = f"{rest or 'file'}_{i:03d}{ext}"
    elif op == "lowercase": new = p.name.lower()
    elif op == "uppercase": new = stem.upper() + ext
    elif op == "underscores" or op == "spaces": new = p.name.replace(" ", "_")
    if not rest and op in ("prefix", "suffix"): fail(f"Say what the {op} should be.")
    if any(c in new for c in '/\\:*?"<>|') or not new.strip(". "):
        fail(f"'{new}' is not a valid file name.")
    if new != p.name: plan.append((p, folder / new))
if not plan:
    print("Nothing to rename."); raise SystemExit(0)
targets = [str(b).lower() for _, b in plan]
existing = {str(p).lower() for p in files} - {str(a).lower() for a, _ in plan}
if len(set(targets)) != len(targets) or any(x in existing for x in targets):
    fail("Two files would end up with the same name. Nothing was renamed; choose a different pattern.")
for a, b in plan[:40]:
    print(f"  {a.name}  ->  {b.name}")
if len(plan) > 40: print(f"  ... and {len(plan) - 40} more")
if not apply:
    print(f"{len(plan)} file(s) would change in {folder}. Add 'apply' to do it."); raise SystemExit(0)
tmp = []
for i, (a, b) in enumerate(plan):             # two steps so swapping names can never overwrite
    t1 = a.with_name(f".tr_tmp_{os.getpid()}_{i}")
    os.rename(a, t1); tmp.append((t1, b))
for t1, b in tmp:
    os.rename(t1, b)
print(f"Renamed {len(plan)} file(s).")
