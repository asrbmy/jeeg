# keywords: music, songs, playlist, search
# desc: Open Spotify web player or search it
# category: entertainment
# usage: open spotify <words>
from _lib import web_task
web_task('https://open.spotify.com', 'https://open.spotify.com/search/{q}')
