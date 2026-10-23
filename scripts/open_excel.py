# keywords: excel, spreadsheet editor, xls, xlsx
# desc: Open Microsoft Excel / a spreadsheet app
# category: apps
from _lib import launch
launch(win=[('start', 'excel')], mac=[('open', '-a', 'Microsoft Excel')], linux=[('libreoffice', '--calc'), ('soffice', '--calc')], name='Excel')
