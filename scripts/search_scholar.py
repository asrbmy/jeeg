# keywords: papers, research, academic, paper, journal
# desc: Search Google Scholar for papers
# category: search
# usage: search scholar <words>
from _lib import web_task
web_task('https://scholar.google.com', 'https://scholar.google.com/scholar?q={q}')
