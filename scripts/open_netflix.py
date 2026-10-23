# keywords: movies, series, shows, watch, stream
# desc: Open Netflix
# category: entertainment
# usage: open netflix <words>
from _lib import web_task
web_task('https://www.netflix.com/browse', 'https://www.netflix.com/search?q={q}')
