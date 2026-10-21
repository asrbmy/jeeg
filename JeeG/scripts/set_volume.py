# keywords: set volume, volume to, volume level, volume percent, sound level
# desc: Set the volume to a level (set volume 40)
# category: hardware
# usage: set volume <0-100>
import re
from _lib import args_text, fail
from _sys import volume_set
m = re.search(r"\d+", args_text())
if not m:
    fail("Give a level 0-100, e.g. set volume 40")
print(f"Volume set to {volume_set(int(m.group()))}%.")
