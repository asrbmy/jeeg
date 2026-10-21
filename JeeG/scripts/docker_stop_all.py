# keywords: stop docker, stop containers, docker stop, stop all containers, docker down
# desc: Stop all running Docker containers
# category: developer
# confirm: yes
import subprocess
from _lib import call, fail
try:
    ids = subprocess.run(["docker", "ps", "-q"], capture_output=True, text=True).stdout.split()
except FileNotFoundError:
    fail("Docker is not installed.")
if not ids:
    print("No running containers.")
else:
    raise SystemExit(call(["docker", "stop", *ids]))
