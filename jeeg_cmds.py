"""Extra JeeG commands: update, plugin tools, setup wizard, tab completion, local web page.

Kept apart from jeeg.py so the engine stays small. Standard library only.
"""
from __future__ import annotations

import http.server
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

REPO = "asrbmy/jeeg"
RELEASE_API = f"https://api.github.com/repos/{REPO}/releases/latest"
RELEASE_PAGE = f"https://github.com/{REPO}/releases"
NAME_RE = re.compile(r"[a-z][a-z0-9_]{1,40}")
MAX_PLUGIN_BYTES = 200_000
RISKY = ("subprocess", "os.system", "os.popen", "socket", "urllib", "requests", "http.client", "shutil.rmtree",
         "os.remove", "os.unlink", "eval(", "exec(", "ctypes", "__import__", "pickle", "base64.b64decode")


def _ask(prompt: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        print("This needs your confirmation. Run it in a terminal, or add -y.")
        return False
    return input(prompt + " [y/N] ").strip().lower() in {"y", "yes"}


# ------------------------------------------------------------------ update
def _vtuple(v: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3]) or (0,)


def latest_version(timeout: float = 8.0):
    """(version, url) of the newest GitHub release, or raises OSError with a plain message."""
    req = urllib.request.Request(RELEASE_API, headers={"User-Agent": "JeeG-update-check", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read(200_000).decode("utf-8", "replace"))
    except urllib.error.HTTPError as ex:
        if ex.code == 404:
            raise OSError("no release has been published on GitHub yet")
        raise OSError(f"GitHub answered {ex.code}")
    except (urllib.error.URLError, TimeoutError, ValueError) as ex:
        raise OSError("could not reach GitHub (are you online?)") from ex
    tag = str(data.get("tag_name", "")).lstrip("vV")
    if not tag:
        raise OSError("GitHub did not report a version")
    return tag, str(data.get("html_url") or RELEASE_PAGE)


def install_kind(here: Path) -> str:
    if (here / ".git").exists():
        return "git"
    if "site-packages" in here.parts or "dist-packages" in here.parts:
        return "pip"
    return "zip"


def cmd_update(q: str, here: Path, version: str, assume_yes: bool = False) -> int:
    now = "now" in q.lower().split()
    try:
        tag, url = latest_version()
    except OSError as ex:
        print(f"JeeG {version}. Could not check for a newer version: {ex}.")
        return 1
    if _vtuple(tag) <= _vtuple(version):
        print(f"JeeG {version} is up to date.")
        return 0
    kind = install_kind(here)
    cmd = {"git": ["git", "-C", str(here), "pull", "--ff-only"],
           "pip": [sys.executable, "-m", "pip", "install", "--upgrade", "jeeg"]}.get(kind)
    print(f"A newer version is available: {tag} (you have {version}).")
    if not cmd:
        print(f"Download it from {url}, unzip over your JeeG folder (your data in ~/.jeeg is kept).")
        return 0
    shown = " ".join(cmd)
    if not now:
        print(f"Update with:  {shown}\nor say:  update now")
        return 0
    if not _ask(f"Run: {shown}?", assume_yes):
        return 3
    if not shutil.which(cmd[0]) and cmd[0] != sys.executable:
        print(f"{cmd[0]} was not found on this computer.")
        return 1
    return subprocess.run(cmd).returncode


# ----------------------------------------------------------------- plugins
def _plugin_name(raw: str) -> str | None:
    n = re.sub(r"\.py$", "", raw.strip().lower().replace("-", "_").replace(" ", "_"))
    return n if NAME_RE.fullmatch(n) else None


TEMPLATE = '''# keywords: {words}
# desc: {desc}
# category: custom
# usage: {words} <text>
# JeeG task. Say any of the keywords and this script runs; extra words arrive in sys.argv[1:].
import sys

text = " ".join(sys.argv[1:]).strip()
print("Hello from {name}!", text)
'''


def cmd_plugin(args: str, plugin_dir: Path, entries: list[dict], parse_header, assume_yes: bool = False) -> int:
    words = args.split()
    sub = words[0].lower() if words else "list"
    rest = words[1:]
    builtin = {e["name"] for e in entries if Path(e["path"]).resolve().parent != plugin_dir.resolve()}
    mine = sorted(p for p in plugin_dir.glob("*.py")) if plugin_dir.is_dir() else []

    if sub in {"search", "library", "browse", "get"}:
        return cmd_library("get" if sub == "get" else "search", rest, plugin_dir, entries, parse_header, assume_yes)

    if sub == "list":
        print(f"Plugin folder: {plugin_dir}")
        print("A plugin is one .py file with a header (keywords, desc, category). Commands:")
        print("  plugin search <word>        find shared plugins    plugin get <name>   add one from the library")
        print("  plugin new <name>           make a starter file    plugin install <file or https link>")
        print("  plugin export <name>        copy one to share      plugin remove <name>")
        print("Plugins are ordinary programs that run with your permissions: only install ones you trust.")
        if not mine:
            print("No plugins installed.")
        for p in mine:
            print(f"  {p.stem.replace('_', ' '):<24}{parse_header(p).get('desc', '')[:70]}")
        return 0

    if sub in {"new", "create"}:
        name = _plugin_name(" ".join(rest[:1])) if rest else None
        if not name:
            print("Usage: plugin new <name>   (letters, numbers and _ ; for example: plugin new tea_timer)")
            return 1
        if name in builtin:
            print(f"'{name}' is already a built-in task. Choose another name.")
            return 1
        target = plugin_dir / f"{name}.py"
        if target.exists():
            print(f"{target} already exists.")
            return 1
        plugin_dir.mkdir(parents=True, exist_ok=True)
        target.write_text(TEMPLATE.format(name=name, words=name.replace("_", " "), desc=f"Describe what {name} does"), encoding="utf-8")
        print(f"Created {target}\nEdit it, then run:  reindex   and say:  {name.replace('_', ' ')}")
        return 0

    if sub in {"remove", "delete", "uninstall"}:
        name = _plugin_name(" ".join(rest[:1])) if rest else None
        target = plugin_dir / f"{name}.py" if name else None
        if not target or not target.is_file():
            print("Usage: plugin remove <name>   (see: plugin list)")
            return 1
        if not _ask(f"Delete plugin '{name}'?", assume_yes):
            return 3
        target.unlink()
        print(f"Removed plugin '{name}'. Say 'reindex' to refresh.")
        return 0

    if sub == "export":
        name = _plugin_name(" ".join(rest[:1])) if rest else None
        src = plugin_dir / f"{name}.py" if name else None
        if not src or not src.is_file():
            print("Usage: plugin export <name>   (see: plugin list)")
            return 1
        dst = Path.cwd() / src.name
        if dst.exists():
            print(f"{dst} already exists; move it first.")
            return 1
        shutil.copyfile(src, dst)
        print(f"Copied to {dst}. Anyone can add it with:  plugin install {src.name}")
        return 0

    if sub == "install":
        force = "force" in [w.lower() for w in rest]
        rest = [w for w in rest if w.lower() != "force"]
        if not rest:
            print("Usage: plugin install <file.py or https address> [force]")
            return 1
        src = rest[0]
        if re.match(r"(?i)https?://", src):
            if not src.lower().startswith("https://"):
                print("Only https links are allowed.")
                return 1
            try:
                req = urllib.request.Request(src, headers={"User-Agent": "JeeG-plugin"})
                with urllib.request.urlopen(req, timeout=15) as r:
                    data = r.read(MAX_PLUGIN_BYTES + 1)
            except (urllib.error.URLError, TimeoutError, ValueError) as ex:
                print(f"Could not download that link: {getattr(ex, 'reason', ex)}")
                return 1
            stem = Path(src.split("?")[0].rstrip("/")).name
        else:
            p = Path(src).expanduser()
            if not p.is_file():
                print(f"File not found: {p}")
                return 1
            try:
                data = p.read_bytes()[:MAX_PLUGIN_BYTES + 1]
            except OSError as ex:
                print(f"Could not read it: {ex.strerror or ex}")
                return 1
            stem = p.name
        if len(data) > MAX_PLUGIN_BYTES:
            print("That file is too large for a plugin (over 200 KB).")
            return 1
        name = _plugin_name(stem)
        if not name or not stem.lower().endswith(".py"):
            print("A plugin must be a .py file named with letters, numbers and _ (for example tea_timer.py).")
            return 1
        if name in builtin:
            print(f"'{name}' is already a built-in task; rename the file first.")
            return 1
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            print("That file is not plain UTF-8 text.")
            return 1
        meta = {}
        for line in text.splitlines()[:15]:
            m = re.match(r"^\s*#\s*(\w+)\s*:\s*(.*?)\s*$", line)
            if m:
                meta[m.group(1).lower()] = m.group(2)
        if not meta.get("keywords") or not meta.get("desc"):
            print("The file needs '# keywords:' and '# desc:' lines at the top (see: plugin new <name>).")
            return 1
        target = plugin_dir / f"{name}.py"
        if target.exists() and not force:
            print(f"Plugin '{name}' is already installed. Add the word 'force' to replace it.")
            return 1
        print(f"Plugin: {name}\nDoes:   {meta['desc']}\nSays:   {meta['keywords']}\nSize:   {len(text.splitlines())} lines")
        hits = [r for r in RISKY if r in text]
        print("Uses:   " + (", ".join(hits) if hits else "nothing unusual found") + "   (a quick scan, not a guarantee)")
        print("It will run as a normal program with your permissions. Read the file if you are not sure of its author.")
        if not _ask(f"Install '{name}'?", assume_yes):
            return 3
        plugin_dir.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        print(f"Installed. Say 'reindex' to refresh, then try: {meta['keywords'].split(',')[0].strip()}")
        return 0

    print("Unknown plugin command. Try: plugin list | search | get | new | install | export | remove")
    return 1


# --------------------------------------------------------------- tab completion
def cmd_completion(shell: str, entries: list[dict]) -> int:
    shell = (shell or "bash").lower()
    words = sorted({w for e in entries for w in e["name"].split("_") if len(w) > 2})
    base = ["list", "again", "history", "reindex", "selftest", "alias", "explain", "misses", "stats", "doctor",
            "pack", "tips", "plugins", "update", "setup", "web", "completion"]
    allw = " ".join(sorted(set(words) | set(base)))
    if shell == "bash":
        print(f'_jeeg() {{ COMPREPLY=($(compgen -W "{allw}" -- "${{COMP_WORDS[COMP_CWORD]}}")); }}\ncomplete -F _jeeg jeeg')
    elif shell == "zsh":
        print(f"#compdef jeeg\n_arguments '*: :({allw})'")
    elif shell in {"powershell", "pwsh"}:
        arr = ", ".join(f"'{w}'" for w in allw.split())
        print("Register-ArgumentCompleter -Native -CommandName jeeg -ScriptBlock {\n"
              "  param($wordToComplete)\n"
              f"  @({arr}) | Where-Object {{ $_ -like \"$wordToComplete*\" }} | ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_) }}\n}}")
    else:
        print("Shells: bash, zsh, powershell")
        return 1
    return 0


COMPLETION_HELP = ("Tab completion: add this to your shell start-up file\n"
                   "  bash:  eval \"$(jeeg completion bash)\"      (in ~/.bashrc)\n"
                   "  zsh:   jeeg completion zsh > ~/.zfunc/_jeeg    (and: fpath+=~/.zfunc)\n"
                   "  PowerShell:  jeeg completion powershell | Out-String | Invoke-Expression   (in $PROFILE)")


# ------------------------------------------------------------------ setup wizard
def cmd_setup(here: Path, state: Path, entries: list[dict], assume_yes: bool = False) -> int:
    print("JeeG setup (about a minute). Nothing here is sent anywhere.\n")
    print(f"1. Python {sys.version.split()[0]} - {'fine' if sys.version_info >= (3, 9) else 'needs 3.9 or newer'}")
    print(f"2. {len(entries)} tasks found. Your data lives in {state} (private to you).")
    inst = here / "install.py"
    launcher = shutil.which("jeeg")
    if launcher:
        print(f"3. The 'jeeg' command is already installed: {launcher}")
    elif inst.is_file():
        if _ask("3. Install the 'jeeg' command so you can type  jeeg open youtube  from any terminal?", assume_yes):
            rc = subprocess.run([sys.executable, str(inst)]).returncode
            print("   done." if rc == 0 else "   it did not finish; see the message above.")
        else:
            print("   skipped (run  python install.py  any time).")
    else:
        print("3. Installed with pip: the 'jeeg' command is ready.")
    print("4. " + COMPLETION_HELP.replace("\n", "\n   "))
    print("\nTry these now:\n  jeeg open youtube\n  jeeg gst 2500 18\n  jeeg add expense 250 lunch\n  jeeg list")
    print("Say 'tips' for a task you have not used yet, 'doctor' to check this computer.")
    return 0


# ----------------------------------------------------------------- local web page
PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JeeG</title><style>
:root{--bg:#faf9f5;--fg:#1f1e1d;--mut:#73726c;--card:#fff;--line:#e8e6dc;--acc:#c96442}
@media(prefers-color-scheme:dark){:root{--bg:#262624;--fg:#f0eee6;--mut:#a09f97;--card:#30302e;--line:#444441;--acc:#d97757}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:680px;margin:0 auto;padding:40px 16px}h1{font:600 28px Georgia,serif;margin:0 0 4px}p.s{color:var(--mut);margin:0 0 24px}
form{display:flex;gap:8px}input{flex:1;padding:12px 14px;font:inherit;color:inherit;background:var(--card);border:1px solid var(--line);border-radius:12px}
button{padding:0 18px;border:0;border-radius:12px;background:var(--acc);color:#fff;font:inherit;cursor:pointer}
pre{white-space:pre-wrap;word-wrap:break-word;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin:12px 0 0;font:14px/1.5 ui-monospace,Menlo,Consolas,monospace}
.q{color:var(--mut);margin-top:20px;font-size:14px}.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.chips button{background:var(--card);color:var(--fg);border:1px solid var(--line);padding:6px 12px;font-size:14px}
footer{margin-top:32px;color:var(--mut);font-size:13px}</style></head><body><main>
<h1>JeeG</h1><p class="s">Say the task. It runs on this computer. Nothing leaves it.</p>
<form id="f"><input id="q" autocomplete="off" autofocus placeholder="for example: gst 2500 18" maxlength="500"><button>Run</button></form>
<div class="chips" id="c"></div><div id="out"></div>
<footer>Local page, only reachable from this computer. Tasks that ask for confirmation are declined here; run them in the terminal.</footer></main>
<script>
const T="__TOKEN__",o=document.getElementById("out"),q=document.getElementById("q");
for(const s of["system info","show ip","weather mumbai","gst 2500 18","emi 5 lakh 8.5 5 years","todo list"]){const b=document.createElement("button");b.type="button";b.textContent=s;b.onclick=()=>{q.value=s;run()};document.getElementById("c").append(b)}
async function run(){const v=q.value.trim();if(!v)return;const d=document.createElement("div");d.className="q";d.textContent="> "+v;const p=document.createElement("pre");p.textContent="...";o.prepend(p);o.prepend(d);
try{const r=await fetch("/run",{method:"POST",headers:{"Content-Type":"application/json","X-JeeG-Token":T},body:JSON.stringify({q:v})});const j=await r.json();p.textContent=j.out||"(no output)"}catch(e){p.textContent="Could not reach JeeG."}q.value=""}
document.getElementById("f").onsubmit=e=>{e.preventDefault();run()};
</script></body></html>"""


def serve(here: Path, state: Path, port: int = 8765, open_browser: bool = True) -> int:
    token = secrets.token_urlsafe(24)
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
    engine = here / "jeeg.py"

    class H(http.server.BaseHTTPRequestHandler):
        server_version = "JeeG"

        def log_message(self, *a):
            pass

        def _send(self, code, body, ctype="text/html; charset=utf-8"):
            b = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(b)

        def _host_ok(self):
            return self.headers.get("Host", "") in allowed_hosts      # blocks DNS-rebinding

        def do_GET(self):
            if not self._host_ok():
                return self._send(403, "Forbidden", "text/plain")
            if self.path.split("?")[0] == "/":
                return self._send(200, PAGE.replace("__TOKEN__", token))
            self._send(404, "Not found", "text/plain")

        def do_POST(self):
            if not self._host_ok() or self.path != "/run":
                return self._send(403, "Forbidden", "text/plain")
            if not secrets.compare_digest(self.headers.get("X-JeeG-Token", ""), token):
                return self._send(403, "Forbidden", "text/plain")
            origin = self.headers.get("Origin")
            if origin and origin not in {f"http://{h}" for h in allowed_hosts}:
                return self._send(403, "Forbidden", "text/plain")
            try:
                n = int(self.headers.get("Content-Length", "0"))
                if not 0 < n <= 4096:
                    raise ValueError
                q = str(json.loads(self.rfile.read(n).decode("utf-8")).get("q", "")).strip()[:500]
            except (ValueError, UnicodeDecodeError, AttributeError):
                return self._send(400, json.dumps({"out": "Bad request."}), "application/json")
            if not q:
                return self._send(200, json.dumps({"out": "Say something first."}), "application/json")
            ws = q.lower().split()
            low = ws[1] if ws[0] == "jeeg" and len(ws) > 1 else ws[0]
            if low in {"web", "ui", "setup", "update", "upgrade", "plugin", "plugins", "exit", "quit", "q", "first", "completion"}:
                return self._send(200, json.dumps({"out": f"'{low}' is only available in the terminal."}), "application/json")
            try:
                r = subprocess.run([sys.executable, str(engine), q], capture_output=True, text=True, timeout=60,
                                   stdin=subprocess.DEVNULL, env=dict(os.environ, PYTHONIOENCODING="utf-8"), encoding="utf-8", errors="replace")
                out = ((r.stdout or "") + (r.stderr or "")).strip()[:20000]
            except subprocess.TimeoutExpired:
                out = "That took over 60 seconds, so it was stopped."
            self._send(200, json.dumps({"out": out}), "application/json")

    try:
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), H)
    except OSError as ex:
        print(f"Could not start on port {port}: {ex.strerror or ex}. Try:  serve 8800")
        return 1
    url = f"http://127.0.0.1:{port}/"
    print(f"JeeG web page: {url}\nOnly this computer can open it. Press Ctrl+C to stop.")
    if open_browser:
        threading.Timer(0.6, lambda: __import__("webbrowser").open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()
    return 0


# ============================================================ plugin library
import hashlib

LIBRARY_URL = "https://raw.githubusercontent.com/asrbmy/jeeg/main/library"
LIB_MAX_INDEX = 500_000


def _library_base() -> str:
    return os.environ.get("JEEG_LIBRARY", "").strip() or LIBRARY_URL


def _lib_read(base: str, rel: str, limit: int) -> bytes:
    """Read one file of the library from a folder or an https address."""
    if re.match(r"(?i)https?://", base):
        if not base.lower().startswith("https://"):
            raise OSError("the library address must use https")
        try:
            req = urllib.request.Request(base.rstrip("/") + "/" + rel, headers={"User-Agent": "JeeG-library"})
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.read(limit + 1)
        except urllib.error.HTTPError as ex:
            raise OSError(f"the library answered {ex.code}")
        except (urllib.error.URLError, TimeoutError, ValueError) as ex:
            raise OSError("could not reach the library (are you online?)") from ex
    p = Path(base).expanduser() / rel
    try:
        return p.read_bytes()[:limit + 1]
    except OSError as ex:
        raise OSError(f"could not read {p}") from ex


def library_index(base: str | None = None) -> dict:
    base = base or _library_base()
    raw = _lib_read(base, "index.json", LIB_MAX_INDEX)
    if len(raw) > LIB_MAX_INDEX:
        raise OSError("the library index is too large")
    try:
        data = json.loads(raw.decode("utf-8"))
        plugins = data["plugins"]
        assert isinstance(plugins, dict)
    except (ValueError, KeyError, AssertionError, UnicodeDecodeError):
        raise OSError("the library index is not valid")
    good = {}
    for k, v in plugins.items():
        if (NAME_RE.fullmatch(str(k)) and isinstance(v, dict) and re.fullmatch(r"[0-9a-f]{64}", str(v.get("sha256", "")))
                and isinstance(v.get("desc"), str)):
            good[k] = v
    return good


def cmd_library(sub: str, rest: list[str], plugin_dir: Path, entries: list[dict], parse_header, assume_yes: bool = False) -> int:
    base = _library_base()
    try:
        idx = library_index(base)
    except OSError as ex:
        print(f"Could not open the plugin library: {ex}.")
        return 1
    if sub in {"search", "library", "browse"}:
        q = [w.lower() for w in rest]
        hits = {k: v for k, v in idx.items() if all(w in (k + " " + v["desc"] + " " + str(v.get("tags", ""))).lower() for w in q)}
        if not hits:
            print("Nothing in the library matches that. See everything with:  plugin library")
            return 1
        for k, v in sorted(hits.items()):
            print(f"  {k:<20}{v['desc'][:80]}")
        print("Add one with:  plugin get <name>")
        return 0
    name = _plugin_name(rest[0]) if rest else None           # sub == "get"
    if not name or name not in idx:
        print("Usage: plugin get <name>   (find names with: plugin search <word>)")
        return 1
    meta = idx[name]
    if name in {e["name"] for e in entries if Path(e["path"]).resolve().parent != plugin_dir.resolve()}:
        print(f"'{name}' clashes with a built-in task name.")
        return 1
    try:
        data = _lib_read(base, f"{name}.py", MAX_PLUGIN_BYTES)
    except OSError as ex:
        print(f"Could not download it: {ex}.")
        return 1
    if len(data) > MAX_PLUGIN_BYTES:
        print("That plugin is too large.")
        return 1
    if hashlib.sha256(data).hexdigest() != meta["sha256"]:
        print("The downloaded file does not match the fingerprint in the library index, so it was NOT installed.")
        return 1
    tmp = plugin_dir.parent / f".lib_{name}.py"
    plugin_dir.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(data)
    try:
        return _install_local(tmp, name, plugin_dir, entries, parse_header, assume_yes)
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


def _install_local(tmp: Path, name: str, plugin_dir: Path, entries, parse_header, assume_yes: bool) -> int:
    """Install an already-verified file under the library name (the temp file has a different name)."""
    text = tmp.read_text(encoding="utf-8")
    meta = parse_header(tmp)
    if not meta.get("keywords") or not meta.get("desc"):
        print("That plugin has no keywords/desc header, so it was not installed.")
        return 1
    print(f"Plugin: {name}  (from the JeeG plugin library, fingerprint checked)\nDoes:   {meta['desc']}\nSays:   {meta['keywords']}\nSize:   {len(text.splitlines())} lines")
    hits = [r for r in RISKY if r in text]
    print("Uses:   " + (", ".join(hits) if hits else "nothing unusual found") + "   (a quick scan, not a guarantee)")
    target = plugin_dir / f"{name}.py"
    if not _ask(f"Install '{name}'" + (" (replaces your current copy)" if target.exists() else "") + "?", assume_yes):
        return 3
    plugin_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    print(f"Installed. Say 'reindex' to refresh, then try: {meta['keywords'].split(',')[0].strip()}")
    return 0


# ====================================================== routines export / import
def _validate_routines(data) -> dict:
    if not isinstance(data, dict) or data.get("kind") != "routines" or not isinstance(data.get("routines"), dict):
        raise ValueError("this is not a JeeG routines file")
    out = {}
    for k, steps in data["routines"].items():
        if not re.fullmatch(r"[a-z0-9][a-z0-9 _-]{0,39}", str(k)):
            raise ValueError(f"routine name '{str(k)[:30]}' is not allowed")
        if not isinstance(steps, list) or not 1 <= len(steps) <= 50 or not all(isinstance(s, str) and 0 < len(s) <= 200 for s in steps):
            raise ValueError(f"routine '{k}' must be 1-50 short text steps")
        if any(re.search(r"[\x00-\x08\x0b-\x1f\x7f]", s) for s in steps):
            raise ValueError(f"routine '{k}' contains control characters")
        out[str(k)] = steps
    if not out or len(out) > 50:
        raise ValueError("a routines file needs 1-50 routines")
    return out


def cmd_routines_io(args: str, state: Path, assume_yes: bool = False) -> int:
    words = args.split()
    sub = words[0].lower() if words else ""
    f = state / "routines.json"
    if sub == "export":
        try:
            mine = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        except (OSError, ValueError):
            mine = {}
        mine = {k: v for k, v in mine.items() if isinstance(v, list)}
        if not mine:
            print("You have no routines of your own yet. Create one with:  edit routines")
            return 1
        dst = Path.cwd() / "jeeg-routines.json"
        if dst.exists():
            print(f"{dst} already exists; move it first.")
            return 1
        dst.write_text(json.dumps({"jeeg": 1, "kind": "routines", "routines": mine}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {len(mine)} routine(s) to {dst}. Share it, and others can add it with:  routines import jeeg-routines.json")
        return 0
    if sub == "import" and len(words) > 1:
        src = Path(" ".join(words[1:]).strip("\"'")).expanduser()
        try:
            if not src.is_file() or src.stat().st_size > 200_000:
                raise ValueError("that file was not found or is too large")
            new = _validate_routines(json.loads(src.read_text(encoding="utf-8")))
        except (OSError, ValueError, UnicodeDecodeError) as ex:
            print(f"Could not import: {ex}.")
            return 1
        try:
            cur = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        except (OSError, ValueError):
            cur = {}
        for k, steps in new.items():
            print(f"  {k}{' (replaces yours)' if k in cur else ''}: " + " | ".join(steps[:6]) + (" ..." if len(steps) > 6 else ""))
        print("Routines run JeeG tasks one after another; steps that ask for confirmation will still ask.")
        if not _ask(f"Add {len(new)} routine(s)?", assume_yes):
            return 3
        cur.update(new)
        state.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(cur, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Done. Run one with:  run routine <name>")
        return 0
    print("Usage: routines export | routines import <file>")
    return 1


# ============================================================ guided tour
TOUR = [
    ("Say what you want", "JeeG matches your words to a small script and runs it. Try a calculator task:", "gst 2500 18"),
    ("Several tasks at once", "Join tasks with 'and'. This only shows the plan; nothing is opened:", "--dry-run open gmail and open calendar"),
    ("See why it chose that", "'explain' shows which tasks matched and their scores:", "explain open youtube"),
    ("Keep a to-do", "Your data stays in a private folder on this computer:", "add todo finish the JeeG tour"),
    ("Look at it again", "", "todo list"),
    ("Browse everything", "Tasks are grouped by category:", "list money"),
    ("Get a suggestion", "JeeG can point out a task you have not used:", "tips"),
]


def cmd_learn(run_line, interactive: bool) -> int:
    print("JeeG tour: 7 short steps. Press Enter to run each example, or type s to skip it, q to stop.\n" if interactive
          else "JeeG tour (run it in a terminal to try each step):\n")
    for i, (title, text, cmd) in enumerate(TOUR, 1):
        print(f"{i}. {title}")
        if text:
            print(f"   {text}")
        print(f"   try:  {cmd}")
        if interactive:
            ans = input("   [Enter = run, s = skip, q = quit] ").strip().lower()
            if ans == "q":
                print("Stopped. Come back any time with:  learn")
                return 0
            if ans != "s":
                print()
                run_line(cmd)
        print()
    print("That is the whole idea. Next: 'list' for every task, 'plugin search' for extra ones, 'alias add' for your own short words.")
    return 0
