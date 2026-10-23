# keywords: application, program, software, launch, app
# desc: Open any installed app by name (open app <name>)
# category: apps
# usage: open app <name>
import os, shutil, subprocess, sys
from _lib import MAC, WIN, args_text, fail, spawn

name = args_text()
if not name:
    fail("Say which app: open app <name>")
if any(c in name for c in '&|<>^%"\n'):
    fail("That app name contains characters that are not allowed.")
if WIN:
    exe = shutil.which(name)
    if exe:
        spawn([exe])
    elif subprocess.run(["cmd", "/c", "start", "", name], capture_output=True).returncode:
        fail(f"Could not find an app called '{name}'.")
elif MAC:
    if subprocess.run(["open", "-a", name], capture_output=True).returncode:
        fail(f"Could not find an app called '{name}'.")
else:
    exe = shutil.which(name) or shutil.which(name.lower().replace(" ", "-"))
    if exe:
        spawn([exe])
    elif shutil.which("gtk-launch") and subprocess.run(["gtk-launch", name], capture_output=True).returncode == 0:
        pass
    else:
        fail(f"Could not find an app called '{name}'.")
