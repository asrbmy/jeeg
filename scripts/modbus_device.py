# keywords: modbus, plc, modbus tcp, industrial controller, holding register, energy meter modbus
# desc: Read Modbus TCP devices on your network such as PLCs and energy meters (modbus read 192.168.1.60 holding 0 2). Writing is a separate task that asks first: modbus write ...
# category: network
# usage: modbus read <host[:502]> holding|input|coil|discrete <address> [count] [unit N]
# rawargs: full
# network: yes
# patterns: ^\s*modbus\b
# priority: 3
import re
from _lib import args_text, fail
import _modbus
t = re.sub(r"^\s*modbus\s*", "", args_text(), flags=re.I).strip()
if t.lower().startswith("write"):
    fail("Writing is a separate task that asks first. Say:  modbus write <host> holding|coil <address> <value>")
op, host, port, kind, addr, unit, rest = _modbus.parse(t)
if op != "read":
    fail("Use:  modbus read <host> holding|input|coil|discrete <address> [count]")
count = int(rest[0]) if rest and rest[0].isdigit() else 1
if not 1 <= count <= 100:
    fail("Read 1 to 100 values at a time.")
for i, v in enumerate(_modbus.read(host, port, kind, addr, unit, count)):
    print(f"  {kind} {addr + i}: {v}")
