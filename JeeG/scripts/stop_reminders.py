# keywords: stop reminders, cancel reminders, clear reminders, cancel alarm, stop alarm, remove reminders, delete reminders, stop water reminder
# desc: Cancel all background reminders and alarms
# category: reminders
# priority: 1
from _time import kill_pid, load_reminders, save_reminders
items = load_reminders()
for i in items:
    kill_pid(i["pid"])
save_reminders([])
print(f"Cancelled {len(items)} reminder(s).")
