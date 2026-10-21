# keywords: hash, checksum, sha256, sha1, md5, sha, file hash, digest
# desc: SHA-256 / SHA-1 / MD5 of text or a file
# category: utility
# usage: hash text <text|file>
import hashlib, os
from pathlib import Path
from _lib import args_text, fail
t = args_text()
if not t:
    fail("Usage: hash text <text or file path>")
p = Path(t.strip('"\'')).expanduser()
if p.is_file():
    hs = {n: hashlib.new(n) for n in ("sha256", "sha1", "md5")}
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            for h in hs.values(): h.update(chunk)
    print(f"File: {p}")
else:
    hs = {n: hashlib.new(n, t.encode()) for n in ("sha256", "sha1", "md5")}
for n, h in hs.items():
    print(f"{n.upper():<7}{h.hexdigest()}")
