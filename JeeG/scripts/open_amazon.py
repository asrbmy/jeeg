# keywords: shop, buy, order, shopping, search
# desc: Open Amazon India or search it
# category: shopping
# usage: open amazon <words>
from _lib import web_task
web_task('https://www.amazon.in', 'https://www.amazon.in/s?k={q}')
