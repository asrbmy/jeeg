# keywords: clothes, fashion, shoes, shop, search
# desc: Open Myntra or search it
# category: shopping
# usage: open myntra <words>
from _lib import web_task
web_task('https://www.myntra.com', 'https://www.myntra.com/{q}')
