# keywords: backup status, last backup, when did i back up, backup check, is my data backed up, data size, how much data
# desc: Show when your data was last backed up and how much data you have
# category: backup
import time
from _lib import human
from _backup import data_files, last
fs = data_files()
print(f"{len(fs)} data file(s), {human(sum(p.stat().st_size for p in fs))} in total.")
t = last()
if t: print(f"Last backup: {time.strftime('%d %b %Y %H:%M', time.localtime(t))} ({int((time.time() - t) / 86400)} days ago)")
else: print("Never backed up. Type:  export data")
