# keywords: powerpoint, ppt, pptx, presentation editor, slideshow
# desc: Open PowerPoint / a presentation app
# category: apps
from _lib import launch
launch(win=[('start', 'powerpnt')], mac=[('open', '-a', 'Microsoft PowerPoint')], linux=[('libreoffice', '--impress'), ('soffice', '--impress')], name='PowerPoint')
