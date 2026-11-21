"""JeeG link: two JeeG computers talk to each other, safely.  (experimental)

    link name <my name>          how other people see you
    link listen [PORT] [relay HOST:PORT] [yes]     wait for other JeeGs (stay in this window)
    link find                    find JeeGs that are listening on your network
    link pair <host[:port]>      pair with one (both people compare a 6-digit number)
    link pair relay <host:port> <CODE>           pair through a relay, from anywhere
    link peers | link forget <name> | link level <name> <block|chat|safe|read|ask|full>
    link send <name> <message> | link file <name> <path> | link inbox | link ping <name>
    link run <name> <task in plain words>        run a task on that computer (what it allows)
    link relay serve [PORT]      run a relay for people who are behind routers (see jeeg_relay.py)

How it is protected (plain words):
  * Pairing is by a short number that BOTH people read out and compare (like Bluetooth). It is made so a person in the middle,
    or a relay, gets a different number and you see the mismatch.
  * After pairing the two computers share a secret key. Every later connection checks that key both ways and uses a fresh
    Diffie-Hellman exchange, so recorded traffic cannot be read later.
  * Messages are encrypted and authenticated (SHAKE-256 stream + HMAC-SHA256, numbered so nothing can be replayed).
  * What a paired computer may do on yours is the LEVEL you give it. block < chat < safe < read < ask < full.
    Settings, plugins, updates, autorun and this link command itself are never available remotely.
This is built from the Python standard library only (it has no TLS certificate maker). It has NOT had an independent
security review. For anything very sensitive use your own SSH or VPN as well.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import socket
import struct
import sys
import threading
import time
from pathlib import Path

DEFAULT_PORT = 8767
LEVELS = ["block", "chat", "safe", "read", "ask", "full"]
MODE = {"safe": "safe", "read": "read", "ask": "ask", "full": "god"}
MAX_RAW = 8 * 1024                  # handshake frames
MAX_FRAME = 2 * 1024 * 1024         # encrypted frames
MAX_FILE = 100 * 1024 * 1024
CHUNK = 192 * 1024
BAD_EXT = {".exe", ".msi", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".jar", ".scr", ".dll", ".com", ".sh", ".app", ".dmg", ".pkg", ".apk",
           ".lnk", ".reg", ".hta", ".msix", ".deb", ".rpm", ".appimage", ".py", ".command", ".desktop"}
P = int("FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF", 16)               # RFC 3526 group 14 (2048-bit safe prime)
G = 2
Q = (P - 1) // 2


# ------------------------------------------------------------------ small crypto helpers (standard library only)
def _hkdf(salt: bytes, ikm: bytes, info: bytes, n: int) -> bytes:
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    out, t, i = b"", b"", 1
    while len(out) < n:
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
        out += t
        i += 1
    return out[:n]


def _b(x: int) -> bytes:
    return x.to_bytes(256, "big")


def _new_dh():
    priv = secrets.randbelow(Q - 2) + 2
    return priv, pow(G, priv, P)


def _check_pub(y) -> int:
    if not isinstance(y, str) or not re.fullmatch(r"[0-9a-f]{1,512}", y):
        raise LinkError("bad key")
    v = int(y, 16)
    if not 2 <= v <= P - 2 or pow(v, Q, P) != 1:           # must be in the right subgroup (blocks small-subgroup tricks)
        raise LinkError("bad key")
    return v


def _hx(x: int) -> str:
    return f"{x:x}"


class LinkError(Exception):
    pass


# ------------------------------------------------------------------ framing
def _recv_exact(sock, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise LinkError("the other side closed the connection")
        buf += chunk
    return buf


def send_raw(sock, obj: dict) -> None:
    data = json.dumps(obj, separators=(",", ":")).encode()
    if len(data) > MAX_RAW:
        raise LinkError("message too large")
    sock.sendall(struct.pack(">I", len(data)) + data)


def recv_raw(sock) -> dict:
    n = struct.unpack(">I", _recv_exact(sock, 4))[0]
    if n > MAX_RAW:
        raise LinkError("message too large")
    try:
        d = json.loads(_recv_exact(sock, n).decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise LinkError("not a JeeG link message")
    if not isinstance(d, dict):
        raise LinkError("not a JeeG link message")
    return d


class Chan:
    """An encrypted, numbered, authenticated two-way channel."""

    def __init__(self, sock, kse: bytes, ksm: bytes, kre: bytes, krm: bytes):
        self.sock, self.kse, self.ksm, self.kre, self.krm = sock, kse, ksm, kre, krm
        self.ss = self.rs = 0
        self._lock = threading.Lock()

    @staticmethod
    def _xor(data: bytes, key: bytes, sb: bytes) -> bytes:
        if not data:
            return b""
        ks = hashlib.shake_256(key + sb).digest(len(data))
        return (int.from_bytes(data, "big") ^ int.from_bytes(ks, "big")).to_bytes(len(data), "big")

    def send(self, obj: dict) -> None:
        data = json.dumps(obj, separators=(",", ":")).encode()
        if len(data) > MAX_FRAME:
            raise LinkError("message too large")
        with self._lock:
            sb = struct.pack(">Q", self.ss)
            self.ss += 1
            ct = self._xor(data, self.kse, sb)
            tag = hmac.new(self.ksm, sb + ct, hashlib.sha256).digest()
            frame = sb + ct + tag
            self.sock.sendall(struct.pack(">I", len(frame)) + frame)

    def recv(self) -> dict:
        n = struct.unpack(">I", _recv_exact(self.sock, 4))[0]
        if n > MAX_FRAME + 64 or n < 40:
            raise LinkError("bad frame")
        frame = _recv_exact(self.sock, n)
        sb, ct, tag = frame[:8], frame[8:-32], frame[-32:]
        if not hmac.compare_digest(tag, hmac.new(self.krm, sb + ct, hashlib.sha256).digest()):
            raise LinkError("message failed its check (tampered, or the wrong key)")
        if struct.unpack(">Q", sb)[0] != self.rs:
            raise LinkError("message out of order (replay?)")
        self.rs += 1
        try:
            d = json.loads(self._xor(ct, self.kre, sb).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            raise LinkError("unreadable message")
        if not isinstance(d, dict):
            raise LinkError("unreadable message")
        return d


# ------------------------------------------------------------------ opening a session with someone already paired
def _transcript(idc: str, xc: int, nc: str, xs: int, ns: str) -> bytes:
    return bytes.fromhex(idc) + _b(xc) + bytes.fromhex(nc) + _b(xs) + bytes.fromhex(ns)


def _keys(psk: bytes, shared: int, tr: bytes):
    k = _hkdf(hashlib.sha256(tr).digest(), psk + _b(shared), b"jeeg-link-v1", 128)
    return k[0:32], k[32:64], k[64:96], k[96:128]          # c2s enc, c2s mac, s2c enc, s2c mac


def client_session(sock, my_id: str, psk: bytes) -> Chan:
    x, X = _new_dh()
    nc = secrets.token_hex(16)
    send_raw(sock, {"t": "hello", "v": 1, "id": my_id, "pub": _hx(X), "n": nc})
    r = recv_raw(sock)
    if r.get("t") != "hello2":
        raise LinkError("the other computer does not know this pairing (forgotten, or a different computer)")
    Ys = _check_pub(r.get("pub"))
    ns = str(r.get("n", ""))
    if not re.fullmatch(r"[0-9a-f]{32}", ns):
        raise LinkError("bad reply")
    tr = _transcript(my_id, X, nc, Ys, ns)
    if not hmac.compare_digest(str(r.get("mac", "")), hmac.new(psk, b"S" + tr, hashlib.sha256).hexdigest()):
        raise LinkError("the other computer could not prove who it is")
    send_raw(sock, {"t": "fin", "mac": hmac.new(psk, b"C" + tr, hashlib.sha256).hexdigest()})
    c_enc, c_mac, s_enc, s_mac = _keys(psk, pow(Ys, x, P), tr)
    return Chan(sock, c_enc, c_mac, s_enc, s_mac)


def server_session(sock, first: dict, find_psk) -> tuple:
    """first = the client's hello. find_psk(id) -> bytes or None. Returns (Chan, peer id)."""
    idc = str(first.get("id", ""))
    nc = str(first.get("n", ""))
    if not re.fullmatch(r"[0-9a-f]{32}", idc) or not re.fullmatch(r"[0-9a-f]{32}", nc):
        raise LinkError("bad hello")
    Xc = _check_pub(first.get("pub"))
    psk = find_psk(idc)
    if psk is None:
        send_raw(sock, {"t": "err", "m": "unknown"})
        raise LinkError("a computer that is not paired tried to connect")
    y, Y = _new_dh()
    ns = secrets.token_hex(16)
    tr = _transcript(idc, Xc, nc, Y, ns)
    send_raw(sock, {"t": "hello2", "pub": _hx(Y), "n": ns, "mac": hmac.new(psk, b"S" + tr, hashlib.sha256).hexdigest()})
    f = recv_raw(sock)
    if f.get("t") != "fin" or not hmac.compare_digest(str(f.get("mac", "")), hmac.new(psk, b"C" + tr, hashlib.sha256).hexdigest()):
        raise LinkError("the connecting computer could not prove who it is")
    c_enc, c_mac, s_enc, s_mac = _keys(psk, pow(Xc, y, P), tr)
    return Chan(sock, s_enc, s_mac, c_enc, c_mac), idc


# ------------------------------------------------------------------ pairing: both people compare a 6-digit number
def _clean_name(s) -> str:
    s = re.sub(r"[^\w .\-]", "", str(s or ""), flags=re.UNICODE).strip()[:32]
    return s or "unnamed"


def _sas(Xi, ni, Xr, nr, shared) -> str:
    d = hashlib.sha256(b"JEEG-SAS" + _b(Xi) + bytes.fromhex(ni) + _b(Xr) + bytes.fromhex(nr) + _b(shared)).digest()
    return f"{int.from_bytes(d[:8], 'big') % 1000000:06d}"


def _pair_keys(Xi, ni, Xr, nr, shared):
    tr = _b(Xi) + bytes.fromhex(ni) + _b(Xr) + bytes.fromhex(nr)
    k = _hkdf(hashlib.sha256(tr).digest(), _b(shared), b"jeeg-link-pair", 64)
    return k[:32], k[32:]                                   # psk, confirmation key


def pair_initiator(sock, my_name: str, my_id: str, confirm) -> tuple:
    """confirm(peer_name, sas_text) -> bool (does the number match on both screens?). Returns (peer id, peer name, psk)."""
    x, X = _new_dh()
    ni = secrets.token_hex(16)
    name = _clean_name(my_name)
    commit = hashlib.sha256(b"JEEG-COMMIT" + _b(X) + bytes.fromhex(ni) + name.encode() + bytes.fromhex(my_id)).hexdigest()
    send_raw(sock, {"t": "pair", "v": 1, "commit": commit})
    r = recv_raw(sock)
    if r.get("t") != "pair2":
        raise LinkError("that computer is not accepting pairing (start it with:  link listen)")
    Yr = _check_pub(r.get("pub"))
    nr, idr, peer = str(r.get("n", "")), str(r.get("id", "")), _clean_name(r.get("name"))
    if not (re.fullmatch(r"[0-9a-f]{32}", nr) and re.fullmatch(r"[0-9a-f]{32}", idr)):
        raise LinkError("bad reply")
    send_raw(sock, {"t": "pair3", "pub": _hx(X), "n": ni, "name": name, "id": my_id})
    shared = pow(Yr, x, P)
    sas = _sas(X, ni, Yr, nr, shared)
    psk, kc = _pair_keys(X, ni, Yr, nr, shared)
    ok = bool(confirm(peer, sas))
    send_raw(sock, {"t": "ok" if ok else "no", "mac": hmac.new(kc, b"I" + (b"1" if ok else b"0"), hashlib.sha256).hexdigest()})
    if not ok:
        raise LinkError("you said the numbers do not match, so nothing was saved")
    a = recv_raw(sock)
    if a.get("t") != "ok" or not hmac.compare_digest(str(a.get("mac", "")), hmac.new(kc, b"R1", hashlib.sha256).hexdigest()):
        raise LinkError("the other person did not confirm the number")
    return idr, peer, psk


def pair_responder(sock, first: dict, my_name: str, my_id: str, confirm) -> tuple:
    commit = str(first.get("commit", ""))
    if not re.fullmatch(r"[0-9a-f]{64}", commit):
        raise LinkError("bad pairing request")
    y, Y = _new_dh()
    nr = secrets.token_hex(16)
    send_raw(sock, {"t": "pair2", "pub": _hx(Y), "n": nr, "name": _clean_name(my_name), "id": my_id})
    r = recv_raw(sock)
    if r.get("t") != "pair3":
        raise LinkError("bad pairing request")
    Xi = _check_pub(r.get("pub"))
    ni, idi, peer = str(r.get("n", "")), str(r.get("id", "")), _clean_name(r.get("name"))
    if not (re.fullmatch(r"[0-9a-f]{32}", ni) and re.fullmatch(r"[0-9a-f]{32}", idi)):
        raise LinkError("bad pairing request")
    want = hashlib.sha256(b"JEEG-COMMIT" + _b(Xi) + bytes.fromhex(ni) + peer.encode() + bytes.fromhex(idi)).hexdigest()
    if not hmac.compare_digest(want, commit):
        raise LinkError("the pairing request was not what it first promised (someone may be interfering)")
    shared = pow(Xi, y, P)
    sas = _sas(Xi, ni, Y, nr, shared)
    psk, kc = _pair_keys(Xi, ni, Y, nr, shared)
    a = recv_raw(sock)
    if a.get("t") != "ok" or not hmac.compare_digest(str(a.get("mac", "")), hmac.new(kc, b"I1", hashlib.sha256).hexdigest()):
        raise LinkError("the other person did not confirm the number")
    ok = bool(confirm(peer, sas))
    send_raw(sock, {"t": "ok" if ok else "no", "mac": hmac.new(kc, b"R" + (b"1" if ok else b"0"), hashlib.sha256).hexdigest()})
    if not ok:
        raise LinkError("you said the numbers do not match, so nothing was saved")
    return idi, peer, psk


# ------------------------------------------------------------------ what is saved on this computer
class Store:
    def __init__(self, state):
        self.dir = Path(state) / "link"

    def _read(self, name, default):
        try:
            d = json.loads((self.dir / name).read_text(encoding="utf-8"))
            return d if isinstance(d, type(default)) else default
        except (OSError, ValueError):
            return default

    def _write(self, name, data) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        tmp = self.dir / (name + ".tmp")
        tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
        try:
            os.chmod(tmp, 0o600)                           # keys: only you
        except OSError:
            pass
        os.replace(tmp, self.dir / name)

    def identity(self) -> dict:
        d = self._read("identity.json", {})
        if not re.fullmatch(r"[0-9a-f]{32}", str(d.get("id", ""))):
            host = _clean_name(socket.gethostname())
            d = {"id": secrets.token_hex(16), "name": host}
            self._write("identity.json", d)
        return d

    def set_name(self, name: str) -> str:
        d = self.identity()
        d["name"] = _clean_name(name)
        self._write("identity.json", d)
        return d["name"]

    def peers(self) -> dict:
        d = self._read("peers.json", {})
        return {k: v for k, v in d.items() if re.fullmatch(r"[0-9a-f]{32}", k) and isinstance(v, dict) and re.fullmatch(r"[0-9a-f]{64}", str(v.get("psk", "")))}

    def save_peers(self, d: dict) -> None:
        self._write("peers.json", d)

    def add_peer(self, pid: str, name: str, psk: bytes, level: str, addr: str = "", relay: str = "") -> None:
        d = self.peers()
        old = d.get(pid, {})
        d[pid] = {"name": name, "psk": psk.hex(), "level": level, "addr": addr or old.get("addr", ""), "relay": relay or old.get("relay", ""), "since": int(time.time())}
        self.save_peers(d)

    def find(self, name: str):
        n = _clean_name(name).lower()
        hits = [(k, v) for k, v in self.peers().items() if v.get("name", "").lower() == n]
        return hits[0] if len(hits) == 1 else (None, None)

    def inbox_add(self, who: str, text: str) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        f = self.dir / "inbox.jsonl"
        lines = f.read_text(encoding="utf-8").splitlines()[-999:] if f.exists() else []
        lines.append(json.dumps({"t": int(time.time()), "from": who, "text": text[:2000]}))
        f.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def inbox(self, n: int = 20) -> list:
        f = self.dir / "inbox.jsonl"
        out = []
        for ln in (f.read_text(encoding="utf-8").splitlines()[-n:] if f.exists() else []):
            try:
                out.append(json.loads(ln))
            except ValueError:
                pass
        return out


def level_ok(level: str, need: str) -> bool:
    return level in LEVELS and LEVELS.index(level) >= LEVELS.index(need)


def received_dir() -> Path:
    d = Path.home() / "Downloads" / "JeeG received"
    d.mkdir(parents=True, exist_ok=True)
    return d


def safe_file_name(n: str) -> str:
    n = re.sub(r"[^\w.\- ]", "_", Path(str(n).replace("\\", "/")).name).strip(" .")[:100]
    return n or "file"


def _unique(p: Path) -> Path:
    if not p.exists():
        return p
    for i in range(1, 1000):
        q = p.with_name(f"{p.stem} ({i}){p.suffix}")
        if not q.exists():
            return q
    raise LinkError("too many files with that name")


# ------------------------------------------------------------------ the side that waits for others
class Listener:
    def __init__(self, state, port=DEFAULT_PORT, out=None, interactive=True, auto_yes=False, relay: str = "", host="0.0.0.0"):
        self.store = Store(state)
        self.state = state
        self.port, self.host = port, host
        self.out = out or (lambda s: print(s, flush=True))
        self.interactive = interactive
        self.auto_yes = auto_yes
        self.relay = relay
        self.stop_ev = threading.Event()
        self._prompt_lock = threading.Lock()
        self._run_lock = threading.Lock()
        self._sem = threading.Semaphore(16)
        self._bad: dict = {}
        self.pair_code = ""
        self.ready = threading.Event()
        self.sock = None

    # --- talking to the person at this computer
    def log(self, s: str) -> None:
        self.out(f"{time.strftime('%H:%M:%S')}  {s}")

    def prompt(self, text: str, default: str = "") -> str:
        with self._prompt_lock:
            if not self.interactive:
                return default
            try:
                return input(text + " ").strip().lower()
            except (EOFError, OSError):
                return default

    def _confirm_pair(self, peer: str, sas: str):
        self.out(f"\n  Pairing request from '{peer}'.\n  The number on BOTH screens must be:   {sas}\n")
        ok = self.prompt("  Do both screens show exactly this number? [y/N]") in {"y", "yes"}
        if not ok:
            return False
        self.out("  What may this computer do on yours?  chat (messages and files only), safe, read, ask (you approve each), full (any task)")
        lv = self.prompt("  Level [chat]:", "chat") or "chat"
        self._level_for_new = lv if lv in LEVELS and lv != "block" else "chat"
        return True

    # --- rules against guessing and flooding
    def _blocked(self, ip: str) -> bool:
        t = self._bad.get(ip)
        return bool(t and t[0] >= 5 and time.time() - t[1] < 300)

    def _fail(self, ip: str) -> None:
        n, t = self._bad.get(ip, (0, 0))
        self._bad[ip] = (1 if time.time() - t > 60 else n + 1, time.time())

    # --- connections
    def serve(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(16)
        s.settimeout(0.5)
        self.sock = s
        self.port = s.getsockname()[1]
        threading.Thread(target=self._discovery, daemon=True).start()
        if self.relay:
            threading.Thread(target=self._relay_loop, daemon=True).start()
        self.ready.set()
        while not self.stop_ev.is_set():
            try:
                c, a = s.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            self._start(c, a[0])
        try:
            s.close()
        except OSError:
            pass

    def _start(self, c, ip: str) -> None:
        if self._blocked(ip) or not self._sem.acquire(blocking=False):
            c.close()
            return
        threading.Thread(target=self._handle, args=(c, ip), daemon=True).start()

    def stop(self) -> None:
        self.stop_ev.set()

    def _discovery(self) -> None:
        try:
            u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            u.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            u.bind((self.host, DEFAULT_PORT))
            u.settimeout(0.5)
        except OSError:
            return
        while not self.stop_ev.is_set():
            try:
                data, a = u.recvfrom(64)
            except socket.timeout:
                continue
            except OSError:
                break
            if data == b"JEEG-LINK?":
                me = self.store.identity()
                try:
                    u.sendto(json.dumps({"name": me["name"], "port": self.port, "fp": me["id"][:8]}).encode(), a)
                except OSError:
                    pass
        u.close()

    def _relay_loop(self) -> None:
        import jeeg_relay
        jeeg_relay.keep_parked(self)

    def handle_socket(self, c, ip: str = "relay") -> None:
        """Used by the relay code: a connection that arrived through the relay."""
        if self._sem.acquire(blocking=False):
            threading.Thread(target=self._handle, args=(c, ip), daemon=True).start()
        else:
            c.close()

    def _handle(self, c, ip: str) -> None:
        peer_name = "?"
        try:
            c.settimeout(15)
            first = recv_raw(c)
            t = first.get("t")
            if t == "hello":
                peers = self.store.peers()
                chan, pid = server_session(c, first, lambda i: bytes.fromhex(peers[i]["psk"]) if i in peers and peers[i].get("level") != "block" else None)
                rec = peers[pid]
                peer_name = rec.get("name", "?")
                c.settimeout(120)
                self._session(chan, pid, rec)
            elif t == "pair":
                if not self.interactive:
                    send_raw(c, {"t": "err", "m": "pairing needs a person at this computer"})
                    return
                if not self._prompt_lock.acquire(blocking=False):
                    send_raw(c, {"t": "err", "m": "busy"})
                    return
                self._prompt_lock.release()
                c.settimeout(180)
                me = self.store.identity()
                self._level_for_new = "chat"
                pid, name, psk = pair_responder(c, first, me["name"], me["id"], self._confirm_pair)
                self.store.add_peer(pid, name, psk, self._level_for_new, addr=(f"{ip}:{DEFAULT_PORT}" if ip != "relay" else ""), relay=(self.relay if ip == "relay" else ""))
                self.log(f"Paired with '{name}' (level {self._level_for_new}). Change it any time:  link level {name} <level>")
            else:
                send_raw(c, {"t": "err", "m": "not a JeeG link"})
        except (LinkError, OSError, ValueError, KeyError) as ex:
            if "closed the connection" not in str(ex):
                self._fail(ip)
            if not isinstance(ex, (socket.timeout, TimeoutError)):
                self.log(f"Refused a connection ({str(ex)[:90]})")
        finally:
            try:
                c.close()
            except OSError:
                pass
            self._sem.release()

    # --- what a paired computer can ask
    def _session(self, chan: Chan, pid: str, rec: dict) -> None:
        name = rec.get("name", "?")
        count = 0
        while not self.stop_ev.is_set() and count < 500:
            try:
                m = chan.recv()
            except (LinkError, OSError, socket.timeout):
                return
            count += 1
            level = self.store.peers().get(pid, {}).get("level", "block")   # re-read: `link level` takes effect at once
            t = m.get("t")
            if level == "block":
                chan.send({"t": "err", "m": "blocked"})
                return
            if t == "ping":
                chan.send({"t": "pong", "name": self.store.identity()["name"], "level": level})
            elif t == "chat":
                text = str(m.get("text", ""))[:2000]
                self.store.inbox_add(name, text)
                self.log(f"Message from {name}: {text[:200]}")
                chan.send({"t": "ok"})
            elif t == "file":
                self._receive_file(chan, name, m)
            elif t == "run":
                chan.send(self._run(name, level, str(m.get("q", ""))))
            elif t == "bye":
                return
            else:
                chan.send({"t": "err", "m": "unknown request"})

    def _receive_file(self, chan: Chan, who: str, m: dict) -> None:
        n = safe_file_name(m.get("name", ""))
        size = m.get("size")
        if not isinstance(size, int) or not 0 <= size <= MAX_FILE:
            chan.send({"t": "err", "m": f"files over {MAX_FILE // 1048576} MB are not accepted"})
            return
        if Path(n).suffix.lower() in BAD_EXT:
            chan.send({"t": "err", "m": "programs and scripts are not accepted"})
            return
        dest = _unique(received_dir() / n)
        part = dest.with_name(dest.name + ".part")
        chan.send({"t": "ok"})
        got, h = 0, hashlib.sha256()
        try:
            with open(part, "wb") as fh:
                while True:
                    c = chan.recv()
                    if c.get("t") == "chunk":
                        b = base64.b64decode(str(c.get("d", "")), validate=True)
                        got += len(b)
                        if got > size:
                            raise LinkError("more data than announced")
                        h.update(b)
                        fh.write(b)
                    elif c.get("t") == "end":
                        break
                    else:
                        raise LinkError("unexpected message during a file")
            if got != size or not hmac.compare_digest(h.hexdigest(), str(c.get("sha", ""))):
                raise LinkError("the file did not arrive intact")
            os.replace(part, dest)
            self.log(f"File from {who}: {dest}")
            chan.send({"t": "done", "saved": dest.name})
        except (LinkError, ValueError, OSError) as ex:
            try:
                part.unlink()
            except OSError:
                pass
            try:
                chan.send({"t": "err", "m": str(ex)[:100]})
            except OSError:
                pass

    def _approver(self, who: str, level: str):
        import jeeg_remote

        def ask(text: str) -> bool:
            if self.auto_yes and level == "full":
                return True
            return self.prompt(f"\n  {who} wants this computer to: {text}\n  Allow? [y/N]") in {"y", "yes"}
        return jeeg_remote.Approver(ask_fn=ask)

    def _run(self, who: str, level: str, q: str) -> dict:
        if not level_ok(level, "safe"):
            return {"t": "result", "text": f"Your level here is '{level}': messages and files only. Ask the owner for more.", "err": True}
        try:
            import jeeg_policy
            if jeeg_policy.load().get("block_link"):
                return {"t": "result", "text": "Your administrator has turned off JeeG link on this computer.", "err": True}
        except ImportError:
            pass
        first = q.split(None, 1)[0].lower() if q.split() else ""
        import jeeg_remote
        if first in ("link", "update", "upgrade", "autorun", "kit", "audit", "policy", "gui", "window", "windows", "desktop", "plugin", "plugins", "allow", "deny", "pack", "connect", "install"):
            return {"t": "result", "text": f"'{first}' can only be used at this computer itself.", "err": True}
        with self._run_lock:                                  # one remote task at a time: it also sets who is asking
            os.environ["JEEG_VIA_PEER"] = who
            try:
                self.log(f"{who} ({level}) runs: {q[:120]}")
                text, err = jeeg_remote.run_for_ai(q, MODE.get(level, "safe"), self._approver(who, level), self.state, log=lambda s: None, source="peer")
            finally:
                os.environ.pop("JEEG_VIA_PEER", None)
                os.environ.pop("JEEG_VIA_AI", None)
        return {"t": "result", "text": text[:100000], "err": bool(err)}


# ------------------------------------------------------------------ the side that calls
def _tcp(addr: str, timeout: float = 8.0):
    host, _, port = addr.rpartition(":")
    if not host:
        host, port = addr, str(DEFAULT_PORT)
    s = socket.create_connection((host, int(port)), timeout=timeout)
    s.settimeout(timeout)
    return s


def open_session(store: Store, pid: str, rec: dict, timeout: float = 8.0) -> Chan:
    me = store.identity()
    errs = []
    sock = None
    if rec.get("addr"):
        try:
            sock = _tcp(rec["addr"], timeout)
        except (OSError, ValueError) as ex:
            errs.append(f"direct: {ex}")
    if sock is None and rec.get("relay"):
        try:
            import jeeg_relay
            sock = jeeg_relay.join(rec["relay"], jeeg_relay.room_for(bytes.fromhex(rec["psk"])), timeout)
        except (OSError, ValueError, LinkError) as ex:
            errs.append(f"relay: {ex}")
    if sock is None:
        raise LinkError("could not reach " + rec.get("name", "that computer") + (" (" + "; ".join(errs)[:150] + ")" if errs else " (no address saved)"))
    try:
        sock.settimeout(120)
        return client_session(sock, me["id"], bytes.fromhex(rec["psk"]))
    except Exception:
        sock.close()
        raise


def ask(chan: Chan, msg: dict) -> dict:
    chan.send(msg)
    return chan.recv()


def send_file(chan: Chan, path: Path) -> str:
    size = path.stat().st_size
    if size > MAX_FILE:
        raise LinkError(f"files over {MAX_FILE // 1048576} MB are not sent")
    if path.suffix.lower() in BAD_EXT:
        raise LinkError("programs and scripts are not sent")
    r = ask(chan, {"t": "file", "name": path.name, "size": size})
    if r.get("t") != "ok":
        raise LinkError(r.get("m", "refused"))
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(CHUNK)
            if not b:
                break
            h.update(b)
            chan.send({"t": "chunk", "d": base64.b64encode(b).decode()})
    r = ask(chan, {"t": "end", "sha": h.hexdigest()})
    if r.get("t") != "done":
        raise LinkError(r.get("m", "failed"))
    return str(r.get("saved", ""))


def find_on_lan(wait: float = 2.0) -> list:
    out, seen = [], set()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(0.4)
    for target in ("255.255.255.255", "127.0.0.1"):
        try:
            s.sendto(b"JEEG-LINK?", (target, DEFAULT_PORT))
        except OSError:
            pass
    end = time.time() + wait
    while time.time() < end and len(out) < 50:
        try:
            data, a = s.recvfrom(512)
            d = json.loads(data.decode("utf-8", "replace"))
            key = (a[0], d.get("port"))
            if key not in seen and isinstance(d.get("port"), int):
                seen.add(key)
                out.append({"name": _clean_name(d.get("name")), "addr": f"{a[0]}:{d['port']}", "fp": str(d.get("fp", ""))[:8]})
        except (socket.timeout, ValueError, OSError):
            continue
    s.close()
    return out


# ------------------------------------------------------------------ the `link` command
USAGE = """link name <your name>                 how others see you
link listen [PORT] [relay HOST:PORT] [yes]   wait for other JeeGs (leave this window open)
link find                             JeeGs listening on your network
link pair <host[:port]>               pair (both people compare a 6-digit number)
link pair relay <host:port> <CODE>    pair through a relay, from anywhere
link peers | link forget <name> | link level <name> <block|chat|safe|read|ask|full>
link send <name> <message> | link file <name> <path> | link inbox | link ping <name>
link run <name> <task in plain words>
link relay serve [PORT]               run a relay (for people behind routers)"""


def cli(q: str, state, interactive: bool = True, out=print, inp=input) -> int:
    store = Store(state)
    words = q.strip().split()
    if words and words[0].lower() == "link":
        words = words[1:]
    sub = words[0].lower() if words else "status"
    rest = words[1:]
    try:
        import jeeg_policy
        if jeeg_policy.load().get("block_link") and sub != "status":
            out("Your administrator has turned off JeeG link on this computer.")
            return 1
    except ImportError:
        pass
    me = store.identity()

    def peer_or_fail(n):
        pid, rec = store.find(n)
        if not pid:
            out("No paired computer is called '%s'. See:  link peers" % n if n else "Say who:  link peers")
            return None, None
        return pid, rec

    try:
        if sub == "status":
            ps = store.peers()
            out(f"This computer is '{me['name']}' (id {me['id'][:8]}). {len(ps)} paired computer(s). Say:  link peers   or   link listen")
            return 0
        if sub == "help":
            out(USAGE)
            return 0
        if sub == "name":
            if not rest:
                out("Say: link name <your name>")
                return 1
            out(f"You are now '{store.set_name(' '.join(rest))}'.")
            return 0
        if sub == "find":
            found = find_on_lan()
            if not found:
                out("No JeeG is listening on this network (the other computer needs:  link listen).")
                return 1
            for f in found:
                out(f"  {f['name']:<20}{f['addr']:<22}id {f['fp']}")
            out("Pair with one:  link pair <address>")
            return 0
        if sub == "peers":
            ps = store.peers()
            if not ps:
                out("No paired computers yet. Try:  link find   then   link pair <address>")
                return 0
            for pid, r in sorted(ps.items(), key=lambda x: x[1].get("name", "")):
                out(f"  {r.get('name', '?'):<20}level {r.get('level', '?'):<6} {r.get('addr') or '-':<22}{('relay ' + r['relay']) if r.get('relay') else ''}")
            out("'level' is what THEY may do on THIS computer.")
            return 0
        if sub == "forget":
            pid, rec = peer_or_fail(" ".join(rest))
            if not pid:
                return 1
            d = store.peers()
            d.pop(pid, None)
            store.save_peers(d)
            out(f"Forgot {rec['name']}. They can no longer connect here.")
            return 0
        if sub == "level":
            if len(rest) < 2 or rest[-1].lower() not in LEVELS:
                out("Say: link level <name> <" + "|".join(LEVELS) + ">")
                return 1
            pid, rec = peer_or_fail(" ".join(rest[:-1]))
            if not pid:
                return 1
            d = store.peers()
            d[pid]["level"] = rest[-1].lower()
            store.save_peers(d)
            out(f"{rec['name']} may now do: {rest[-1].lower()}." + (" (any task; things that change or delete still ask you unless you started  link listen yes)" if rest[-1].lower() == "full" else ""))
            return 0
        if sub == "inbox":
            msgs = store.inbox(20)
            if not msgs:
                out("No messages.")
            for m in msgs:
                out(f"  {time.strftime('%d %b %H:%M', time.localtime(m['t']))}  {m['from']}: {m['text']}")
            return 0
        if sub == "listen":
            return _cmd_listen(store, rest, interactive, out)
        if sub == "pair":
            return _cmd_pair(store, rest, interactive, out, inp)
        if sub == "relay":
            if rest[:1] == ["serve"]:
                import jeeg_relay
                port = int(rest[1]) if len(rest) > 1 and rest[1].isdigit() else jeeg_relay.DEFAULT_RELAY_PORT
                r = jeeg_relay.Relay(port, out=out)
                out(f"Relay running on port {port}. It only passes encrypted bytes between two JeeG computers. Ctrl+C stops it.")
                try:
                    r.serve()
                except KeyboardInterrupt:
                    pass
                return 0
            out("Say: link relay serve [PORT]")
            return 1
        if sub in {"send", "file", "run", "ping"}:
            if not rest:
                out(USAGE.split("\n")[6] if sub != "run" else "Say: link run <name> <task>")
                return 1
            # the name may be several words: take the longest prefix that matches a paired computer
            pid = rec = None
            for k in range(min(3, len(rest)), 0, -1):
                pid, rec = store.find(" ".join(rest[:k]))
                if pid:
                    arg = " ".join(rest[k:])
                    break
            if not pid:
                out("No paired computer is called '%s'. See:  link peers" % rest[0])
                return 1
            if sub != "ping" and not arg:
                out(f"Say what to {sub}:  link {sub} {rec['name']} ...")
                return 1
            chan = open_session(store, pid, rec)
            try:
                if sub == "ping":
                    r = ask(chan, {"t": "ping"})
                    out(f"{r.get('name', rec['name'])} answered. It lets you: {r.get('level', '?')}.")
                elif sub == "send":
                    r = ask(chan, {"t": "chat", "text": arg[:2000]})
                    out("Delivered." if r.get("t") == "ok" else f"Not delivered: {r.get('m', '?')}")
                    return 0 if r.get("t") == "ok" else 1
                elif sub == "file":
                    p = Path(arg.strip("\"'")).expanduser()
                    if not p.is_file():
                        out(f"No such file: {p}")
                        return 1
                    out(f"Sent as {send_file(chan, p)}.")
                else:
                    r = ask(chan, {"t": "run", "q": arg[:500]})
                    out(str(r.get("text", r.get("m", "(no answer)"))))
                    return 1 if r.get("err") or r.get("t") == "err" else 0
                return 0
            finally:
                try:
                    chan.send({"t": "bye"})
                except (OSError, LinkError):
                    pass
                chan.sock.close()
        out("Not a link command. " + "\n" + USAGE)
        return 1
    except LinkError as ex:
        out(f"Link problem: {ex}")
        return 1
    except (OSError, ValueError) as ex:
        out(f"Link problem: {getattr(ex, 'strerror', None) or ex}")
        return 1


def _cmd_listen(store, rest, interactive, out) -> int:
    port, relay, auto = DEFAULT_PORT, "", False
    i = 0
    while i < len(rest):
        w = rest[i].lower()
        if w.isdigit():
            port = int(w)
        elif w == "relay" and i + 1 < len(rest):
            relay = rest[i + 1]
            i += 1
        elif w in {"yes", "approve"}:
            auto = True
        else:
            out("Say: link listen [PORT] [relay HOST:PORT] [yes]")
            return 1
        i += 1
    ln = Listener(store.dir.parent, port=port, out=out, interactive=interactive, auto_yes=auto, relay=relay)
    if relay:
        import jeeg_relay
        ln.pair_code = jeeg_relay.new_code()
    try:
        t = threading.Thread(target=ln.serve, daemon=True)
        t.start()
        if not ln.ready.wait(5):
            out("Could not start listening (is the port already in use?).")
            return 1
    except OSError as ex:
        out(f"Could not start listening: {ex}")
        return 1
    me = store.identity()
    out(f"Listening as '{me['name']}' on port {ln.port}. Other JeeGs on your network can find you with:  link find")
    if relay:
        out(f"Relay: {relay}.  To pair from anywhere, the other person runs:  link pair relay {relay} {ln.pair_code}")
    if auto:
        out("WARNING: 'yes' means paired computers at level 'full' can run things that change or delete, without asking you.")
    out("Leave this window open. Ctrl+C stops listening.")
    try:
        while t.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        ln.stop()
        out("Stopped listening.")
    return 0


def _cmd_pair(store, rest, interactive, out, inp) -> int:
    if not interactive:
        out("Pairing needs a person at the keyboard (both people compare a number). Run it in a terminal.")
        return 1
    me = store.identity()
    chosen = {"level": "chat"}

    def confirm(peer: str, sas: str) -> bool:
        out(f"\n  Pairing with '{peer}'.\n  The number on BOTH screens must be:   {sas}\n")
        if inp("  Do both screens show exactly this number? [y/N] ").strip().lower() not in {"y", "yes"}:
            return False
        out("  What may that computer do on yours?  chat (messages and files only), safe, read, ask (you approve each), full (any task)")
        lv = inp("  Level [chat]: ").strip().lower() or "chat"
        chosen["level"] = lv if lv in LEVELS and lv != "block" else "chat"
        return True

    relay = addr = ""
    if rest[:1] == ["relay"]:
        if len(rest) < 3:
            out("Say: link pair relay <host:port> <CODE>")
            return 1
        import jeeg_relay
        relay = rest[1]
        sock = jeeg_relay.join(relay, jeeg_relay.pairing_room(rest[2]), 10)
    elif rest:
        addr = rest[0] if ":" in rest[0] else f"{rest[0]}:{DEFAULT_PORT}"
        sock = _tcp(addr, 10)
    else:
        out("Say: link pair <host[:port]>      (find one with:  link find)")
        return 1
    try:
        sock.settimeout(180)
        pid, name, psk = pair_initiator(sock, me["name"], me["id"], confirm)
    finally:
        sock.close()
    store.add_peer(pid, name, psk, chosen["level"], addr=addr, relay=relay)
    out(f"Paired with '{name}'. They may do: {chosen['level']} on your computer. Try:  link ping {name}")
    return 0
