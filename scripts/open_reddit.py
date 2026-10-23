# keywords: subreddit, social, search
# desc: Open Reddit or search it
# category: social
# usage: open reddit <words>
from _lib import web_task
web_task('https://www.reddit.com', 'https://www.reddit.com/search/?q={q}')
