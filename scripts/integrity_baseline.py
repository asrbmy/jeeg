# keywords: integrity baseline, integrity save, integrity check, detect changed files, file tampering check, watch folder for changes, folder fingerprint
# desc: Save the fingerprints of a folder, then check later which files were added, changed or removed (integrity save myfolder, integrity check myfolder)
# category: security
# usage: integrity save <folder> | integrity check <folder> | integrity list | integrity forget <folder>
# rawargs: full
# patterns: ^\s*integrity\s+(?:save|check|list|forget)\b
# priority: 3
import hashlib, json, re, time
from _lib import args_text, data_dir, fail
from _devscan import walk
from _files import path_arg
t = re.sub(r"^\s*integrity\s*", "", args_text(), flags=re.I).strip()
cmd, _, rest = t.partition(" ")
cmd = cmd.lower()
store = data_dir() / "integrity.json"
db = json.loads(store.read_text()) if store.exists() else {}
def scan(root):
    out = {}
    for p in walk(root, 5000):
        try:
            if p.stat().st_size > 200_000_000: continue
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
            out[str(p.relative_to(root))] = h.hexdigest()
        except OSError: pass
    return out
if cmd == "list":
    for k, v in db.items(): print(f"{k}  ({len(v['files'])} files, saved {time.strftime('%Y-%m-%d %H:%M', time.localtime(v['when']))})")
    if not db: print("Nothing saved yet. Try:  integrity save <folder>")
    raise SystemExit(0)
if cmd not in ("save", "check", "forget"): fail("Usage: integrity save <folder> | integrity check <folder> | integrity list | integrity forget <folder>")
root = path_arg(rest)
if not root.is_dir(): fail("Give a folder.")
key = str(root)
if cmd == "forget":
    if db.pop(key, None) is None: fail("No saved fingerprints for that folder.")
    store.write_text(json.dumps(db)); print("Forgotten."); raise SystemExit(0)
now = scan(root)
if cmd == "save":
    db[key] = {"when": time.time(), "files": now}; store.write_text(json.dumps(db))
    print(f"Saved fingerprints of {len(now)} files in {root}. Run  integrity check {rest}  later to see what changed."); raise SystemExit(0)
if key not in db: fail("Nothing saved for that folder. Run  integrity save  first.")
old = db[key]["files"]
added, gone = sorted(set(now) - set(old)), sorted(set(old) - set(now))
changed = sorted(k for k in set(now) & set(old) if now[k] != old[k])
print(f"Compared with the copy saved {time.strftime('%Y-%m-%d %H:%M', time.localtime(db[key]['when']))}:")
for label, items in (("Changed", changed), ("Added", added), ("Removed", gone)):
    print(f"{label}: {len(items)}")
    for k in items[:30]: print("   " + k)
if not (added or gone or changed): print("Nothing changed.")
