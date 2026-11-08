# keywords: verify checksum, check hash, checksum matches, verify download, compare checksum, sha256 matches, is my download safe
# desc: Check a file against a checksum you were given (verify checksum setup.exe 9f86d0...)
# category: developer
# usage: verify checksum <file> <checksum>
# rawargs: full
# patterns: \bverify\s+(the\s+)?(checksum|hash|download)\b ;; \b(checksum|hash)\s+(matches|verify|check)\b ;; \bcompare\s+(the\s+)?(checksum|hash)\b ;; \bis\s+my\s+download\s+(safe|ok|correct)\b
# priority: 3
import hashlib, hmac, re
from _lib import args_text, fail
from _files import path_arg, tokens
toks = tokens(args_text())
sums = [x for x in toks if re.fullmatch(r"[0-9a-fA-F]{32,128}", x)]
files = [x for x in toks if x not in sums and x.lower() not in {"verify", "checksum", "check", "hash", "sha256", "sha1", "md5", "sha512", "matches", "compare", "my", "download", "of", "the", "is", "safe", "against"}]
if not sums or not files:
    fail("Usage: verify checksum setup.exe 9f86d081884c7d65...   (a file, then the checksum from the website)")
want = sums[0].lower()
algo = {32: "md5", 40: "sha1", 64: "sha256", 128: "sha512"}.get(len(want))
if algo is None:
    fail("That checksum has an unusual length. JeeG checks MD5 (32), SHA-1 (40), SHA-256 (64) and SHA-512 (128).")
p = path_arg(files[0])
if not p.is_file():
    fail(f"{p} is not a file.")
h = hashlib.new(algo)
with open(p, "rb") as f:
    for chunk in iter(lambda: f.read(1 << 20), b""):
        h.update(chunk)
got = h.hexdigest()
if hmac.compare_digest(got, want):
    print(f"MATCH: {p.name} has the expected {algo.upper()} checksum. The file is exactly what was published.")
else:
    print(f"DIFFERENT: {p.name} does NOT match.\n  expected {want}\n  got      {got}\n  Download it again from the official site; do not run it.")
    raise SystemExit(1)
if algo in ("md5", "sha1"):
    print(f"  ({algo.upper()} is weak against deliberate tampering; use a SHA-256 checksum when the site offers one.)")
