# keywords: clock, alarm, timer app, stopwatch app
# desc: Open the Clock / alarms app
# category: apps
from _lib import launch
launch(win=[('start', 'ms-clock:')], mac=[('open', '-a', 'Clock')], linux=[('gnome-clocks',)], name='a clock app')
