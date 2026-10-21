# keywords: import data, restore data, restore backup, restore my data, import backup, load backup, recover data
# desc: Restore your data from a backup zip made by 'export data' (current data is saved first)
# category: backup
# usage: import data <backup.zip>
# confirm: yes
# rawargs: yes
import json, re, shutil, time, zipfile
from _lib import args_text, data_dir, fail
from _backup import data_files
from _files import path_arg
t = re.sub(r"^\s*(?:(?:import|restore|load|recover)\s+)?(?:(?:my|the)\s+)?(?:data|backup)?\s*(?:from)?\s*", "", args_text(), flags=re.I)
if not t.strip(): fail("Usage: import data <backup.zip>")
p = path_arg(t)
try:
    z = zipfile.ZipFile(p)
except zipfile.BadZipFile:
    fail("That is not a valid zip file.")
with z:
    try: man = json.loads(z.read("manifest.json"))
    except (KeyError, ValueError): fail("This zip was not made by 'export data' (no manifest).")
    if man.get("jeeg") != "backup": fail("This zip was not made by 'export data'.")
    names = [n for n in z.namelist() if n != "manifest.json"]
    total = sum(z.getinfo(n).file_size for n in names)
    if total > 200 * 1024 * 1024: fail("The backup is larger than 200 MB; refusing.")
    for n in names:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}", n) or n.endswith(".tmp") or n in ("index.json", "reminders.json"):
            fail(f"Unsafe or unexpected file name in the backup: {n!r}. Nothing was imported.")
    keep = data_dir() / "trash" / time.strftime("before-import-%Y%m%d-%H%M%S")
    cur = data_files()
    if cur:
        keep.mkdir(parents=True, exist_ok=True)
        for f in cur: shutil.copy2(f, keep / f.name)
    for n in names:
        (data_dir() / n).write_bytes(z.read(n))
print(f"Restored {len(names)} file(s) from the backup made {man.get('created', '?')}.")
if cur: print(f"Your previous data was copied to {keep}")
