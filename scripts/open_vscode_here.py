# keywords: vscode here, code here, open project, open this folder, edit here, project in vscode
# desc: Open the current folder in VS Code
# category: developer
from _lib import launch
launch(win=[('code', '.')], mac=[('code', '.'), ('open', '-a', 'Visual Studio Code', '.')], linux=[('code', '.')], name='VS Code')
