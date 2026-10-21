# keywords: notes, text editor, write, notepad, textedit
# desc: Open a simple text editor
# category: apps
from _lib import launch
launch(win=[('notepad',)], mac=[('open', '-a', 'TextEdit')], linux=[('gedit',), ('kate',), ('mousepad',), ('xed',), ('pluma',)], name='a text editor')
