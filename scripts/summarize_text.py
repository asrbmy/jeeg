# keywords: summarize, summary, summarise, key sentences, shorten text, tldr, short version
# desc: Pick the key sentences from a text file, PDF or the clipboard (summarize notes.txt, summarize clipboard 5). Not AI: it scores sentences by word frequency.
# category: text
# usage: summarize <file | clipboard> [sentences]
# rawargs: full
# patterns: ^\s*(summari[sz]e|tldr|key sentences)\b
# priority: 3
import math, re
from collections import Counter
from _lib import args_text, fail
t = re.sub(r"^\s*(?:summari[sz]e|tldr|key sentences)\s*(?:of\s+|for\s+)?", "", args_text(), flags=re.I).strip()
k = 5
m = re.search(r"\s+(\d{1,2})\s*(?:sentences?)?\s*$", t)
if m and t[:m.start()].strip():
    k = max(1, min(30, int(m.group(1)))); t = t[:m.start()].strip()
t = t.strip("\"'")
if not t or t.lower() in {"clipboard", "the clipboard", "my clipboard", "what i copied"}:
    from _sys import clip_get
    text = clip_get() or ""
    if not text.strip():
        fail("The clipboard is empty. Copy some text first, or say:  summarize <file>")
else:
    from _files import path_arg
    p = path_arg(t)
    if p.is_dir():
        fail("Give one file, not a folder.")
    if p.stat().st_size > 30_000_000:
        fail("That file is too large (limit 30 MB).")
    if p.suffix.lower() == ".pdf":
        from _lib import need
        need("pypdf")
        from pypdf import PdfReader
        rd = PdfReader(str(p))
        if rd.is_encrypted:
            fail("This PDF is password-protected.")
        text = "\n".join((pg.extract_text() or "") for pg in rd.pages[:200])
    elif p.suffix.lower() == ".docx":
        import zipfile
        try:
            with zipfile.ZipFile(p) as z:
                xml = z.read("word/document.xml").decode("utf-8", "replace")
        except (KeyError, zipfile.BadZipFile):
            fail("I could not read that Word file.")
        text = re.sub(r"<[^>]+>", " ", re.sub(r"</w:p>", "\n", xml))
    else:
        text = p.read_text(encoding="utf-8", errors="replace")
text = re.sub(r"[ \t]+", " ", text)
sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n{2,}|\n(?=[A-Z0-9•\-\*])", text) if 25 <= len(s.strip()) <= 500]
if len(sents) < 3:
    fail("There is not enough text to summarize (I need at least 3 sentences).")
STOP = set("the a an and or but of to in on for with is are was were be been it this that as at by from not have has had you your we our they their he she his her i me my so if then than also can will would could should about into over more most such there these those which who what when how".split())
words = lambda s: [w for w in re.findall(r"[a-z][a-z'-]{2,}", s.lower()) if w not in STOP]
freq = Counter(w for s in sents for w in words(s))
if not freq:
    fail("I could not find words to score.")
top = max(freq.values())
sc = []
for i, s in enumerate(sents):
    w = words(s)
    base = sum(freq[x] / top for x in w) / math.sqrt(len(w) + 4) if w else 0
    sc.append((base * (1.25 if i < 3 else 1.0), i))
pick = sorted(i for _, i in sorted(sc, reverse=True)[:min(k, len(sents) - 1)])
print(f"Key sentences ({len(pick)} of {len(sents)}; picked by word frequency, not written by an AI):")
for i in pick:
    print("  - " + sents[i])
