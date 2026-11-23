# keywords: modbus write, write plc, set modbus register, modbus coil
# desc: Write to a Modbus TCP device (modbus write 192.168.1.60 coil 5 on, modbus write 192.168.1.60 holding 10 500). Asks first.
# category: network
# usage: modbus write <host[:502]> holding <address> <value> | modbus write <host[:502]> coil <address> on|off
# rawargs: full
# network: yes
# confirm: yes
# patterns: ^\s*modbus\s+write\b
# priority: 5
import re
from _lib import args_text, fail
import _modbus
t = re.sub(r"^\s*modbus\s*", "", args_text(), flags=re.I).strip()
op, host, port, kind, addr, unit, rest = _modbus.parse(t)
if op != "write" or not rest:
    fail("Usage: modbus write <host> holding <address> <value>   |   modbus write <host> coil <address> on|off")
print(_modbus.write(host, port, kind, addr, unit, rest[0]))
