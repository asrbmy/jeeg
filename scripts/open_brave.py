# keywords: brave
# desc: Open Brave browser
# category: apps
from _lib import launch
launch(win=[('start', 'brave')], mac=[('open', '-a', 'Brave Browser')], linux=[('brave-browser',), ('brave',)], name='Brave')
