# keywords: shred file, secure delete, wipe file, permanently delete file, erase file, destroy file, shred, securely delete
# desc: Overwrite a file with random data and delete it (cannot be undone)
# category: security
# usage: shred file <file>
# confirm: yes
# rawargs: yes
import os, secrets
from pathlib import Path
from _lib import args_text, fail
from _files import path_arg
p = path_arg(args_text())
if p.is_dir(): fail("Give a single file, not a folder.")
if p.is_symlink(): fail("Refusing to shred a link.")
size = p.stat().st_size
if size > 2 * 1024 ** 3: fail("That file is larger than 2 GB; refusing.")
with open(p, "r+b", buffering=0) as f:
    for _ in range(2):
        f.seek(0); left = size
        while left > 0:
            n = min(left, 1 << 20); f.write(secrets.token_bytes(n)); left -= n
        os.fsync(f.fileno())
new = p.with_name(secrets.token_hex(8))
os.rename(p, new); os.remove(new)
print(f"Shredded {p.name}. Note: on SSDs and cloud-synced folders, overwriting cannot be guaranteed; full-disk encryption is the real protection.")
