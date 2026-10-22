"""Undo log for file moves and renames. Not a task."""
import os
from pathlib import Path
from _store import load, save

KEEP = 20


def record(label, pairs):
    """pairs: [(old_path, new_path)] describing what was done. Best effort: never breaks the task."""
    try:
        ops = [[str(a), str(b)] for a, b in pairs]
        if not ops:
            return
        log = load("undo.json", [])
        log.append({"label": label, "ops": ops})
        save("undo.json", log[-KEEP:])
    except Exception:
        pass


def pending():
    log = load("undo.json", [])
    return log[-1] if log else None


def undo_last():
    """Reverse the newest entry. Returns (done, skipped, label). Never overwrites anything."""
    log = load("undo.json", [])
    if not log:
        return None
    entry = log.pop()
    done, skipped = 0, []
    for old, new in reversed(entry["ops"]):
        o, n = Path(old), Path(new)
        if not os.path.lexists(n):
            skipped.append(f"{n.name} is no longer there"); continue
        if os.path.lexists(o):
            skipped.append(f"{o.name} already exists at the old place"); continue
        try:
            o.parent.mkdir(parents=True, exist_ok=True)
            os.rename(n, o)
            done += 1
        except OSError:
            import shutil
            try:
                shutil.move(str(n), str(o)); done += 1
            except OSError as e:
                skipped.append(f"{n.name}: {e.strerror or e}")
    save("undo.json", log)
    return done, skipped, entry["label"]
