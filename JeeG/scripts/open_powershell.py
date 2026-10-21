# keywords: powershell, ps, shell, console
# desc: Open PowerShell
# category: apps
from _lib import launch
launch(win=[('start', 'powershell')], mac=[('pwsh',)], linux=[('pwsh',)], name='PowerShell')
