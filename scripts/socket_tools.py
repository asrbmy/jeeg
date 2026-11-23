# keywords: tcp, udp, websocket, ws, raw socket, send tcp message, send udp packet, listen udp
# desc: Talk to devices over plain TCP, UDP or WebSocket on your own network (tcp send 192.168.1.40:9000 hello, udp send 192.168.1.40:4210 on, udp listen 4210 10, ws send ws://192.168.1.5:81 hi)
# category: network
# usage: tcp send <host:port> <text> | tcp read <host:port> [seconds] | udp send <host:port> <text> | udp listen <port> [seconds] | ws send <ws://address> <text> | ws read <ws://address> [seconds]
# rawargs: full
# network: yes
# patterns: ^\s*(?:tcp|udp|ws|websockets?)\b
# priority: 3
import re, socket, sys, time
from _lib import args_text, fail
from _conn import need_private, split_host
import _ws
from urllib.parse import urlparse
t = args_text().strip()
w = t.split(None, 2)
if len(w) < 2:
    fail("Use:  tcp send|read | udp send|listen | ws send|read     (see the usage line)")
proto, cmd = w[0].lower().rstrip("s") if w[0].lower().startswith("websocket") else w[0].lower(), w[1].lower()
proto = "ws" if proto.startswith("websocket") else proto
rest = w[2] if len(w) > 2 else ""
secs_default = 5


def hp(v):
    host, port = split_host(v.split()[0] if v.split() else "", 0)
    if not host or not port or port > 65535:
        fail("Give the address as host:port, for example 192.168.1.40:9000")
    need_private(host, "Device")
    return host, port


def secs(s, d=secs_default):
    return max(1, min(60, int(s))) if str(s).isdigit() else d


if proto == "tcp":
    host, port = hp(rest)
    body = rest.split(None, 1)[1] if len(rest.split(None, 1)) > 1 else ""
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            if cmd == "send":
                if not body:
                    fail("Usage: tcp send <host:port> <text>")
                s.sendall(body[:2000].encode("utf-8") + b"\n")
                s.settimeout(1.5)
                try:
                    r = s.recv(2000).decode("utf-8", "replace").strip()
                except socket.timeout:
                    r = ""
                print("Sent." + (f" It answered: {r[:300]}" if r else ""))
            elif cmd == "read":
                s.settimeout(secs(body))
                end = time.time() + secs(body)
                got = b""
                while time.time() < end and len(got) < 4000:
                    try:
                        c = s.recv(1000)
                    except socket.timeout:
                        break
                    if not c:
                        break
                    got += c
                print(got.decode("utf-8", "replace").strip()[:2000] or "Nothing arrived.")
            else:
                fail("Use:  tcp send | tcp read")
    except OSError as ex:
        fail(f"Could not talk to {host}:{port}: {ex}")
elif proto == "udp":
    if cmd == "send":
        host, port = hp(rest)
        body = rest.split(None, 1)[1] if len(rest.split(None, 1)) > 1 else ""
        if not body:
            fail("Usage: udp send <host:port> <text>")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(1.5)
            try:
                s.sendto(body[:1400].encode("utf-8"), (host, port))
            except OSError as ex:
                fail(f"Could not send: {ex}")
            try:
                r, _ = s.recvfrom(2000)
                print("Sent. It answered: " + r.decode("utf-8", "replace").strip()[:300])
            except (socket.timeout, OSError):
                print("Sent.")
    elif cmd == "listen":
        p = rest.split()
        if not p or not p[0].isdigit() or not 1024 <= int(p[0]) <= 65535:
            fail("Usage: udp listen <port 1024-65535> [seconds]")
        end = time.time() + secs(p[1] if len(p) > 1 else "", 10)
        n = 0
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", int(p[0])))
            while time.time() < end and n < 50:
                s.settimeout(max(0.1, end - time.time()))
                try:
                    d, a = s.recvfrom(2000)
                except socket.timeout:
                    break
                n += 1
                print(f"  {a[0]}: {d.decode('utf-8', 'replace').strip()[:300]}")
        print(f"{n} packet(s)." if n else "Nothing arrived.")
    else:
        fail("Use:  udp send | udp listen")
elif proto == "ws":
    p = rest.split(None, 1)
    if not p:
        fail("Usage: ws send <ws://address> <text>   |   ws read <ws://address> [seconds]")
    u = urlparse(p[0])
    if u.scheme == "ws":
        need_private(u.hostname or "", "Device")
    elif u.scheme != "wss":
        fail("Use ws:// (your own network) or wss://")
    try:
        s = _ws.connect(p[0])
        s.settimeout(secs(p[1], 5) if cmd == "read" else 3)
        if cmd == "send":
            if len(p) < 2:
                fail("Usage: ws send <address> <text>")
            _ws.send_text(s, p[1][:4000])
            try:
                r = _ws.recv_text(s)
                print("Sent." + (f" It answered: {r[:300]}" if r else ""))
            except (socket.timeout, OSError):
                print("Sent.")
        elif cmd == "read":
            end = time.time() + secs(p[1] if len(p) > 1 else "", 5)
            n = 0
            while time.time() < end and n < 30:
                try:
                    m = _ws.recv_text(s)
                except (socket.timeout, OSError):
                    break
                if m is None:
                    break
                n += 1
                print("  " + m[:300].replace("\n", " "))
            print(f"{n} message(s)." if n else "Nothing arrived.")
        else:
            fail("Use:  ws send | ws read")
        s.close()
    except _ws.WsError as ex:
        fail(str(ex))
    except OSError as ex:
        fail(f"Could not connect: {ex}")
else:
    fail("Use:  tcp | udp | ws")
