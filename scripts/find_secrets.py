# keywords: find secrets, scan for secrets, leaked keys in code, api keys in code, hardcoded passwords, secret scan, leaked token
# desc: Look for passwords, API keys and private keys left in a project folder before you share it (find secrets myproject). Values are hidden in the answer.
# category: security
# usage: find secrets [folder]
# rawargs: full
# patterns: ^\s*(?:find|scan|check)\s+(?:for\s+|my\s+)?(?:leaked\s+)?secrets?\b
# priority: 3
import re
from _lib import args_text
from _devscan import root_from, walk, read_text
t = re.sub(r"^\s*(?:find|scan|check)\s+(?:for\s+|my\s+)?(?:leaked\s+)?secrets?\s*(?:in|of|for)?\s*", "", args_text(), flags=re.I)
root = root_from(t)
RULES = [("Private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
         ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
         ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b")),
         ("PyPI token", re.compile(r"\bpypi-[A-Za-z0-9_\-]{40,}")),
         ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}")),
         ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
         ("Stripe key", re.compile(r"\b[sr]k_live_[0-9A-Za-z]{20,}\b")),
         ("Password in text", re.compile(r"""(?i)\b(?:password|passwd|secret|api[_-]?key|token)\b\s*[:=]\s*["']([^"'\s]{8,})["']"""))]
PLACE = re.compile(r"(?i)example|your|changeme|placeholder|xxxx|<.*>|\{.*\}|\$\{|os\.environ|getenv|process\.env|\*{3,}|dummy|sample")
SKIPEXT = {".png", ".jpg", ".jpeg", ".gif", ".zip", ".gz", ".pdf", ".lock", ".min.js"}
hits = []
for p in walk(root):
    if p.suffix.lower() in SKIPEXT:
        continue
    s = read_text(p)
    if s is None:
        continue
    for i, line in enumerate(s.splitlines(), 1):
        if len(line) > 600:
            continue
        for name, rx in RULES:
            m = rx.search(line)
            if m:
                val = m.group(1) if m.groups() else m.group(0)
                if name == "Password in text" and PLACE.search(val):
                    continue
                hits.append((p, i, name, val[:4] + "…" + f"({len(val)} chars)"))
                break
if not hits:
    print(f"No obvious secrets found in {root}. (This looks for common patterns only; it cannot prove a folder is clean.)")
else:
    for p, i, n, v in hits[:100]:
        try: rel = p.relative_to(root)
        except ValueError: rel = p
        print(f"{rel}:{i}  {n}  {v}")
    print(f"\n{len(hits)} possible secret(s). Remove them, and change any that were real, because git history keeps old copies.")
