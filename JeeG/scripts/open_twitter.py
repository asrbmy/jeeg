# keywords: x, tweet, social
# desc: Open X (Twitter)
# category: social
# usage: open twitter <words>
from _lib import web_task
web_task('https://x.com', 'https://x.com/search?q={q}')
