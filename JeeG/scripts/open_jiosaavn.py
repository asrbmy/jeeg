# keywords: music, songs, saavn, hindi songs
# desc: Open JioSaavn music
# category: entertainment
# usage: open jiosaavn <words>
from _lib import web_task
web_task('https://www.jiosaavn.com', 'https://www.jiosaavn.com/search/{q}')
