# keywords: volume down, quieter, decrease volume, lower volume, turn down, sound down, reduce volume
# desc: Lower the volume
# category: hardware
# usage: volume down [amount]
import re
from _lib import args_text
from _sys import volume_step
m = re.search(r"\d+", args_text())
volume_step(-(min(100, int(m.group())) if m else 10))
print("Volume down.")
