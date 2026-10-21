# keywords: shop, buy, order, shopping, search
# desc: Open Flipkart or search it
# category: shopping
# usage: open flipkart <words>
from _lib import web_task
web_task('https://www.flipkart.com', 'https://www.flipkart.com/search?q={q}')
