# keywords: notes, show notes, list notes, my notes, read notes, search notes, find note, recent notes
# desc: Show your recent notes (optionally filter by a word)
# category: productivity
# usage: show notes [word]
from _lib import args_text, data_dir
f = data_dir() / "notes.txt"
lines = f.read_text(encoding="utf-8").splitlines() if f.exists() else []
q = args_text().lower()
if q:
    lines = [l for l in lines if q in l.lower()]
if not lines:
    print("No notes found." if q else "You have no notes yet. Add one with: add note <text>")
for l in lines[-20:]:
    print(l)
