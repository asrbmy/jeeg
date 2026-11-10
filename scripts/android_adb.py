# keywords: android, adb, android phone, my android, android battery, android screenshot, phone over usb
# desc: Look at an Android phone over USB or Wi-Fi with adb (android devices, android battery, android screenshot, android open https://example.com)
# category: hardware
# usage: android devices | android battery | android screenshot | android open <web address>
# rawargs: full
# patterns: ^\s*android\b ;; \badb\b
# priority: 3
import re, shutil, subprocess, time
from pathlib import Path
from _lib import args_text, fail
t = re.sub(r"^\s*(?:my\s+)?(?:android|adb)\s*(?:phone)?\s*", "", args_text(), flags=re.I).strip()
parts = t.split(None, 1)
cmd = parts[0].lower() if parts else "devices"
adb = shutil.which("adb")
if not adb:
    fail("adb is not installed. Get 'platform-tools' from developer.android.com/tools/releases/platform-tools, and turn on USB debugging on the phone.")


def run(*a, binary=False, timeout=30):
    try:
        r = subprocess.run([adb, *a], capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        fail("The phone did not answer in time.")
    if r.returncode != 0:
        fail((r.stderr or r.stdout).decode("utf-8", "replace").strip()[:300] or "adb failed")
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


if cmd == "devices":
    out = run("devices", "-l").strip().splitlines()[1:]
    print("\n".join(out) if out else "No phone found. Plug it in, unlock it and allow USB debugging.")
elif cmd == "battery":
    info = run("shell", "dumpsys", "battery")
    lvl = re.search(r"level:\s*(\d+)", info)
    chg = re.search(r"status:\s*(\d+)", info)
    print(f"Phone battery: {lvl.group(1) if lvl else '?'}%" + ("  (charging)" if chg and chg.group(1) == "2" else ""))
elif cmd == "screenshot":
    data = run("exec-out", "screencap", "-p", binary=True)
    if not data.startswith(b"\x89PNG"):
        fail("The phone did not return a picture.")
    folder = Path.home() / "Pictures"
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / f"android_{time.strftime('%Y%m%d_%H%M%S')}.png"
    dest.write_bytes(data)
    print(f"Saved {dest}")
elif cmd == "open":
    url = parts[1].strip() if len(parts) > 1 else ""
    if not re.fullmatch(r"https?://[^\s'\"`;&|<>$\\]{3,500}", url):
        fail("Give a web address like https://example.com")
    run("shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url)
    print("Opened on the phone.")
else:
    fail("Use:  android devices | battery | screenshot | open <web address>")
