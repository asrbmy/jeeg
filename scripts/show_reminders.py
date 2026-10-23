# keywords: show reminders, list reminders, my reminders, active reminders, pending reminders, what reminders, alarms
# desc: List active background reminders and alarms
# category: reminders
import time
from _time import load_reminders, save_reminders
items = load_reminders()
save_reminders(items)
if not items:
    print("No active reminders.")
for i in items:
    print(f"  #{i['pid']}  {i['desc']}")
