"""Modbus TCP frames (standard library only). Not a task."""
import re, socket, struct
from _lib import fail
from _conn import need_private, split_host


def parse(t):
    """-> (op, host, port, kind, addr, unit, rest words) after the first word (read|write)."""
    unit = 1
    um = re.search(r"\bunit\s+(\d{1,3})\b", t, re.I)
    if um:
        unit = int(um.group(1))
        t = re.sub(r"\bunit\s+\d{1,3}\b", "", t, flags=re.I)
    w = t.split()
    if len(w) < 4:
        fail("Usage: modbus read <host> holding|input|coil|discrete <address> [count]   |   modbus write <host> holding <address> <value>   |   modbus write <host> coil <address> on|off")
    host, port = split_host(w[1], 502)
    need_private(host, "Modbus device")
    kind, addr = w[2].lower(), w[3]
    if not addr.isdigit() or int(addr) > 65535 or kind not in {"holding", "input", "coil", "discrete"}:
        fail("The address is a number up to 65535; the kind is holding, input, coil or discrete.")
    return w[0].lower(), host, port, kind, int(addr), unit, w[4:]


def exchange(host, port, unit, pdu):
    try:
        with socket.create_connection((host, port), timeout=5) as s:
            s.settimeout(5)
            s.sendall(struct.pack(">HHHB", 1, 0, len(pdu) + 1, unit) + pdu)
            h = b""
            while len(h) < 7:
                c = s.recv(7 - len(h))
                if not c:
                    fail("The device closed the connection.")
                h += c
            n = struct.unpack(">H", h[4:6])[0] - 1
            body = b""
            while len(body) < n:
                c = s.recv(n - len(body))
                if not c:
                    break
                body += c
            return body
    except OSError as ex:
        fail(f"Could not talk to the device: {ex}")


def check(body, fc):
    if not body or body[0] == fc | 0x80:
        fail(f"The device refused (Modbus error {body[1] if len(body) > 1 else '?'}).")
    if body[0] != fc:
        fail("Unexpected answer from the device.")


def read(host, port, kind, addr, unit, count):
    fc = {"coil": 1, "discrete": 2, "holding": 3, "input": 4}[kind]
    body = exchange(host, port, unit, struct.pack(">BHH", fc, addr, count))
    check(body, fc)
    if fc in {1, 2}:
        return [(body[2 + i // 8] >> (i % 8)) & 1 for i in range(count)]
    return list(struct.unpack(">" + "H" * (body[1] // 2), body[2:2 + body[1]]))


def write(host, port, kind, addr, unit, value):
    if kind in {"input", "discrete"}:
        fail("Input registers and discrete inputs are read-only.")
    if kind == "coil":
        v = value.lower()
        if v not in {"on", "off", "1", "0"}:
            fail("Coil value: on or off.")
        check(exchange(host, port, unit, struct.pack(">BHH", 5, addr, 0xFF00 if v in {"on", "1"} else 0)), 5)
        return f"Coil {addr} set {'on' if v in {'on', '1'} else 'off'}."
    if not value.isdigit() or int(value) > 65535:
        fail("Value: a whole number from 0 to 65535.")
    check(exchange(host, port, unit, struct.pack(">BHH", 6, addr, int(value))), 6)
    return f"Register {addr} set to {int(value)}."
