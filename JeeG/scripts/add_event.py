# keywords: new event, schedule, remind, reminder, meeting, appointment
# desc: Add a Google Calendar event (words become the title)
# category: workspace
# usage: add event <words>
from _lib import web_task
web_task('https://calendar.google.com/calendar/r/eventedit', 'https://calendar.google.com/calendar/r/eventedit?text={q}')
