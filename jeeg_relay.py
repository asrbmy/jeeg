"""A tiny relay so two JeeG computers behind home routers can reach each other. Run it on any server you control:

    jeeg link relay serve [PORT]        (default 8768)

The relay only passes bytes between two connections that asked for the same room. Everything is already encrypted end to
end between the two JeeG computers, so the relay (and whoever runs it) sees only who connected and how much data moved.
It cannot read, change or add messages, and it cannot pair people (pairing needs both people to compare a number).
Limits: 1000 rooms, one waiting computer per room, 10 minutes of waiting, 5 minutes with no traffic, 20 connections per address.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
import socket
import struct
import threading
import time

DEFAULT_RELAY_PORT = 8768
MAX_ROOMS = 1000
WAIT_SECONDS = 600
IDLE_SECONDS = 300
PER_IP = 20


def room_for(psk: bytes) -> str:
    """The room two paired computers meet in. Derived from their shared secret, so only they know it."""
    return hashlib.sha256(b"jeeg-room" + psk).hexdigest()[:32]


def pairing_room(code: str) -> str:
    return hashlib.sha256(b"jeeg-pair-room" + re.sub(r"[^A-Z0-9]", "", code.upper()).encode()).hexdigest()[:32]


def new_code() -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    c = "".join(secrets.choice(alphabet) for _ in range(10))
    return f"JG-{c[:5]}-{c[5:]}"


def _send(s, obj: dict) -> None:
    d = json.dumps(obj, separators=(",", ":")).encode()
    s.sendall(struct.pack(">I", len(d)) + d)


def _recv(s) -> dict:
    h = b""
    while len(h) < 4:
        b = s.recv(4 - len(h))
        if not b:
            raise OSError("closed")
        h += b
    n = struct.unpack(">I", h)[0]
    if n > 512:
        raise OSError("too big")
    d = b""
    while len(d) < n:
        b = s.recv(n - len(d))
        if not b:
            raise OSError("closed")
        d += b
    x = json.loads(d.decode("utf-8"))
    if not isinstance(x, dict):
        raise OSError("bad")
    return x


def _split(addr: str):
    host, _, port = addr.rpartition(":")
    if not host:
        return addr, DEFAULT_RELAY_PORT
    return host, int(port)


# ---------------------------------------------------------------- the relay itself
class Relay:
    def __init__(self, port: int = DEFAULT_RELAY_PORT, host: str = "0.0.0.0", out=print):
        self.port, self.host, self.out = port, host, out
        self.rooms: dict = {}                       # room -> (socket, time)
        self.lock = threading.Lock()
        self.per_ip: dict = {}
        self.stop_ev = threading.Event()
        self.ready = threading.Event()
        self.bytes_passed = 0

    def serve(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(64)
        s.settimeout(0.5)
        self.port = s.getsockname()[1]
        self.ready.set()
        while not self.stop_ev.is_set():
            try:
                c, a = s.accept()
            except socket.timeout:
                self._expire()
                continue
            except OSError:
                break
            with self.lock:
                n = self.per_ip.get(a[0], 0)
                if n >= PER_IP:
                    c.close()
                    continue
                self.per_ip[a[0]] = n + 1
            threading.Thread(target=self._one, args=(c, a[0]), daemon=True).start()
        s.close()

    def stop(self) -> None:
        self.stop_ev.set()

    def _expire(self) -> None:
        now = time.time()
        with self.lock:
            for r in [r for r, (s, t) in self.rooms.items() if now - t > WAIT_SECONDS]:
                try:
                    self.rooms.pop(r)[0].close()
                except OSError:
                    pass

    def _one(self, c, ip: str) -> None:
        keep = False
        try:
            c.settimeout(10)
            m = _recv(c)
            room = str(m.get("room", ""))
            if not re.fullmatch(r"[0-9a-f]{32}", room):
                return
            if m.get("t") == "wait":
                with self.lock:
                    if room in self.rooms or len(self.rooms) >= MAX_ROOMS:
                        _send(c, {"t": "busy"})
                        return
                    self.rooms[room] = (c, time.time())
                keep = True
                _send(c, {"t": "waiting"})
                return
            if m.get("t") == "join":
                with self.lock:
                    other = self.rooms.pop(room, (None, 0))[0]
                if other is None:
                    _send(c, {"t": "nobody"})
                    return
                keep = True
                try:
                    _send(other, {"t": "go"})
                    _send(c, {"t": "go"})
                except OSError:
                    other.close()
                    return
                threading.Thread(target=self._pipe, args=(other, c), daemon=True).start()
                self._pipe(c, other)
        except (OSError, ValueError):
            pass
        finally:
            with self.lock:
                self.per_ip[ip] = max(0, self.per_ip.get(ip, 1) - 1)
            if not keep:
                try:
                    c.close()
                except OSError:
                    pass

    def _pipe(self, a, b) -> None:
        a.settimeout(IDLE_SECONDS)
        try:
            while True:
                d = a.recv(65536)
                if not d:
                    break
                self.bytes_passed += len(d)
                b.sendall(d)
        except (OSError, socket.timeout):
            pass
        for s in (a, b):
            try:
                s.close()
            except OSError:
                pass


# ---------------------------------------------------------------- the computers using it
def join(relay: str, room: str, timeout: float = 8.0):
    host, port = _split(relay)
    s = socket.create_connection((host, port), timeout=timeout)
    s.settimeout(timeout)
    _send(s, {"t": "join", "room": room})
    r = _recv(s)
    if r.get("t") != "go":
        s.close()
        raise OSError("nobody is waiting there (is the other computer running  link listen  with this relay?)")
    s.settimeout(120)
    return s


def wait_in_room(relay: str, room: str, stop_ev, timeout: float = 8.0):
    """Park one connection in a room and wait until a computer joins. Returns the socket (or None when stopped/failed)."""
    host, port = _split(relay)
    s = socket.create_connection((host, port), timeout=timeout)
    _send(s, {"t": "wait", "room": room})
    r = _recv(s)
    if r.get("t") != "waiting":
        s.close()
        return None
    s.settimeout(1.0)
    while not stop_ev.is_set():
        try:
            m = _recv(s)
        except socket.timeout:
            continue
        except OSError:
            s.close()
            return None
        if m.get("t") == "go":
            s.settimeout(15)
            return s
    s.close()
    return None


def keep_parked(listener) -> None:
    """For a Listener started with a relay: keep one connection waiting per paired computer, and one for pairing."""
    rooms: dict = {}

    def park(room, pairing=False):
        while not listener.stop_ev.is_set():
            try:
                s = wait_in_room(listener.relay, room, listener.stop_ev)
            except (OSError, ValueError):
                time.sleep(5)
                continue
            if s is None:
                if listener.stop_ev.wait(3):
                    return
                continue
            listener.handle_socket(s, "relay")
            if pairing:
                return                                   # a pairing room is used once

    while not listener.stop_ev.is_set():
        if listener.pair_code and "pair" not in rooms:
            rooms["pair"] = True
            threading.Thread(target=park, args=(pairing_room(listener.pair_code), True), daemon=True).start()
        for pid, rec in listener.store.peers().items():
            if pid not in rooms and rec.get("level") != "block":
                rooms[pid] = True
                threading.Thread(target=park, args=(room_for(bytes.fromhex(rec["psk"])),), daemon=True).start()
        listener.stop_ev.wait(5)
