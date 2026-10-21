# keywords: control panel, legacy settings
# desc: Open the classic Control Panel
# category: apps
from _lib import launch
launch(win=[('control',)], mac=[('open', '-a', 'System Settings')], linux=[('gnome-control-center',)], name='Control Panel')
