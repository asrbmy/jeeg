# keywords: camera, webcam, photo booth, selfie
# desc: Open the camera
# category: apps
from _lib import launch
launch(win=[('start', 'microsoft.windows.camera:')], mac=[('open', '-a', 'Photo Booth')], linux=[('cheese',)], name='a camera app')
