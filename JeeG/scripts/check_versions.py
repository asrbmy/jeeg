# keywords: versions, version, installed, check version, python version, node version, git version, java version, which version, tools installed
# desc: Show installed versions of Python, Node, Git, Docker, Java
# category: developer
import shutil, subprocess, sys
print(f"python  {sys.version.split()[0]}  ({sys.executable})")
for name, cmd in (("pip", [sys.executable, "-m", "pip", "--version"]), ("node", ["node", "--version"]),
                  ("npm", ["npm", "--version"]), ("git", ["git", "--version"]), ("docker", ["docker", "--version"]),
                  ("java", ["java", "-version"]), ("go", ["go", "version"]), ("rustc", ["rustc", "--version"])):
    if name != "pip" and not shutil.which(cmd[0]):
        print(f"{name:<7} not installed"); continue
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        lines = [l for l in ((r.stdout or '') + (r.stderr or '')).splitlines() if l.strip() and not l.startswith("Picked up")]
        print(f"{name:<7} {lines[0].strip() if lines else 'unknown'}")
    except Exception:
        print(f"{name:<7} could not run")
