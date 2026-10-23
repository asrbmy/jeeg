# keywords: python, package, pip, library
# desc: Open PyPI or search Python packages
# category: developer
# usage: open pypi <words>
from _lib import web_task
web_task('https://pypi.org', 'https://pypi.org/search/?q={q}')
