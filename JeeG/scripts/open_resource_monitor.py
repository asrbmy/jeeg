# keywords: resource monitor, resmon, performance monitor
# desc: Open Resource Monitor
# category: apps
from _lib import launch
launch(win=[('start', 'resmon')], mac=[('open', '-a', 'Activity Monitor')], linux=[('gnome-system-monitor',)], name='a resource monitor')
