"""Device-code login (RFC 8628): you approve on a web page, nothing is pasted. Not a task itself.
JeeG asks the service for a short code, shows it, and polls until you approve. The token goes to the same place a pasted one would.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from _conn import local_only_override

GRANT = "urn:ietf:params:oauth:grant-type:device_code"
DEFAULTS = {"github": {"code_url": "https://github.com/login/device/code", "token_url": "https://github.com/login/oauth/access_token", "scope": "repo read:user notifications"}}


def _post(url, data):
    r = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method="POST",
                               headers={"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "JeeG-apps"})

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    try:
        with urllib.request.build_opener(NoRedirect).open(r, timeout=15) as resp:
            return json.loads(resp.read(100_000).decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError as ex:                     # OAuth errors often come as 400 with a JSON body
        try:
            return json.loads(ex.read(100_000).decode("utf-8", "replace"))
        except ValueError:
            raise RuntimeError(f"The login service answered HTTP {ex.code}.")
    except (urllib.error.URLError, OSError, ValueError) as ex:
        raise RuntimeError("Could not reach the login service: " + str(getattr(ex, "reason", ex)))


def urls_for(app, code_url="", token_url=""):
    base = local_only_override("JEEG_DEVICE_BASE", "")          # tests only: this computer
    d = DEFAULTS.get(app, {})
    c, t = code_url or d.get("code_url", ""), token_url or d.get("token_url", "")
    if base:
        c, t = base + "/device/code", base + "/token"
    for u in (c, t):
        if not (u.startswith("https://") or (base and u.startswith(base))):
            return None, None
    return c, t


def login(app, client_id, code_url="", token_url="", scope="", out=print):
    """Returns the access token. Raises RuntimeError with a plain-words reason."""
    c, t = urls_for(app, code_url, token_url)
    if not c:
        raise RuntimeError("This app has no device login address. Give them:  code_url=https://... token_url=https://...")
    if not client_id:
        raise RuntimeError("Give the app's client id:  client_id=...  (create an OAuth app in the service's settings and tick 'Device flow')")
    scope = scope or DEFAULTS.get(app, {}).get("scope", "")
    r = _post(c, {"client_id": client_id, "scope": scope})
    if r.get("error") or not r.get("device_code"):
        raise RuntimeError("The service refused the login request: " + str(r.get("error_description") or r.get("error") or "no device code"))
    uri = str(r.get("verification_uri") or r.get("verification_url") or "")
    if not uri.startswith("https://") and not (os.environ.get("JEEG_DEVICE_BASE") and uri.startswith("http://127.0.0.1")):
        raise RuntimeError("The service gave a page address that is not https. Stopped.")
    out(f"Open  {uri}  and type this code:  {r.get('user_code', '?')}")
    interval = max(1, int(r.get("interval") or 5))
    if os.environ.get("JEEG_DEVICE_INTERVAL"):
        interval = max(0.05, min(interval, float(os.environ["JEEG_DEVICE_INTERVAL"])))
    end = time.time() + min(int(r.get("expires_in") or 900), 900)
    while time.time() < end:
        time.sleep(interval)
        p = _post(t, {"client_id": client_id, "device_code": r["device_code"], "grant_type": GRANT})
        e = p.get("error")
        if not e and p.get("access_token"):
            return str(p["access_token"])
        if e == "authorization_pending":
            continue
        if e == "slow_down":
            interval += 5 if interval >= 1 else 0.2
            continue
        if e == "access_denied":
            raise RuntimeError("You said no on the web page.")
        if e == "expired_token":
            raise RuntimeError("The code ran out. Start again.")
        raise RuntimeError("The login failed: " + str(p.get("error_description") or e or "no token"))
    raise RuntimeError("Waited 15 minutes and nobody approved. Start again.")
