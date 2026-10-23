# keywords: study, learn, lessons, maths, science
# desc: Open Khan Academy
# category: learning
# usage: open khanacademy <words>
from _lib import web_task
web_task('https://www.khanacademy.org', 'https://www.khanacademy.org/search?page_search_query={q}')
