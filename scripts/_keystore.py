"""Optional: keep linked-app logins in the system keychain instead of a file. Not a task itself.

  Linux    secret-tool (libsecret), the secret goes in on stdin
  macOS    security -i (Keychain), the command goes in on stdin, so the secret is never in a process list
  Windows  Credential Manager through ctypes (written from the documentation; not tested on a real Windows machine)

It is off until you say  keystore on  in a terminal. A login is moved only after JeeG read it back from the keychain
and got the same text. If anything fails, the login stays in its file as before. Only linked-app logins are covered
(not the older connect/github files).
"""
import os
import re
import shutil
import subprocess
import sys

SERVICE = "jeeg"


def backend():
    forced = os.environ.get("JEEG_TEST_KEYSTORE", "")
    if forced in {"linux", "mac"}:
        return forced
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "mac"
    return "linux"


def available():
    b = backend()
    if b == "windows":
        return True
    return shutil.which("secret-tool" if b == "linux" else "security") is not None


def _flag():
    from _store import load
    d = load("keystore.json", {})
    return isinstance(d, dict) and d.get("on") is True


def enabled():
    return _flag() and available()


def set_flag(on):
    from _store import save
    save("keystore.json", {"on": bool(on)})


def _run(argv, stdin=None):
    try:
        r = subprocess.run(argv, input=(stdin.encode("utf-8") if stdin is not None else None), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=15,
                           stdin=None if stdin is not None else subprocess.DEVNULL)
        return r.returncode, r.stdout.decode("utf-8", "replace")
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def _account(name):
    return "app-" + re.sub(r"[^a-z0-9_\-]", "", name.lower())


# ------------------------------------------------------------------ Windows (ctypes)
def _win(op, account, secret=""):
    import ctypes
    from ctypes import wintypes

    class CRED(ctypes.Structure):
        _fields_ = [("Flags", wintypes.DWORD), ("Type", wintypes.DWORD), ("TargetName", wintypes.LPWSTR), ("Comment", wintypes.LPWSTR),
                    ("LastWritten", wintypes.FILETIME), ("CredentialBlobSize", wintypes.DWORD), ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
                    ("Persist", wintypes.DWORD), ("AttributeCount", wintypes.DWORD), ("Attributes", ctypes.c_void_p), ("TargetAlias", wintypes.LPWSTR),
                    ("UserName", wintypes.LPWSTR)]
    adv = ctypes.WinDLL("advapi32", use_last_error=True)
    target = f"{SERVICE}/{account}"
    if op == "put":
        blob = secret.encode("utf-16-le")
        buf = (ctypes.c_ubyte * len(blob)).from_buffer_copy(blob)
        c = CRED()
        c.Type, c.TargetName, c.CredentialBlobSize, c.CredentialBlob, c.Persist, c.UserName = 1, target, len(blob), buf, 2, "jeeg"
        return bool(adv.CredWriteW(ctypes.byref(c), 0))
    if op == "get":
        p = ctypes.POINTER(CRED)()
        if not adv.CredReadW(target, 1, 0, ctypes.byref(p)):
            return ""
        try:
            return ctypes.string_at(p.contents.CredentialBlob, p.contents.CredentialBlobSize).decode("utf-16-le")
        finally:
            adv.CredFree(p)
    return bool(adv.CredDeleteW(target, 1, 0))


# ------------------------------------------------------------------ public
def get(name):
    a, b = _account(name), backend()
    try:
        if b == "windows":
            return _win("get", a) or ""
        if b == "linux":
            rc, out = _run(["secret-tool", "lookup", "service", SERVICE, "account", a])
        else:
            rc, out = _run(["security", "find-generic-password", "-s", SERVICE, "-a", a, "-w"])
            out = out.rstrip("\n")
        return out if rc == 0 else ""
    except Exception:
        return ""


def put(name, value):
    """True only when the secret was stored and read back identical."""
    if not value or re.search(r"[\x00-\x1f\x7f]", value):
        return False
    a, b = _account(name), backend()
    try:
        if b == "windows":
            ok = _win("put", a, value)
        elif b == "linux":
            rc, _ = _run(["secret-tool", "store", "--label=JeeG " + a, "service", SERVICE, "account", a], stdin=value)
            ok = rc == 0
        else:
            if '"' in value or "\\" in value:                      # cannot be quoted safely for security -i
                return False
            rc, _ = _run(["security", "-i"], stdin=f'add-generic-password -U -s {SERVICE} -a {a} -w "{value}"\n')
            ok = rc == 0
        return bool(ok) and get(name) == value
    except Exception:
        return False


def remove(name):
    a, b = _account(name), backend()
    try:
        if b == "windows":
            return bool(_win("del", a))
        if b == "linux":
            return _run(["secret-tool", "clear", "service", SERVICE, "account", a])[0] == 0
        return _run(["security", "delete-generic-password", "-s", SERVICE, "-a", a])[0] == 0
    except Exception:
        return False
