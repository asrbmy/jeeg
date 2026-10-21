# keywords: check updates, software updates, windows update, available updates, pending updates, upgradable packages, outdated software, any updates
# desc: Check which programs and system updates are waiting (does not install)
# category: system
# confirm: yes
import shutil
from _lib import WIN, MAC, call, fail
if WIN:
    if shutil.which("winget"): call(["winget", "upgrade"])
    else: fail("winget was not found. Open Settings > Windows Update instead.")
elif MAC:
    call(["softwareupdate", "-l"])
elif shutil.which("apt"):
    call(["apt", "list", "--upgradable"])
elif shutil.which("dnf"):
    call(["dnf", "check-update"])
else:
    fail("No supported package manager found (apt or dnf).")
