# keywords: pins, ideas, social, search
# desc: Open Pinterest or search it
# category: social
# usage: open pinterest <words>
from _lib import web_task
web_task('https://www.pinterest.com', 'https://www.pinterest.com/search/pins/?q={q}')
