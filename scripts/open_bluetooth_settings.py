# keywords: bluetooth, pair, headphones, earbuds
# desc: Open Bluetooth settings
# category: apps
from _lib import launch
launch(win=[('start', 'ms-settings:bluetooth')], mac=[('open', 'x-apple.systempreferences:com.apple.BluetoothSettings'), ('open', '-a', 'System Settings')], linux=[('gnome-control-center', 'bluetooth'), ('blueman-manager',)], name='Bluetooth settings')
