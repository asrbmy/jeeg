# keywords: copy, clipboard, copy text, copy to clipboard, put on clipboard
# desc: Copy text to the clipboard (copy hello world)
# category: clipboard
# usage: copy to clipboard <text>
# stdin: yes
from _lib import args_or_stdin, fail
from _sys import clip_set
t = args_or_stdin()
if not t:
    fail("Say what to copy: copy to clipboard <text>")
clip_set(t)
print(f"Copied {len(t)} characters.")
