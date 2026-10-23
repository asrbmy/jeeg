# keywords: git, repo, repository, code, search
# desc: Open GitHub or search it
# category: developer
# usage: open github <words>
from _lib import web_task
web_task('https://github.com', 'https://github.com/search?q={q}')
