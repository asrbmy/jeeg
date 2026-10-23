# keywords: export data, backup data, backup my data, save my data, export everything, back up jeeg, data backup, export backup, backup records
# desc: Back up all your JeeG data (to-dos, notes, expenses, journal...) into one zip file (export data)
# category: backup
# usage: export data [folder]
# rawargs: yes
# patterns: \b(back ?up|export|save)\b.*\b(my |all )?(data|everything)\b(?!.*\b(status|check)\b)
# priority: 1
import json, re, time, zipfile
from pathlib import Path
from _lib import args_text, data_dir, fail
from _backup import data_files, mark
from _files import resolve_folder, unique_path
from _files import drop_tokens
t = drop_tokens(args_text(), {"export", "data", "backup", "back", "up", "my", "to", "into", "in", "everything", "jeeg", "all"})
dest = resolve_folder(t) if t else Path.cwd()
files = data_files()
if not files: fail("You have no saved data yet (nothing to back up).")
out = unique_path(dest / time.strftime("jeeg_backup_%Y%m%d_%H%M.zip"))
manifest = {"jeeg": "backup", "format": 1, "created": time.strftime("%Y-%m-%d %H:%M:%S"), "files": [p.name for p in files]}
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("manifest.json", json.dumps(manifest, indent=1))
    for p in files: z.write(p, p.name)
mark()
print(f"Backed up {len(files)} file(s) -> {out}")
print("Keep it somewhere safe (another drive or cloud folder). Restore with:  import data <file>")
