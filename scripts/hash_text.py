# keywords: hash, checksum, sha256, sha1, md5, sha, file hash, digest
# desc: SHA-256 / SHA-1 / MD5 of text or a file
# category: utility
# usage: hash text <text|file>
# stdin: yes
import hashlib, os
from pathlib import Path
from _lib import args_or_stdin, fail, safe_is_file
t = args_or_stdin()
if not t:
    fail("Usage: hash text <text or file path>")
p = Path(t.strip('"\'')[:1000]).expanduser() if len(t) < 1000 else Path('.nofile')
if safe_is_file(p):
    hs = {n: hashlib.new(n) for n in ("sha256", "sha1", "md5")}
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            for h in hs.values(): h.update(chunk)
    print(f"File: {p}")
else:
    hs = {n: hashlib.new(n, t.encode()) for n in ("sha256", "sha1", "md5")}
for n, h in hs.items():
    print(f"{n.upper():<7}{h.hexdigest()}")
