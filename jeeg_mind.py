"""JeeG's local memory, skills and run log. Plain files in your JeeG folder; nothing here touches the network.

* memory: short facts and preferences you told JeeG to remember (`remember ...`). Never secrets. At most 200 items.
* skills: named lists of plain-words requests (`skill add ...`) that can be run again, with a use count.
* runs: what the agent did for each goal (the last 30), so a good run can become a skill.
Only a person at the keyboard changes memory or skills; an AI or a chat connection cannot (see TERMINAL_ONLY)."""
import json
import os
import re
import time
from pathlib import Path

MAX_MEMORY, MAX_TEXT, MAX_SKILLS, MAX_STEPS, MAX_RUNS = 200, 300, 60, 12, 30
SECRET_LIKE = re.compile(r"(?i)\b(?:password|passwd|passcode|pin|api[_ -]?key|secret|token|private key|otp)\b\s*(?:is|=|:)|"
                         r"\bAKIA[0-9A-Z]{16}\b|\bgh[pousr]_[A-Za-z0-9]{20,}|\bpypi-[A-Za-z0-9_\-]{20,}|\bsk-[A-Za-z0-9_\-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY")
BAD_FIRST = {"agent", "skill", "skills", "remember", "memory", "goal"}       # a skill cannot start another agent, skill or memory change


class MindError(Exception):
    pass


def _read(p: Path, default):
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, type(default)) else default
    except (OSError, ValueError):
        return default


def _write(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, p)


def _stem(w: str) -> str:
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def words(s: str):
    return [_stem(w) for w in re.findall(r"[a-z0-9]+", str(s).lower()) if len(w) > 2]


class Mind:
    def __init__(self, state):
        self.dir = Path(str(state))

    # ---------------------------------------------------------------- memory
    def _mem(self):
        return _read(self.dir / "memory.json", [])

    def remember(self, text: str, kind: str = "fact", days: int = 0) -> int:
        text = re.sub(r"\s+", " ", str(text)).strip()
        if not text:
            raise MindError("Say what to remember, for example:  remember I prefer metric units")
        if len(text) > MAX_TEXT:
            raise MindError(f"Keep it under {MAX_TEXT} characters.")
        if SECRET_LIKE.search(text):
            raise MindError("That looks like a password or key. JeeG does not keep those in memory.")
        mem = self._mem()
        for m in mem:
            if m["text"].lower() == text.lower():
                raise MindError("Already remembered.")
        if len(mem) >= MAX_MEMORY:
            raise MindError(f"Memory is full ({MAX_MEMORY}). Forget something first:  remember forget <number>")
        nid = max([m["id"] for m in mem], default=0) + 1
        item = {"id": nid, "text": text, "kind": kind, "ts": int(time.time())}
        if days:
            item["expires"] = int(time.time()) + int(days) * 86400
        mem.append(item)
        _write(self.dir / "memory.json", mem)
        return nid

    def memories(self, include_expired: bool = True):
        mem = self._mem()
        if include_expired:
            return mem
        now = time.time()
        return [m for m in mem if not m.get("expires") or m["expires"] > now]

    def drop_expired(self) -> int:
        mem = self._mem()
        live = self.memories(include_expired=False)
        if len(live) != len(mem):
            _write(self.dir / "memory.json", live)
        return len(mem) - len(live)

    # facts a model, a chat or a scheduled run suggested: kept only after a person reviews them
    def suggest(self, text: str, source: str = "agent") -> bool:
        text = re.sub(r"\s+", " ", str(text)).strip()
        if not text or len(text) > MAX_TEXT or SECRET_LIKE.search(text):
            return False
        sug = _read(self.dir / "memory_suggestions.json", [])
        if any(x["text"].lower() == text.lower() for x in sug) or any(m["text"].lower() == text.lower() for m in self._mem()):
            return False
        sug.append({"text": text, "source": source, "ts": int(time.time())})
        _write(self.dir / "memory_suggestions.json", sug[-30:])
        return True

    def suggestions(self):
        return _read(self.dir / "memory_suggestions.json", [])

    def resolve_suggestion(self, index: int, keep: bool):
        sug = self.suggestions()
        item = sug.pop(index)
        _write(self.dir / "memory_suggestions.json", sug)
        if keep:
            self.remember(item["text"])
        return item

    def forget(self, which: str) -> int:
        mem = self._mem()
        if which.strip().lower() == "all":
            _write(self.dir / "memory.json", [])
            return len(mem)
        if not which.strip().isdigit():
            raise MindError("Say which one:  remember forget <number>   or   remember forget all")
        keep = [m for m in mem if m["id"] != int(which)]
        if len(keep) == len(mem):
            raise MindError("No memory with that number.")
        _write(self.dir / "memory.json", keep)
        return 1

    def relevant(self, query: str, n: int = 8):
        q = set(words(query))
        mem = self.memories(include_expired=False)
        scored = sorted(((len(q & set(words(m["text"]))), m["id"], m) for m in mem), key=lambda t: (-t[0], -t[1]))
        hits = [m for s, _, m in scored if s > 0][:n]
        if len(hits) < n:                                              # preferences are useful in every goal
            hits += [m for m in reversed(mem) if m.get("kind") == "preference" and m not in hits][: n - len(hits)]
        return hits[:n]

    # ---------------------------------------------------------------- skills
    def skills(self) -> dict:
        return _read(self.dir / "skills.json", {})

    @staticmethod
    def check_steps(steps):
        if not steps or len(steps) > MAX_STEPS:
            raise MindError(f"A skill needs 1 to {MAX_STEPS} steps.")
        out = []
        for s in steps:
            s = re.sub(r"\s+", " ", str(s)).strip()
            if not s or len(s) > 300:
                raise MindError("Each step must be 1 to 300 characters.")
            first = s.split()[0].lower()
            if first in BAD_FIRST:
                raise MindError(f"A step cannot start with '{first}'.")
            if SECRET_LIKE.search(s):
                raise MindError("A step looks like it contains a password or key. Keep those out of skills.")
            out.append(s)
        return out

    def save_skill(self, name: str, steps, desc: str = "", source: str = "you", replace: bool = False):
        name = str(name).strip().lower()
        if not re.fullmatch(r"[a-z0-9][a-z0-9_\-]{0,31}", name):
            raise MindError("Use a short name of letters, numbers, - or _ (for example: morning).")
        sk = self.skills()
        if name in sk and not replace:
            raise MindError(f"A skill called '{name}' already exists. Remove it first or pick another name.")
        if name not in sk and len(sk) >= MAX_SKILLS:
            raise MindError(f"You already have {MAX_SKILLS} skills.")
        steps = self.check_steps(steps)
        old = sk.get(name, {})
        sk[name] = {"desc": (desc or old.get("desc") or "")[:200], "steps": steps, "uses": old.get("uses", 0), "ok": old.get("ok", 0),
                    "failed": old.get("failed", 0), "created": old.get("created", int(time.time())), "source": source}
        if old and old.get("steps") != steps:
            sk[name]["prev"] = old["steps"]                              # one step back, for `skill undo`
        _write(self.dir / "skills.json", sk)

    def drop_skill(self, name: str):
        sk = self.skills()
        if sk.pop(name.strip().lower(), None) is None:
            raise MindError("No skill with that name.")
        _write(self.dir / "skills.json", sk)

    def note_skill_run(self, name: str, ok: bool, error: str = ""):
        sk = self.skills()
        if name in sk:
            sk[name]["uses"] = sk[name].get("uses", 0) + 1
            sk[name]["ok" if ok else "failed"] = sk[name].get("ok" if ok else "failed", 0) + 1
            if ok:
                sk[name].pop("last_error", None)
            else:
                sk[name]["last_error"] = str(error)[:400]
            _write(self.dir / "skills.json", sk)

    def undo_skill(self, name: str):
        sk = self.skills()
        s = sk.get(name.strip().lower())
        if not s or not s.get("prev"):
            raise MindError("There is no earlier version of that skill.")
        s["steps"], s["prev"] = s["prev"], s["steps"]
        _write(self.dir / "skills.json", sk)

    # ---------------------------------------------------------------- runs
    def save_run(self, run: dict) -> str:
        d = self.dir / "agent_runs"
        d.mkdir(parents=True, exist_ok=True)
        name = f"{time.time_ns():020d}.json"
        _write(d / name, run)
        for old in sorted(d.glob("*.json"))[:-MAX_RUNS]:
            old.unlink(missing_ok=True)
        return name

    def last_run(self):
        d = self.dir / "agent_runs"
        files = sorted(d.glob("*.json")) if d.is_dir() else []
        return _read(files[-1], {}) if files else {}


# ---------------------------------------------------------------- skill packs (bundled; read every step before installing)
PACKS = {
    "developer": {"desc": "Quick health checks for a code project (run in the project folder)", "skills": {
        "dev-status": {"desc": "Git status and disk space", "steps": ["git status", "disk space"]},
        "dev-todos": {"desc": "List TODO and FIXME comments here", "steps": ["find todo"]},
        "dev-secrets": {"desc": "Look for leaked keys before you share", "steps": ["find secrets"]}}},
    "student": {"desc": "Study-day helpers", "skills": {
        "study-start": {"desc": "What is due, then a 25-minute timer", "steps": ["what is due", "timer 25 minutes"]},
        "study-day": {"desc": "Reminders and what is due", "steps": ["show reminders", "what is due"]}}},
    "home": {"desc": "Check on the house and the computer", "skills": {
        "home-check": {"desc": "Devices and disk space", "steps": ["iot list", "disk space"]},
        "home-weather": {"desc": "Weather and what is due", "steps": ["weather", "what is due"]}}},
}
