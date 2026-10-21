# keywords: wiki, encyclopedia, search, article
# desc: Open Wikipedia or look up an article
# category: reference
# usage: open wikipedia <words>
from _lib import web_task
web_task('https://www.wikipedia.org', 'https://en.wikipedia.org/w/index.php?search={q}')
