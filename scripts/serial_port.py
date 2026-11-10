# keywords: serial port, arduino, com port, usb serial, serial ports
# desc: List serial ports or send a line to a device such as an Arduino (serial ports, serial send COM3 hello). Needs pip install pyserial.
# category: hardware
# usage: serial ports | serial send <port> <text> [baud 9600] | serial read <port> [seconds]
# rawargs: full
# patterns: ^\s*serial\b ;; \barduino\b
# priority: 3
import re, time
from _lib import args_text, fail, need
t = re.sub(r"^\s*serial\s*", "", args_text(), flags=re.I).strip()
need("serial", "pyserial")
import serial
from serial.tools import list_ports
parts = t.split(None, 2)
cmd = parts[0].lower() if parts else "ports"
if cmd == "ports":
    ports = list(list_ports.comports())
    print("\n".join(f"  {p.device:<14} {p.description}" for p in ports) if ports else "No serial ports found.")
elif cmd in {"send", "read"}:
    if len(parts) < 2:
        fail("Usage: serial send <port> <text>   |   serial read <port> [seconds]")
    port = parts[1]
    if not re.fullmatch(r"(?:COM\d{1,3}|/dev/[A-Za-z0-9_./\-]{3,40}|cu\.[A-Za-z0-9_.\-]+)", port):
        fail("Give a port such as COM3 or /dev/ttyUSB0 (see:  serial ports).")
    rest = parts[2] if len(parts) > 2 else ""
    baud = 9600
    bm = re.search(r"\bbaud\s+(\d{3,7})\b", rest, re.I)
    if bm:
        baud = int(bm.group(1))
        rest = rest.replace(bm.group(0), " ").strip()
    try:
        with serial.Serial(port, baud, timeout=1) as s:
            if cmd == "send":
                s.write((rest[:500] + "\n").encode("utf-8"))
                time.sleep(0.4)
                reply = s.read(s.in_waiting or 1).decode("utf-8", "replace").strip()
                print("Sent." + (f" The device answered: {reply[:300]}" if reply else ""))
            else:
                secs = int(rest) if rest.strip().isdigit() else 3
                end = time.time() + max(1, min(30, secs))
                buf = b""
                while time.time() < end:
                    buf += s.read(s.in_waiting or 1)
                print(buf.decode("utf-8", "replace").strip()[:2000] or "Nothing received.")
    except (serial.SerialException, OSError) as ex:
        fail(f"Could not use {port}: {ex}")
else:
    fail("Use:  serial ports | send | read")
