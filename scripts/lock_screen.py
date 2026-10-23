# keywords: lock, lock pc, lock computer, secure, lock screen, lock my
# desc: Lock the computer
# category: power
import shutil, subprocess
from _lib import WIN, MAC, fail
if WIN:
    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
elif MAC:
    if subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke "q" using {control down, command down}'],
                      capture_output=True).returncode:
        subprocess.run(["pmset", "displaysleepnow"])
else:
    for cmd in (["loginctl", "lock-session"], ["xdg-screensaver", "lock"], ["gnome-screensaver-command", "-l"]):
        if shutil.which(cmd[0]) and subprocess.run(cmd).returncode == 0:
            break
    else:
        fail("No screen-lock command found.")
