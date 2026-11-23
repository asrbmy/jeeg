# keywords: task manager, processes, performance, system monitor, activity monitor
# desc: Open Task Manager / system monitor
# category: apps
# patterns: \btask\s*manager\b
# priority: 4
from _lib import launch
launch(win=[('taskmgr',)], mac=[('open', '-a', 'Activity Monitor')], linux=[('gnome-system-monitor',), ('ksysguard',), ('plasma-systemmonitor',), ('mate-system-monitor',)], name='a task manager')
