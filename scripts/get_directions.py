# keywords: route, navigate, navigation, direction, way, destination
# desc: Directions to a place in Google Maps
# category: maps
# usage: get directions <words>
from _lib import web_task
web_task('https://www.google.com/maps/dir/', 'https://www.google.com/maps/dir/?api=1&destination={q}')
