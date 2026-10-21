# keywords: task manager, processes, performance, system monitor, activity monitor
# desc: Open Task Manager / system monitor
# category: apps
from _lib import launch
launch(win=[('taskmgr',)], mac=[('open', '-a', 'Activity Monitor')], linux=[('gnome-system-monitor',), ('ksysguard',), ('plasma-systemmonitor',), ('mate-system-monitor',)], name='a task manager')
