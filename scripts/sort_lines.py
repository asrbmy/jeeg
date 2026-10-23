# keywords: sort lines, sort list, alphabetical order, sort alphabetically, sort items, order list, sort names, sort numbers, sort words
# desc: Sort a list alphabetically or by number (sort lines pear, apple, fig); add 'reverse' for Z-A
# category: text
# usage: sort lines <items>
# rawargs: yes
import re
from _lib import args_text
from _text import get_text, emit, items
t = args_text()
rev = bool(re.search(r"\b(reverse|descending|desc|z-a|backwards)\b", t, re.I))
t = re.sub(r"\b(reverse|descending|desc|z-a|backwards|ascending|a-z)\b", " ", t, flags=re.I) if t.strip() else t
parts = items(get_text() if not t.strip() else t)
def key(s):
    try: return (0, float(s.replace(",", "")), s.lower())
    except ValueError: return (1, 0, s.lower())
emit("\n".join(sorted(parts, key=key, reverse=rev)))
