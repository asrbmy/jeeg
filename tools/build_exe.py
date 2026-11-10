#!/usr/bin/env python3
"""Build the standalone program (no Python needed to run it) with PyInstaller.

    pip install pyinstaller
    python tools/build_exe.py            # result: dist/jeeg  (dist/jeeg.exe on Windows)

The task scripts are plain Python files that the program runs itself, so every standard-library
module they import has to be bundled. This script finds those imports and passes them on.
"""
import ast, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEP = ";" if os.name == "nt" else ":"


def stdlib_imports(folder: Path) -> list:
    own = {p.stem for p in folder.glob("*.py")} | {"jeeg", "jeeg_cmds", "jeeg_api", "jeeg_bridge", "jeeg_autorun", "jeeg_remote", "jeeg_connect"}
    found = set()
    for f in folder.glob("*.py"):
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                found.update(a.name.split(".")[0] for a in n.names)
            elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                found.add(n.module.split(".")[0])
    std = getattr(sys, "stdlib_module_names", None)
    if std is None:
        return sorted(m for m in found if m not in own)
    return sorted(m for m in found if m in std and m not in own)


def main() -> int:
    mods = stdlib_imports(ROOT / "scripts")
    mods += [m for m in ("email.header", "email.message", "email.utils", "http.client", "urllib.parse", "ssl", "imaplib", "smtplib") if m not in mods]   # sub-modules the scripts reach through their parent
    cmd = [sys.executable, "-m", "PyInstaller", "--onefile", "--noconfirm", "--clean", "--name", "jeeg",
           "--add-data", f"{ROOT / 'scripts'}{SEP}scripts", "--add-data", f"{ROOT / 'library'}{SEP}library"]
    for m in mods:
        cmd += ["--hidden-import", m]
    cmd.append(str(ROOT / "jeeg.py"))
    print(f"bundling {len(mods)} standard-library modules used by the task scripts")
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    sys.exit(main())
