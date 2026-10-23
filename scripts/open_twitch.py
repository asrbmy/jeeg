# keywords: streams, gaming, live
# desc: Open Twitch
# category: entertainment
# usage: open twitch <words>
from _lib import web_task
web_task('https://www.twitch.tv', 'https://www.twitch.tv/search?term={q}')
