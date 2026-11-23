"""Shared folder walking for the developer and security tasks (reads only; never changes anything)."""
import os
from pathlib import Path
from _files import path_arg
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".tox", ".mypy_cache", ".idea", ".vs", "target", ".next"}
MAX_FILES, MAX_SIZE = 20000, 1_000_000


def root_from(text):
    """A folder from the words typed, or the current folder."""
    t = (text or "").strip()
    return path_arg(t) if t else Path.cwd()


def walk(root, limit=MAX_FILES):
    """Yield (path, truncated_flag) for files under root, skipping vendor and build folders."""
    n = 0
    root = Path(root)
    if root.is_file():
        yield root
        return
    for d, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(x for x in dirs if x not in SKIP and not x.startswith(".git"))
        for f in sorted(files):
            n += 1
            if n > limit:
                return
            yield Path(d) / f


def read_text(p, limit=MAX_SIZE):
    """Text of a file, or None if it is big or looks binary."""
    try:
        if p.stat().st_size > limit:
            return None
        b = p.read_bytes()
    except OSError:
        return None
    if b"\0" in b[:4096]:
        return None
    return b.decode("utf-8", "replace")
