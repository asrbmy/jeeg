# keywords: time, date, today, clock, day, what time, current time
# desc: Show the current time and date
# category: time
import datetime
n = datetime.datetime.now().astimezone()
print(n.strftime("%I:%M %p, %A %d %B %Y  (%Z, UTC%z)"))
