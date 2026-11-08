# keywords: anagram, anagram check, are anagrams, same letters
# desc: Check whether two words or phrases are anagrams (anagram listen silent)
# category: fun
# usage: anagram <first> <second>
# rawargs: yes
import re
import sys
from collections import Counter

t = " ".join(sys.argv[1:])
t = re.sub(r"^\s*(?:anagram|anagrams|check|are)\b\s*", "", t, flags=re.I)
parts = [p.strip() for p in re.split(r"\s+(?:and|vs|with|\||,)\s+|\s*[,|]\s*", t) if p.strip()]
if len(parts) != 2:
    parts = t.split()
if len(parts) != 2 or max(map(len, parts)) > 200:
    sys.exit("Usage: anagram listen silent     (for phrases separate with a comma:  anagram dormitory, dirty room)")
clean = [Counter(c for c in p.lower() if c.isalnum()) for p in parts]
print(f"'{parts[0]}' and '{parts[1]}': " + ("YES, they are anagrams." if clean[0] == clean[1] and clean[0] else "no, they are not anagrams."))
if clean[0] != clean[1]:
    extra, missing = clean[0] - clean[1], clean[1] - clean[0]
    print("  Only in the first: " + (" ".join(sorted(extra.elements())) or "-") + "   Only in the second: " + (" ".join(sorted(missing.elements())) or "-"))
