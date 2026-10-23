# keywords: terminal, command prompt, cmd, shell, console, bash
# desc: Open a terminal / command prompt
# category: apps
from _lib import launch
launch(win=[('wt',), ('start', 'cmd')], mac=[('open', '-a', 'Terminal')], linux=[('x-terminal-emulator',), ('gnome-terminal',), ('konsole',), ('xfce4-terminal',), ('xterm',)], name='a terminal')
