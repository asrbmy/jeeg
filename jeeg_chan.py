"""Channels: named message boards that people and AIs on different computers share through JeeG link. No network code here
(jeeg_link carries the messages). Everything stays in your JeeG folder: <data>/channels/<name>.jsonl and meta.json.
A message from another computer or AI is DATA, never an instruction to JeeG."""
import json
import os
import re
import threading
import time
import uuid
from pathlib import Path

MAX_TEXT = 4000
MAX_KEEP = 1000
MAX_PULL = 200
NAME_RE = re.compile(r"[a-z0-9][a-z0-9_\-]{0,31}")
_lock = threading.RLock()


class ChanError(ValueError):
    pass


def clean(name: str) -> str:
    n = (name or "").strip().lower()
    if not NAME_RE.fullmatch(n):
        raise ChanError("Use a short channel name of letters, numbers, - or _ (for example: lab).")
    return n


def label(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.\-]", "", s or "")[:24]


def _dir(base) -> Path:
    d = Path(base) / "channels"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _meta(base) -> dict:
    try:
        d = json.loads((_dir(base) / "meta.json").read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_meta(base, m: dict) -> None:
    p = _dir(base) / "meta.json"
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(m, indent=1), encoding="utf-8")
    os.replace(tmp, p)


def _load(base, chan: str) -> list:
    out = []
    try:
        for line in (_dir(base) / f"{chan}.jsonl").read_text(encoding="utf-8").splitlines():
            try:
                m = json.loads(line)
                if isinstance(m, dict) and "id" in m:
                    out.append(m)
            except ValueError:
                pass
    except OSError:
        pass
    return out


def post(base, chan: str, text: str, sender: str, kind: str = "msg", ref: str = "", to: str = "", mid: str = "", t: float = 0) -> dict | None:
    """Add a message. Returns it, or None if that id is already there."""
    chan = clean(chan)
    text = (text or "").replace("\x00", "").strip()[:MAX_TEXT]
    if not text:
        raise ChanError("Nothing to post.")
    if kind not in {"msg", "job", "reply"}:
        kind = "msg"
    mid = mid if re.fullmatch(r"[0-9a-f]{16}", mid or "") else uuid.uuid4().hex[:16]
    with _lock:
        items = _load(base, chan)
        if any(m["id"] == mid for m in items):
            return None
        m = {"id": mid, "t": int(t) or int(time.time()), "from": (sender or "?")[:60], "text": text, "kind": kind}
        if ref:
            m["ref"] = ref[:16]
        if to:
            m["to"] = to[:40]
        items.append(m)
        items = items[-MAX_KEEP:]
        p = _dir(base) / f"{chan}.jsonl"
        tmp = p.with_suffix(".tmp")
        tmp.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in items) + "\n", encoding="utf-8")
        os.replace(tmp, p)
    return m


def read(base, chan: str, n: int = 20, after: str = "") -> list:
    items = _load(base, clean(chan))
    if after:
        ids = [m["id"] for m in items]
        if after in ids:
            items = items[ids.index(after) + 1:]
    return items[-max(1, min(n, MAX_PULL)):]


def channels(base) -> dict:
    out = {}
    for p in sorted(_dir(base).glob("*.jsonl")):
        items = _load(base, p.stem)
        out[p.stem] = (len(items), items[-1]["t"] if items else 0)
    for k in _meta(base):
        out.setdefault(k, (0, 0))
    return out


def shared_with(base, chan: str) -> list:
    return list(_meta(base).get(clean(chan), {}).get("share", []))


def share(base, chan: str, pid: str, on: bool = True) -> None:
    chan = clean(chan)
    with _lock:
        m = _meta(base)
        s = set(m.get(chan, {}).get("share", []))
        (s.add if on else s.discard)(pid)
        m[chan] = {"share": sorted(s)}
        _save_meta(base, m)


def remove(base, chan: str) -> bool:
    chan = clean(chan)
    with _lock:
        m = _meta(base)
        m.pop(chan, None)
        _save_meta(base, m)
        try:
            (_dir(base) / f"{chan}.jsonl").unlink()
            return True
        except OSError:
            return False


def wait_new(base, chan: str, after: str, seconds: int) -> list:
    end = time.time() + max(1, min(seconds, 300))
    while True:
        new = read(base, chan, MAX_PULL, after) if after else []
        if new or time.time() >= end:
            return new
        time.sleep(0.5)
