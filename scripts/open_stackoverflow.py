# keywords: programming, error, question, code, search
# desc: Open Stack Overflow or search it
# category: developer
# usage: open stackoverflow <words>
from _lib import web_task
web_task('https://stackoverflow.com', 'https://stackoverflow.com/search?q={q}')
