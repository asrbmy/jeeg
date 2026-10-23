# keywords: clear clipboard, empty clipboard, wipe clipboard, erase clipboard
# desc: Clear the clipboard
# category: clipboard
from _sys import clip_set
clip_set("")
print("Clipboard cleared.")
