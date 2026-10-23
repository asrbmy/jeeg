# keywords: music, songs, listen, search
# desc: Open YouTube Music or search it
# category: entertainment
# usage: open youtube music <words>
# priority: 1
from _lib import web_task
web_task('https://music.youtube.com', 'https://music.youtube.com/search?q={q}')
