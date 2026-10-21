"""Run an editable routine (a list of task phrases). Not a task."""
import json
import os
import re
import sys
import time

from _lib import data_dir, fail

DEFAULTS = {
    "start_work_day": ["say:Starting your work day...", "open gmail", "open calendar", "todo list"],
    "end_work_day": ["todo list", "say:Locking the screen in 5 seconds - press Ctrl+C to cancel", "wait:5", "lock screen"],
    "study_mode": ["say:Study mode: 25 minutes, volume low", "open notepad", "set volume 20", "set timer 25 minutes study session"],
    "meeting_mode": ["say:Meeting mode", "open meet", "open calendar"],
    "night_mode": ["dark mode on", "set brightness 30", "set volume 20"],
}


def config_path():
    return data_dir() / "routines.json"


def load():
    p = config_path()
    cfg = {}
    if p.exists():
        try:
            cfg = json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            fail(f"{p} is not valid JSON. Fix it or delete it to restore the defaults.")
    return {**DEFAULTS, **{k: v for k, v in cfg.items() if isinstance(v, list)}}


def ensure_file():
    p = config_path()
    if not p.exists():
        p.write_text(json.dumps(DEFAULTS, indent=2), encoding="utf-8")
    return p


def fill(step, words):
    """Replace {args} and {1} {2} ... in one step with the words typed after the routine name."""
    step = step.replace("{args}", " ".join(words))
    return re.sub(r"\{(\d+)\}", lambda m: words[int(m.group(1)) - 1] if int(m.group(1)) <= len(words) else m.group(0), step)


def needs(steps):
    """Highest placeholder number used, and whether {args} is used."""
    top, anyargs = 0, False
    for s in steps:
        s = str(s)
        anyargs = anyargs or "{args}" in s
        for m in re.finditer(r"\{(\d+)\}", s):
            top = max(top, int(m.group(1)))
    return top, anyargs


def run(key, words=()):
    routines = load()
    steps = routines.get(key)
    if steps is None:
        fail(f"No routine called '{key}'. Known: {', '.join(sorted(routines))}")
    top, anyargs = needs(steps)
    words = list(words)
    if len(words) < top or (anyargs and not words):
        fail(f"'{key.replace('_', ' ')}' needs {max(top, 1)} extra word(s):  run routine {key.replace('_', ' ')} <word>" + (" <word>" * (top - 1) if top > 1 else ""))
    steps = [fill(str(s), words) for s in steps]
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(here))
    import jeeg as tr
    entries = tr.load_index(tr.script_dirs([]))
    opt = {"yes": False, "dry": False, "timeout": None}
    print(f"== {key.replace('_', ' ')} ({len(steps)} steps) ==")
    try:
        for s in steps:
            s = str(s)
            if s.startswith("say:"):
                print(s[4:].strip())
            elif s.startswith("wait:"):
                time.sleep(float(s[5:] or 1))
            else:
                tr.run_query(s, entries, opt)
    except KeyboardInterrupt:
        print("\nRoutine stopped.")
    ensure_file()
