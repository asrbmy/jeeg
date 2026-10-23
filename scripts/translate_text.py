# keywords: translator, translation, language
# desc: Translate text with Google Translate
# category: search
# usage: translate text <words>
from _lib import web_task
web_task('https://translate.google.com', 'https://translate.google.com/?sl=auto&tl=en&text={q}&op=translate')
