"""OS-level helpers (memory, battery, volume, clipboard, ...). Standard library only.
Not a task itself: names starting with _ are skipped by the runner."""
import ctypes
import glob
import os
import re
import shutil
import subprocess
import sys
import time

from _lib import LINUX, MAC, WIN, fail, spawn


def out(cmd, timeout=10, **kw):
    """Run a command, return stdout text ('' on any failure)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=timeout, **kw)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def ps(script, timeout=20, **env):
    """Run a PowerShell snippet (Windows). Values in env are passed as TR_<NAME> variables."""
    e = dict(os.environ, **{f"TR_{k.upper()}": str(v) for k, v in env.items()})
    exe = shutil.which("powershell") or shutil.which("pwsh")
    if not exe:
        return ""
    try:
        r = subprocess.run([exe, "-NoProfile", "-NonInteractive", "-Command", script],
                           capture_output=True, text=True, errors="replace", timeout=timeout, env=e)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


# ------------------------------------------------------------------ status
def mem_info():
    """(total_bytes, available_bytes) or None."""
    if WIN:
        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        ms = MS()
        ms.dwLength = ctypes.sizeof(MS)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms)):
            return ms.ullTotalPhys, ms.ullAvailPhys
        return None
    if MAC:
        total = int(out(["sysctl", "-n", "hw.memsize"]) or 0)
        vm = out(["vm_stat"])
        size = re.search(r"page size of (\d+)", vm)
        pages = {k: int(v) for k, v in re.findall(r"Pages (free|inactive|speculative):\s+(\d+)", vm)}
        if total and size:
            return total, sum(pages.values()) * int(size.group(1))
        return None
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, _, v = line.partition(":")
                info[k] = int(v.split()[0]) * 1024
        return info["MemTotal"], info.get("MemAvailable", info.get("MemFree", 0))
    except (OSError, KeyError, ValueError):
        return None


def uptime_seconds():
    if WIN:
        return ctypes.windll.kernel32.GetTickCount64() / 1000.0
    if MAC:
        m = re.search(r"sec = (\d+)", out(["sysctl", "-n", "kern.boottime"]))
        return time.time() - int(m.group(1)) if m else None
    try:
        with open("/proc/uptime") as f:
            return float(f.read().split()[0])
    except (OSError, ValueError):
        return None


def battery():
    """(percent, status_text) or None when there is no battery."""
    if WIN:
        class SPS(ctypes.Structure):
            _fields_ = [("ac", ctypes.c_ubyte), ("flag", ctypes.c_ubyte), ("pct", ctypes.c_ubyte),
                        ("sys", ctypes.c_ubyte), ("life", ctypes.c_ulong), ("full", ctypes.c_ulong)]
        s = SPS()
        if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s)) or s.pct == 255 or s.flag == 128:
            return None
        return s.pct, "plugged in" if s.ac == 1 else "on battery"
    if MAC:
        m = re.search(r"(\d+)%;\s*([^;]+);", out(["pmset", "-g", "batt"]))
        return (int(m.group(1)), m.group(2).strip()) if m else None
    for d in sorted(glob.glob("/sys/class/power_supply/BAT*")):
        try:
            pct = int(open(os.path.join(d, "capacity")).read())
            st = open(os.path.join(d, "status")).read().strip().lower()
            return pct, st
        except (OSError, ValueError):
            continue
    return None


def cpu_percent():
    try:
        import psutil
        return psutil.cpu_percent(interval=1)
    except ImportError:
        pass
    if LINUX:
        def snap():
            with open("/proc/stat") as f:
                v = [int(x) for x in f.readline().split()[1:]]
            return sum(v), v[3] + (v[4] if len(v) > 4 else 0)
        try:
            t1, i1 = snap()
            time.sleep(0.5)
            t2, i2 = snap()
            return 100.0 * (1 - (i2 - i1) / max(1, t2 - t1))
        except (OSError, ValueError, IndexError):
            return None
    if MAC:
        m = re.findall(r"([\d.]+)% idle", out(["top", "-l", "2", "-n", "0"], timeout=15))
        return 100.0 - float(m[-1]) if m else None
    v = ps("(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average")
    try:
        return float(v)
    except ValueError:
        return None


# ----------------------------------------------------------------- control
def press_key(vk, times=1, hold=()):
    """Windows: send a virtual key (optionally with modifier keys held)."""
    u = ctypes.windll.user32
    for _ in range(times):
        for k in hold:
            u.keybd_event(k, 0, 0, 0)
        u.keybd_event(vk, 0, 0, 0)
        u.keybd_event(vk, 0, 2, 0)
        for k in reversed(hold):
            u.keybd_event(k, 0, 2, 0)
        time.sleep(0.004)


def _linux_vol(args_pactl, args_amixer):
    if shutil.which("pactl"):
        subprocess.run(["pactl"] + args_pactl, capture_output=True)
    elif shutil.which("amixer"):
        subprocess.run(["amixer", "-q", "sset", "Master"] + args_amixer, capture_output=True)
    else:
        fail("No volume control found (install pulseaudio-utils or alsa-utils).")


def mac_volume():
    v = out(["osascript", "-e", "output volume of (get volume settings)"])
    return int(v) if v.isdigit() else 50


def volume_set(pct):
    pct = max(0, min(100, int(pct)))
    if WIN:
        press_key(0xAE, 50)                    # volume down x50 -> 0
        press_key(0xAF, round(pct / 2))        # each step = 2%
    elif MAC:
        subprocess.run(["osascript", "-e", f"set volume output volume {pct}"])
    else:
        _linux_vol(["set-sink-volume", "@DEFAULT_SINK@", f"{pct}%"], [f"{pct}%"])
    return pct


def volume_step(delta):
    if WIN:
        press_key(0xAF if delta > 0 else 0xAE, max(1, abs(delta) // 2))
    elif MAC:
        volume_set(mac_volume() + delta)
    else:
        sign = "+" if delta > 0 else "-"
        _linux_vol(["set-sink-volume", "@DEFAULT_SINK@", f"{sign}{abs(delta)}%"], [f"{abs(delta)}%{sign}"])


def mute_toggle():
    if WIN:
        press_key(0xAD)
    elif MAC:
        subprocess.run(["osascript", "-e", "set volume output muted (not (output muted of (get volume settings)))"])
    elif shutil.which("pactl"):
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
    else:
        _linux_vol([], ["toggle"])


def media_key(kind):
    """kind: play | next | prev"""
    if WIN:
        press_key({"play": 0xB3, "next": 0xB0, "prev": 0xB1}[kind])
    elif LINUX and shutil.which("playerctl"):
        subprocess.run(["playerctl", {"play": "play-pause", "next": "next", "prev": "previous"}[kind]])
    elif MAC:
        app = next((a for a in ("Spotify", "Music") if out(["pgrep", "-x", a])), None)
        if not app:
            fail("Open Spotify or Music first.")
        cmd = {"play": "playpause", "next": "next track", "prev": "previous track"}[kind]
        subprocess.run(["osascript", "-e", f'tell application "{app}" to {cmd}'])
    else:
        fail("Media control on Linux needs 'playerctl' (sudo apt install playerctl).")


# --------------------------------------------------------------- clipboard
def clip_set(text):
    if WIN:
        subprocess.run(["clip"], input=b"\xff\xfe" + text.encode("utf-16-le"), check=False)
    elif MAC:
        subprocess.run(["pbcopy"], input=text.encode())
    else:
        for cmd in (["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "-ib"]):
            if shutil.which(cmd[0]):
                subprocess.run(cmd, input=text.encode())
                return
        fail("Clipboard needs wl-clipboard, xclip or xsel on Linux.")


def clip_get():
    if WIN:
        return ps("Get-Clipboard -Raw")
    if MAC:
        return out(["pbpaste"])
    for cmd in (["wl-paste", "-n"], ["xclip", "-o", "-selection", "clipboard"], ["xsel", "-ob"]):
        if shutil.which(cmd[0]):
            return out(cmd)
    fail("Clipboard needs wl-clipboard, xclip or xsel on Linux.")


def valid_host(h):
    return bool(re.fullmatch(r"[A-Za-z0-9]([A-Za-z0-9.\-]*[A-Za-z0-9])?|[0-9a-fA-F:.]+", h)) and not h.startswith("-")
