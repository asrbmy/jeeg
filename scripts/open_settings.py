# keywords: settings, preferences, configuration, setup
# desc: Open system Settings
# category: apps
from _lib import launch
launch(win=[('start', 'ms-settings:')], mac=[('open', '-a', 'System Settings'), ('open', '-a', 'System Preferences')], linux=[('gnome-control-center',), ('systemsettings',), ('systemsettings5',), ('xfce4-settings-manager',)], name='Settings')
