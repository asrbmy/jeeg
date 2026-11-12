"""Network helpers: parse the neighbour/ARP table, pick the local /24, diagnose a connection, read printer lists. Not a task.
Pure functions where possible so they can be tested without a network."""
import ipaddress
import re
import socket
import subprocess
import sys

_MAC = r"[0-9a-fA-F]{1,2}(?:[:-][0-9a-fA-F]{1,2}){5}"


def norm_mac(m):
    return ":".join(p.zfill(2) for p in re.split(r"[:-]", m.lower()))


def parse_neighbours(text):
    """Lines of `ip neigh`, `arp -a` (mac, linux, windows) -> [(ip, mac)]. Skips incomplete and broadcast entries."""
    out, seen = [], set()
    for ln in (text or "").splitlines():
        m = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})\D.*?(" + _MAC + ")", ln)
        if not m:
            continue
        ip, mac = m.group(1), norm_mac(m.group(2))
        if mac in {"ff:ff:ff:ff:ff:ff", "00:00:00:00:00:00"} or mac.startswith("01:00:5e") or ip.endswith(".255"):
            continue
        if "FAILED" in ln or "INCOMPLETE" in ln.upper():
            continue
        try:
            a = ipaddress.ip_address(ip)
        except ValueError:
            continue
        if a.is_multicast or ip in seen:
            continue
        seen.add(ip)
        out.append((ip, mac))
    return sorted(out, key=lambda x: ipaddress.ip_address(x[0]))


def local_ip():
    """This computer's address on the local network, or None. A UDP 'connect' sends no data."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.0.2.1", 9))
        ip = s.getsockname()[0]
        return None if ip.startswith("127.") or ip == "0.0.0.0" else ip
    except OSError:
        return None
    finally:
        s.close()


def subnet_hosts(ip, max_hosts=254):
    """The other addresses on the same /24 as `ip`, only for private networks."""
    a = ipaddress.ip_address(ip)
    if not a.is_private or a.is_loopback:
        return []
    net = ipaddress.ip_network(ip + "/24", strict=False)
    return [str(h) for h in net.hosts() if str(h) != ip][:max_hosts]


def run_text(cmd, timeout=8):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, errors="replace", stdin=subprocess.DEVNULL)
        return (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.TimeoutExpired):
        return ""


def neighbour_table():
    if sys.platform.startswith("linux"):
        t = run_text(["ip", "neigh"])
        if t.strip():
            return t
    return run_text(["arp", "-a"])


def default_gateway():
    """Best-effort router address, or None."""
    try:
        if sys.platform.startswith("win"):
            t = run_text(["ipconfig"])
            m = re.search(r"Default Gateway[ .]*:\s*(\d{1,3}(?:\.\d{1,3}){3})", t)
        elif sys.platform == "darwin":
            m = re.search(r"gateway:\s*(\S+)", run_text(["route", "-n", "get", "default"]))
        else:
            m = re.search(r"default via (\S+)", run_text(["ip", "route", "show", "default"]))
        return m.group(1) if m and re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", m.group(1)) else None
    except AttributeError:
        return None


def diagnose(r):
    """r: dict(local_ip, gateway_ok (True/False/None), dns_ok, internet_ok, dns_ms, internet_ms).
    Returns (headline, [advice lines]). Pure."""
    tips = []
    if not r.get("local_ip"):
        return "This computer is not on a network.", ["Turn on Wi-Fi or plug in the cable, then run this again.",
                                                      "If Wi-Fi is on, forget the network and join it again."]
    if r.get("gateway_ok") is False:
        return "Your router does not answer.", ["Restart the router (off for 30 seconds), then wait two minutes.",
                                                "Move closer to the router, or try a cable to rule out Wi-Fi.",
                                                "If other devices also cannot connect, the problem is the router or the line."]
    if not r.get("internet_ok"):
        if r.get("dns_ok"):
            return "Names resolve but the internet is unreachable.", ["Your provider may be blocking traffic or a firewall/VPN is in the way. Turn the VPN off and retry."]
        return "The router works but nothing reaches the internet.", ["Your internet line or provider is probably down. Restart the router and modem.",
                                                                     "Check your provider's status page or call them if it stays down."]
    if not r.get("dns_ok"):
        return "The internet works but website names do not resolve (a DNS problem).",\
            ["Run:  flush dns", "Set your DNS to 1.1.1.1 and 8.8.8.8 in your network settings, or in the router."]
    slow = []
    if (r.get("internet_ms") or 0) > 150:
        slow.append("Round trips are slow (over 150 ms): weak Wi-Fi or a busy line.")
    if (r.get("dns_ms") or 0) > 400:
        slow.append("Name lookups are slow: try DNS 1.1.1.1 or 8.8.8.8.")
    if slow:
        return "You are online, but it is slow.", slow + ["Try a cable, move closer to the router, or pause big downloads.", "Measure it with:  check speed"]
    return "Everything looks fine.", tips


# ---------------------------------------------------------------- printers
def parse_lpstat(text):
    """`lpstat -p -d` -> ([(name, state)], default or None)."""
    printers, default = [], None
    for ln in (text or "").splitlines():
        m = re.match(r"printer\s+(\S+)\s+(is\s+)?(.*?)\.?\s*(?:since|\.|$)", ln)
        if m:
            state = "idle" if "idle" in ln else "disabled" if "disabled" in ln else "printing" if "now printing" in ln else m.group(3)[:40]
            printers.append((m.group(1), state))
        d = re.match(r"system default destination:\s*(\S+)", ln)
        if d:
            default = d.group(1)
    return printers, default


def parse_powershell_printers(text):
    """Output of `Get-Printer | ft -HideTableHeaders Name,PrinterStatus` -> [(name, state)]."""
    out = []
    for ln in (text or "").splitlines():
        ln = ln.strip()
        if not ln or set(ln) <= {"-", " "}:
            continue
        m = re.match(r"(.+?)\s{2,}(\S+)$", ln)
        out.append((m.group(1).strip(), m.group(2)) if m else (ln, "unknown"))
    return out
