# keywords: vlc, video player, media player, movie player
# desc: Open VLC media player
# category: apps
from _lib import launch
launch(win=[('start', 'vlc')], mac=[('open', '-a', 'VLC')], linux=[('vlc',)], name='VLC')
