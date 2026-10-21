# keywords: map, location, place, nearby, search, navigate, where
# desc: Open Google Maps or search a place
# category: maps
# usage: open maps <words>
from _lib import web_task
web_task('https://www.google.com/maps', 'https://www.google.com/maps/search/{q}')
