# keywords: write email, new email, send email, draft, new mail, compose
# desc: Compose a Gmail message (words become the subject)
# category: email
# usage: compose email <words>
from _lib import web_task
web_task('https://mail.google.com/mail/?view=cm&fs=1', 'https://mail.google.com/mail/?view=cm&fs=1&su={q}')
