# keywords: volume up, louder, increase volume, raise volume, turn up, sound up
# desc: Raise the volume
# category: hardware
# usage: volume up [amount]
import re
from _lib import args_text
from _sys import volume_step
m = re.search(r"\d+", args_text())
volume_step(min(100, int(m.group())) if m else 10)
print("Volume up.")
