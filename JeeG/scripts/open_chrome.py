# keywords: chrome, chromium
# desc: Open Google Chrome
# category: apps
from _lib import launch
launch(win=[('start', 'chrome')], mac=[('open', '-a', 'Google Chrome')], linux=[('google-chrome',), ('google-chrome-stable',), ('chromium',), ('chromium-browser',)], name='Chrome')
