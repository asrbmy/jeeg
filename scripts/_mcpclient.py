"""A small MCP client for servers that speak JSON lines over stdin/stdout. Standard library only. Not a task."""
import json
import os
import queue
import shutil
import subprocess
import threading
import urllib.error
import urllib.parse
import urllib.request

from _conn import is_private_host, local_only_override

MAX_REPLY = 2_000_000


class MCPError(Exception):
    pass


class Server:
    def __init__(self, argv, timeout=60, env=None):
        self.timeout = timeout
        argv = list(argv)
        exe = shutil.which(argv[0])                               # on Windows this finds npx.cmd and friends
        if exe:
            argv[0] = exe
        e = None
        if env:
            e = dict(os.environ)
            e.update(env)
        try:
            self.p = subprocess.Popen(argv, env=e, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace", bufsize=1)
        except OSError as ex:
            raise MCPError(f"could not start the server: {ex.strerror or ex}")
        self.q = queue.Queue()
        self.n = 0
        threading.Thread(target=self._pump, daemon=True).start()
        self.request("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "jeeg", "version": "1"}})
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _pump(self):
        try:
            for line in self.p.stdout:
                line = line.strip()
                if line.startswith("{"):
                    try:
                        self.q.put(json.loads(line))
                    except ValueError:
                        pass
        except (OSError, ValueError):
            pass
        self.q.put(None)

    def _send(self, msg):
        try:
            self.p.stdin.write(json.dumps(msg) + "\n")
            self.p.stdin.flush()
        except (OSError, ValueError):
            raise MCPError("the server stopped")

    def request(self, method, params=None):
        self.n += 1
        mid = self.n
        self._send({"jsonrpc": "2.0", "id": mid, "method": method, "params": params or {}})
        while True:
            try:
                msg = self.q.get(timeout=self.timeout)
            except queue.Empty:
                raise MCPError(f"no answer within {self.timeout} seconds")
            if msg is None:
                raise MCPError("the server stopped")
            if msg.get("id") == mid:
                if "error" in msg:
                    raise MCPError(str(msg["error"].get("message", msg["error"]))[:300])
                return msg.get("result", {})

    def close(self):
        try:
            self.p.stdin.close()
            self.p.terminate()
            self.p.wait(timeout=5)
        except Exception:
            try:
                self.p.kill()
            except Exception:
                pass


class HTTPServer:
    """MCP over 'streamable HTTP': every message is a POST; the answer is JSON or a short event stream. Only https to a public address."""

    def __init__(self, url, timeout=60, bearer=""):
        self.timeout, self.bearer, self.session, self.n = timeout, bearer, "", 0
        self.url = self._check(url)
        r = self.request("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "jeeg", "version": "1"}})
        self.version = str(r.get("protocolVersion") or "2025-03-26")
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    @staticmethod
    def _check(url):
        base = local_only_override("JEEG_MCP_BASE", "")                       # tests only: this computer
        u = urllib.parse.urlsplit(url)
        if base:
            return base.rstrip("/") + (u.path or "/")
        if u.scheme != "https" or not u.hostname or u.username or u.password:
            raise MCPError("a web MCP server must be an https address")
        if is_private_host(u.hostname):
            raise MCPError("that address is on this computer or your own network; web MCP servers must be public https")
        return url

    def _post(self, msg):
        h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "User-Agent": "JeeG-mcp"}
        if self.bearer:
            h["Authorization"] = "Bearer " + self.bearer
        if self.session:
            h["Mcp-Session-Id"] = self.session
        r = urllib.request.Request(self.url, data=json.dumps(msg).encode(), headers=h, method="POST")

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None
        try:
            with urllib.request.build_opener(NoRedirect).open(r, timeout=self.timeout) as resp:
                self.session = resp.headers.get("Mcp-Session-Id") or self.session
                ctype = resp.headers.get("Content-Type", "")
                body = resp.read(MAX_REPLY + 1)
        except urllib.error.HTTPError as ex:
            if ex.code in (401, 403):
                raise MCPError("the server did not accept the login (HTTP %d). Log in with:  mcp login <name>" % ex.code)
            raise MCPError(f"the server answered HTTP {ex.code}")
        except (urllib.error.URLError, OSError) as ex:
            raise MCPError("could not reach the server: " + str(getattr(ex, "reason", ex)))
        if len(body) > MAX_REPLY:
            raise MCPError("the answer was too big")
        text = body.decode("utf-8", "replace")
        out = []
        if "text/event-stream" in ctype:
            for ev in text.replace("\r\n", "\n").split("\n\n"):
                data = "\n".join(x[5:].strip() for x in ev.split("\n") if x.startswith("data:"))
                if data.startswith("{") or data.startswith("["):
                    try:
                        out.append(json.loads(data))
                    except ValueError:
                        pass
        elif text.strip():
            try:
                j = json.loads(text)
            except ValueError:
                raise MCPError("the server did not answer in JSON")
            out = j if isinstance(j, list) else [j]
        return [m for m in out if isinstance(m, dict)]

    def request(self, method, params=None):
        self.n += 1
        mid = self.n
        for msg in self._post({"jsonrpc": "2.0", "id": mid, "method": method, "params": params or {}}):
            if msg.get("id") == mid:
                if "error" in msg:
                    raise MCPError(str(msg["error"].get("message", msg["error"]))[:300])
                return msg.get("result", {})
        raise MCPError("no answer to " + method)

    def close(self):
        pass


def open_server(target, timeout=60, env=None, bearer=""):
    """target is the saved command (a list), or a single https address for a web server."""
    if len(target) == 1 and target[0].lower().startswith(("http://", "https://")):
        return HTTPServer(target[0], timeout, bearer)
    return Server(target, timeout, env)
