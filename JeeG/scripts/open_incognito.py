# keywords: private, incognito, secret, anonymous, window
# desc: Open a private / incognito browser window
# category: apps
from _lib import launch
launch(win=[('start', 'chrome', '--incognito'), ('start', 'msedge', '-inprivate'), ('start', 'firefox', '-private-window')], mac=[('open', '-na', 'Google Chrome', '--args', '--incognito'), ('open', '-na', 'Firefox', '--args', '-private-window')], linux=[('google-chrome', '--incognito'), ('chromium', '--incognito'), ('firefox', '--private-window')], name='a browser')
