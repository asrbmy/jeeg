# keywords: action items, find action items, extract action items, to dos from notes, tasks from notes, what do i need to do from notes, follow ups from meeting
# desc: Pull the to-do lines out of meeting notes (action items notes.txt, or paste text after it). Simple rules, no AI.
# category: work
# usage: action items <notes file | text>
# rawargs: full
# patterns: \baction\s+items?\b ;; \b(extract|find|pull)\b.*\b(to-?dos?|follow-?ups?|tasks)\b.*\bnotes?\b
# priority: 2
import re
from pathlib import Path
from _lib import args_text, fail, stdin_text
t = re.sub(r"^\s*(?:please\s+)?(?:(?:find|extract|get|pull|list|show)\s+)?(?:the\s+)?action\s+items?\s*(?:from|in|of)?\s*", "", args_text(), flags=re.I).strip()
text = ""
if t:
    p = Path(t.strip("\"'")).expanduser()
    try:
        if len(t) < 300 and p.is_file() and not p.is_symlink() and p.stat().st_size < 2_000_000:
            text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        pass
    if not text:
        text = t.replace(" ; ", "\n")
if not text:
    text = stdin_text()
if not text.strip():
    fail("Give a notes file or paste the notes:  action items meeting.txt")
CUE = re.compile(r"^\s*(?:[-*•]\s*\[ ?\]|[-*•]?\s*(?:todo|to-do|to do|action|ai|next step|follow[- ]?up)\b\s*[:\-]?)|\b(?:will|shall|needs? to|has to|have to|must|should|to be done|please|agreed to|assigned to|owner|deadline|due|by (?:mon|tue|wed|thu|fri|sat|sun|tomorrow|eod|end of|next|\d))\b|@\w+", re.I)
items, seen = [], set()
for raw in text.splitlines():
    line = raw.strip(" \t-*•")
    if len(line) < 6 or len(line) > 300 or line.endswith("?") and not re.search(r"\b(todo|action)\b", line, re.I):
        continue
    if CUE.search(raw) and line.lower() not in seen:
        seen.add(line.lower())
        items.append(re.sub(r"^\[ ?\]\s*", "", line))
if not items:
    print("No action items found. Lines such as 'Ravi will send the quote by Friday' or 'TODO: book room' are picked up.")
    raise SystemExit(0)
print(f"{len(items)} action item(s):")
for i, it in enumerate(items[:60], 1):
    print(f"  {i:>2}. {it}")
print("\nAdd one to your list with:  todo add <text>")
