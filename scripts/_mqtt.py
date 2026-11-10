"""A very small MQTT 3.1.1 client: connect, publish (QoS 0), subscribe and read. Standard library only. Not a task."""
import socket
import ssl
import struct
import time


def _len(n):
    out = bytearray()
    while True:
        b, n = n % 128, n // 128
        out.append(b | (128 if n else 0))
        if not n:
            return bytes(out)


def _str(s):
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def _read_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise OSError("the broker closed the connection")
        buf += chunk
    return buf


def _read_packet(sock):
    first = _read_exact(sock, 1)[0]
    mult, n = 1, 0
    for _ in range(4):
        b = _read_exact(sock, 1)[0]
        n += (b & 127) * mult
        if not b & 128:
            break
        mult *= 128
    if n > 1_000_000:
        raise OSError("packet too large")
    return first, _read_exact(sock, n) if n else b""


def connect(host, port=1883, user="", password="", tls=False, timeout=10, client_id="jeeg"):
    sock = socket.create_connection((host, port), timeout=timeout)
    if tls:
        sock = ssl.create_default_context().wrap_socket(sock, server_hostname=host)
    flags = 0x02 | (0x80 if user else 0) | (0x40 if user and password else 0)
    body = _str("MQTT") + bytes([4, flags]) + struct.pack(">H", 30) + _str(f"{client_id}-{int(time.time()) % 100000}")
    if user:
        body += _str(user) + (_str(password) if password else b"")
    sock.sendall(bytes([0x10]) + _len(len(body)) + body)
    first, data = _read_packet(sock)
    if first >> 4 != 2 or len(data) < 2 or data[1] != 0:
        codes = {1: "wrong protocol", 2: "client id refused", 3: "server unavailable", 4: "bad user name or password", 5: "not authorised"}
        raise OSError("the broker refused the connection: " + codes.get(data[1] if len(data) > 1 else 0, "unknown reason"))
    return sock


def publish(sock, topic, payload):
    body = _str(topic) + payload.encode("utf-8")
    sock.sendall(bytes([0x30]) + _len(len(body)) + body)


def subscribe(sock, topic):
    body = struct.pack(">H", 1) + _str(topic) + b"\x00"
    sock.sendall(bytes([0x82]) + _len(len(body)) + body)


def read_messages(sock, seconds, limit=50):
    """Yield (topic, text) until the time is up or `limit` messages arrived."""
    end = time.time() + seconds
    got = 0
    while time.time() < end and got < limit:
        sock.settimeout(max(0.2, min(2.0, end - time.time())))
        try:
            first, data = _read_packet(sock)
        except socket.timeout:
            continue
        if first >> 4 == 3 and len(data) >= 2:
            tl = struct.unpack(">H", data[:2])[0]
            topic = data[2:2 + tl].decode("utf-8", "replace")
            off = 2 + tl + (2 if (first >> 1) & 3 else 0)
            got += 1
            yield topic, data[off:].decode("utf-8", "replace")


def disconnect(sock):
    try:
        sock.sendall(b"\xe0\x00")
        sock.close()
    except OSError:
        pass
