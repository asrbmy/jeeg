# keywords: alarm, set alarm, wake me, wake up, alarm clock, wake me up at, morning alarm
# desc: Set an alarm for a clock time (set alarm 6:30 am)
# category: reminders
# usage: set alarm <time>
# rawargs: yes
from _lib import args_text, fail
from _time import schedule_from_text
t = args_text()
if not t:
    fail("Usage: set alarm 6:30am   (or: set alarm 18:45 gym)")
schedule_from_text(t, "Alarm!")
