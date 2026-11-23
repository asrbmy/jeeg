"""Where bridge rules get their messages from. Each start_* runs in its own thread and calls emit(topic, text, sender). Not a task."""
import json, os, re, socket, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def start(rule_name, src, emit, stop, log):
    k = src["kind"]
    fn = {"mqtt": _mqtt, "webhook": _webhook, "udp": _udp, "tcp": _tcp, "serial": _serial, "ws": _ws, "channel": _channel, "chat": _chat, "timer": _timer}[k]
    th = threading.Thread(target=_guard, args=(fn, rule_name, src, emit, stop, log), daemon=True)
    th.start()
    return th


def _guard(fn, name, src, emit, stop, log):
    """Keep a source alive: if it fails, say so once and retry every 10 seconds."""
    said = False
    while not stop.is_set():
        try:
            fn(name, src, emit, stop)
        except Exception as ex:                                  # a source must never take the bridge down
            if not said:
                log(f"[{name}] source problem: {str(ex)[:100]} (retrying)")
                said = True
        stop.wait(10)


def _mqtt(name, src, emit, stop):
    import _mqtt as m
    from _conn import load_reg
    b = load_reg("mqtt").get(src["broker"])
    if not b:
        raise RuntimeError(f"no MQTT broker named '{src['broker']}'")
    s = m.connect(b["host"], b["port"], b.get("user", ""), b.get("password", ""), b.get("tls", False), client_id="jeeg-br-" + name[:10])
    try:
        m.subscribe(s, src["topic"])
        while not stop.is_set():
            for tp, text in m.read_messages(s, 8, 50):
                emit(tp, text, "mqtt:" + src["broker"])
                if stop.is_set():
                    return
            s.sendall(b"\xc0\x00")                               # keep-alive ping
    finally:
        m.disconnect(s)


def _webhook(name, src, emit, stop):
    token = src["token"]

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _go(self, body=""):
            p = self.path.split("?", 1)
            if p[0].rstrip("/") != "/hook/" + token:
                self.send_response(404); self.end_headers()
                return
            if not body and len(p) > 1:
                m = re.search(r"(?:^|&)msg=([^&]*)", p[1])
                from urllib.parse import unquote_plus
                body = unquote_plus(m.group(1)) if m else ""
            emit("webhook", body[:4000], self.client_address[0])
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")

        def do_GET(self):
            self._go()

        def do_POST(self):
            n = min(int(self.headers.get("Content-Length") or 0), 4096)
            self._go(self.rfile.read(n).decode("utf-8", "replace"))
    srv = ThreadingHTTPServer(("0.0.0.0", src["port"]), H)
    srv.timeout = 0.5
    srv.daemon_threads = True
    try:
        while not stop.is_set():
            srv.handle_request()
    finally:
        srv.server_close()


def _udp(name, src, emit, stop):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", src["port"]))
        s.settimeout(0.5)
        while not stop.is_set():
            try:
                d, a = s.recvfrom(4000)
            except socket.timeout:
                continue
            emit("udp", d.decode("utf-8", "replace").strip(), a[0])


def _tcp(name, src, emit, stop):
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", src["port"]))
    srv.listen(8)
    srv.settimeout(0.5)

    def one(c, ip):
        try:
            c.settimeout(5)
            buf = b""
            while len(buf) < 4000 and not stop.is_set():
                d = c.recv(1000)
                if not d:
                    break
                buf += d
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    emit("tcp", line.decode("utf-8", "replace").strip(), ip)
            if buf.strip():
                emit("tcp", buf.decode("utf-8", "replace").strip(), ip)
        except OSError:
            pass
        finally:
            c.close()
    try:
        while not stop.is_set():
            try:
                c, a = srv.accept()
            except socket.timeout:
                continue
            threading.Thread(target=one, args=(c, a[0]), daemon=True).start()
    finally:
        srv.close()


def _serial(name, src, emit, stop):
    import serial
    with serial.Serial(src["port"], src.get("baud", 9600), timeout=1) as s:
        while not stop.is_set():
            line = s.readline().decode("utf-8", "replace").strip()
            if line:
                emit("serial", line, src["port"])


def _ws(name, src, emit, stop):
    import _ws as w
    s = w.connect(src["url"])
    try:
        s.settimeout(1)
        while not stop.is_set():
            try:
                m = w.recv_text(s)
            except socket.timeout:
                continue
            if m is None:
                raise RuntimeError("the server closed the connection")
            emit("ws", m, src["url"])
    finally:
        s.close()


def _channel(name, src, emit, stop):
    import jeeg_chan, jeeg_link
    from _lib import data_dir
    base = data_dir()
    me = jeeg_link.Store(base).identity()["name"]
    last = (jeeg_chan.read(base, src["name"], 1) or [{"id": ""}])[-1]["id"]
    while not stop.is_set():
        for m in jeeg_chan.read(base, src["name"], jeeg_chan.MAX_PULL, last):
            last = m["id"]
            if m.get("from") == me or str(m.get("from", "")).endswith("@" + me):
                continue                                         # your own posts do not trigger your own rules
            emit("channel:" + src["name"], m.get("text", ""), m.get("from", "?"))
        stop.wait(1)


def _chat(name, src, emit, stop):
    import jeeg_link
    from _lib import data_dir
    st = jeeg_link.Store(data_dir())
    key = lambda m: (m.get("t"), m.get("from"), m.get("text"))
    seen = {key(m) for m in st.inbox(1000)}
    while not stop.is_set():
        for m in st.inbox(1000):
            if key(m) not in seen:
                seen.add(key(m))
                emit("chat", m.get("text", ""), m.get("from", "?"))
        stop.wait(1)


def _timer(name, src, emit, stop):
    while not stop.wait(src["secs"]):
        emit("timer", "tick", "timer")
