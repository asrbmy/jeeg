#!/usr/bin/env python3
"""Add "Send to JeeG" to your file manager, so you can right-click a file and run a JeeG task on it.

    python integrations/sendto/install.py            install
    python integrations/sendto/install.py --remove   remove
    python integrations/sendto/install.py --dry      show what would be written

Windows : a shortcut in the Send to menu (right-click > Send to > JeeG)
Linux   : a script for Nautilus (Files), Nemo and Caja (right-click > Scripts > Send to JeeG)
macOS   : a small app in ~/Applications; drop files on it, or right-click > Open With > JeeG (made with osacompile)

You are asked what to do with the file ("compress", "hash", "word count" ...), then JeeG runs it with the file's path.
Nothing is sent anywhere. Only standard-library Python is used.
"""
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent.parent / "jeeg.py"


def jeeg_command() -> list:
    exe = shutil.which("jeeg")
    if exe:
        return [exe]
    if ENGINE.is_file():
        return [sys.executable, str(ENGINE)]
    raise SystemExit("Could not find JeeG. Install it first (pip install jeeg) or run this from the JeeG folder.")


def quote_sh(parts: list) -> str:
    import shlex
    return " ".join(shlex.quote(p) for p in parts)


def windows_file() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    return Path(base) / "Microsoft" / "Windows" / "SendTo" / "JeeG.cmd"


def windows_body(cmd: list) -> str:
    line = " ".join('"%s"' % c for c in cmd)
    return ('@echo off\r\nchcp 65001 >nul\r\nset /p T=What should JeeG do with this file (for example: hash, word count, compress)? \r\n'
            'if "%T%"=="" exit /b\r\n' + line + ' %T% "%~1"\r\necho.\r\npause\r\n')


def linux_files() -> list:
    base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    out = []
    for fm in ("nautilus", "nemo", "caja"):
        d = base / fm / "scripts" if fm == "nautilus" else (Path.home() / ".local" / "share" / fm / "scripts")
        if d.parent.exists() or fm == "nautilus":
            out.append(d / "Send to JeeG")
    return out


def linux_body(cmd: list) -> str:
    run = quote_sh(cmd)
    return ("#!/bin/sh\n# Send to JeeG: asks what to do, then runs it on the selected file(s).\n"
            'if command -v zenity >/dev/null 2>&1; then T=$(zenity --entry --title "JeeG" --text "What should JeeG do with this file? (hash, word count, compress ...)") || exit 0\n'
            'else printf "What should JeeG do with this file? "; read -r T; fi\n'
            '[ -n "$T" ] || exit 0\n'
            'for F in "$@"; do\n'
            '  OUT=$(' + run + ' $T "$F" 2>&1)\n'
            '  if command -v zenity >/dev/null 2>&1; then printf "%s\\n" "$OUT" | zenity --text-info --title "JeeG" --width 640 --height 360\n'
            '  else printf "%s\\n" "$OUT"; fi\n'
            'done\n')


def mac_app() -> Path:
    return Path.home() / "Applications" / "JeeG.app"


def mac_script(cmd: list) -> str:
    run = quote_sh(cmd).replace("\\", "\\\\").replace('"', '\\"')
    return ('on open theFiles\n'
            '  set t to text returned of (display dialog "What should JeeG do with this file? (hash, word count, compress ...)" default answer "" with title "JeeG")\n'
            '  repeat with f in theFiles\n'
            '    set p to quoted form of POSIX path of f\n'
            '    set r to do shell script "' + run + ' " & t & " " & p & " 2>&1"\n'
            '    display dialog r with title "JeeG" buttons {"OK"} default button "OK"\n'
            '  end repeat\n'
            'end open\n')


def main(argv: list) -> int:
    remove, dry = "--remove" in argv, "--dry" in argv
    if sys.platform == "win32":
        f = windows_file()
        if remove:
            f.unlink(missing_ok=True) if sys.version_info >= (3, 8) else None
            print("Removed" if not f.exists() else "Could not remove", f)
            return 0
        body = windows_body(jeeg_command())
        print(f"{'Would write' if dry else 'Writing'} {f}")
        if not dry:
            f.parent.mkdir(parents=True, exist_ok=True)
            with open(f, "w", newline="") as fh:
                fh.write(body)
            print("Done. Right-click a file > Send to > JeeG.")
        return 0
    if sys.platform == "darwin":
        app = mac_app()
        if remove:
            shutil.rmtree(app, ignore_errors=True)
            print("Removed", app)
            return 0
        scr = mac_script(jeeg_command())
        print(f"{'Would build' if dry else 'Building'} {app}")
        if not dry:
            app.parent.mkdir(parents=True, exist_ok=True)
            tmp = HERE / "_jeeg_droplet.applescript"
            tmp.write_text(scr, encoding="utf-8")
            try:
                subprocess.run(["osacompile", "-o", str(app), str(tmp)], check=True)
            except (OSError, subprocess.CalledProcessError) as ex:
                print(f"Could not build the app: {ex}")
                return 1
            finally:
                tmp.unlink(missing_ok=True) if sys.version_info >= (3, 8) else None
            print("Done. Drop a file on JeeG in ~/Applications, or right-click a file > Open With > JeeG.")
        return 0
    files = linux_files()
    for f in files:
        if remove:
            if f.exists():
                f.unlink()
            print("Removed", f)
            continue
        print(f"{'Would write' if dry else 'Writing'} {f}")
        if not dry:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(linux_body(jeeg_command()), encoding="utf-8")
            f.chmod(f.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if not remove and not dry:
        print("Done. Right-click a file > Scripts > Send to JeeG (you may need to restart your file manager).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
