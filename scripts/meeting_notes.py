# keywords: meeting notes, new meeting notes, minutes of meeting, mom template, notes for meeting, meeting minutes, create meeting notes, agenda template
# desc: Create a dated meeting-notes file from a template (meeting notes weekly sync)
# category: work
# usage: meeting notes [title]
# rawargs: yes
import datetime, re
from pathlib import Path
from _lib import args_text, open_path
from _files import unique_path
title = " ".join(re.sub(r"\b(meeting|notes|new|create|make|for|minutes|of|template|a)\b", " ", args_text(), flags=re.I).split()) or "meeting"
safe = re.sub(r"[^\w .-]", "", title).strip()[:60] or "meeting"
base = Path.home() / "Documents"
folder = (base if base.is_dir() else Path.home()) / "Meeting Notes"
folder.mkdir(parents=True, exist_ok=True)
today = datetime.date.today()
p = unique_path(folder / f"{today:%Y-%m-%d} {safe}.md")
p.write_text(f"""# {title.title()}

Date: {today:%A, %d %B %Y}
Attendees:

## Agenda
-

## Notes
-

## Decisions
-

## Action items
| Owner | Task | Due |
|---|---|---|
|  |  |  |
""", encoding="utf-8")
print(f"Created {p}")
try: open_path(p)
except SystemExit: pass
