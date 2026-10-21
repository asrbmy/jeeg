# keywords: edit routines, change routine, customize routine, add routine, routines file, edit routine
# desc: Open the routines file to add or change routines
# category: routines
from _lib import open_path
from _routine import ensure_file
p = ensure_file()
print(f"Editing {p}\nEach routine is a list of task phrases, e.g. \"open slack\", \"wait:5\", \"say:Hello\".")
open_path(p)
