# keywords: course, courses, learn, study, certificate
# desc: Open Coursera
# category: learning
# usage: open coursera <words>
from _lib import web_task
web_task('https://www.coursera.org', 'https://www.coursera.org/search?query={q}')
