"""Background reminder process: _worker.py once|repeat <epoch|seconds> <message>. Not a task."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _time import alert, load_reminders, save_reminders  # noqa: E402


def finish():
    save_reminders([i for i in load_reminders() if i.get("pid") != os.getpid()])


def main():
    mode, value, message = sys.argv[1], float(sys.argv[2]), " ".join(sys.argv[3:]) or "Reminder"
    if mode == "once":
        time.sleep(max(0, value - time.time()))
        alert("Reminder", message)
        finish()
        return
    while True:                                   # repeat until stopped ("stop reminders")
        time.sleep(max(30, value))
        alert("Reminder", message)


if __name__ == "__main__":
    main()
