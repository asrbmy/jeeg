"""The desktop window (needs tkinter and a display; skipped otherwise). Run: xvfb-run python tests/test_gui.py"""
import os, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["JEEG_HOME"] = tempfile.mkdtemp(prefix="jeeg-gui-")
P = F = 0


def ok(c, label):
    global P, F
    if c:
        P += 1
    else:
        F += 1
        print("FAIL:", label)


import jeeg_gui
rc, out = jeeg_gui.run_line("gst 100 18")
ok(rc == 0 and "Total      : 118.00" in out, "run_line runs a task")
rc, out = jeeg_gui.run_line("shutdown pc")
ok(rc == 3 and "needs confirmation" in out, "run_line reports a confirmation")
rc, out = jeeg_gui.run_line("zzzz qqqq")
ok(rc != 0 and "No matching task" in out, "run_line reports a miss")
ok("tkinter" in jeeg_gui.tk_missing_message(), "missing-tkinter message")
try:
    import tkinter as tk
    root = tk.Tk()
except Exception as ex:
    print(f"SKIP window checks: {str(ex)[:80]}")
    print(f"{P} passed, {F} failed (window parts skipped)")
    sys.exit(1 if F else 0)
app = jeeg_gui.App(root)


def go(line):
    app.entry.insert(0, line)
    app.submit(sync=True)
    root.update()


go("gst 100 18"); go("25 * 4"); go("zzzz qqqq")
t = app.text()
ok("Total      : 118.00" in t and "25 * 4 = 100" in t and "No matching task" in t, "results are shown")
ok("task> gst 100 18" in t, "the typed line is echoed")
asked = []
app.messagebox.askyesno = lambda *a, **k: (asked.append(a), False)[1]
go("shutdown pc")
ok(asked and "Not run." in app.text() and "Shutting down" not in app.text(), "a confirmation shows a box and No does not run it")
app.entry.insert(0, "x"); app.entry.delete(0, "end"); app.walk(-1)
ok(app.entry.get() == "shutdown pc", "Up brings back the last line")
app.entry.delete(0, "end"); app.entry.insert(0, "clear"); app.submit(); root.update()
ok("gst 100 18" not in app.text(), "clear empties the panel")
root.destroy()
print(f"{P} passed, {F} failed")
sys.exit(1 if F else 0)
