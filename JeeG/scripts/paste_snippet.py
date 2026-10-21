# keywords: paste snippet, use snippet, get snippet, copy snippet, snippet, insert text, my snippet
# desc: Copy a saved snippet to the clipboard (paste snippet email)
# category: snippets
# usage: paste snippet <name>
# rawargs: yes
from _lib import args_text, fail
from _store import load
from _sys import clip_set
n = args_text().strip().lower()
s = load("snippets.json", {})
if n not in s:
    fail("No such snippet. See: list snippets")
print(s[n])
try:
    clip_set(s[n]); print(f"(copied '{n}' to the clipboard)")
except SystemExit:
    print("(could not copy to the clipboard on this system)")
