"""Clock parsing, alerts and background reminders. Not a task."""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from _lib import MAC, WIN, data_dir, fail, notify, spawn

UNITS = {"h": 3600, "hr": 3600, "hrs": 3600, "hour": 3600, "hours": 3600, "m": 60, "min": 60, "mins": 60,
         "minute": 60, "minutes": 60, "s": 1, "sec": 1, "secs": 1, "second": 1, "seconds": 1}
UNIT_RE = "|".join(sorted(UNITS, key=len, reverse=True))


def beep(n=3):
    for _ in range(n):
        if WIN:
            import winsound
            winsound.Beep(1000, 250)
        else:
            sys.stdout.write("\a"); sys.stdout.flush()
        time.sleep(0.3)


def alert(title, text):
    """A message you cannot miss: sound + pop-up (or notification / terminal line)."""
    beep()
    if WIN:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x40 | 0x1000)     # info icon, always on top
    elif MAC:
        subprocess.run(["osascript", "-e", "on run argv", "-e",
                        'display dialog (item 2 of argv) with title (item 1 of argv) buttons {"OK"} default button 1',
                        "-e", "end run", title, text])
    elif not notify(title, text):
        print(f"\n*** {title}: {text} ***")


def parse_duration(text):
    """'1 hour 30 minutes' / '90 sec' -> seconds (0 if none)."""
    return sum(float(n) * UNITS[u] for n, u in re.findall(rf"(\d+(?:\.\d+)?)\s*({UNIT_RE})\b", text.lower()))


def parse_clock(text, now=None):
    """Find a clock time ('5:30pm', '17:30', '6 am', 'noon') -> (epoch_of_next_occurrence, matched_text) or None."""
    now = now or time.time()
    t = text.lower()
    m = re.search(r"\b(\d{1,2})[:.](\d{2})\s*(am|pm|a\.m\.|p\.m\.)?", t) or \
        re.search(r"\b(\d{1,2})()\s*(am|pm|a\.m\.|p\.m\.)", t)
    if m:
        h, mi, ap = int(m.group(1)), int(m.group(2) or 0), (m.group(3) or "").replace(".", "")
        if ap == "pm" and h < 12: h += 12
        if ap == "am" and h == 12: h = 0
        span = m.group(0)
    elif "noon" in t:
        h, mi, span = 12, 0, "noon"
    elif "midnight" in t:
        h, mi, span = 0, 0, "midnight"
    else:
        return None
    if not (0 <= h <= 23 and 0 <= mi <= 59):
        return None
    tm = time.localtime(now)
    target = time.mktime((tm.tm_year, tm.tm_mon, tm.tm_mday, h, mi, 0, 0, 0, -1))
    if "tomorrow" in t or target <= now:
        target = time.mktime((tm.tm_year, tm.tm_mon, tm.tm_mday + 1, h, mi, 0, 0, 0, -1))
    return target, span


def clean_message(text, *remove):
    t = text
    for r in remove:
        t = t.replace(r, " ", 1) if isinstance(r, str) else re.sub(r, " ", t, count=1, flags=re.I)
    t = re.sub(r"\b(remind me|remind|alarm|set an?|please|tomorrow)\b", " ", t, flags=re.I)
    t = re.sub(r"^\s*me\b", "", re.sub(r"\s+", " ", t).strip(), flags=re.I).strip()
    t = re.sub(r"^\s*(?:at|in|every|to|that|about|for|on)\s+", "", t, flags=re.I)
    t = re.sub(r"^\s*(?:to|that|about)\s+", "", t.strip(), flags=re.I)
    return t.strip(" ,.-")


# ------------------------------------------------------------ background workers
def _reg():
    return data_dir() / "reminders.json"


def load_reminders():
    try:
        items = json.loads(_reg().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [i for i in items if pid_alive(i.get("pid", 0))]


def save_reminders(items):
    _reg().write_text(json.dumps(items, indent=1), encoding="utf-8")


def pid_alive(pid):
    if pid <= 0:
        return False
    if WIN:
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not h:
            return False
        code = ctypes.c_ulong()
        ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(h)
        return code.value == 259
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def kill_pid(pid):
    if WIN:
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
    else:
        try:
            os.kill(pid, 15)
        except OSError:
            pass


def start_worker(mode, value, message, desc):
    """mode 'once': value = epoch to fire at.  mode 'repeat': value = seconds between alerts."""
    worker = Path(__file__).with_name("_worker.py")
    p = spawn([sys.executable, str(worker), mode, str(value), message])
    items = load_reminders()
    items.append({"pid": p.pid, "desc": desc, "mode": mode, "value": value, "message": message,
                  "created": time.time()})
    save_reminders(items)
    return p.pid


def countdown(seconds, label=""):
    end = time.time() + seconds
    try:
        while True:
            left = end - time.time()
            if left <= 0:
                break
            sys.stdout.write(f"\r  {label} {int(left // 3600):02d}:{int(left % 3600 // 60):02d}:{int(left % 60):02d} ")
            sys.stdout.flush()
            time.sleep(min(0.5, left))
    except KeyboardInterrupt:
        fail("\nStopped.", 130)
    sys.stdout.write("\r" + " " * 60 + "\r")


def schedule_from_text(text, default_msg):
    """'at 5:30pm call mom' / 'in 20 minutes ...' / 'every 2 hours ...' -> start a background reminder."""
    m = re.search(rf"every\s+(\d+(?:\.\d+)?)\s*({UNIT_RE})\b", text, re.I)
    if m:
        secs = float(m.group(1)) * UNITS[m.group(2).lower()]
        if secs < 60:
            fail("Repeating reminders need at least 1 minute between alerts.")
        msg = clean_message(text, m.group(0)) or default_msg
        start_worker("repeat", secs, msg, f"every {m.group(1)} {m.group(2)}: {msg}")
        print(f"OK - I will remind you every {m.group(1)} {m.group(2)}: {msg}\n(stop with: stop reminders)")
        return
    m = re.search(rf"\bin\s+((?:\d+(?:\.\d+)?\s*(?:{UNIT_RE})\b[\s,]*(?:and\s+)?)+)", text, re.I)
    if m and parse_duration(m.group(1)) > 0:
        when, msg = time.time() + parse_duration(m.group(1)), clean_message(text, m.group(0)) or default_msg
    else:
        c = parse_clock(text)
        if not c:
            fail("Say when: remind me at 5:30pm to call mom  |  remind me in 20 minutes to ...  |  remind me every 2 hours to stretch")
        when, msg = c[0], clean_message(text, c[1]) or default_msg
    if when - time.time() > 7 * 86400:
        fail("Reminders are limited to 7 days ahead.")
    start_worker("once", when, msg, f"{time.strftime('%a %H:%M', time.localtime(when))}: {msg}")
    print(f"OK - I will remind you at {time.strftime('%A %I:%M %p', time.localtime(when))}: {msg}\n(runs in the background; list: show reminders, cancel: stop reminders)")
