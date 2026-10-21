# keywords: snip, snipping, clip, screenshot tool, crop screen
# desc: Open the snipping / screenshot tool
# category: apps
from _lib import launch
launch(win=[('start', 'ms-screenclip:')], mac=[('open', '-a', 'Screenshot')], linux=[('gnome-screenshot', '-i'), ('spectacle',), ('flameshot', 'gui')], name='a screenshot tool')
