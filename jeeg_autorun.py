"""autorun: run a JeeG phrase or routine by itself at a time you choose, using the system's own scheduler.

    autorun add "start work day" at 9:00 weekdays   (a task phrase, or one of your own routines)
    autorun add "gst 2500 18" at 6:30 pm weekdays   Monday to Friday
    autorun add backup folder documents at 21:00 every sun,wed
    autorun list | autorun remove <number> | autorun remove all

Windows uses Task Scheduler (schtasks), macOS and Linux use cron. Nothing runs in the background by itself:
the system scheduler starts JeeG at the time. Tasks that ask for confirmation are never auto-confirmed.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
MAX_ITEMS = 20
TAG = "jeeg-autorun"


def parse(text: str):
    """'morning at 9:00 pm weekdays' -> ('morning', 21, 0, ['mon', ...]).  Raises ValueError with a plain message."""
    t = text.strip()
    m = re.match(r"^(?P<what>.+?)\s+(?:at|@)\s+(?P<h>\d{1,2})(?::(?P<m>\d{2}))?\s*(?P<ap>am|pm)?\b(?P<rest>.*)$", t, re.I)
    if not m:
        raise ValueError("Say what to run and when, for example:  autorun add morning at 9:00")
    what = m.group("what").strip().strip("\"'").strip()
    h, mi, ap = int(m.group("h")), int(m.group("m") or 0), (m.group("ap") or "").lower()
    if ap:
        if not 1 <= h <= 12:
            raise ValueError("With am/pm the hour is 1 to 12.")
        h = h % 12 + (12 if ap == "pm" else 0)
    if not (0 <= h <= 23 and 0 <= mi <= 59):
        raise ValueError("That is not a valid time. Use 24-hour like 18:30, or 6:30 pm.")
    if not what or len(what) > 150 or re.search(r"[\x00-\x1f\x7f]", what):
        raise ValueError("The phrase must be 1 to 150 characters on one line.")
    if what.split()[0].lower() in {"autorun", "update", "upgrade", "plugin", "plugins", "setup", "web", "ui", "exit", "quit"}:
        raise ValueError(f"'{what.split()[0]}' cannot be scheduled.")
    rest = m.group("rest").lower()
    if re.search(r"\bweekdays?\b", rest):
        days = DAYS[:5]
    elif re.search(r"\bweekends?\b", rest):
        days = DAYS[5:]
    elif re.search(r"\bdaily\b|\bevery\s*day\b", rest) or not rest.strip():
        days = DAYS[:]
    else:
        days = [d for d in DAYS if re.search(rf"\b{d}", rest)]
        if not days:
            raise ValueError("I could not read the days. Use daily, weekdays, weekends, or names like  every mon,thu")
    return what, h, mi, days


def describe(h: int, mi: int, days) -> str:
    when = f"{h:02d}:{mi:02d}"
    if len(days) == 7:
        return f"every day at {when}"
    if days == DAYS[:5]:
        return f"weekdays at {when}"
    if days == DAYS[5:]:
        return f"weekends at {when}"
    return f"every {', '.join(days)} at {when}"


def _cmd(here: Path, state: Path, phrase: str) -> list:
    if getattr(sys, "frozen", False):
        return [sys.executable, phrase]
    return [sys.executable, str(here / "jeeg.py"), phrase]


def cron_line(here: Path, state: Path, item_id: str, phrase: str, h: int, mi: int, days) -> str:
    dow = "*" if len(days) == 7 else ",".join(str((DAYS.index(d) + 1) % 7) for d in days)
    cmd = " ".join(shlex.quote(x) for x in _cmd(here, state, phrase)).replace("%", "\\%")
    return f"{mi} {h} * * {dow} JEEG_HOME={shlex.quote(str(state))} {cmd} >/dev/null 2>&1  # {TAG}:{item_id}"


def schtasks_args(here: Path, state: Path, item_id: str, phrase: str, h: int, mi: int, days) -> list:
    tr = subprocess.list2cmdline(_cmd(here, state, phrase))
    base = ["schtasks", "/Create", "/TN", f"JeeG-{item_id}", "/TR", tr, "/ST", f"{h:02d}:{mi:02d}", "/F"]
    if len(days) == 7:
        return base + ["/SC", "DAILY"]
    return base + ["/SC", "WEEKLY", "/D", ",".join(d.upper() for d in days)]


def _load(state: Path) -> list:
    try:
        d = json.loads((state / "autorun.json").read_text(encoding="utf-8"))
        return d if isinstance(d, list) else []
    except (OSError, ValueError):
        return []


def _save(state: Path, items: list) -> None:
    state.mkdir(parents=True, exist_ok=True)
    tmp = state / "autorun.json.tmp"
    tmp.write_text(json.dumps(items, indent=1), encoding="utf-8")
    os.replace(tmp, state / "autorun.json")


def _crontab_read():
    r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def _crontab_write(text: str) -> bool:
    r = subprocess.run(["crontab", "-"], input=text, capture_output=True, text=True)
    return r.returncode == 0


def _install(here, state, item, dry: bool) -> bool:
    p, h, mi, days, i = item["phrase"], item["h"], item["m"], item["days"], item["id"]
    if os.name == "nt":
        args = schtasks_args(here, state, i, p, h, mi, days)
        if dry:
            print("[dry-run] " + subprocess.list2cmdline(args))
            return True
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode != 0:
            print("Task Scheduler refused it: " + (r.stderr or r.stdout).strip()[:200])
        return r.returncode == 0
    line = cron_line(here, state, i, p, h, mi, days)
    if dry:
        print("[dry-run] add to crontab:  " + line)
        return True
    if shutil.which("crontab") is None:
        print("This computer has no 'crontab' command. Install cron, or use your system's own scheduler with:\n  " + line)
        return False
    cur = _crontab_read()
    new = "\n".join(l for l in cur.splitlines() if f"{TAG}:{i}" not in l) + ("\n" if cur.strip() else "") + line + "\n"
    ok = _crontab_write(new)
    if not ok:
        print("Could not update your crontab.")
    return ok


def _uninstall(item_id: str) -> None:
    if os.name == "nt":
        subprocess.run(["schtasks", "/Delete", "/TN", f"JeeG-{item_id}", "/F"], capture_output=True, text=True)
    elif shutil.which("crontab"):
        cur = _crontab_read()
        keep = [l for l in cur.splitlines() if f"{TAG}:{item_id}" not in l]
        if len(keep) != len(cur.splitlines()):
            _crontab_write("\n".join(keep) + ("\n" if keep else ""))


def cmd_autorun(arg: str, here: Path, state: Path, dry: bool = False) -> int:
    a = arg.strip()
    low = a.lower()
    items = _load(state)
    if low in {"", "help"}:
        print(__doc__.strip())
        return 0
    if low in {"list", "show", "ls"}:
        if not items:
            print("Nothing is scheduled. Example:  autorun add morning at 9:00 weekdays")
        for n, it in enumerate(items, 1):
            print(f"  {n}. {it['phrase']}  -  {describe(it['h'], it['m'], it['days'])}")
        return 0
    if low.startswith(("remove", "delete", "cancel")):
        rest = low.split(None, 1)[1] if " " in low else ""
        targets = list(items) if rest == "all" else [items[int(rest) - 1]] if rest.isdigit() and 1 <= int(rest) <= len(items) else None
        if targets is None:
            print("Say which one:  autorun remove 1   (see  autorun list)   or  autorun remove all")
            return 1
        for it in targets:
            if not dry:
                _uninstall(it["id"])
            print(f"Removed: {it['phrase']}  ({describe(it['h'], it['m'], it['days'])})")
        if not dry:
            _save(state, [x for x in items if x not in targets])
        return 0
    if low.startswith("add "):
        try:
            what, h, mi, days = parse(a[4:])
        except ValueError as ex:
            print(ex)
            return 1
        if len(items) >= MAX_ITEMS:
            print(f"You already have {MAX_ITEMS} scheduled items. Remove one first.")
            return 1
        try:                                     # a saved routine name -> "run routine <name>"
            known = set(json.loads((state / "routines.json").read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError):
            known = set()
        key = re.sub(r"\s+", "_", what.lower())
        if key in known:
            what = f"run routine {key}"
        used = {int(x["id"]) for x in items if str(x.get("id", "")).isdigit()}
        item = {"id": str(next(i for i in range(1, 100) if i not in used)), "phrase": what, "h": h, "m": mi, "days": days}
        if not _install(here, state, item, dry):
            return 1
        if not dry:
            _save(state, items + [item])
        print(("Would schedule" if dry else "Scheduled") + f": '{what}'  {describe(h, mi, days)}.")
        print("It runs when your computer is on at that time. Tasks that ask for confirmation will not run by themselves.")
        return 0
    print("Usage: autorun add <phrase or routine> at <time> [daily|weekdays|weekends|every mon,thu] | autorun list | autorun remove <n>")
    return 1
