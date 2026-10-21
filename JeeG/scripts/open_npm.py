# keywords: node, package, javascript, library
# desc: Open npm or search Node packages
# category: developer
# usage: open npm <words>
from _lib import web_task
web_task('https://www.npmjs.com', 'https://www.npmjs.com/search?q={q}')
