# keywords: kill, stop, terminate, end, close, force quit, end task, process, program
# desc: Close a program by name (e.g. kill process notepad)
# category: system
# usage: kill process <name>
# confirm: yes
import subprocess
from _lib import WIN, args_text, fail
name = args_text()
if not name:
    fail("Say which program: kill process <name>")
BLOCK = {"system", "systemd", "init", "launchd", "kernel_task", "csrss", "wininit", "winlogon",
         "services", "lsass", "smss", "dwm", "sshd", "loginwindow", "windowserver"}
base = name.lower().removesuffix(".exe")
if base in BLOCK:
    fail(f"'{name}' is a critical system process; refusing.")
if WIN:
    exe = name if name.lower().endswith(".exe") else name + ".exe"
    rc = subprocess.run(["taskkill", "/IM", exe, "/F"]).returncode
else:
    rc = subprocess.run(["pkill", "-x", name]).returncode
    if rc == 1:
        rc = subprocess.run(["pkill", "-i", "-x", name]).returncode
if rc:
    fail(f"Nothing was closed: no running program called '{name}' (or access denied).")
print(f"Closed '{name}'.")
