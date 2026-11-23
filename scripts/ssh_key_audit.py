# keywords: ssh key audit, audit ssh keys, check ssh keys, ssh key security, ssh folder permissions, authorized keys check
# desc: Check your SSH keys and folder for weak or risky settings (old key types, no passphrase, loose permissions). Reads only; never shows a key.
# category: security
# usage: ssh key audit
# patterns: ^\s*(?:ssh\s+key\s+audit|audit\s+(?:my\s+)?ssh|check\s+(?:my\s+)?ssh\s+keys?)\b
# priority: 3
import os, stat
from pathlib import Path
d = Path.home() / ".ssh"
if not d.is_dir():
    print("No .ssh folder found, so there is nothing to check."); raise SystemExit(0)
notes, n = [], 0
def mode(p): return stat.S_IMODE(p.stat().st_mode)
if os.name != "nt" and mode(d) & 0o077: notes.append(f".ssh folder is open to other users (mode {oct(mode(d))}); run: chmod 700 ~/.ssh")
for p in sorted(d.iterdir()):
    if not p.is_file() or p.suffix == ".pub" or p.name in ("known_hosts", "config", "authorized_keys", "known_hosts.old"): continue
    try: head = p.read_text(errors="replace")[:4000]
    except OSError: continue
    if "PRIVATE KEY-----" not in head: continue
    n += 1
    if os.name != "nt" and mode(p) & 0o077: notes.append(f"{p.name}: private key readable by others (mode {oct(mode(p))}); run: chmod 600 ~/.ssh/{p.name}")
    if "BEGIN RSA PRIVATE KEY" in head and "ENCRYPTED" not in head: notes.append(f"{p.name}: old-format RSA key with no passphrase")
    elif "BEGIN OPENSSH PRIVATE KEY" in head:
        import base64, re
        try:
            raw = base64.b64decode(re.sub(r"-----.*?-----|\s", "", head))
            if raw.startswith(b"openssh-key-v1\0") and raw[15:19] == b"\x00\x00\x00\x04" and raw[19:23] == b"none": notes.append(f"{p.name}: no passphrase (anyone who copies this file can use it)")
        except Exception: pass
    elif "BEGIN PRIVATE KEY" in head: notes.append(f"{p.name}: unencrypted key")
    pub = p.with_name(p.name + ".pub")
    if pub.exists():
        t = pub.read_text(errors="replace").split()[:1]
        if t and t[0] in ("ssh-dss",): notes.append(f"{p.name}: DSA keys are obsolete; make a new ed25519 key")
        if t and t[0] == "ssh-rsa": notes.append(f"{p.name}: RSA key; fine if 3072 bits or more, otherwise make an ed25519 key")
print(f"Checked {n} private key(s) in {d}.")
print("\n".join("- " + x for x in notes) if notes else "No problems found.")
ak = d / "authorized_keys"
if ak.exists():
    c = sum(1 for l in ak.read_text(errors="replace").splitlines() if l.strip() and not l.startswith("#"))
    print(f"authorized_keys lists {c} key(s) that can log in to this computer; remove any you do not recognise.")
