"""Which linked apps an AI may use, and whether an AI only gets previews. Not a task itself.
The file  app_policy.json  can only be changed by you in a terminal (app ai ...). AI mode sets JEEG_VIA_AI=1 for the tasks it starts.
"""
import os
import re

from _store import load, save

KEYS = ("ai_allow", "ai_deny", "dry")


def get():
    d = load("app_policy.json", {})
    d = d if isinstance(d, dict) else {}
    return {"ai_allow": [x for x in d.get("ai_allow", []) if isinstance(x, str)], "ai_deny": [x for x in d.get("ai_deny", []) if isinstance(x, str)], "dry": d.get("dry") is True}


def put(d):
    save("app_policy.json", {k: d[k] for k in KEYS})


def via_ai():
    return os.environ.get("JEEG_VIA_AI") == "1"


def refuse(app):
    """Plain-words reason when an AI may not use this app, else None. Always None for the person in a terminal."""
    if not via_ai():
        return None
    p = get()
    if app in p["ai_deny"]:
        return f"You turned {app} off for AI. (In a terminal:  app ai allow {app})"
    if p["ai_allow"] and app not in p["ai_allow"]:
        return f"{app} is not on the list of apps an AI may use. (In a terminal:  app ai allow {app})"
    return None


def visible(names):
    if not via_ai():
        return list(names)
    return [n for n in names if refuse(n) is None]


def action_key(query):
    """'app do github comment repo=a/b ...' -> 'linked_do:github:comment', else ''."""
    m = re.match(r"^\s*(?:app|linked)\s+do\s+([a-z][a-z0-9_\-]*)\s+([a-z][a-z0-9_\-]*)\b", query or "", re.I)
    return f"linked_do:{m.group(1).lower()}:{m.group(2).lower()}" if m else ""
