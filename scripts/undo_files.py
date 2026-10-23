# keywords: undo move, undo rename, undo file change, undo last move, undo organise, revert rename, undo files
# desc: Undo your last file move, rename or Downloads tidy (undo, undo move, undo rename)
# category: files
# usage: undo
# patterns: ^\s*undo\s*$ ;; ^\s*undo\s+(my\s+|the\s+)?(last\s+)?(file\s+)?(move|moves|rename|renames|organi[sz]e|files?|change)\b
# priority: 1
from _undo import undo_last, pending
from _lib import fail
if not pending(): fail("Nothing to undo. (JeeG remembers your last 20 file moves and renames.)")
done, skipped, label = undo_last()
print(f"Undid '{label}': {done} file(s) put back.")
for s in skipped: print(f"  skipped: {s}")
