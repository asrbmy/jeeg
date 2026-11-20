# keywords: windows list, list windows, focus window, close window, minimize window, maximize window, move window, snap window, switch to window
# desc: List and control open windows (windows list, window focus chrome, window minimize notepad, window snap chrome left, window close notepad). Windows built in; Linux needs wmctrl or xdotool; macOS uses System Events.
# category: system
# usage: windows list | window focus|minimize|maximize|restore|close <part of title> | window snap <part of title> left|right|full
# rawargs: full
# patterns: ^\s*windows?\s+(list|focus|minimi[sz]e|maximi[sz]e|restore|close|snap|move)\b ;; ^\s*(list|show)\s+(my\s+)?(open\s+)?windows\s*$ ;; ^\s*(switch|go)\s+to\s+window\b
# priority: 4
import re, shutil, subprocess, sys
from _lib import args_text, fail, WIN, MAC
t = args_text().strip()
t = re.sub(r"^\s*(?:list|show|switch to|go to)\s+(?:my\s+)?(?:open\s+)?windows?\s*$", "windows list", t, flags=re.I)
t = re.sub(r"^\s*(?:switch|go)\s+to\s+window\s+", "window focus ", t, flags=re.I)
m = re.match(r"^\s*windows?\s+(\w+)\s*(.*)$", t, re.I)
if not m:
    fail("Say: windows list | window focus|minimize|maximize|restore|close <part of title> | window snap <title> left|right|full")
act, rest = m.group(1).lower(), m.group(2).strip().strip("\"'")
act = {"minimise": "minimize", "maximise": "maximize", "move": "snap"}.get(act, act)
if act not in {"list", "focus", "minimize", "maximize", "restore", "close", "snap"}:
    fail("Say: windows list | window focus|minimize|maximize|restore|close <part of title> | window snap <title> left|right|full")
side = "full"
if act == "snap":
    sm = re.search(r"\b(left|right|full|top|bottom)\s*$", rest, re.I)
    if not sm:
        fail("Say where: window snap <title> left|right|full")
    side, rest = sm.group(1).lower(), rest[:sm.start()].strip()
if act != "list" and not rest:
    fail(f"Say which window (part of its title), for example:  window {act} chrome")
if act != "list" and len(rest) > 80:
    fail("That title is too long.")

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=15)

# ---- one small backend per system: list() -> [(id, title)], do(id, act, side)
if WIN:
    import ctypes
    from ctypes import wintypes
    u = ctypes.windll.user32
    def wlist():
        out = []
        CB = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def cb(h, _):
            if u.IsWindowVisible(h):
                n = u.GetWindowTextLengthW(h)
                if n:
                    b = ctypes.create_unicode_buffer(n + 1); u.GetWindowTextW(h, b, n + 1)
                    if b.value.strip() and b.value != "Program Manager":
                        out.append((h, b.value))
            return True
        u.EnumWindows(CB(cb), 0)
        return out
    def wdo(h, a, s):
        if a == "focus":
            u.ShowWindow(h, 9); u.SetForegroundWindow(h)
        elif a == "minimize": u.ShowWindow(h, 6)
        elif a == "maximize": u.ShowWindow(h, 3)
        elif a == "restore": u.ShowWindow(h, 9)
        elif a == "close": u.PostMessageW(h, 0x10, 0, 0)
        elif a == "snap":
            r = wintypes.RECT(); u.SystemParametersInfoW(48, 0, ctypes.byref(r), 0)
            W, H = r.right - r.left, r.bottom - r.top
            x, y, w, hh = {"left": (r.left, r.top, W // 2, H), "right": (r.left + W // 2, r.top, W // 2, H), "top": (r.left, r.top, W, H // 2),
                           "bottom": (r.left, r.top + H // 2, W, H // 2), "full": (r.left, r.top, W, H)}[s]
            u.ShowWindow(h, 9); u.MoveWindow(h, x, y, w, hh, True)
elif MAC:
    def osa(script):
        r = run(["osascript", "-e", script])
        if r.returncode != 0: fail("macOS refused (allow Terminal under System Settings > Privacy > Accessibility): " + r.stderr.strip()[:150])
        return r.stdout
    def wlist():
        o = osa('tell application "System Events" to get name of (processes where background only is false)')
        return [(n.strip(), n.strip()) for n in o.split(",") if n.strip()]
    def wdo(h, a, s):
        q = h.replace('"', "")
        if a == "focus" or a == "restore": osa(f'tell application "{q}" to activate')
        elif a == "close": osa(f'tell application "System Events" to tell process "{q}" to click (first button of window 1 whose subrole is "AXCloseButton")')
        elif a == "minimize": osa(f'tell application "System Events" to tell process "{q}" to set value of attribute "AXMinimized" of window 1 to true')
        else:
            b = osa('tell application "Finder" to get bounds of window of desktop').replace(" ", "").split(",")
            W, H = int(b[2]), int(b[3])
            x, y, w, hh = {"left": (0, 25, W // 2, H - 25), "right": (W // 2, 25, W // 2, H - 25), "top": (0, 25, W, (H - 25) // 2),
                           "bottom": (0, 25 + (H - 25) // 2, W, (H - 25) // 2), "full": (0, 25, W, H - 25)}[s if a == "snap" else "full"]
            osa(f'tell application "System Events" to tell process "{q}" to set {{position, size}} of window 1 to {{{{{x}, {y}}}, {{{w}, {hh}}}}}')
else:
    if not (shutil.which("wmctrl") or shutil.which("xdotool")):
        fail("On Linux this needs 'wmctrl' or 'xdotool' (sudo apt install wmctrl xdotool). Wayland desktops may not allow it.")
    def wlist():
        if shutil.which("wmctrl"):
            r = run(["wmctrl", "-l"])
            return [(p[0], p[3]) for p in (ln.split(None, 3) for ln in r.stdout.splitlines()) if len(p) == 4 and p[1] != "-1"]
        r = run(["xdotool", "search", "--onlyvisible", "--name", ""])
        res = []
        for wid in r.stdout.split()[:200]:
            n = run(["xdotool", "getwindowname", wid]).stdout.strip()
            if n: res.append((wid, n))
        return res
    def wdo(h, a, s):
        if shutil.which("wmctrl"):
            if a == "focus": run(["wmctrl", "-i", "-a", h])
            elif a == "close": run(["wmctrl", "-i", "-c", h])
            elif a == "maximize": run(["wmctrl", "-i", "-r", h, "-b", "add,maximized_vert,maximized_horz"])
            elif a == "restore": run(["wmctrl", "-i", "-r", h, "-b", "remove,maximized_vert,maximized_horz,hidden"])
            elif a == "minimize" and shutil.which("xdotool"): run(["xdotool", "windowminimize", str(int(h, 16))])
            elif a == "minimize": run(["wmctrl", "-i", "-r", h, "-b", "add,hidden"])
        else:
            n = str(int(h)) if not h.startswith("0x") else str(int(h, 16))
            {"focus": lambda: run(["xdotool", "windowactivate", n]), "close": lambda: run(["xdotool", "windowclose", n]),
             "minimize": lambda: run(["xdotool", "windowminimize", n])}.get(a, lambda: fail("That action needs wmctrl on Linux."))()
        if a == "snap":
            if not shutil.which("xdotool"): fail("Snapping needs xdotool on Linux.")
            n = str(int(h, 16)) if str(h).startswith("0x") else str(h)
            g = run(["xdotool", "getdisplaygeometry"]).stdout.split()
            W, H = int(g[0]), int(g[1])
            x, y, w, hh = {"left": (0, 0, W // 2, H), "right": (W // 2, 0, W // 2, H), "top": (0, 0, W, H // 2), "bottom": (0, H // 2, W, H // 2), "full": (0, 0, W, H)}[s]
            run(["wmctrl", "-i", "-r", h, "-b", "remove,maximized_vert,maximized_horz"]) if shutil.which("wmctrl") else None
            run(["xdotool", "windowmove", n, str(x), str(y)]); run(["xdotool", "windowsize", n, str(w), str(hh)])
ws = wlist()
if act == "list":
    if not ws: print("No open windows found.")
    for _, n in ws[:60]: print("  " + n[:90])
    raise SystemExit(0)
hits = [w for w in ws if rest.lower() in w[1].lower()]
if not hits: fail(f"No window has '{rest}' in its title. Say  windows list.")
if len(hits) > 1:
    exact = [w for w in hits if w[1].lower() == rest.lower()]
    if len(exact) == 1: hits = exact
    elif act == "close" or len(hits) > 5:
        fail(f"{len(hits)} windows match '{rest}'; be more specific:\n" + "\n".join("  " + n[:80] for _, n in hits[:8]))
    else: hits = hits[:1]
wdo(hits[0][0], act, side)
print(f"Done: {act} '{hits[0][1][:70]}'" + (f" ({side})" if act == "snap" else "") + ".")
