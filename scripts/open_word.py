# keywords: word, document editor, doc editor
# desc: Open Microsoft Word / a word processor
# category: apps
from _lib import launch
launch(win=[('start', 'winword')], mac=[('open', '-a', 'Microsoft Word')], linux=[('libreoffice', '--writer'), ('soffice', '--writer')], name='Word')
