# keywords: meaning, dictionary, definition, define, means, word meaning, what does, synonym
# desc: Dictionary meaning in the terminal (meaning of ephemeral); opens Google if offline
# category: info
# usage: meaning of <word>
# rawargs: yes
import webbrowser, urllib.parse
from _lib import args_text, fail
from _info import define
w = " ".join(x for x in args_text().split() if x.lower() not in ("of", "the", "word", "meaning", "definition", "define", "what", "does", "mean", "means"))
if not w: fail("Usage: meaning of <word>")
r = define(w.split()[0].lower())
if r:
    print(r)
else:
    print(f"No dictionary entry found here for '{w}' - opening Google instead.")
    webbrowser.open("https://www.google.com/search?q=define+" + urllib.parse.quote_plus(w))
