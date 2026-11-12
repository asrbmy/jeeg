"""Safe public-web fetching for watchers, feeds and downloads. Standard library only. Not a task.
Only public https addresses are fetched: this computer and home-network addresses are refused, also after a redirect.
(Tests may set JEEG_TEST_ALLOW_LOCAL=1 to reach 127.0.0.1.)"""
import os
import re
import socket
import ssl
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse

from _conn import is_private_host

UA = {"User-Agent": "Mozilla/5.0 JeeG/2"}


class WebError(Exception):
    pass


def allow_local():
    return os.environ.get("JEEG_TEST_ALLOW_LOCAL") == "1"


def check_public(url):
    u = urlparse((url or "").strip())
    if u.scheme not in {"http", "https"} or not u.hostname or u.username or u.password:
        raise WebError("Give a full web address starting with https://")
    local = is_private_host(u.hostname)
    if local and not allow_local():
        raise WebError("That address is on this computer or your home network. This task only reaches public websites.")
    if u.scheme == "http" and not allow_local():
        raise WebError("Use https:// (plain http is not allowed).")
    return u


class _Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_public(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_OPENER = urllib.request.build_opener(_Redirect)


def fetch(url, max_bytes=2_000_000, timeout=12):
    """-> (bytes, final_url, content_type). Raises WebError with a plain message."""
    check_public(url)
    try:
        with _OPENER.open(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            data = r.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise WebError(f"That page is bigger than {max_bytes // 1_000_000} MB, so I stopped.")
            return data, r.geturl(), r.headers.get("Content-Type", "")
    except WebError:
        raise
    except urllib.error.HTTPError as ex:
        raise WebError(f"The site answered with an error ({ex.code}).") from None
    except (urllib.error.URLError, OSError, ValueError) as ex:
        raise WebError("Could not reach it (offline, wrong address, or the site is down).") from None


def fetch_to_file(url, dest, max_bytes=200_000_000, timeout=30):
    """Stream a download to dest (a pathlib.Path). Returns the number of bytes."""
    check_public(url)
    n = 0
    try:
        with _OPENER.open(urllib.request.Request(url, headers=UA), timeout=timeout) as r, open(dest, "wb") as fh:
            while True:
                chunk = r.read(65536)
                if not chunk:
                    break
                n += len(chunk)
                if n > max_bytes:
                    raise WebError(f"larger than {max_bytes // 1_000_000} MB")
                fh.write(chunk)
    except WebError:
        dest.unlink(missing_ok=True)
        raise
    except urllib.error.HTTPError as ex:
        dest.unlink(missing_ok=True)
        raise WebError(f"error {ex.code}") from None
    except (urllib.error.URLError, OSError, ValueError):
        dest.unlink(missing_ok=True)
        raise WebError("could not download") from None
    return n


def decode(data, content_type=""):
    m = re.search(r"charset=([\w\-]+)", content_type or "", re.I)
    for enc in ([m.group(1)] if m else []) + ["utf-8"]:
        try:
            return data.decode(enc, "replace")
        except LookupError:
            continue
    return data.decode("utf-8", "replace")


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "template"}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "template"} and self.skip:
            self.skip -= 1

    def handle_data(self, d):
        if not self.skip and d.strip():
            self.out.append(d.strip())


def visible_text(html):
    p = _Text()
    try:
        p.feed(html)
    except (ValueError, AssertionError):
        pass
    return re.sub(r"\s+", " ", " ".join(p.out)).strip()


def ssl_info(host, port=443, timeout=8):
    """-> dict(days=int, expires='YYYY-MM-DD', issuer=str) or dict(error=str). Uses the normal trust store."""
    if is_private_host(host) and not allow_local():
        return {"error": "That address is on this computer or your home network."}
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=timeout) as s, ctx.wrap_socket(s, server_hostname=host) as t:
            c = t.getpeercert()
    except ssl.SSLCertVerificationError as ex:
        return {"error": f"The certificate is not trusted ({ex.verify_message})."}
    except (OSError, ssl.SSLError):
        return {"error": "Could not connect with https (offline, wrong name, or no https there)."}
    end = ssl.cert_time_to_seconds(c["notAfter"])
    issuer = next((v for rdn in c.get("issuer", ()) for k, v in rdn if k == "organizationName"), "")
    return {"days": int((end - time.time()) // 86400), "expires": time.strftime("%Y-%m-%d", time.gmtime(end)), "issuer": issuer}
