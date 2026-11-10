"""Shared helpers for connector tasks (webhooks, devices, computers, mail ...). Standard library only. Not a task.
Saved settings live in your JeeG folder in conn_<name>.json, readable only by you. Secrets are never printed."""
import ipaddress
import json
import os
import re
import socket
from urllib.parse import urlparse

from _lib import data_dir, fail


def load_reg(name):
    p = data_dir() / f"conn_{name}.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save_reg(name, data):
    p = data_dir() / f"conn_{name}.json"
    tmp = p.with_suffix(".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, p)
    try:
        os.chmod(p, 0o600)
    except OSError:
        pass


def clean_name(s, what="name"):
    s = (s or "").strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_\-]{0,31}", s):
        fail(f"Use a short {what} of letters, numbers, - or _ (for example: home).")
    return s


def is_private_host(host):
    """True for this computer, home-network addresses and .local names (not the public internet)."""
    h = (host or "").strip("[]").lower()
    if h in {"localhost"} or h.endswith(".local") or h.endswith(".lan") or h.endswith(".home.arpa"):
        return True
    try:
        ip = ipaddress.ip_address(h)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        pass
    try:                                           # a plain host name: private only if every address it resolves to is private
        infos = {i[4][0] for i in socket.getaddrinfo(h, None)}
        return bool(infos) and all(ipaddress.ip_address(a.split("%")[0]).is_private or ipaddress.ip_address(a.split("%")[0]).is_loopback for a in infos)
    except (OSError, ValueError):
        return False


def need_private(host, what="device"):
    if not is_private_host(host):
        fail(f"{what} addresses must be on your own network (like 192.168.1.50), not '{host}'.")


def check_url(url, allow_private_http=True):
    """https anywhere; http only to this computer or your home network. Returns the parsed URL."""
    u = urlparse((url or "").strip())
    if u.scheme not in {"http", "https"} or not u.hostname or u.username or u.password:
        fail("Give a full web address starting with https://")
    if u.scheme == "http" and not (allow_private_http and is_private_host(u.hostname)):
        fail("Plain http is only allowed to this computer or your home network. Use https://")
    return u


def mask_url(url):
    u = urlparse(url)
    return f"{u.scheme}://{u.hostname}{(':' + str(u.port)) if u.port else ''}/..."


def ask_secret(prompt):
    """Read a secret without putting it on the command line: from a terminal prompt, or from piped input."""
    import getpass
    import sys
    try:
        if sys.stdin is not None and sys.stdin.isatty():
            return getpass.getpass(prompt).strip()
        return (sys.stdin.readline() if sys.stdin is not None else "").strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def words(text, drop=()):
    return [w for w in (text or "").split() if w.lower() not in drop]


def split_host(value, default_port):
    """'mail.example.com' or 'mail.example.com:993' -> (host, port)."""
    host, _, port = (value or "").partition(":")
    return host, int(port) if port.isdigit() else default_port


def local_only_override(env_name, default):
    """An address from an environment variable is accepted only if it points at this computer (used by tests); otherwise the real one."""
    v = os.environ.get(env_name, "")
    u = urlparse(v)
    if v and u.scheme == "http" and (u.hostname or "") in {"127.0.0.1", "localhost"}:
        return v.rstrip("/")
    return default
