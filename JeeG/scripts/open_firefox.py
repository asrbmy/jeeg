# keywords: firefox, mozilla
# desc: Open Firefox
# category: apps
from _lib import launch
launch(win=[('start', 'firefox')], mac=[('open', '-a', 'Firefox')], linux=[('firefox',)], name='Firefox')
