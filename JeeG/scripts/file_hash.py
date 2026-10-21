# keywords: file hash, checksum, sha256 of file, md5 of file, verify download, hash of file, file checksum, check file integrity, compute checksum, fingerprint of file
# desc: Show the SHA-256, SHA-1 and MD5 fingerprint of a file, to check a download (file hash setup.exe)
# category: security
# usage: file hash <file> [expected hash]
# rawargs: yes
import hashlib, re
from _lib import args_text, fail
from _files import path_arg
t = args_text()
exp = re.search(r"\b([0-9a-fA-F]{32}|[0-9a-fA-F]{40}|[0-9a-fA-F]{64})\b", t)
t2 = t.replace(exp.group(1), " ") if exp else t
p = path_arg(re.sub(r"^\s*(?:(?:file|of|for)\s+)*(?:hash|checksum|sha256|md5|sha1)?\s*(?:(?:of|for)\s+)?", "", re.sub(r"\b(compare|against|expected|verify|matches?|with)\b", " ", t2, flags=re.I), flags=re.I).strip())
if p.is_dir(): fail("Give a file, not a folder.")
hs = {"sha256": hashlib.sha256(), "sha1": hashlib.sha1(), "md5": hashlib.md5()}
with open(p, "rb") as f:
    for c in iter(lambda: f.read(1 << 20), b""):
        for h in hs.values(): h.update(c)
print(p.name)
for k, h in hs.items(): print(f"  {k:<7}{h.hexdigest()}")
if exp:
    e = exp.group(1).lower()
    hit = next((k for k, h in hs.items() if h.hexdigest() == e), None)
    print(f"MATCH ({hit}): the file is exactly what the publisher listed." if hit else "NO MATCH: this file differs from the expected hash. Do not run it; download it again from the official site.")
