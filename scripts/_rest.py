"""Saved REST services (shared by rest get / rest post). Not a task."""
import json, re, urllib.error, urllib.request
from _lib import fail
from _conn import load_reg, check_url


def request(reg, name, method, path, body=None):
    if name not in reg:
        fail(f"No service named '{name}'. Saved: {', '.join(sorted(reg)) or 'none'}")
    s = reg[name]
    if path and not path.startswith("/") or "://" in path or ".." in path or " " in path:
        fail("Give a path that starts with /, such as /orders")
    url = s["url"].rstrip("/") + path
    check_url(url)
    hd = {"User-Agent": "JeeG", "Accept": "application/json"}
    if s.get("auth") == "bearer":
        hd["Authorization"] = "Bearer " + s["secret"]
    elif s.get("auth") == "header":
        hd[s["header"]] = s["secret"]
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        hd["Content-Type"] = "application/json"

    class NoRedirect(urllib.request.HTTPRedirectHandler):          # a redirect could carry your key to another site
        def redirect_request(self, *a, **k):
            return None
    try:
        with urllib.request.build_opener(NoRedirect).open(urllib.request.Request(url, data=data, method=method, headers=hd), timeout=15) as r:
            raw = r.read(1_000_000).decode("utf-8", "replace")
            return r.status, raw
    except urllib.error.HTTPError as ex:
        return ex.code, ex.read(2000).decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as ex:
        fail(f"Could not reach '{name}': {getattr(ex, 'reason', ex)}")
