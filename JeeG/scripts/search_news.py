# keywords: headlines, latest, current, events
# desc: Search Google News / latest headlines
# category: search
# usage: search news <words>
from _lib import web_task
web_task('https://news.google.com', 'https://news.google.com/search?q={q}')
