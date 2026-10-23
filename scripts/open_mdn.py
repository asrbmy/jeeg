# keywords: javascript, html, css, web docs, documentation
# desc: Open MDN Web Docs or search it
# category: developer
# usage: open mdn <words>
from _lib import web_task
web_task('https://developer.mozilla.org', 'https://developer.mozilla.org/en-US/search?q={q}')
