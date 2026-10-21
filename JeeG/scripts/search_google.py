# keywords: find, lookup, look up, web, google
# desc: Search Google (or open it)
# category: search
# usage: search google <words>
# priority: 1
from _lib import web_task
web_task('https://www.google.com', 'https://www.google.com/search?q={q}')
