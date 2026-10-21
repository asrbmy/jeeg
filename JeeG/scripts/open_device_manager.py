# keywords: device manager, drivers, hardware, devices
# desc: Open Device Manager
# category: apps
from _lib import launch
launch(win=[('start', 'devmgmt.msc')], mac=[('open', '-a', 'System Information')], linux=[('gnome-control-center', 'about')], name='Device Manager')
