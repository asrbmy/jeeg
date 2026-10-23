# keywords: docker, container, image
# desc: Open Docker Hub
# category: developer
# usage: open dockerhub <words>
from _lib import web_task
web_task('https://hub.docker.com', 'https://hub.docker.com/search?q={q}')
