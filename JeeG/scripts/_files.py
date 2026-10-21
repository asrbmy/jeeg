"""File-system helpers shared by file tasks. Not a task itself."""
import os
import re
import time
import zipfile
from pathlib import Path

from _lib import fail

KNOWN = {"downloads": ("Downloads",), "documents": ("Documents",), "docs": ("Documents",),
         "desktop": ("Desktop", "OneDrive/Desktop"), "pictures": ("Pictures", "OneDrive/Pictures"),
         "photos": ("Pictures",), "music": ("Music",), "videos": ("Videos", "Movies"), "home": ("",)}
SKIP_DIRS = {"node_modules", "__pycache__", ".git", ".venv", "venv", ".cache", "$RECYCLE.BIN",
             "System Volume Information", "AppData", "Library", ".npm", ".cargo", ".gradle", "proc", "sys"}


def resolve_folder(text, default=None):
    """'downloads' / '~/Projects' / 'C:\\data' -> Path. Empty text -> default or cwd."""
    t = text.strip().strip("\"'")
    if not t:
        return Path(default) if default else Path.cwd()
    p = Path(t).expanduser()
    if p.exists():
        return p.resolve()
    for w in re.findall(r"[a-z]+", t.lower()):
        for n in KNOWN.get(w, ()):
            q = Path.home() / n
            if q.is_dir():
                return q
    fail(f"Folder not found: {t}")


def walk_files(root, seconds=15, skip=SKIP_DIRS, hidden=False):
    """Yield (path, DirEntry-stat) for files under root, never following links, stopping after `seconds`."""
    deadline = time.time() + seconds
    stack = [str(root)]
    while stack:
        if time.time() > deadline:
            print(f"(stopped after {seconds}s - results may be incomplete)")
            return
        d = stack.pop()
        try:
            it = os.scandir(d)
        except OSError:
            continue
        with it:
            for e in it:
                try:
                    if e.is_symlink():
                        continue
                    if e.is_dir(follow_symlinks=False):
                        if e.name in skip or (not hidden and e.name.startswith(".")):
                            continue
                        stack.append(e.path)
                    elif e.is_file(follow_symlinks=False):
                        yield e.path, e.stat(follow_symlinks=False)
                except OSError:
                    continue


def make_zip(src, dest, exclude=("node_modules", "__pycache__", ".venv", ".git"), limit=2 * 1024 ** 3):
    src = Path(src).resolve()
    if src == Path.home().resolve() or src == Path(src.anchor):
        fail("Refusing to zip your whole home folder or drive; choose a specific folder.")
    files, total = [], 0
    for path, st in walk_files(src, seconds=60, skip=set(exclude), hidden=True):
        files.append(path)
        total += st.st_size
        if total > limit:
            fail("That folder is larger than 2 GB; refusing to zip it.")
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in files:
            z.write(f, os.path.relpath(f, src.parent))
    return len(files), total


def unique_path(p):
    p = Path(p)
    if not p.exists():
        return p
    for i in range(1, 10000):
        q = p.with_name(f"{p.stem} ({i}){p.suffix}")
        if not q.exists():
            return q
    fail("Too many files with the same name.")


# ---------------------------------------------------------------- argument parsing
def clean_arg(t):
    return t.strip().strip("\"'").strip()


def split_on(text, word):
    """Split on the LAST whole word `word` ('a to b' -> ('a', 'b')); (text, '') when absent."""
    found = list(re.finditer(rf"\s+{word}\s+", text, re.I))
    if not found:
        return text.strip(), ""
    m = found[-1]
    return text[:m.start()].strip(), text[m.end():].strip()


def tokens(text):
    """Split on spaces but keep "quoted names" together; drop 'and' and commas."""
    out = []
    for q1, q2, bare in re.findall(r'"([^"]+)"|\'([^\']+)\'|(\S+)', text):
        t = (q1 or q2 or bare).strip(",")
        if t and t.lower() != "and":
            out.append(t)
    return out


def path_arg(text, must_exist=True):
    """'report.pdf' / '~/x' / 'downloads/x.zip' -> Path. Bare names are looked for in the
    current folder, then Downloads, Desktop and Documents."""
    t = clean_arg(text)
    if not t:
        fail("Tell me which file or folder.")
    p = Path(t).expanduser()
    if p.exists():
        return p.resolve()
    head, _, rest = t.replace("\\", "/").partition("/")
    for n in KNOWN.get(head.lower(), ()):
        q = Path.home() / n / rest
        if q.exists():
            return q.resolve()
    if "/" not in t.replace("\\", "/"):
        for n in ("Downloads", "Desktop", "Documents"):
            q = Path.home() / n / t
            if q.exists():
                return q.resolve()
    if must_exist:
        fail(f"Not found: {t}")
    return p


def is_text_file(path, size_limit=5 * 1024 * 1024):
    try:
        if os.path.getsize(path) > size_limit:
            return False
        with open(path, "rb") as f:
            return b"\0" not in f.read(2048)
    except OSError:
        return False
