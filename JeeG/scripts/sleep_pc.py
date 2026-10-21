# keywords: sleep, suspend, standby, sleep mode, sleep pc
# desc: Put the computer to sleep
# category: power
# confirm: yes
import subprocess
from _lib import WIN, MAC
if WIN:
    subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
elif MAC:
    subprocess.run(["pmset", "sleepnow"])
else:
    subprocess.run(["systemctl", "suspend"])
