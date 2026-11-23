# keywords: notify me, notification, show notification, popup message, desktop alert, alert me
# desc: Show a desktop notification (notify me dinner is ready, notify Front door opened)
# category: reminders
# usage: notify <text>
# rawargs: full
# patterns: ^\s*notify\s+(?!due\b)(?:me\s+)?\S
# priority: 3
import re
from _lib import args_text, fail, notify
t = re.sub(r"^\s*notify\s+(?:me\s+)?", "", args_text(), flags=re.I).strip()
if not t:
    fail("Usage: notify <text>")
shown = notify("JeeG", t[:200])
print(("Notification shown: " if shown else "No desktop notification is available here, so the message is only printed: ") + t[:200])
