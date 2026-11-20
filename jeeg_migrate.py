"""Saved-data versions. When a new JeeG needs your records in a different shape, a migration upgrades them once,
after saving a zip copy of everything. A failed migration is rolled back. Records from a NEWER JeeG are never touched.
"""
from __future__ import annotations

import json
import os
import time
import zipfile
from pathlib import Path

DATA_VERSION = 1
# MIGRATIONS[n] upgrades records from version n-1 to n. Each takes the state folder. (Version 1 is the first stamped version: no change.)
MIGRATIONS: dict = {}
SKIP = {"index.json", "log.jsonl", "history.jsonl", "misses.log", "misses.jsonl"}


def _read(state: Path):
    try:
        v = json.loads((state / "data_version.json").read_text(encoding="utf-8")).get("v")
        return v if isinstance(v, int) and v >= 0 else 0
    except (OSError, ValueError, AttributeError):
        return None


def _stamp(state: Path, v: int) -> None:
    tmp = state / "data_version.json.tmp"
    tmp.write_text(json.dumps({"v": v, "when": int(time.time())}), encoding="utf-8")
    os.replace(tmp, state / "data_version.json")


def _backup(state: Path, tag: str) -> Path:
    d = state / "backups"
    d.mkdir(exist_ok=True)
    z = d / f"before-{tag}-{time.strftime('%Y%m%d-%H%M%S')}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(state.iterdir()):
            if p.is_file() and p.name not in SKIP and not p.name.endswith(".tmp"):
                zf.write(p, p.name)
    for old in sorted(d.glob("before-*.zip"))[:-5]:          # keep the five newest
        try:
            old.unlink()
        except OSError:
            pass
    return z


def _restore(state: Path, z: Path) -> None:
    with zipfile.ZipFile(z) as zf:
        for n in zf.namelist():
            if "/" not in n and "\\" not in n:
                (state / n).write_bytes(zf.read(n))


def run(state: Path, current: int | None = None, migrations: dict | None = None) -> str:
    """Bring saved data up to date. Returns '' normally, or one plain sentence to show the person."""
    cur = DATA_VERSION if current is None else current
    mig = MIGRATIONS if migrations is None else migrations
    try:
        if not state.is_dir():
            return ""
        have = _read(state)
        if have is None:                                    # no stamp yet: new folder, or records from before stamping
            has_data = any(p.is_file() and p.name not in SKIP and p.suffix in {".json", ".csv"} and p.name != "data_version.json" for p in state.iterdir())
            have = 0 if has_data else cur
            if not has_data:
                _stamp(state, cur)
                return ""
        if have > cur:
            return (f"Your records were saved by a newer JeeG (data version {have}; this one understands {cur}). "
                    "I did not change them. Update JeeG to be safe.")
        if have == cur:
            return ""
        todo = [n for n in range(have + 1, cur + 1) if n in mig]
        if not todo:
            _stamp(state, cur)
            return ""
        z = _backup(state, f"v{cur}")
        try:
            for n in todo:
                mig[n](state)
        except Exception as ex:                             # roll back to the copy; never leave records half-converted
            _restore(state, z)
            return f"Upgrading your records failed ({type(ex).__name__}); I put everything back. A copy is in {z}."
        _stamp(state, cur)
        return f"Your records were upgraded to data version {cur}. A copy of the old ones is in {z}."
    except OSError:
        return ""
