"""Tiny HTTP helper (standard library). Returns None when offline instead of raising. Not a task."""
import json
import urllib.error
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 JeeG/2"}


def get(url, timeout=8, as_json=False):
    if not url.lower().startswith(("https://", "http://")):
        return None
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read(2_000_000).decode("utf-8", "replace")
        return json.loads(data) if as_json else data
    except (urllib.error.URLError, OSError, ValueError):
        return None
