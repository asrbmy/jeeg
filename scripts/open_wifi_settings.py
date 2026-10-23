# keywords: wifi settings, wireless, network settings
# desc: Open Wi-Fi settings
# category: apps
from _lib import launch
launch(win=[('start', 'ms-settings:network-wifi')], mac=[('open', 'x-apple.systempreferences:com.apple.Network-Settings.extension'), ('open', '-a', 'System Settings')], linux=[('gnome-control-center', 'wifi'), ('nm-connection-editor',)], name='Wi-Fi settings')
