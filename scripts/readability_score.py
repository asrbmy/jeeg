# keywords: readability, reading level, flesch, grade level, how easy to read, readability score, reading ease
# desc: Reading level of a text or file (Flesch score and grade). Works with piped text.
# category: text
# stdin: yes
# usage: readability <text or file>
# rawargs: full
# patterns: \breadability\b ;; \b(reading|grade)\s+level\b ;; \bflesch\b
# priority: 1
import re
from _lib import args_text, stdin_text, fail, safe_is_file
from pathlib import Path
t = re.sub(r"^\s*(?:readability(?: score)?|reading (?:level|ease)|flesch|grade level|how easy to read)\s*(?:of|for)?\s*", "", args_text(), flags=re.I)
if not t.strip():
    t = stdin_text()
if not t.strip():
    fail("Usage: readability <text or file>   (or pipe text in:  type essay.txt | jeeg readability)")
if len(t) < 300 and safe_is_file(Path(t.strip())):
    t = Path(t.strip()).read_text(encoding="utf-8", errors="replace")[:2_000_000]
words = re.findall(r"[A-Za-z']+", t)
if len(words) < 30:
    fail("Give at least 30 words for a meaningful score.")
sent = max(1, len(re.findall(r"[.!?]+(?:\s|$)", t)))
def syl(w):
    w = w.lower()
    g = re.findall(r"[aeiouy]+", w)
    n = len(g)
    if w.endswith("e") and not w.endswith(("le", "ee")) and n > 1:
        n -= 1
    return max(1, n)
sy = sum(syl(x) for x in words)
wps, spw = len(words) / sent, sy / len(words)
ease = 206.835 - 1.015 * wps - 84.6 * spw
grade = 0.39 * wps + 11.8 * spw - 15.59
label = ("very easy" if ease >= 90 else "easy" if ease >= 80 else "fairly easy" if ease >= 70 else "plain English" if ease >= 60 else
         "fairly difficult" if ease >= 50 else "difficult" if ease >= 30 else "very difficult")
longw = sum(1 for x in words if len(x) >= 7)
print(f"Reading ease : {ease:.0f} / 100  ({label})")
print(f"Grade level  : about {max(grade, 0):.1f}  (US school grade)")
print(f"Words {len(words):,}, sentences {sent:,}, average {wps:.1f} words per sentence, {100 * longw / len(words):.0f}% long words")
if wps > 22:
    print("Tip: sentences are long; try splitting a few.")
