"""Shared helpers for task scripts (not itself a task: names starting with _ are skipped)."""
import json
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
    if issubclass(kind, BrokenPipeError):            # the reader (for example "| head") closed the pipe: not an error
        try:
            sys.stdout = open(os.devnull, "w")
        except OSError:
            pass
        os._exit(0)
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


def safe_is_file(p):
    """Path.is_file() that never raises, even when 'p' is really a long piece of text."""
    try:
        return len(str(p)) < 1000 and p.is_file()
    except (OSError, ValueError):
        return False


def stdin_text(limit=1_000_000, wait=0.5):
    """Text piped into JeeG (type notes.txt | jeeg word count), or "". Never blocks for long when nothing is piped."""
    import threading
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return ""
    except (AttributeError, ValueError, OSError):
        return ""
    box = []

    def read():
        try:
            box.append(sys.stdin.read(limit + 1))
        except (OSError, ValueError, UnicodeDecodeError):
            box.append("")
    th = threading.Thread(target=read, daemon=True)
    th.start()
    th.join(wait)
    if th.is_alive() or not box:
        return ""
    return box[0][:limit].replace("\x00", "")


def args_or_stdin(default=""):
    """The words after the task name; when there are none, the piped-in text."""
    return args_text() or stdin_text() or default


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


# ---------------------------------------------------------------- number words ("five lakh" -> 500000)
_UNITS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
          "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
          "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
_MAGS = {"thousand": 1e3, "lakh": 1e5, "lakhs": 1e5, "lac": 1e5, "lacs": 1e5, "million": 1e6, "crore": 1e7, "crores": 1e7, "billion": 1e9}
_NUMW = set(_UNITS) | set(_MAGS) | {"hundred"}


def words_to_digits(text: str) -> str:
    """Turn spelled-out numbers of 10 or more into digits: 'five lakh' -> '500000', 'twenty five percent' -> '25 percent',
    'two thousand twenty six' -> '2026'. A lone 'one' .. 'nine' is left alone (it is usually just a word)."""
    import re as _re
    toks = _re.findall(r"[A-Za-z]+|[^A-Za-z]+", text)
    out, i = [], 0
    while i < len(toks):
        if toks[i].lower() not in _NUMW:
            out.append(toks[i]); i += 1
            continue
        words, j, end = [], i, i
        while j < len(toks):
            low = toks[j].lower()
            if low in _NUMW:
                words.append(low); end = j; j += 1
            elif _re.fullmatch(r"[\s\-]+", toks[j]) and j + 1 < len(toks) and (
                    toks[j + 1].lower() in _NUMW or (toks[j + 1].lower() == "and" and j + 3 < len(toks) and toks[j + 3].lower() in _NUMW)):
                j += 1 if toks[j + 1].lower() in _NUMW else 3
            else:
                break
        total, cur = 0.0, 0.0
        for w in words:
            if w in _UNITS: cur += _UNITS[w]
            elif w == "hundred": cur = (cur or 1) * 100
            else: total += (cur or 1) * _MAGS[w]; cur = 0.0
        val = total + cur
        if val >= 10 and val < 1e13 and any(w in _UNITS or w == "hundred" for w in words):   # '5 lakh' (digits + a magnitude word) is left for the number reader
            out.append(str(int(val))); i = end + 1
        else:
            out.append("".join(toks[i:end + 1])); i = end + 1
    return "".join(out)


# ---------------------------------------------------------------- your variables (set var rate = 18, then use $rate)
def _vars_file():
    return data_dir() / "vars.json"


def var_all() -> dict:
    try:
        v = json.loads(_vars_file().read_text(encoding="utf-8"))
        return v if isinstance(v, dict) else {}
    except (OSError, ValueError):
        return {}


def var_save(vs: dict) -> None:
    f = _vars_file()
    tmp = f.with_name(f.name + ".tmp")
    tmp.write_text(json.dumps(vs, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, f)
