# keywords: logout, log out, sign out, signout, log off, logoff
# desc: Sign out of the current user
# category: power
# confirm: yes
import shutil, subprocess
from _lib import WIN, MAC
if WIN:
    subprocess.run(["shutdown", "/l"])
elif MAC:
    subprocess.run(["osascript", "-e", 'tell application "System Events" to log out'])
elif shutil.which("gnome-session-quit"):
    subprocess.run(["gnome-session-quit", "--logout", "--no-prompt"])
else:
    subprocess.run(["loginctl", "terminate-user", ""])
