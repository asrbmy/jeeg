# keywords: time, date, today, clock, day, what time, current time
# desc: Show the current time and date
# category: time
# patterns: \b(what('?s| is)\s+(the\s+)?(date|time|day)|today'?s?\s+date|current\s+date)\b
# priority: 3
import datetime
n = datetime.datetime.now().astimezone()
print(n.strftime("%I:%M %p, %A %d %B %Y  (%Z, UTC%z)"))
