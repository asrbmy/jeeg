# keywords: desktop type, desktop key, desktop click, press keys on screen, type into app, click on screen, mouse click, send keys
# desc: Type, press keys or click at a screen position in whatever window is in front (desktop type hello, desktop key ctrl+s, desktop click 500 300). Asks first; you only, never an AI. Windows built in; Linux needs xdotool; macOS needs cliclick for clicks.
# category: system
# confirm: yes
# usage: desktop type <text> | desktop key <combo> | desktop click <x> <y> | add 'preview' to see what would happen
# rawargs: full
# patterns: ^\s*desktop\s+(type|key|keys|press|click|move)\b
# priority: 4
import re, shutil, subprocess, time
from _lib import args_text, fail, WIN, MAC
t = args_text().strip()
preview = bool(re.search(r"\b(preview|dry-run|dryrun)\s*$", t, re.I))
t = re.sub(r"\s*\b(preview|dry-run|dryrun)\s*$", "", t, flags=re.I)
m = re.match(r"^\s*desktop\s+(type|keys?|press|click|move)\s+(.+)$", t, re.I | re.S)
if not m:
    fail("Say: desktop type <text> | desktop key <combo, like ctrl+s> | desktop click <x> <y>")
act, arg = m.group(1).lower(), m.group(2).strip()
act = "key" if act in {"keys", "press"} else act
if act == "type":
    if len(arg) > 300 or re.search(r"[\x00-\x08\x0b-\x1f\x7f]", arg):
        fail("Text must be 1 to 300 characters on one line.")
elif act == "key":
    parts = [p_.strip().lower() for p_ in arg.split("+") if p_.strip()]
    if not parts or len(parts) > 4:
        fail("Say a key or combination, like  enter  or  ctrl+s")
else:
    mm = re.match(r"^(\d{1,5})[ ,]+(\d{1,5})$", arg)
    if not mm:
        fail("Say two numbers:  desktop click 500 300   (pixels from the top left)")
    x, y = int(mm.group(1)), int(mm.group(2))
if preview:
    print(f"Would {act} " + (f"'{arg}'" if act != "click" and act != "move" else f"at {x},{y}") + " in the window that is in front, after a 3 second pause. Nothing was changed.")
    raise SystemExit(0)
print("Starting in 3 seconds; click into the right window now (Ctrl+C cancels)...")
time.sleep(3)
NAMED = {"enter": 0x0D, "return": 0x0D, "tab": 0x09, "esc": 0x1B, "escape": 0x1B, "space": 0x20, "backspace": 0x08, "delete": 0x2E, "del": 0x2E,
         "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27, "home": 0x24, "end": 0x23, "pageup": 0x21, "pagedown": 0x22,
         "ctrl": 0x11, "control": 0x11, "shift": 0x10, "alt": 0x12, "win": 0x5B, "windows": 0x5B}
if WIN:
    import ctypes
    u = ctypes.windll.user32
    if act in {"click", "move"}:
        u.SetCursorPos(x, y)
        if act == "click":
            u.mouse_event(2, 0, 0, 0, 0); u.mouse_event(4, 0, 0, 0, 0)
    elif act == "type":
        for ch in arg:
            c = ord(ch)
            for up in (0, 2):
                u.keybd_event(0, c & 0xFFFF, 4 | up, 0)       # KEYEVENTF_UNICODE
            time.sleep(0.01)
    else:
        vks = []
        for p_ in parts:
            v = NAMED.get(p_) or (0x70 + int(p_[1:]) - 1 if re.fullmatch(r"f([1-9]|1[0-2])", p_) else None) or (ord(p_.upper()) if len(p_) == 1 and p_.isalnum() else None)
            if v is None: fail(f"I do not know the key '{p_}'.")
            vks.append(v)
        for v in vks: u.keybd_event(v, 0, 0, 0)
        for v in reversed(vks): u.keybd_event(v, 0, 2, 0)
elif MAC:
    if act == "type":
        r = subprocess.run(["osascript", "-e", f'tell application "System Events" to keystroke "{arg.replace(chr(92), chr(92) * 2).replace(chr(34), chr(92) + chr(34))}"'], capture_output=True, text=True)
    elif act == "key":
        mods = [p_ for p_ in parts if p_ in {"ctrl", "control", "shift", "alt", "win", "cmd", "command"}]
        key = [p_ for p_ in parts if p_ not in mods]
        codes = {"enter": 36, "return": 36, "tab": 48, "esc": 53, "escape": 53, "space": 49, "backspace": 51, "delete": 117, "left": 123, "right": 124, "down": 125, "up": 126}
        if len(key) != 1: fail("Give exactly one main key, like ctrl+s")
        using = ",".join({"ctrl": "control down", "control": "control down", "shift": "shift down", "alt": "option down", "win": "command down", "cmd": "command down", "command": "command down"}[x_] for x_ in mods)
        body = f"key code {codes[key[0]]}" if key[0] in codes else f'keystroke "{key[0][:1]}"'
        r = subprocess.run(["osascript", "-e", f'tell application "System Events" to {body}' + (f" using {{{using}}}" if using else "")], capture_output=True, text=True)
    else:
        if not shutil.which("cliclick"): fail("Clicking on macOS needs 'cliclick' (brew install cliclick).")
        r = subprocess.run(["cliclick", ("c" if act == "click" else "m") + f":{x},{y}"], capture_output=True, text=True)
    if r.returncode != 0: fail("macOS refused (allow Terminal under Privacy > Accessibility): " + r.stderr.strip()[:150])
else:
    if not shutil.which("xdotool"): fail("On Linux this needs 'xdotool' (sudo apt install xdotool). Wayland desktops may not allow it.")
    if act == "type": r = subprocess.run(["xdotool", "type", "--delay", "20", "--", arg], capture_output=True, text=True)
    elif act == "key": r = subprocess.run(["xdotool", "key", "--"] + ["+".join({"control": "ctrl", "win": "super", "windows": "super"}.get(p_, p_) for p_ in parts)], capture_output=True, text=True)
    else:
        r = subprocess.run(["xdotool", "mousemove", str(x), str(y)] + (["click", "1"] if act == "click" else []), capture_output=True, text=True)
    if r.returncode != 0: fail("xdotool refused: " + r.stderr.strip()[:150])
print(f"Done: {act}.")
