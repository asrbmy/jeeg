# keywords: configure git, setup git, git identity, git name email, setup ssh key, generate ssh key, create ssh key, vscode extension, python project setup, create virtual environment, configure app
# desc: Set up common tools: git name and email, an ssh key, a VS Code extension, a Python virtual environment (configure git name Ravi email r@x.com; add "preview" to see what would run)
# category: developer
# network: yes
# usage: configure git [name N] [email E] [branch B] | configure ssh key | configure vscode extension <id> | configure python project
# confirm: yes
# rawargs: full
# patterns: ^\s*(?:configure|setup|set\s+up)\s+(?:my\s+)?(?:git|ssh|vscode|vs\s+code|python)\b ;; \b(?:generate|create|make)\s+(?:an?\s+)?ssh\s+key\b
# priority: 4
import os, re, shutil, socket, subprocess, sys
from pathlib import Path
from _lib import args_text, fail
t = args_text()
tl = t.lower()
preview = any(w in {"preview", "dry-run", "dryrun"} for w in tl.split())


def run(cmd, **kw):
    print("Command:  " + " ".join(cmd))
    if preview:
        return 0
    return subprocess.call(cmd, **kw)


if re.search(r"\bssh\b", tl) and re.search(r"\bkey\b", tl):
    ssh = shutil.which("ssh-keygen")
    if not ssh:
        fail("ssh-keygen is not installed. Windows: Settings > Optional features > OpenSSH Client.")
    d = Path.home() / ".ssh"
    key = d / "id_ed25519"
    if key.exists():
        print(f"You already have a key at {key}. Not touching it. Your public key (safe to share):")
        pub = Path(str(key) + ".pub")
        print(pub.read_text(encoding="utf-8", errors="replace").strip() if pub.exists() else "(public file missing: ssh-keygen -y -f " + str(key) + ")")
        raise SystemExit(0)
    if not preview:
        d.mkdir(mode=0o700, exist_ok=True)
    c = [ssh, "-t", "ed25519", "-f", str(key), "-C", f"{os.environ.get('USER') or os.environ.get('USERNAME') or 'me'}@{socket.gethostname()}"]
    rc = run(c)                                     # ssh-keygen asks for a passphrase itself, in your terminal
    if rc == 0 and not preview and Path(str(key) + ".pub").exists():
        print("Done. Your public key (add it to GitHub or a server; never share the file without .pub):")
        print(Path(str(key) + ".pub").read_text(encoding="utf-8").strip())
    raise SystemExit(rc)

if re.search(r"\b(?:vscode|vs\s*code|code)\b", tl) and re.search(r"\bextension\b", tl):
    m = re.search(r"\b([A-Za-z0-9][\w\-]*\.[A-Za-z0-9][\w\-.]*)\b(?!.*\b[A-Za-z0-9][\w\-]*\.[A-Za-z0-9])", re.sub(r"(?i)\b(vs\s*code|vscode)\b", " ", t))
    if not m or not re.fullmatch(r"[A-Za-z0-9][\w\-]*\.[A-Za-z0-9][\w\-.]*", m.group(1)):
        fail("Give the extension id, for example:  configure vscode extension ms-python.python")
    code = shutil.which("code")
    if not code:
        fail("The 'code' command was not found. In VS Code: Command Palette > 'Shell Command: Install code command in PATH'.")
    raise SystemExit(run([code, "--install-extension", m.group(1)]))

if re.search(r"\bpython\b|\bvenv\b|virtual\s+environment", tl):
    env = Path(".venv")
    if env.exists():
        print(f"{env.resolve()} already exists. Not touching it.")
    else:
        rc = run([sys.executable, "-m", "venv", str(env)])
        if rc:
            raise SystemExit(rc)
    req = Path("requirements.txt")
    py = env / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if req.is_file() and (preview or py.exists()):
        rc = run([str(py), "-m", "pip", "install", "-r", "requirements.txt"])
        raise SystemExit(rc)
    print("Ready. Activate it:  " + (r".venv\Scripts\activate" if os.name == "nt" else "source .venv/bin/activate"))
    raise SystemExit(0)

if re.search(r"\bgit\b", tl):
    git = shutil.which("git")
    if not git:
        fail("git is not installed. Say:  install git")
    nm = re.search(r"\bname\s+(.+?)(?=\s+(?:email|branch|editor)\b|\s*$)", t, re.I)
    em = re.search(r"\bemail\s+(\S+)", t, re.I)
    br = re.search(r"\bbranch\s+([A-Za-z0-9._\-/]+)", t, re.I)
    sets = []
    if nm:
        v = re.sub(r"\s*\b(preview|dry-run|dryrun)\b\s*$", "", nm.group(1).strip().strip("\"'"), flags=re.I)
        if not v or len(v) > 80 or re.search(r"[\x00-\x1f]", v):
            fail("The name must be 1 to 80 characters.")
        sets.append(("user.name", v))
    if em:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", em.group(1)):
            fail("That email address does not look right.")
        sets.append(("user.email", em.group(1)))
    if br:
        sets.append(("init.defaultBranch", br.group(1)))
    if not sets:
        print("Current git settings:")
        for k in ("user.name", "user.email", "init.defaultBranch", "core.editor"):
            r = subprocess.run([git, "config", "--global", "--get", k], capture_output=True, text=True)
            print(f"  {k:<20} {r.stdout.strip() or '(not set)'}")
        print("Set them:  configure git name Ravi Kumar email ravi@example.com branch main")
        raise SystemExit(0)
    for k, v in sets:
        if run([git, "config", "--global", k, v]):
            raise SystemExit(1)
    print("Preview only: nothing was changed." if preview else "Saved to your global git settings.")
    raise SystemExit(0)

fail("I can configure: git (name, email, branch), an ssh key, a VS Code extension, a Python virtual environment.\n  e.g. configure git name Ravi email ravi@example.com")
