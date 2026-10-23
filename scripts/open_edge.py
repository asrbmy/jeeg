# keywords: edge, msedge
# desc: Open Microsoft Edge
# category: apps
from _lib import launch
launch(win=[('start', 'msedge')], mac=[('open', '-a', 'Microsoft Edge')], linux=[('microsoft-edge',), ('microsoft-edge-stable',)], name='Edge')
