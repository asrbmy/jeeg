# keywords: shred file, secure delete, wipe file, permanently delete file, erase file, destroy file, shred, securely delete
# desc: Overwrite a file with random data and delete it (cannot be undone)
# category: security
# usage: shred file <file> [preview]
# confirm: yes
# rawargs: yes
import os, secrets
from pathlib import Path
from _lib import args_text, fail
from _files import path_arg
t = args_text()
preview = any(w in {"preview", "dry-run", "dryrun"} for w in t.lower().split())
if preview:
    t = " ".join(w for w in t.split() if w.lower() not in {"preview", "dry-run", "dryrun"})
p = path_arg(t)
if p.is_dir(): fail("Give a single file, not a folder.")
if p.is_symlink(): fail("Refusing to shred a link.")
size = p.stat().st_size
if size > 2 * 1024 ** 3: fail("That file is larger than 2 GB; refusing.")
if preview:
    print(f"Preview: {p.name} ({size} bytes) would be overwritten and deleted. Nothing was changed.")
    raise SystemExit(0)
with open(p, "r+b", buffering=0) as f:
    for _ in range(2):
        f.seek(0); left = size
        while left > 0:
            n = min(left, 1 << 20); f.write(secrets.token_bytes(n)); left -= n
        os.fsync(f.fileno())
new = p.with_name(secrets.token_hex(8))
os.rename(p, new); os.remove(new)
print(f"Shredded {p.name}. Note: on SSDs and cloud-synced folders, overwriting cannot be guaranteed; full-disk encryption is the real protection.")
