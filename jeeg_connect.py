"""Connectors that run for a while: the Telegram bot and incoming hooks.

    telegram setup                    save your bot token (asked privately; make a bot with @BotFather)
    telegram start [safe|read|ask|god] [for 60 minutes] [limit 50]
                                      message your bot from your phone, and JeeG answers. Same modes as AI mode.
    telegram forget                   delete the token and the paired chats
    hook add deploy = git pull        a named task that a web address can start (the caller cannot choose the task)
    hook list | hook remove deploy
    hook listen [for 60 minutes] [keep] [no tunnel] [via ngrok]
                                      start the listener and print one link per hook (needs a tunnel program for the internet)

Telegram: JeeG calls the Telegram servers (outbound only, no tunnel). Only chats you pair with a one-time code
shown on this computer can use it. Telegram and anyone who can read your chat can see what is said.
Hooks: whoever has a hook link can start that one saved task (never anything else); tasks that ask for confirmation are refused.
"""
from __future__ import annotations

import getpass
import http.server
import json
import os
import re
import secrets
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import jeeg_api
import jeeg_remote
from jeeg_bridge import dispatch

TOKEN_RE = re.compile(r"\d{6,12}:[A-Za-z0-9_\-]{30,50}")
DEFAULT_API = "https://api.telegram.org"


# ------------------------------------------------------------------ small private files
def _read(state, name):
    try:
        d = json.loads((Path(state) / name).read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _write(state, name, data):
    p = Path(state) / name
    Path(state).mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1)
    os.replace(tmp, p)


def _secret_input(prompt):
    import sys
    try:
        if sys.stdin is not None and sys.stdin.isatty():
            return getpass.getpass(prompt).strip()
        return (sys.stdin.readline() if sys.stdin is not None else "").strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def api_base() -> str:
    """The Telegram address. Only this computer may stand in for it (for tests); a token is never sent to another host."""
    env = os.environ.get("JEEG_TELEGRAM_API", "")
    if env:
        h = (urlparse(env).hostname or "").lower()
        if h in {"127.0.0.1", "localhost"} and urlparse(env).scheme == "http":
            return env.rstrip("/")
    return DEFAULT_API


# ------------------------------------------------------------------ Telegram
class Telegram:
    def __init__(self, token: str, base: str | None = None):
        self.token = token
        self.base = base or api_base()

    def call(self, method: str, params: dict | None = None, timeout: float = 40):
        url = f"{self.base}/bot{self.token}/{method}"
        req = urllib.request.Request(url, data=json.dumps(params or {}).encode(), headers={"Content-Type": "application/json", "User-Agent": "JeeG"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read(2_000_000).decode("utf-8", "replace"))
        except urllib.error.HTTPError as ex:
            raise OSError(f"Telegram answered {ex.code}")
        except (urllib.error.URLError, ValueError) as ex:
            raise OSError(str(getattr(ex, "reason", ex)).replace(self.token, "***"))
        if not d.get("ok"):
            raise OSError(str(d.get("description", "Telegram refused"))[:120])
        return d.get("result")

    def send(self, chat_id, text: str):
        for i in range(0, max(1, len(text)), 3900):
            self.call("sendMessage", {"chat_id": chat_id, "text": text[i:i + 3900] or "(no output)", "disable_web_page_preview": True}, timeout=20)
            if i > 3900 * 3:
                break


HELP = ("JeeG. Send a task in plain words, for example:  gst 2500 18   or   convert 5 km to miles\n"
        "/mode shows what I may do.  /stop ends the session.")


def handle_message(tg: Telegram, msg: dict, st: dict) -> bool:
    """Process one Telegram message. Returns False when the session should end."""
    chat = msg.get("chat") or {}
    cid = chat.get("id")
    text = (msg.get("text") or "").strip()
    if cid is None or chat.get("type") != "private" or not text:
        return True
    log = st["log"]
    allowed = st["allowed"]
    if cid not in allowed:
        m = re.fullmatch(r"/pair\s+(\d{6})", text)
        if st["pair_bad"] >= 5:
            return True                                              # pairing is locked for this session
        if m and secrets.compare_digest(m.group(1), st["code"]):
            allowed.append(cid)
            _write(st["state"], "telegram.json", {"token": tg.token, "allowed": allowed})
            log(f"{jeeg_remote._ts()}  Telegram chat {cid} paired")
            tg.send(cid, "Paired. " + HELP)
        else:
            st["pair_bad"] += 1
            log(f"{jeeg_remote._ts()}  Telegram: unknown chat {cid} tried to use the bot ({st['pair_bad']}/5 wrong)")
            tg.send(cid, "This bot is private. If it is yours, send  /pair  and the 6-digit code shown on the computer, like:  /pair 123456")
        return True
    low = text.lower()
    if low in {"/start", "/help", "help"}:
        tg.send(cid, HELP)
    elif low == "/mode":
        tg.send(cid, f"Mode: {st['mode']}. " + {"safe": "Only calculators, converters and small lists.", "read": "Safe tasks and look-only tasks.",
                "ask": "Safe tasks at once; other tasks wait for approval on the computer.", "god": "Every task (confirmation tasks still need approval on the computer)."}[st["mode"]])
    elif low in {"/stop", "stop"}:
        tg.send(cid, "Stopped. Bye.")
        return False
    else:
        if text.startswith("/"):
            text = text.lstrip("/")
        if st["limit"] and st["calls"] >= st["limit"]:
            tg.send(cid, f"The limit of {st['limit']} requests for this session is used up.")
            return True
        st["calls"] += 1
        out, bad = jeeg_remote.run_for_ai(text, st["mode"], st["approver"], st["state"], log, "telegram", st["extra"])
        tg.send(cid, ("Failed: " if bad else "") + out)
    return True


def _cmd_telegram(state, rest: str = "", approver=None, tg_factory=Telegram) -> int:
    low = (rest or "").strip().lower()
    cfg = _read(state, "telegram.json")
    if low in {"forget", "remove", "logout"}:
        try:
            (Path(state) / "telegram.json").unlink()
            print("The Telegram token and paired chats were deleted from this computer. (Also revoke the token in @BotFather if it may have leaked.)")
        except OSError:
            print("Nothing was saved.")
        return 0
    if low in {"setup", "login", ""} or low.startswith("setup"):
        print("1) In Telegram, talk to @BotFather, send /newbot and follow the steps.\n2) Paste the token it gives you here.")
        tok = _secret_input("Bot token (typing is hidden): ")
        if not TOKEN_RE.fullmatch(tok):
            print("That does not look like a bot token (like 123456789:AA...). Nothing was saved.")
            return 1
        try:
            me = tg_factory(tok).call("getMe", timeout=20)
        except OSError as ex:
            print(f"Telegram did not accept it: {ex}")
            return 1
        _write(state, "telegram.json", {"token": tok, "allowed": []})
        print(f"Saved privately. Your bot is @{me.get('username', '?')}. Now run:  telegram start   and open the bot in Telegram.")
        return 0
    m = re.fullmatch(r"start(?:\s+(.*))?", low)
    if not m:
        print("Use:  telegram setup | start [safe|read|ask|god] [for 60 minutes] [limit 50] | forget")
        return 1
    if not cfg.get("token"):
        print("No bot yet. Run:  telegram setup")
        return 1
    try:
        o = jeeg_remote.parse_args(m.group(1) or "")
    except ValueError as ex:
        print(ex)
        return 1
    tg = tg_factory(cfg["token"])
    try:
        me = tg.call("getMe", timeout=20)
    except OSError as ex:
        print(f"Could not reach Telegram: {ex}")
        return 1
    log = print
    logpath = None
    if o["log"]:
        logpath, write = jeeg_remote._open_log(state)
        if write:
            def log(line, _w=write):
                print(line, flush=True)
                _w(line)
    approver = approver or jeeg_remote.Approver()
    approver.dry = approver.dry or o.get("dry", False)
    st = {"mode": o["mode"], "approver": approver, "state": str(state), "extra": tuple(o["allow"]), "log": log,
          "allowed": list(cfg.get("allowed", [])), "code": "".join(secrets.choice("0123456789") for _ in range(6)), "pair_bad": 0,
          "limit": o["limit"], "calls": 0}
    print(f"\n  JeeG on Telegram ({o['mode']}) as @{me.get('username', '?')}  - closes in {o['minutes']} minutes, on /stop, or Ctrl+C")
    if st["allowed"]:
        print(f"  {len(st['allowed'])} paired chat(s). To add another, send the bot:  /pair {st['code']}")
    else:
        print(f"  Open @{me.get('username', '?')} in Telegram and send:  /pair {st['code']}")
    print({"safe": "  Safe mode: only calculators, converters and small lists.", "read": "  Read-only mode: safe tasks and look-only tasks.",
           "ask": "  Ask mode: safe tasks run at once; anything else waits for your y here (no answer = no).",
           "god": "  GOD mode: every task runs (tasks that change or delete things still ask you here)."}[o["mode"]])
    print("  Telegram and anyone who can read that chat can see what is said. Every call is printed below.\n", flush=True)
    end = time.time() + o["minutes"] * 60
    offset = 0
    try:
        while time.time() < end:
            try:
                ups = tg.call("getUpdates", {"timeout": 20, "offset": offset, "allowed_updates": ["message"]}, timeout=40) or []
            except OSError as ex:
                print(f"  (Telegram: {ex}; retrying)", flush=True)
                time.sleep(3)
                continue
            for u in ups:
                offset = max(offset, int(u.get("update_id", 0)) + 1)
                try:
                    if not handle_message(tg, u.get("message") or {}, st):
                        return 0
                except OSError as ex:
                    print(f"  (could not answer: {ex})", flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nTelegram session closed.")
    return 0


# ------------------------------------------------------------------ incoming hooks
def cmd_telegram(state, rest: str = "", approver=None, tg_factory=Telegram) -> int:
    old = os.environ.get("JEEG_VIA_AI")
    try:
        return _cmd_telegram(state, rest, approver, tg_factory)
    finally:
        if old is None:
            os.environ.pop("JEEG_VIA_AI", None)
        else:
            os.environ["JEEG_VIA_AI"] = old


def cmd_hook(state, rest: str = "", tunnel_which=None) -> int:
    rest = (rest or "").strip()
    hooks = _read(state, "hooks.json")
    low = rest.lower()
    if low in {"", "list"}:
        print("Saved hooks:" if hooks else "None saved. Example:  hook add backup = backup folder documents")
        for k, v in sorted(hooks.items()):
            print(f"  {k:<14} runs:  {v}")
        return 0
    m = re.fullmatch(r"add\s+([a-z0-9][a-z0-9_\-]{0,31})\s*=\s*(.+)", rest, re.I | re.S)
    if m:
        name, task = m.group(1).lower(), m.group(2).strip()[:300]
        first = (task.split() or [""])[0].lower()
        if first in jeeg_remote.TERMINAL_ONLY or first in jeeg_api.TERMINAL_ONLY or re.search(r"\bthen\b", task, re.I):
            print("A hook runs one ordinary task (not a terminal command, and no 'then').")
            return 1
        pl = jeeg_api.plan(task, home=str(state))
        if not pl:
            print("I could not match that to one task. Try it on its own first, then save it.")
            return 1
        hooks[name] = task
        _write(state, "hooks.json", hooks)
        print(f"Saved hook '{name}' -> {pl[0]}. Tasks that ask for confirmation are refused when started from a hook. Start the listener:  hook listen")
        return 0
    m = re.fullmatch(r"(?:remove|delete)\s+([a-z0-9_\-]+)", low)
    if m:
        if hooks.pop(m.group(1), None) is None:
            print("No hook with that name.")
            return 1
        _write(state, "hooks.json", hooks)
        print("Removed.")
        return 0
    m = re.fullmatch(r"listen(?:\s+(.*))?", low)
    if not m:
        print("Use:  hook add <name> = <task> | list | remove <name> | listen [for 60 minutes] [keep] [no tunnel] [via ngrok]")
        return 1
    if not hooks:
        print("No hooks yet. Add one:  hook add backup = backup folder documents")
        return 1
    try:
        o = jeeg_remote.parse_args(m.group(1) or "")
    except ValueError as ex:
        print(ex)
        return 1
    secret = ""
    if o["keep"]:
        secret = _read(state, "hook_link.json").get("secret", "")
        if len(secret) < 40:
            secret = secrets.token_urlsafe(32)
            _write(state, "hook_link.json", {"secret": secret})
    secret = secret or secrets.token_urlsafe(32)
    log = print
    logpath = None
    if o["log"]:
        logpath, write = jeeg_remote._open_log(state)
        if write:
            def log(line, _w=write):
                print(line, flush=True)
                _w(line)
    hits: list = []
    lock = threading.Lock()
    base = f"/{secret}/"
    hosts: set = set()
    deadline = time.time() + o["minutes"] * 60
    gate = threading.BoundedSemaphore(2)

    class H(http.server.BaseHTTPRequestHandler):
        server_version = "JeeG"
        sys_version = ""

        def log_message(self, *a):
            pass

        def _send(self, code, obj):
            data = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _go(self):
            host = (self.headers.get("Host") or "").lower()
            raw = urlparse(self.path).path.encode("utf-8", "replace")
            pre = base.encode()
            if host not in hosts or self.headers.get("Origin") or len(raw[:len(pre)]) != len(pre) or not secrets.compare_digest(raw[:len(pre)], pre):
                return self._send(404, {"ok": False, "output": "Not found"})
            if time.time() > deadline:
                threading.Thread(target=httpd.shutdown, daemon=True).start()
                return self._send(403, {"ok": False, "output": "This link has expired."})
            name = raw[len(pre):].decode("utf-8", "replace").strip("/").lower()
            cur = _read(state, "hooks.json")
            if name not in cur:
                return self._send(404, {"ok": False, "output": "Not found"})
            now = time.time()
            with lock:
                hits[:] = [t for t in hits if now - t < 60]
                if len(hits) >= 12:
                    return self._send(429, {"ok": False, "output": "Too many calls. Try again in a minute."})
                hits.append(now)
            if self.command == "POST":                                     # the body is read and ignored: the caller cannot change the task
                try:
                    n = int(self.headers.get("Content-Length", "0"))
                    if 0 < n <= 65536:
                        self.rfile.read(n)
                except ValueError:
                    pass
            if not gate.acquire(blocking=False):
                return self._send(503, {"ok": False, "output": "Busy"})
            try:
                task = cur[name]
                log(f"{jeeg_remote._ts()}  hook '{name}' -> {task}")
                d = dispatch({"op": "run", "query": task, "timeout": 120}, allow_confirm=False, home=str(state), source="hook")
            finally:
                gate.release()
            r = d.get("result") or {}
            if d.get("ok") and r.get("needs_confirmation"):
                return self._send(200, {"ok": False, "output": "That task needs confirmation, so it does not run from a hook."})
            self._send(200, {"ok": bool(d.get("ok") and r.get("ok")), "output": str(r.get("output") or d.get("error") or "")[:4000]})

        do_GET = do_POST = _go

    try:
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", o["port"] if o["port"] != jeeg_remote.DEFAULT_PORT else 8768), H)
    except OSError:
        if o["keep"]:
            print("That port is busy. Choose another:  hook listen port 8800 ...")
            return 1
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    port = httpd.server_address[1]
    hosts.update({f"127.0.0.1:{port}", f"localhost:{port}"})
    proc, public, note = None, "", ""
    if o["url"]:
        public = o["url"]
        hosts.add(urlparse(public).netloc.lower())
    elif o["tunnel"]:
        print("Starting the tunnel ...", flush=True)
        proc, res = jeeg_remote.start_tunnel(port, o["via"], **({"which": tunnel_which} if tunnel_which else {}))
        if proc is None:
            note = res
        else:
            public = res
            hosts.add(urlparse(public).netloc.lower())
    root = (public.rstrip("/") if public else f"http://127.0.0.1:{port}") + base
    print(f"\n  JeeG hooks - closes in {o['minutes']} minutes or on Ctrl+C\n")
    for k in sorted(hooks):
        print(f"  {k:<14} {root}{k}")
    if note:
        print("\n  " + note.replace("\n", "\n  "))
    print("\n  Call a link with GET or POST. It runs only the saved task named in it. Whoever has a link can start that task; keep the links private.")
    print("  Tasks that ask for confirmation are refused. At most 12 calls a minute. Every call is printed below.\n", flush=True)
    t = threading.Timer(o["minutes"] * 60 + 1, httpd.shutdown)
    t.daemon = True
    t.start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        t.cancel()
        httpd.server_close()
        jeeg_remote.stop_tunnel(proc)
        print("\nHooks closed. The links no longer work.")
    return 0
