# keywords: pictures, photos, pics, image
# desc: Search Google Images
# category: search
# usage: search images <words>
from _lib import web_task
web_task('https://images.google.com', 'https://www.google.com/search?tbm=isch&q={q}')
