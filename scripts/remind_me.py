# keywords: remind, reminder, remind me, notify me, alert me, nudge, tell me to, minutes, hours, tomorrow
# desc: Background reminder (remind me at 5:30pm to call mom / in 20 minutes ... / every 2 hours ...)
# category: reminders
# usage: remind me <when> <what>
# rawargs: yes
# priority: 1
from _lib import args_text, fail
from _time import schedule_from_text
t = args_text()
if not t:
    fail("Usage: remind me at 5:30pm to call mom   |   remind me in 20 minutes to ...   |   remind me every 2 hours to stretch")
schedule_from_text(t, "Reminder")
