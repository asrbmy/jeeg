"""Administrator policy: a file that only an administrator can write, that limits what JeeG will do on this computer.

Where it is looked for (first found wins):
    environment variable JEEG_POLICY  (a path; useful for testing)
    Windows  %ProgramData%\\JeeG\\policy.json
    macOS    /Library/Application Support/JeeG/policy.json
    Linux    /etc/jeeg/policy.json

Example:
    {"disable_categories": ["system", "files"], "disable_tasks": ["shred file"],
     "block_online": true, "block_plugins": true, "block_link": true, "ai_max": "read", "ai_browser": false, "note": "Set by IT"}

On macOS and Linux a policy file that other users can write is ignored (and reported), because it would not be a policy.
A person using JeeG cannot change it from JeeG. It limits; it never adds anything.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

AI_ORDER = ["off", "safe", "read", "ask", "god"]


def path() -> Path:
    env = os.environ.get("JEEG_POLICY", "").strip()
    if env:
        return Path(env)
    if os.name == "nt":
        return Path(os.environ.get("ProgramData", r"C:\ProgramData")) / "JeeG" / "policy.json"
    if sys.platform == "darwin":
        return Path("/Library/Application Support/JeeG/policy.json")
    return Path("/etc/jeeg/policy.json")


def load() -> dict:
    """The validated policy, or {} when there is none. Problems are returned under '_problems', never raised."""
    p = path()
    try:
        if not p.is_file():
            return {}
        if os.name != "nt":
            st = p.stat()
            if st.st_mode & 0o002 or (hasattr(os, "getuid") and st.st_uid not in (0, os.getuid())):
                return {"_problems": [f"{p} can be changed by other users, so it was ignored."]}
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as ex:
        return {"_problems": [f"{p} could not be read ({str(ex)[:60]}); no policy applied."]}
    if not isinstance(raw, dict):
        return {"_problems": [f"{p} must hold one JSON object."]}
    out, bad = {}, []
    lst = lambda v: [str(x).lower().replace("_", " ").strip() for x in v[:200]] if isinstance(v, list) else None
    for k in ("disable_categories", "disable_tasks"):
        if k in raw:
            v = lst(raw[k])
            if v is None: bad.append(f"{k} must be a list")
            else: out[k] = v
    for k in ("block_online", "block_plugins", "ai_browser", "block_link"):
        if k in raw:
            if isinstance(raw[k], bool): out[k] = raw[k]
            else: bad.append(f"{k} must be true or false")
    if "ai_max" in raw:
        if raw["ai_max"] in AI_ORDER: out["ai_max"] = raw["ai_max"]
        else: bad.append("ai_max must be one of " + ", ".join(AI_ORDER))
    if isinstance(raw.get("note"), str): out["note"] = raw["note"][:200]
    if bad: out["_problems"] = bad
    out["_path"] = str(p)
    return out


def apply(entries: list, plugin_dir: Path | None = None) -> list:
    """Entries without what the policy forbids."""
    pol = load()
    if not pol or not any(k in pol for k in ("disable_categories", "disable_tasks", "block_online", "block_plugins")):
        return entries
    cats, tasks = set(pol.get("disable_categories", [])), set(pol.get("disable_tasks", []))
    pdir = None
    try:
        pdir = plugin_dir.resolve() if plugin_dir else None
    except OSError:
        pass
    keep = []
    for e in entries:
        if e["cat"].lower() in cats or e["name"].replace("_", " ").lower() in tasks:
            continue
        if pol.get("block_online") and e.get("net"):
            continue
        if pol.get("block_plugins") and pdir is not None:
            try:
                if Path(e["path"]).resolve().parent == pdir:
                    continue
            except OSError:
                pass
        keep.append(e)
    return keep


def clamp_ai(mode: str) -> str:
    """The AI mode actually allowed: never more than ai_max."""
    mx = load().get("ai_max")
    if mx and mode in AI_ORDER and AI_ORDER.index(mode) > AI_ORDER.index(mx):
        return mx
    return mode


def ai_browser_allowed() -> bool:
    return load().get("ai_browser", True) is not False


def describe() -> str:
    pol = load()
    if not pol:
        return f"No administrator policy is set (it would be read from {path()})."
    lines = [f"Administrator policy from {pol.get('_path', path())}:"]
    if pol.get("note"): lines.append(f"  Note: {pol['note']}")
    if pol.get("disable_categories"): lines.append("  Switched off categories: " + ", ".join(pol["disable_categories"]))
    if pol.get("disable_tasks"): lines.append("  Switched off tasks: " + ", ".join(pol["disable_tasks"]))
    if pol.get("block_online"): lines.append("  Tasks that use the internet: off")
    if pol.get("block_plugins"): lines.append("  Plugins: off")
    if pol.get("block_link"): lines.append("  JeeG link (talking to other JeeG computers): off")
    if "ai_max" in pol: lines.append(f"  AI mode at most: {pol['ai_max']}")
    if pol.get("ai_browser") is False: lines.append("  AI browser control: off")
    for b in pol.get("_problems", []): lines.append(f"  Problem: {b}")
    if len(lines) == 1: lines.append("  (nothing restricted)")
    return "\n".join(lines)
