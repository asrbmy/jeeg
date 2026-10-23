# keywords: video, videos, watch, search, yt
# desc: Open YouTube or search it
# category: entertainment
# usage: open youtube <words>
from _lib import web_task
web_task('https://www.youtube.com', 'https://www.youtube.com/results?search_query={q}')
