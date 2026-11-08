"""Let other programs use JeeG: a local HTTP API, a line-by-line (JSONL) pipe, and an MCP server.

    jeeg --serve-api [PORT]     JSON over HTTP on 127.0.0.1 only, protected by a token   (any language)
    jeeg --stdio                one JSON request per line on stdin, one JSON answer per line on stdout
    jeeg --mcp                  Model Context Protocol server over stdio (for apps that speak MCP)
    jeeg --api-token            print the token for --serve-api

All three use the same requests (see dispatch). Everything stays on this computer. Tasks that ask for confirmation
(shutdown, delete ...) are refused unless you start with --allow-confirm. Calls are not written to your history.
"""
from __future__ import annotations

import http.server
import json
import re
import os
import secrets
import sys
import threading
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import jeeg
import jeeg_api

MAX_BODY = 64 * 1024
MAX_OUTPUT = 100_000
DEFAULT_PORT = 8766
ORIGIN_OK = re.compile(r"(?:chrome-extension|moz-extension)://[A-Za-z0-9\-]{8,64}")   # browser EXTENSIONS only, never web pages
ALLOWED_ORIGINS: set = set()                                                           # filled by --allow-origin
VERSION = jeeg.__version__


def _result_dict(r) -> dict:
    d = r.to_dict()
    d["output"] = d["output"][:MAX_OUTPUT]
    return d


class Policy:
    """Which tasks outside callers may use. only={"money","gst_amount"}: just these categories/task names.
    deny={"files"}: everything except these. Names and categories are both accepted."""

    def __init__(self, only=(), deny=()):
        self.only = {x.strip().lower() for x in only if x.strip()}
        self.deny = {x.strip().lower() for x in deny if x.strip()}

    @property
    def active(self) -> bool:
        return bool(self.only or self.deny)

    def allows(self, name: str, category: str) -> bool:
        keys = {name.lower(), category.lower()}
        if keys & self.deny:
            return False
        return not self.only or bool(keys & self.only)


_AUDIT_LOCK = threading.Lock()


def audit(path, source: str, op: str, task, exit_code, started: float) -> None:
    """One line per call in a private log: time, where from, what kind, which task, exit code, milliseconds.
    It never records what you asked or what came back."""
    if not path:
        return
    try:
        line = json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "via": source, "op": op, "task": task,
                           "exit": exit_code, "ms": int((time.time() - started) * 1000)})
        with _AUDIT_LOCK:
            p = Path(path)
            if p.exists() and p.stat().st_size > 1_000_000:
                os.replace(p, str(p) + ".1")
            fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            with os.fdopen(fd, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
    except OSError:
        pass


def dispatch(req, *, allow_confirm: bool = False, dirs=(), home=None, policy: Policy | None = None, audit_path=None,
             source: str = "api") -> dict:
    """One request (a dict) in, one answer out: {"ok": bool, "result": ..., "error": ...}. Never raises."""
    started = time.time()
    op, task, code = "?", None, None
    try:
        if not isinstance(req, dict):
            return {"ok": False, "error": "A request must be a JSON object."}
        op = req.get("op", "run" if "query" in req else "task" if "name" in req else "")
        if not isinstance(op, str):
            op = ""
        timeout = req.get("timeout", 60)
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not 0 < timeout <= 300:
            timeout = 60
        pol = policy if policy and policy.active else None
        kw = dict(yes=bool(allow_confirm and req.get("yes")), timeout=timeout, home=home, dirs=dirs)

        def allowed(name, cat):
            return pol is None or pol.allows(name, cat)

        def done(r):
            nonlocal task, code
            task, code = r.task, r.exit
            return {"ok": True, "result": _result_dict(r)}

        if op == "ping":
            return {"ok": True, "result": {"jeeg": VERSION}}
        if op == "run":
            if pol is None:
                return done(jeeg_api.run(req.get("query"), **kw))
            pl = jeeg_api.plan(req.get("query"), home=home, dirs=dirs)          # restricted: exactly one known task
            if pl is None:
                return {"ok": False, "error": "No single matching task. Be more specific."}
            name, args, cat = pl
            if not allowed(name, cat):
                task, code = name, -1
                return {"ok": False, "error": f"'{name}' is not allowed here."}
            return done(jeeg_api.run_task(name, *args, **kw))
        if op == "task":
            args = req.get("args", [])
            if not isinstance(args, list) or len(args) > 50:
                return {"ok": False, "error": "args must be a list of up to 50 values."}
            info = jeeg_api.task_info(str(req.get("name", "")), home=home, dirs=dirs)
            if not allowed(info.name, info.category):
                task, code = info.name, -1
                return {"ok": False, "error": f"'{info.name}' is not allowed here."}
            return done(jeeg_api.run_task(info.name, *args, **kw))
        if op == "find":
            limit = req.get("limit", 5)
            limit = limit if isinstance(limit, int) and not isinstance(limit, bool) and 1 <= limit <= 50 else 5
            found = jeeg_api.find(req.get("query") or "", 50 if pol else limit, home=home, dirs=dirs)
            if pol:
                cats = {t.name: t.category for t in jeeg_api.tasks(home=home, dirs=dirs)}
                found = [m for m in found if allowed(m.name, cats.get(m.name, ""))][:limit]
            return {"ok": True, "result": [{"name": m.name, "score": m.score, "args": list(m.args), "description": m.description}
                                           for m in found]}
        if op == "tasks":
            cat = req.get("category")
            ts = jeeg_api.tasks(cat if isinstance(cat, str) else None, home=home, dirs=dirs)
            return {"ok": True, "result": [t.__dict__ for t in ts if allowed(t.name, t.category)]}
        if op == "categories":
            counts: dict = {}
            for t in jeeg_api.tasks(home=home, dirs=dirs):
                if allowed(t.name, t.category):
                    counts[t.category] = counts.get(t.category, 0) + 1
            return {"ok": True, "result": dict(sorted(counts.items()))}
        if op == "info":
            info = jeeg_api.task_info(str(req.get("name", "")), home=home, dirs=dirs)
            if not allowed(info.name, info.category):
                return {"ok": False, "error": f"No task named {req.get('name')!r}."}
            return {"ok": True, "result": info.__dict__}
        return {"ok": False, "error": "Unknown op. Use: run, task, find, tasks, categories, info, ping."}
    except (jeeg_api.UnknownTaskError, TypeError, ValueError) as ex:
        return {"ok": False, "error": str(ex)[:300]}
    except Exception as ex:                                   # never crash a server on one bad request
        return {"ok": False, "error": f"Unexpected error: {type(ex).__name__}"}
    finally:
        if op not in {"ping", ""}:
            audit(audit_path, source, op, task, code, started)


# ------------------------------------------------------------------ token
MIN_TOKEN = 16


def get_token(state: Path | None = None) -> str:
    env = os.environ.get("JEEG_API_TOKEN", "").strip()
    if len(env) >= MIN_TOKEN:
        return env
    state = Path(state or jeeg.STATE)
    f = state / "api_token"
    try:
        t = f.read_text(encoding="utf-8").strip()
        if len(t) >= 20:
            try:
                os.chmod(f, 0o600)                                    # tighten it if it was ever loosened
            except OSError:
                pass
            return t
    except OSError:
        pass
    state.mkdir(parents=True, exist_ok=True)
    t = secrets.token_urlsafe(32)
    fd = os.open(f, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(t + "\n")
    return t


def _cfg(allow_confirm=False, dirs=(), home=None, policy=None, audit_path=None) -> dict:
    return dict(allow_confirm=allow_confirm, dirs=tuple(dirs), home=home, policy=policy, audit_path=audit_path)


# ------------------------------------------------------------------ HTTP API
MAX_PARALLEL = 8


def make_handler(token: str, port: int, cfg: dict):
    hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
    slots = threading.BoundedSemaphore(MAX_PARALLEL)

    class H(http.server.BaseHTTPRequestHandler):
        server_version = "JeeG"
        protocol_version = "HTTP/1.0"
        timeout = 30                                               # a stalled client cannot hold a thread forever

        def log_message(self, *a):
            pass

        def _cors(self) -> None:
            o = self.headers.get("Origin")
            if o and o in ALLOWED_ORIGINS:
                self.send_header("Access-Control-Allow-Origin", o)
                self.send_header("Vary", "Origin")

        def do_OPTIONS(self):                                       # preflight, only for an allowed extension
            o = self.headers.get("Origin", "")
            if self.headers.get("Host", "") not in hosts or o not in ALLOWED_ORIGINS:
                return self._send(403, {"ok": False, "error": "Forbidden"})
            self.send_response(204)
            self._cors()
            self.send_header("Access-Control-Allow-Methods", "GET, POST")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-JeeG-Token")
            self.send_header("Access-Control-Max-Age", "600")
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _send(self, code: int, obj) -> None:
            b = json.dumps(obj).encode("utf-8")
            self.send_response(code)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(b)

        def _guard(self) -> bool:
            if self.headers.get("Host", "") not in hosts:                       # DNS-rebinding
                self._send(403, {"ok": False, "error": "Forbidden"})
                return False
            origin = self.headers.get("Origin")
            if origin and origin not in ALLOWED_ORIGINS:                        # web pages may not call this
                self._send(403, {"ok": False, "error": "Browsers are not allowed here."})
                return False
            given = self.headers.get("Authorization", "")
            given = given[7:] if given.lower().startswith("bearer ") else self.headers.get("X-JeeG-Token", "")
            if not secrets.compare_digest(given.encode("utf-8", "replace"), token.encode("utf-8")):
                self._send(401, {"ok": False, "error": "Missing or wrong token. Send  Authorization: Bearer <token>"})
                return False
            return True

        def _answer(self, req: dict) -> None:
            if not slots.acquire(blocking=False):
                return self._send(503, {"ok": False, "error": "Too many requests at once. Try again."})
            try:
                self._send(200, dispatch(req, source="http", **cfg))
            finally:
                slots.release()

        def do_GET(self):
            if not self._guard():
                return
            u = urlparse(self.path)
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            lim = q.get("limit", "")
            limit = int(lim) if lim.isascii() and lim.isdigit() and len(lim) < 4 else 5
            routes = {"/v1/health": {"op": "ping"}, "/v1/tasks": {"op": "tasks", "category": q.get("category")},
                      "/v1/categories": {"op": "categories"}, "/v1/find": {"op": "find", "query": q.get("q", ""), "limit": limit},
                      "/v1/info": {"op": "info", "name": q.get("name", "")}}
            if u.path not in routes:
                return self._send(404, {"ok": False, "error": "Not found"})
            self._answer(routes[u.path])

        def do_POST(self):
            if not self._guard():
                return
            path = urlparse(self.path).path
            if path not in {"/v1/run", "/v1/task"}:
                return self._send(404, {"ok": False, "error": "Not found"})
            try:
                n = int(self.headers.get("Content-Length", "0"))
                if not 0 < n <= MAX_BODY:
                    raise ValueError
                req = json.loads(self.rfile.read(n).decode("utf-8"))
                if not isinstance(req, dict):
                    raise ValueError
            except (ValueError, UnicodeDecodeError, OSError):
                return self._send(400, {"ok": False, "error": "Send a JSON object (up to 64 KB) with a Content-Length."})
            req["op"] = "run" if path == "/v1/run" else "task"
            self._answer(req)

    return H


def serve_api(port: int = DEFAULT_PORT, cfg: dict | None = None) -> int:
    cfg = cfg or _cfg()
    try:
        token = get_token()
    except OSError as ex:
        print(f"Could not save the token in {jeeg.STATE}: {ex.strerror or ex}. Set JEEG_API_TOKEN to a long secret instead.")
        return 1
    try:
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), make_handler(token, port, cfg))
    except OSError as ex:
        print(f"Could not start on port {port}: {ex.strerror or ex}. Try another:  jeeg --serve-api 8800")
        return 1
    httpd.daemon_threads = True
    print(f"JeeG API: http://127.0.0.1:{port}/v1/   (this computer only; Ctrl+C to stop)")
    print(f"Token: {token}")
    print("Send it as:  Authorization: Bearer <token>   (it is also saved in your JeeG data folder as api_token)")
    print(f"Try:  curl -H \"Authorization: Bearer {token}\" \"http://127.0.0.1:{port}/v1/find?q=open%20youtube\"")
    pol = cfg.get("policy")
    if pol and pol.active:
        print("Restricted: " + (f"only {', '.join(sorted(pol.only))}" if pol.only else "") + (f"  except {', '.join(sorted(pol.deny))}" if pol.deny else ""))
    if cfg.get("audit_path"):
        print(f"Logging calls (task and exit code only) to {cfg['audit_path']}")
    if cfg.get("allow_confirm"):
        print("WARNING: --allow-confirm lets callers run tasks that ask first (shutdown, delete ...).")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()
    return 0


# ------------------------------------------------------------------ line-based input (stdio and MCP)
def _lines(stream):
    """Read lines even when the other program sends bytes that are not valid UTF-8."""
    if stream is None:
        stream = sys.stdin
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass
    return stream


def _write(stream, obj) -> None:
    stream.write(json.dumps(obj) + "\n")
    stream.flush()


def stdio_loop(cfg: dict | None = None, stdin=None, stdout=None) -> int:
    cfg = cfg or _cfg()
    stdin, stdout = _lines(stdin), stdout or sys.stdout
    try:
        for line in stdin:
            line = line.strip()
            if not line:
                continue
            rid = None
            if len(line) > MAX_BODY:
                ans = {"ok": False, "error": "Line too long."}
            else:
                try:
                    req = json.loads(line)
                    rid = req.get("id") if isinstance(req, dict) else None
                    ans = dispatch(req, source="stdio", **cfg)
                except ValueError:
                    ans = {"ok": False, "error": "Not valid JSON."}
            if rid is not None:
                ans["id"] = rid
            _write(stdout, ans)
    except (BrokenPipeError, KeyboardInterrupt):
        pass
    return 0


# ------------------------------------------------------------------ MCP (Model Context Protocol) over stdio
MCP_TOOLS = [
    {"name": "jeeg_run", "description": "Run a JeeG task from plain words, for example 'gst 2500 18' or 'convert 5 km to miles'. Runs on the user's own computer.",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string", "description": "What to do, in plain words"}}, "required": ["query"]}},
    {"name": "jeeg_find", "description": "Show which JeeG tasks match a phrase, without running anything.",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["query"]}},
    {"name": "jeeg_list", "description": "List available JeeG tasks, optionally for one category.",
     "inputSchema": {"type": "object", "properties": {"category": {"type": "string"}}}},
]


def _mcp_text(text: str, error: bool = False) -> dict:
    return {"content": [{"type": "text", "text": text[:MAX_OUTPUT]}], "isError": error}


def mcp_handle(msg, cfg: dict | None = None):
    """One JSON-RPC message in; a response dict out (or None for notifications)."""
    cfg = cfg or _cfg()
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid request"}}
    mid, method = msg.get("id"), msg.get("method", "")
    params = msg.get("params")
    params = params if isinstance(params, dict) else {}
    if mid is None or not isinstance(method, str):           # notification: no reply
        return None

    def ok(result):
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    def err(code, text):
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": text}}

    def call(req):
        return dispatch(req, source="mcp", **cfg)

    if method == "initialize":
        ver = params.get("protocolVersion")
        return ok({"protocolVersion": ver if isinstance(ver, str) else "2024-11-05", "capabilities": {"tools": {}},
                   "serverInfo": {"name": "jeeg", "version": VERSION}})
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": MCP_TOOLS})
    if method == "tools/call":
        name = params.get("name")
        a = params.get("arguments")
        a = a if isinstance(a, dict) else {}
        if name == "jeeg_run":
            d = call({"op": "run", "query": a.get("query")})
            if not d["ok"]:
                return ok(_mcp_text(d["error"], True))
            r = d["result"]
            note = " (this task asks for confirmation, so it was not run)" if r["needs_confirmation"] else \
                   f" (several tasks fit: {', '.join(r['candidates'])})" if r["ambiguous"] else ""
            return ok(_mcp_text((r["output"] or "(no output)") + note, not r["ok"]))
        if name == "jeeg_find":
            d = call({"op": "find", "query": a.get("query"), "limit": a.get("limit", 5)})
            if not d["ok"]:
                return ok(_mcp_text(d["error"], True))
            return ok(_mcp_text("\n".join(f"{m['name']} ({m['score']}): {m['description']}" for m in d["result"]) or "No match."))
        if name == "jeeg_list":
            d = call({"op": "tasks", "category": a.get("category")})
            if not d["ok"]:
                return ok(_mcp_text(d["error"], True))
            return ok(_mcp_text("\n".join(f"{t['name']} [{t['category']}]: {t['description']}" for t in d["result"]) or "No tasks."))
        return err(-32602, f"Unknown tool: {name}")
    return err(-32601, f"Method not found: {method}")


def mcp_loop(cfg: dict | None = None, stdin=None, stdout=None) -> int:
    cfg = cfg or _cfg()
    stdin, stdout = _lines(stdin), stdout or sys.stdout
    try:
        for line in stdin:
            line = line.strip()
            if not line:
                continue
            try:
                out = mcp_handle(json.loads(line), cfg) if len(line) <= MAX_BODY else \
                    {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Message too long"}}
            except ValueError:
                out = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
            if out is not None:
                _write(stdout, out)
    except (BrokenPipeError, KeyboardInterrupt):
        pass
    return 0


def main(mode: str, port=None, allow_confirm=False, dirs=(), only=(), deny=(), log=False, origins=()) -> int:
    for o in origins:
        if not ORIGIN_OK.fullmatch(o):
            print(f"--allow-origin accepts only a browser extension address like chrome-extension://abcdefghijklmnop, not '{o}'.")
            return 1
        ALLOWED_ORIGINS.add(o)
    if mode == "--api-token":
        try:
            print(get_token())
        except OSError as ex:
            print(f"Could not save the token: {ex.strerror or ex}")
            return 1
        return 0
    cfg = _cfg(allow_confirm, dirs, None, Policy(only, deny), (jeeg.STATE / "api.log") if log else None)
    if mode == "--serve-api":
        return serve_api(port or DEFAULT_PORT, cfg)
    if mode == "--stdio":
        return stdio_loop(cfg)
    if mode == "--mcp":
        return mcp_loop(cfg)
    return 1
