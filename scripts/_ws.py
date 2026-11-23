"""A small WebSocket client (RFC 6455) using only the standard library. Text frames only. Not a task."""
import base64, os, socket, ssl, struct, hashlib
from urllib.parse import urlparse

GUID = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class WsError(OSError):
    pass


class Conn:
    """A socket plus the bytes read ahead of the handshake."""
    def __init__(self, sock, buf=b""):
        self.sock, self.buf = sock, buf

    def settimeout(self, t):
        self.sock.settimeout(t)

    def sendall(self, b):
        self.sock.sendall(b)

    def recv(self, n):
        return self.sock.recv(n)

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


def connect(url, timeout=8):
    u = urlparse(url)
    if u.scheme not in {"ws", "wss"} or not u.hostname:
        raise WsError("Use an address starting with ws:// or wss://")
    port = u.port or (443 if u.scheme == "wss" else 80)
    s = socket.create_connection((u.hostname, port), timeout=timeout)
    if u.scheme == "wss":
        s = ssl.create_default_context().wrap_socket(s, server_hostname=u.hostname)
    key = base64.b64encode(os.urandom(16)).decode()
    path = (u.path or "/") + (("?" + u.query) if u.query else "")
    s.sendall((f"GET {path} HTTP/1.1\r\nHost: {u.hostname}:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\nUser-Agent: JeeG\r\n\r\n").encode())
    head = b""
    while b"\r\n\r\n" not in head:
        c = s.recv(1024)
        if not c or len(head) > 16384:
            raise WsError("The server did not answer the WebSocket handshake.")
        head += c
    top, _, extra = head.partition(b"\r\n\r\n")
    lines = top.decode("latin-1").split("\r\n")
    if " 101 " not in lines[0] + " ":
        raise WsError("The server refused the WebSocket upgrade: " + lines[0][:60])
    want = base64.b64encode(hashlib.sha1(key.encode() + GUID, usedforsecurity=False).digest()).decode()
    if not any(l.lower().startswith("sec-websocket-accept:") and l.split(":", 1)[1].strip() == want for l in lines[1:]):
        raise WsError("The server's WebSocket answer was not valid.")
    return Conn(s, extra)


def send_text(s, text):
    b = text.encode("utf-8")
    mask = os.urandom(4)
    n = len(b)
    h = b"\x81" + (bytes([0x80 | n]) if n < 126 else b"\xfe" + struct.pack(">H", n) if n < 65536 else b"\xff" + struct.pack(">Q", n))
    s.sendall(h + mask + bytes(c ^ mask[i % 4] for i, c in enumerate(b)))


def _need(s, n):
    buf = s.buf
    while len(buf) < n:
        c = s.recv(65536)
        if not c:
            raise WsError("closed")
        buf += c
    s.buf = buf[n:]
    return buf[:n]


def recv_text(s, max_len=1_000_000):
    """Next text message, or None when the server closes. Pings are answered."""
    msg = b""
    while True:
        b1, b2 = _need(s, 2)
        op, ln = b1 & 0x0F, b2 & 0x7F
        if ln == 126:
            ln = struct.unpack(">H", _need(s, 2))[0]
        elif ln == 127:
            ln = struct.unpack(">Q", _need(s, 8))[0]
        if ln > max_len:
            raise WsError("message too large")
        mk = _need(s, 4) if b2 & 0x80 else None
        data = _need(s, ln) if ln else b""
        if mk:
            data = bytes(c ^ mk[i % 4] for i, c in enumerate(data))
        if op == 8:
            return None
        if op == 9:
            s.sendall(b"\x8a" + bytes([0x80 | len(data[:125])]) + b"\0\0\0\0" + data[:125])
            continue
        if op in {1, 0, 2}:
            msg += data
            if b1 & 0x80:
                return msg.decode("utf-8", "replace")
