"""Backup helpers for export/import of your JeeG data. Not a task."""
import json
import time

from _lib import data_dir

EXCLUDE = {"index.json", "reminders.json", "nudge.json", "last_backup.json", ".write_test"}


def data_files():
    d = data_dir()
    return sorted(p for p in d.iterdir() if p.is_file() and p.name not in EXCLUDE
                  and not p.name.endswith(".tmp") and not p.name.startswith("."))


def mark():
    (data_dir() / "last_backup.json").write_text(json.dumps({"t": time.time()}), encoding="utf-8")


def last():
    try:
        return json.loads((data_dir() / "last_backup.json").read_text(encoding="utf-8")).get("t")
    except (OSError, ValueError):
        return None
