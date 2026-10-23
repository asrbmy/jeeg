# keywords: docker, containers, docker ps, running containers, docker status
# desc: List running Docker containers
# category: developer
from _lib import call
raise SystemExit(call(['docker', 'ps']))
