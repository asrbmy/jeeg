"""JeeG in a small window (tkinter, which comes with Python): a text box, a Run button and a results panel.

    jeeg gui            (or:  jeeg --gui)

It is the same JeeG: every line is run exactly as if you typed it in the terminal (through  jeeg --json), so aliases, variables, chains,
confirmations and privacy rules all behave the same. A task that asks first shows a Yes/No box. Nothing leaves your computer.
Keys: Enter runs, Up/Down walk through earlier lines, Ctrl+L clears, Esc empties the box.
"""
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE / "jeeg.py"


def tk_missing_message() -> str:
    if sys.platform.startswith("linux"):
        hint = "Install it with your package manager, for example:  sudo apt install python3-tk   (Fedora: sudo dnf install python3-tkinter)"
    elif sys.platform == "darwin":
        hint = "Use the installer from python.org (it includes it), or:  brew install python-tk"
    else:
        hint = "Reinstall Python from python.org and keep 'tcl/tk and IDLE' ticked."
    return "The window needs tkinter, which this Python does not have. " + hint


def run_line(line: str, yes: bool = False, extra=()):
    """Run one line through the engine. Returns (exit code, text)."""
    cmd = [sys.executable, str(ENGINE)] + list(extra) + ["--json"] + (["--yes"] if yes else []) + [line]
    env = dict(os.environ)
    env.pop("JEEG_VIA_AI", None)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return 124, "That took more than 5 minutes, so I stopped waiting."
    try:
        d = json.loads(r.stdout)
        return int(d.get("exit", r.returncode)), str(d.get("output", ""))
    except ValueError:
        return r.returncode, (r.stdout + r.stderr).strip() or "(no output)"


class App:
    def __init__(self, root, extra=()):
        import tkinter as tk
        from tkinter import messagebox, scrolledtext
        self.tk, self.messagebox, self.root, self.extra = tk, messagebox, root, tuple(extra)
        root.title("JeeG")
        root.geometry("760x520")
        root.minsize(420, 300)
        self.history, self.pos, self.busy = [], 0, False
        top = tk.Frame(root, padx=10, pady=8)
        top.pack(fill="x")
        self.entry = tk.Entry(top, font=("TkDefaultFont", 13))
        self.entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.btn = tk.Button(top, text="Run", width=8, command=self.submit)
        self.btn.pack(side="left", padx=(8, 0))
        tk.Button(top, text="Tasks", command=lambda: self.go("list")).pack(side="left", padx=(6, 0))
        tk.Button(top, text="Tips", command=lambda: self.go("tips")).pack(side="left", padx=(6, 0))
        self.out = scrolledtext.ScrolledText(root, wrap="word", font=("Courier", 11), padx=8, pady=6, state="disabled")
        self.out.pack(fill="both", expand=True, padx=10)
        self.status = tk.Label(root, text="Type what you want to do, for example:  emi loan 25 lakh 8.5% 20 years", anchor="w", padx=10, pady=4)
        self.status.pack(fill="x")
        self.out.tag_configure("cmd", font=("Courier", 11, "bold"))
        self.out.tag_configure("bad", foreground="#b00020")
        self.entry.bind("<Return>", lambda e: self.submit())
        self.entry.bind("<Up>", lambda e: self.walk(-1))
        self.entry.bind("<Down>", lambda e: self.walk(1))
        self.entry.bind("<Escape>", lambda e: self.entry.delete(0, "end"))
        root.bind("<Control-l>", lambda e: self.clear())
        self.entry.focus_set()
        self.write("JeeG - say what you want to do. 'list' shows every task, 'explain <words>' shows how a line is understood.\n", "cmd")

    # ---- output
    def write(self, text, tag=None):
        self.out.configure(state="normal")
        self.out.insert("end", text, tag or ())
        self.out.see("end")
        self.out.configure(state="disabled")

    def clear(self):
        self.out.configure(state="normal")
        self.out.delete("1.0", "end")
        self.out.configure(state="disabled")

    def text(self) -> str:
        return self.out.get("1.0", "end")

    # ---- input
    def walk(self, d):
        if not self.history:
            return
        self.pos = max(0, min(len(self.history), self.pos + d))
        self.entry.delete(0, "end")
        if self.pos < len(self.history):
            self.entry.insert(0, self.history[self.pos])

    def go(self, line):
        self.entry.delete(0, "end")
        self.entry.insert(0, line)
        self.submit()

    def submit(self, sync=False):
        line = self.entry.get().strip()
        if not line or self.busy:
            return
        self.entry.delete(0, "end")
        if line.lower() in {"exit", "quit", "q"}:
            self.root.destroy()
            return
        if line.lower() in {"clear", "cls"}:
            self.clear()
            return
        if not self.history or self.history[-1] != line:
            self.history.append(line)
        self.pos = len(self.history)
        self.write(f"task> {line}\n", "cmd")
        self.busy = True
        self.btn.configure(state="disabled")
        self.status.configure(text="Working...")
        if sync:
            self.finish(line, *run_line(line, extra=self.extra))
        else:
            threading.Thread(target=lambda: self.after_run(line), daemon=True).start()

    def after_run(self, line):
        rc, text = run_line(line, extra=self.extra)
        try:
            self.root.after(0, lambda: self.finish(line, rc, text))
        except Exception:
            pass

    def finish(self, line, rc, text):
        if rc == 3 and "needs confirmation" in text:
            ok = self.messagebox.askyesno("JeeG asks first", f"'{line}' changes something on this computer.\n\nRun it?")
            if ok:
                rc, text = run_line(line, yes=True, extra=self.extra)
            else:
                text, rc = "Not run.", 0
        self.write((text.rstrip() or "(done)") + "\n\n", "bad" if rc not in (0,) else None)
        self.status.configure(text="Done." if rc == 0 else {2: "More than one task fits: be more specific.", 3: "Not run."}.get(rc, f"It did not work (exit code {rc})."))
        self.busy = False
        self.btn.configure(state="normal")
        self.entry.focus_set()


def main(extra=()) -> int:
    try:
        import tkinter as tk
    except ImportError:
        print(tk_missing_message())
        return 1
    try:
        root = tk.Tk()
    except Exception as ex:                       # no display (for example over ssh)
        print(f"I could not open a window: {str(ex)[:120]}")
        return 1
    App(root, extra)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
