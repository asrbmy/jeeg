"""Shared helpers for task scripts (not itself a task: names starting with _ are skipped)."""
import os
import shutil
import subprocess
import sys
import urllib.parse
import webbrowser
from pathlib import Path

for _s in (sys.stdout, sys.stderr):      # never crash on emoji / accents in a legacy console
    try:
        _s.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

def _friendly_crash(kind, value, tb):
    """One plain line instead of a Python traceback. Set JEEG_DEBUG=1 to see the full details."""
    if os.environ.get("JEEG_DEBUG") or issubclass(kind, (SystemExit, KeyboardInterrupt)):
        sys.__excepthook__(kind, value, tb)
        return
    if issubclass(kind, OSError) and getattr(value, "errno", None) == 36:
        msg = "that name is too long"
    elif issubclass(kind, OSError):
        msg = value.strerror or str(value)
    else:
        msg = f"{kind.__name__}: {value}"
    print(f"Could not finish: {msg}. (Set JEEG_DEBUG=1 for details.)")
    sys.stdout.flush()
    os._exit(1)


sys.excepthook = _friendly_crash

WIN = sys.platform.startswith("win")
MAC = sys.platform == "darwin"
LINUX = not (WIN or MAC)


def args_text(default=""):
    """Words the user said beyond the task name, e.g. 'search cats' -> 'cats'."""
    return " ".join(sys.argv[1:]).strip() or default


def fail(msg, code=1):
    print(msg)
    sys.exit(code)


SAFE_SCHEMES = ("http", "https", "mailto", "tel", "sms", "whatsapp")


def open_url(url):
    """Open a web address in the default browser. Only safe link types are allowed, so a bad saved
    link (file:, javascript:, a program path) can never launch anything else."""
    url = str(url).strip()
    scheme = urllib.parse.urlsplit(url).scheme.lower()
    if scheme not in SAFE_SCHEMES or any(c in url for c in "\r\n\0"):
        fail("Refusing to open that link: only http, https, mailto, tel, sms and whatsapp links are allowed.")
    if not webbrowser.open(url):
        fail(f"Could not open a browser for {url}")


def search_url(base, text):
    """base contains '{q}' where the encoded search text goes."""
    return base.replace("{q}", urllib.parse.quote_plus(text))


def web_task(home, search=None):
    """Open `home`, or a search on the site when extra words were given and `search` is set."""
    text = args_text()
    open_url(search_url(search, text) if (search and text) else home)


def open_path(path):
    p = str(Path(path).expanduser())
    if not os.path.exists(p):
        fail(f"Not found: {p}")
    if WIN:
        os.startfile(p)  # noqa: S606
    elif MAC:
        subprocess.Popen(["open", p])
    else:
        subprocess.Popen(["xdg-open", p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def user_dir(*names):
    """First existing folder in the home directory out of `names` (e.g. 'Downloads')."""
    for n in names:
        p = Path.home() / n
        if p.is_dir():
            return p
    fail(f"Folder not found in your home directory: {names[0]}")


def output_dir(name):
    """A folder for files JeeG makes for you: <Documents or Desktop or home>/<name>. Created if needed."""
    base = next((Path.home() / n for n in ("Documents", "Desktop") if (Path.home() / n).is_dir()), Path.home())
    out = base / name
    out.mkdir(exist_ok=True)
    return out


def spawn(cmd, **kw):
    """Start a program without waiting for it."""
    if WIN:
        kw["creationflags"] = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        kw["start_new_session"] = True                    # survives the terminal being closed
    return subprocess.Popen(
        cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, **kw)


def launch(win=(), mac=(), linux=(), name="application"):
    """Open an app. Each argument is a list of candidate commands (lists of strings);
    the first one that works is used. ("start", X) means Windows `start X`;
    ("open", ...) on macOS is checked for success."""
    options = win if WIN else mac if MAC else linux
    for cmd in options:
        cmd = [cmd] if isinstance(cmd, str) else list(cmd)
        if WIN and cmd[0].lower() == "start":
            if subprocess.run(["cmd", "/c", "start", ""] + cmd[1:], capture_output=True).returncode == 0:
                return
            continue
        if MAC and cmd[0] == "open":
            if subprocess.run(cmd, capture_output=True).returncode == 0:
                return
            continue
        exe = shutil.which(cmd[0])
        if exe:
            spawn([exe] + cmd[1:])
            return
    fail(f"Could not find {name} on this computer.")


def call(cmd):
    """Run a command attached to the terminal; return its exit code (clear message if the tool is missing)."""
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        fail(f"'{cmd[0]}' is not installed on this computer.")
    except KeyboardInterrupt:
        return 130


def run(cmd, show=True, check=False, **kw):
    """Run a command and return (returncode, output)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", **kw)
    except (OSError, subprocess.SubprocessError) as ex:
        fail(f"Could not run {cmd[0]}: {ex}")
    out = (r.stdout or "") + (r.stderr or "")
    if show and out.strip():
        print(out.rstrip())
    if check and r.returncode:
        sys.exit(r.returncode)
    return r.returncode, out


def need(module, pip_name=None):
    """Import an optional module or exit with an install hint."""
    try:
        return __import__(module)
    except ImportError:
        fail(f"Missing '{module}'. Install it with:  pip install {pip_name or module}")


def human(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def notify(title, text=""):
    """Desktop notification where one is available. Returns True if shown."""
    try:
        if MAC:
            subprocess.run(["osascript", "-e", "on run argv", "-e",
                            "display notification (item 2 of argv) with title (item 1 of argv)",
                            "-e", "end run", title, text])
            return True
        if LINUX and shutil.which("notify-send"):
            subprocess.run(["notify-send", title, text])
            return True
    except OSError:
        pass
    return False


def data_dir():
    """Folder where tasks keep their data (to-dos, notes). Shared with the runner."""
    env = os.environ.get("JEEG_HOME") or os.environ.get("TASKRUNNER_HOME")
    if env:
        p = Path(env)
    else:
        new, old = Path.home() / ".jeeg", Path.home() / ".taskrunner"
        p = old if (old.exists() and not new.exists()) else new
    p.mkdir(parents=True, exist_ok=True)
    if os.name == "posix":                      # your notes, journal and expenses are private to you
        try:
            if (p.stat().st_mode & 0o077) and p.stat().st_uid == os.getuid():
                p.chmod(0o700)
        except OSError:
            pass
    return p
