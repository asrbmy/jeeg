# keywords: paste, clipboard, show clipboard, what did i copy, read clipboard, clipboard contents
# desc: Show what is on the clipboard
# category: clipboard
from _sys import clip_get
t = clip_get()
print(t if t else "(clipboard is empty or not text)")
