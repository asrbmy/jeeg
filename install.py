#!/usr/bin/env python3
"""Install the JeeG command so you can run tasks from any terminal.

    python install.py                 -> creates the command  jeeg   (jeeg open youtube)
    python install.py --name go       -> a different command name (avoid 'tr': Mac/Linux already have one)
    python install.py --uninstall     -> removes it

It writes one tiny launcher file that points at this folder, so move the folder first, then install.
"""
import os
import re
import stat
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def target_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "Microsoft" / "WindowsApps"          # already on PATH for every user
    return Path.home() / ".local" / "bin"


def launcher_text(name: str) -> str:
    py, tr = sys.executable, HERE / "jeeg.py"
    if os.name == "nt":
        return f'@echo off\r\n"{py}" "{tr}" %*\r\n'
    return f'#!/bin/sh\nexec "{py}" "{tr}" "$@"\n'


def main(argv) -> int:
    name, uninstall, i = "jeeg", False, 0
    while i < len(argv):
        if argv[i] == "--uninstall":
            uninstall = True
        elif argv[i] == "--name" and i + 1 < len(argv):
            i += 1
            name = argv[i]
        else:
            print(__doc__)
            return 1
        i += 1
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{1,30}", name):
        print("The command name must be 2-31 letters, numbers, - or _.")
        return 1
    d = target_dir()
    f = d / (name + (".cmd" if os.name == "nt" else ""))
    if uninstall:
        if f.exists():
            f.unlink()
            print(f"Removed {f}")
        else:
            print(f"Nothing to remove ({f} not found).")
        return 0
    if f.exists() and "jeeg.py" not in f.read_text(errors="ignore"):
        print(f"{f} already exists and is not a JeeG launcher; choose another --name.")
        return 1
    d.mkdir(parents=True, exist_ok=True)
    f.write_text(launcher_text(name), encoding="utf-8", newline="")
    if os.name != "nt":
        f.chmod(f.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"Installed {f}\nTry:  {name} open youtube")
    if str(d) not in os.environ.get("PATH", "").split(os.pathsep):
        print(f"Note: {d} is not on your PATH yet. Add it (for example in ~/.bashrc or ~/.zshrc):\n  export PATH=\"{d}:$PATH\"")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
