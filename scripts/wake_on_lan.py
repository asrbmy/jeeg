# keywords: wake on lan, wake pc, wake computer, wake up pc, wake my nas, magic packet, power on pc over network
# desc: Turn on a computer on your network with a Wake-on-LAN packet (wake add nas AA:BB:CC:DD:EE:FF, then: wake nas)
# category: network
# usage: wake <name | MAC address> | wake add <name> <MAC> | wake list | wake remove <name>
# rawargs: full
# network: yes
# patterns: ^\s*wake\b ;; \bwake\s+on\s+lan\b ;; \bmagic\s+packet\b
# priority: 3
import re, socket
from _lib import args_text, fail
from _conn import load_reg, save_reg, clean_name
t = re.sub(r"^\s*(?:wake\s+on\s+lan|wake\s+up|wake)\s*", "", args_text(), flags=re.I).strip()
parts = t.split()
reg = load_reg("wake")
MAC = re.compile(r"^[0-9a-f]{2}([:-])(?:[0-9a-f]{2}\1){4}[0-9a-f]{2}$", re.I)
if not parts or parts[0].lower() == "list":
    print("Saved computers:" if reg else "None saved. Add one:  wake add nas AA:BB:CC:DD:EE:FF")
    for k, v in sorted(reg.items()):
        print(f"  {k:<14} {v}")
    raise SystemExit(0)
if parts[0].lower() == "add":
    if len(parts) != 3 or not MAC.match(parts[2]):
        fail("Usage: wake add <name> <MAC address like AA:BB:CC:DD:EE:FF>")
    reg[clean_name(parts[1])] = parts[2].upper().replace("-", ":")
    save_reg("wake", reg)
    print(f"Saved. Wake it with:  wake {parts[1].lower()}")
    raise SystemExit(0)
if parts[0].lower() in {"remove", "delete"}:
    if reg.pop(clean_name(parts[1] if len(parts) > 1 else ""), None) is None:
        fail("No computer with that name.")
    save_reg("wake", reg)
    print("Removed.")
    raise SystemExit(0)
target = parts[0]
mac = target if MAC.match(target) else reg.get(target.lower())
if not mac:
    fail(f"'{target}' is not a MAC address or a saved name. Saved: {', '.join(sorted(reg)) or 'none'}")
raw = bytes.fromhex(re.sub(r"[:-]", "", mac))
packet = b"\xff" * 6 + raw * 16
sent = 0
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    for port in (9, 7):
        try:
            s.sendto(packet, ("255.255.255.255", port))
            sent += 1
        except OSError:
            pass
if not sent:
    fail("Could not send the packet (no network?).")
print(f"Wake-up packet sent to {mac.upper()}. It can take a minute. The computer must have Wake-on-LAN turned on in its BIOS and be on the same network.")
