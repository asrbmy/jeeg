"""A small MCP client for servers that speak JSON lines over stdin/stdout. Standard library only. Not a task."""
import json
import queue
import subprocess
import threading


class MCPError(Exception):
    pass


class Server:
    def __init__(self, argv, timeout=60):
        self.timeout = timeout
        try:
            self.p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace", bufsize=1)
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
