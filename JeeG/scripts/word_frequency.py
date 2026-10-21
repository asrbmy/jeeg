# keywords: word frequency, most common words, word count by word, frequent words, top words, count each word, repeated words, which words repeat
# desc: Most common words in some text or a text file (word frequency notes.txt)
# category: text
# usage: word frequency <text|file>
# rawargs: yes
import re
from collections import Counter
from pathlib import Path
from _lib import args_text
from _text import get_text
from _files import is_text_file
t = get_text()
p = Path(t.strip().strip("\"'")).expanduser()
try:
    if len(t) < 300 and p.is_file() and is_text_file(p): t = p.read_text(encoding="utf-8", errors="ignore")
except OSError: pass
STOP = set("the a an and or of to in is it that this for on with as at by be are was were i you he she we they not but from have has had".split())
ws = re.findall(r"[a-z0-9']+", t.lower())
c = Counter(x for x in ws if x not in STOP and len(x) > 1)
print(f"{len(ws):,} words, {len(set(ws)):,} different. Top words (common small words ignored):")
for w_, n in c.most_common(15): print(f"  {w_:<18}{n}")
