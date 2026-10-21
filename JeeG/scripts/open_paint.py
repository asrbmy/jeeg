# keywords: paint, mspaint, draw, drawing, image editor
# desc: Open Paint / an image editor
# category: apps
from _lib import launch
launch(win=[('mspaint',)], mac=[('open', '-a', 'Preview')], linux=[('pinta',), ('kolourpaint',), ('gimp',)], name='a paint program')
