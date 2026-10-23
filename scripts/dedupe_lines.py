# keywords: remove duplicates, dedupe, unique lines, duplicate lines, delete duplicates, remove repeated, uniq, unique items, remove repeats
# desc: Remove duplicate lines or items, keeping the first (remove duplicates a, b, a, c)
# category: text
# usage: remove duplicates <items>
# rawargs: yes
from _text import get_text, emit, items
seen, out = set(), []
parts = items(get_text("remove|delete|duplicates?|duplicated|repeated|repeats?|unique|lines?|items?|from|in"))
for s in parts:
    k = s.lower()
    if k not in seen: seen.add(k); out.append(s)
print(f"{len(parts) - len(out)} duplicate(s) removed, {len(out)} left:")
emit("\n".join(out))
