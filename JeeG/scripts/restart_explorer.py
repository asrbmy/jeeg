# keywords: restart explorer, explorer frozen, taskbar frozen, restart taskbar, fix taskbar, explorer not responding, restart windows explorer, desktop frozen
# desc: Restart Windows Explorer when the taskbar or desktop freezes
# category: system
# confirm: yes
import subprocess, time
from _lib import WIN, fail, spawn
if not WIN: fail("This is for Windows only.")
subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True)
time.sleep(1)
spawn(["explorer.exe"])
print("Explorer restarted.")
