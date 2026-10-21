# keywords: vscode, visual studio, code, editor, ide, programming, vs
# desc: Open Visual Studio Code
# category: apps
from _lib import launch
launch(win=[('code',), ('start', 'code')], mac=[('open', '-a', 'Visual Studio Code')], linux=[('code',)], name='VS Code')
