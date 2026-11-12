"""App adapters: describe an app's web API once (name, address, login style, actions) and JeeG can read from it or act in it.
Used by the linked_* tasks. Not a task itself.

Safety rules that live here:
  - an action that is not GET/HEAD is always a *write* action; read tasks refuse writes, whatever the definition says
  - values the caller supplies only ever fill the path (percent-encoded), query values (encoded) and JSON body strings; never the host or headers
  - redirects are never followed (a login header must not travel to another site)
  - https everywhere; plain http only to this computer or your home network
  - secrets are stored in conn_*.json (0600), never printed, and scrubbed from every message
"""
import base64
import json
import os
import re
import urllib.error
import urllib.request
from urllib.parse import quote, urlparse, urlencode

from _conn import is_private_host, load_reg, local_only_override, save_reg
from _store import load, save

NAME = re.compile(r"[a-z][a-z0-9_\-]{1,23}$")
METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
AUTHS = {"none", "bearer", "header", "query", "basic", "path_token", "url"}
CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
HOLE = re.compile(r"\{(\w+)\}")
DEFAULT_PAT = r"[^\x00-\x1f\x7f]{1,2000}"
MAX_BODY = 1_000_000
UA = "JeeG-apps"


def _p(pat="", **kw):
    return dict(pat=pat or DEFAULT_PAT, **kw)


BUILTIN = {
    "github": {
        "title": "GitHub", "base": "https://api.github.com", "auth": "bearer", "secret_from": ["github", "token"],
        "headers": {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
        "login_help": "Create a token at github.com/settings/tokens (read access to issues and notifications; add write access only if you want comments or new issues). Or run:  github login",
        "actions": {
            "me": {"method": "GET", "path": "/user", "format": "{login}  {name}", "desc": "who you are on GitHub"},
            "issues": {"method": "GET", "path": "/issues?filter=assigned&state=open&per_page=15", "format": "#{number} {title}   ({repository.full_name})", "desc": "issues assigned to you"},
            "notifications": {"method": "GET", "path": "/notifications?per_page=15", "format": "{subject.title}   ({repository.full_name}, {reason})", "desc": "your unread notifications"},
            "repo_issues": {"method": "GET", "path": "/repos/{repo}/issues?state=open&per_page=15", "format": "#{number} {title}   by {user.login}", "desc": "open issues of a repo",
                            "params": {"repo": _p(r"[A-Za-z0-9_.\-]{1,100}/[A-Za-z0-9_.\-]{1,100}", slash=True, help="owner/name")}},
            "pulls": {"method": "GET", "path": "/repos/{repo}/pulls?state=open&per_page=15", "format": "#{number} {title}   by {user.login}", "desc": "open pull requests of a repo",
                      "params": {"repo": _p(r"[A-Za-z0-9_.\-]{1,100}/[A-Za-z0-9_.\-]{1,100}", slash=True, help="owner/name")}},
            "comment": {"method": "POST", "path": "/repos/{repo}/issues/{number}/comments", "body": {"body": "{text}"}, "format": "{html_url}", "desc": "comment on an issue or pull request",
                        "params": {"repo": _p(r"[A-Za-z0-9_.\-]{1,100}/[A-Za-z0-9_.\-]{1,100}", slash=True, help="owner/name"), "number": _p(r"\d{1,9}"), "text": _p(r"[\s\S]{1,10000}")}},
            "create_issue": {"method": "POST", "path": "/repos/{repo}/issues", "body": {"title": "{title}", "body": "{text}"}, "format": "{html_url}", "desc": "open a new issue",
                             "params": {"repo": _p(r"[A-Za-z0-9_.\-]{1,100}/[A-Za-z0-9_.\-]{1,100}", slash=True, help="owner/name"), "title": _p(r"[^\x00-\x1f\x7f]{1,200}"), "text": _p(r"[\s\S]{0,10000}", optional=True)}},
        },
    },
    "telegram": {
        "title": "Telegram (your bot)", "base": "https://api.telegram.org/bot{secret}", "auth": "path_token",
        "login_help": "Talk to @BotFather in Telegram, send /newbot, and paste the token it gives you. Then message your bot once so it can message you back.",
        "actions": {
            "me": {"method": "GET", "path": "/getMe", "format": "{result.first_name}  (@{result.username})", "desc": "check the bot works"},
            "send": {"method": "POST", "path": "/sendMessage", "body": {"chat_id": "{chat}", "text": "{text}"}, "format": "sent", "desc": "send a message from your bot",
                     "params": {"chat": _p(r"-?\d{1,20}|@[A-Za-z0-9_]{4,64}", help="chat id"), "text": _p(r"[\s\S]{1,4000}")}},
        },
    },
    "discord": {
        "title": "Discord (a channel webhook)", "base": "", "auth": "url", "url_must": "discord",
        "login_help": "In Discord: channel settings > Integrations > Webhooks > New Webhook > Copy URL. Paste that URL as the login.",
        "actions": {"send": {"method": "POST", "path": "", "body": {"content": "{text}"}, "format": "sent", "desc": "post a message in the channel",
                             "params": {"text": _p(r"[\s\S]{1,2000}")}}},
    },
    "slack": {
        "title": "Slack (an incoming webhook)", "base": "", "auth": "url", "url_must": "slack",
        "login_help": "In Slack: create an app with Incoming Webhooks, add it to a channel, and paste the webhook URL as the login.",
        "actions": {"send": {"method": "POST", "path": "", "body": {"text": "{text}"}, "format": "sent", "desc": "post a message in the channel",
                             "params": {"text": _p(r"[\s\S]{1,3000}")}}},
    },
    "whatsapp": {
        "title": "WhatsApp (opens the chat for you)", "base": "", "auth": "none",
        "login_help": "No login. WhatsApp has no safe way for another program to send as you, so JeeG opens the chat with your message typed in and you press Send.",
        "actions": {"message": {"kind": "open", "url": "https://wa.me/{phone}?text={text}", "desc": "open a chat with your message ready (you press Send)",
                                "params": {"phone": _p(r"\d{6,15}", digits=True, help="number with country code"), "text": _p(r"[\s\S]{1,2000}")}}},
    },
}


# ------------------------------------------------------------------ definitions
def user_defs():
    d = load("adapters.json", {})
    return d if isinstance(d, dict) else {}


def all_adapters():
    """name -> (definition, builtin?). Built-in names cannot be replaced. Broken user entries are skipped."""
    out = {k: (v, True) for k, v in BUILTIN.items()}
    for k, v in user_defs().items():
        if k not in out and check_def(k, v) is None:
            out[k] = (v, False)
    return out


def holes(s):
    return set(HOLE.findall(s)) if isinstance(s, str) else set()


def _walk(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from _walk(v)
    elif isinstance(x, list):
        for v in x:
            yield from _walk(v)


def check_base(base, auth):
    if auth == "url":
        return None
    u = urlparse(base.replace("{secret}", "x") if auth == "path_token" else base)
    if u.scheme not in {"http", "https"} or not u.hostname or u.username or u.password:
        return "the address must start with https:// (and have no user:password in it)"
    if u.scheme == "http" and not is_private_host(u.hostname):
        return "plain http is only allowed for this computer or your home network"
    if auth != "path_token" and "{" in base:
        return "the address cannot contain { }"
    if auth == "path_token" and "{secret}" not in base:
        return "a token-in-address login needs {secret} in the address"
    if "{" in (u.hostname or ""):
        return "the host name cannot be filled in"
    return None


def check_def(name, d):
    """Returns None when the definition is acceptable, else a plain-words reason."""
    if not NAME.match(name or ""):
        return "the app name uses 2-24 letters, numbers, - or _ and starts with a letter"
    if not isinstance(d, dict) or not isinstance(d.get("actions"), dict):
        return "no actions"
    if d.get("auth") not in AUTHS:
        return "login style must be one of: " + ", ".join(sorted(AUTHS))
    if len(d["actions"]) > 40:
        return "too many actions (40 at most)"
    if d["auth"] == "header" and not re.fullmatch(r"[A-Za-z][A-Za-z0-9\-]{0,40}", str(d.get("header", ""))):
        return "header login needs a header name"
    if d["auth"] == "query" and not re.fullmatch(r"[A-Za-z][A-Za-z0-9_\-]{0,40}", str(d.get("header", ""))):
        return "query login needs a parameter name"
    if not d["actions"] or not all(isinstance(x, dict) and x.get("kind") == "open" for x in d["actions"].values()):
        why = check_base(str(d.get("base", "")), d["auth"])
        if why:
            return why
    for hk, hv in (d.get("headers") or {}).items():
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9\-]{0,40}", str(hk)) or re.search(r"[\x00-\x1f\x7f]", str(hv)) or str(hk).lower() in {"authorization", "cookie", "host", "content-length"}:
            return f"header {hk!r} is not allowed"
    for an, a in d["actions"].items():
        if not NAME.match(an) or not isinstance(a, dict):
            return f"action name {an!r} is not valid"
        params = a.get("params") or {}
        for pn, pd in params.items():
            if not re.fullmatch(r"[a-z][a-z0-9_]{0,23}", pn):
                return f"{an}: parameter name {pn!r} is not valid"
            try:
                re.compile(pd.get("pat", DEFAULT_PAT))
            except (re.error, AttributeError):
                return f"{an}: parameter {pn} has a broken pattern"
        if a.get("kind") == "open":
            if not str(a.get("url", "")).startswith("https://") or not a.get("params"):
                return f"{an}: an 'open' action needs an https:// link and parameters"
            used = holes(a["url"])
        else:
            m = str(a.get("method", "GET")).upper()
            if m not in METHODS:
                return f"{an}: method must be one of {', '.join(sorted(METHODS))}"
            p = str(a.get("path", ""))
            if d["auth"] == "url":
                if p:
                    return f"{an}: a webhook action has no path"
            elif not p.startswith("/") or "://" in p or ".." in p.split("?")[0].split("/") or CONTROL.search(p):
                return f"{an}: the path must start with / and stay on the same site"
            used = holes(p) | {h for s in _walk(a.get("body")) for h in holes(s)} | {h for s in _walk(a.get("query")) for h in holes(s)}
        if used - set(params):
            return f"{an}: {', '.join(sorted(used - set(params)))} is used but not declared as a parameter"
        if len(a.get("format", "")) > 300 or len(a.get("desc", "")) > 200:
            return f"{an}: format or description too long"
    return None


def is_write(a):
    return a.get("kind") == "open" or str(a.get("method", "GET")).upper() not in {"GET", "HEAD"}


# ------------------------------------------------------------------ secrets
def _store_for(name, d):
    ref = d.get("secret_from")
    return (ref[0], ref[1]) if ref else ("appsecrets", name)


def get_secret(name, d):
    reg, key = _store_for(name, d)
    v = load_reg(reg).get(key, "")
    return v if isinstance(v, str) else ""


def set_secret(name, d, value):
    reg, key = _store_for(name, d)
    r = load_reg(reg)
    r[key] = value
    save_reg(reg, r)


def drop_secret(name, d):
    reg, key = _store_for(name, d)
    r = load_reg(reg)
    had = key in r
    r.pop(key, None)
    save_reg(reg, r)
    return had


def check_secret(d, value):
    """A secret is one printable token. A webhook secret is a whole https address."""
    if CONTROL.search(value) or not value or len(value) > 800 or (" " in value and d["auth"] != "basic"):
        return "that does not look like a token (no spaces, one line)"
    if d["auth"] == "url":
        u = urlparse(value)
        if u.scheme not in {"https"} and not (u.scheme == "http" and u.hostname and is_private_host(u.hostname)):
            return "give the full webhook address starting with https://"
        must = d.get("url_must")
        if must and must not in (u.hostname or ""):
            return f"that does not look like a {must} webhook address"
    return None


# ------------------------------------------------------------------ arguments
PAIR = re.compile(r"""(?:^|\s)([a-z][a-z0-9_]*)=("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\S*)""")


def parse_args(action, text):
    """'repo=a/b number=3 hello there' -> ({'repo':..., 'number':..., 'text':...}, None) or (None, 'reason').
    key=value pairs (values may be quoted) fill by name; the other words fill the remaining parameters in order, the last one taking the rest."""
    params = action.get("params") or {}
    vals, rest = {}, text or ""
    for m in list(PAIR.finditer(rest)):
        k, v = m.group(1), m.group(2)
        if k in params:
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = re.sub(r"\\(.)", r"\1", v[1:-1])
            vals[k] = v
    if vals:
        rest = PAIR.sub(lambda m: " " if m.group(1) in params else m.group(0), rest)
    words = rest.split()
    left = [k for k in params if k not in vals]
    for i, k in enumerate(left):
        if not words:
            break
        if i == len(left) - 1:
            vals[k] = " ".join(words)
            words = []
        else:
            vals[k] = words.pop(0)
    for k, pd in params.items():
        v = vals.get(k)
        if v is None or v == "":
            if pd.get("optional"):
                vals[k] = ""
                continue
            return None, f"missing {k}" + (f" ({pd['help']})" if pd.get("help") else "")
        if pd.get("digits"):
            v = re.sub(r"[\s\-+().]", "", v)
        if CONTROL.sub("", v) != v and "\n" not in v:
            return None, f"{k} has a control character"
        if not re.fullmatch(pd.get("pat", DEFAULT_PAT), v):
            return None, f"{k} is not in the expected form" + (f" ({pd['help']})" if pd.get("help") else "")
        if pd.get("slash") and any(seg in {".", ".."} for seg in v.split("/")):
            return None, f"{k} is not allowed"
        vals[k] = v
    extra = " ".join(words)
    if extra and not params:
        return None, "this action takes no arguments"
    return vals, None


def usage(name, an, a):
    ps = " ".join(f"{k}=<{(v.get('help') or k)}>" for k, v in (a.get("params") or {}).items())
    return f"app {'do' if is_write(a) else 'read'} {name} {an} {ps}".strip()


# ------------------------------------------------------------------ requests
def _fill(s, vals, safe=""):
    return HOLE.sub(lambda m: quote(vals.get(m.group(1), ""), safe=safe), s)


def _fill_json(x, vals):
    if isinstance(x, str):
        return HOLE.sub(lambda m: vals.get(m.group(1), ""), x)
    if isinstance(x, dict):
        return {k: _fill_json(v, vals) for k, v in x.items()}
    if isinstance(x, list):
        return [_fill_json(v, vals) for v in x]
    return x


def build(name, d, an, vals, secret):
    """The exact request, as a dict (method, url, headers, body). Does not send anything."""
    a = d["actions"][an]
    params = a.get("params") or {}
    if a.get("kind") == "open":
        url = a["url"]
        url = HOLE.sub(lambda m: quote(vals.get(m.group(1), ""), safe=""), url)
        return {"method": "OPEN", "url": url, "headers": {}, "body": None}
    env_name = "JEEG_APPS_BASE_" + name.upper().replace("-", "_")          # tests only: accepted only when it points at this computer
    base = local_only_override(env_name, "") or (secret if d["auth"] == "url" else d.get("base", ""))
    if d["auth"] == "path_token":
        base = base.replace("{secret}", quote(secret, safe=":"))
    path = a.get("path", "")
    pth, _, lit_q = path.partition("?")
    pth = HOLE.sub(lambda m: quote(vals.get(m.group(1), ""), safe="/" if params.get(m.group(1), {}).get("slash") else ""), pth)
    q = [lit_q] if lit_q else []
    for qk, qv in (a.get("query") or {}).items():
        q.append(urlencode({qk: _fill_raw(qv, vals)}))
    headers = {"User-Agent": UA, "Accept": "application/json"}
    headers.update({str(k): str(v) for k, v in (d.get("headers") or {}).items()})
    if d["auth"] == "bearer":
        headers["Authorization"] = "Bearer " + secret
    elif d["auth"] == "header":
        headers[d["header"]] = secret
    elif d["auth"] == "basic":
        headers["Authorization"] = "Basic " + base64.b64encode(secret.encode("utf-8")).decode("ascii")
    elif d["auth"] == "query":
        q.append(urlencode({d["header"]: secret}))
    url = base.rstrip("/") + pth if d["auth"] != "url" else base
    if q:
        url += ("&" if "?" in url else "?") + "&".join(q)
    body = None
    if a.get("body") is not None:
        body = json.dumps(_fill_json(a["body"], vals), ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    return {"method": str(a.get("method", "GET")).upper(), "url": url, "headers": headers, "body": body}


def _fill_raw(s, vals):
    return HOLE.sub(lambda m: vals.get(m.group(1), ""), s)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def scrub(text, secret):
    t = str(text)
    if secret:
        for v in {secret, quote(secret, safe=""), quote(secret, safe=":"), base64.b64encode(secret.encode()).decode()}:
            t = t.replace(v, "***")
    return CONTROL.sub("", t)


def send(req, secret="", timeout=15):
    """Returns (status, text). Raises RuntimeError with a plain-words message on failure."""
    r = urllib.request.Request(req["url"], data=req["body"], method=req["method"], headers=req["headers"])
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(r, timeout=timeout) as resp:
            return resp.status, resp.read(MAX_BODY).decode("utf-8", "replace")
    except urllib.error.HTTPError as ex:
        body = ""
        try:
            body = ex.read(600).decode("utf-8", "replace")
        except OSError:
            pass
        msg = {401: "The app refused the login. Run:  app login <app>", 403: "The app refused (wrong permission, or a rate limit).", 404: "Not found (or your login cannot see it).",
               422: "The app did not accept that request.", 429: "Too many requests. Wait a bit."}.get(ex.code)
        if 300 <= ex.code < 400:
            msg = "The app redirected the request. JeeG does not follow redirects, so your login is never sent elsewhere."
        detail = re.sub(r"\s+", " ", scrub(body, secret))[:200]
        raise RuntimeError(f"HTTP {ex.code}. " + (msg or "The app returned an error.") + (f"  ({detail})" if detail and ex.code not in {401} else ""))
    except (urllib.error.URLError, OSError, ValueError) as ex:
        raise RuntimeError("Could not reach the app: " + scrub(getattr(ex, "reason", ex), secret))


# ------------------------------------------------------------------ showing results
def dig(x, path):
    for part in path.split("."):
        if isinstance(x, dict) and part in x:
            x = x[part]
        elif isinstance(x, list) and part.isdigit() and int(part) < len(x):
            x = x[int(part)]
        else:
            return ""
    return x


def line(fmt, item):
    def one(m):
        v = dig(item, m.group(1))
        if isinstance(v, (dict, list)):
            v = json.dumps(v, ensure_ascii=False)[:80]
        return "" if v is None else str(v)
    return re.sub(r"\s+", " ", re.sub(r"\{([\w.\-]+)\}", one, fmt)).strip()[:300]


def render(a, text, secret=""):
    try:
        data = json.loads(text)
    except ValueError:
        data = None
    fmt = a.get("format", "")
    if data is None:
        out = re.sub(r"\n{3,}", "\n\n", scrub(text, secret)).strip()[:2000]
        return out or "(empty answer)"
    if fmt == "sent":
        return "Sent."
    src = dig(data, a["list"]) if a.get("list") else data
    if isinstance(src, list):
        rows = [line(fmt, it) if fmt else json.dumps(it, ensure_ascii=False)[:200] for it in src[:25]]
        rows = [r for r in rows if r]
        if not rows:
            return "(nothing)"
        more = f"\n... and {len(src) - 25} more" if len(src) > 25 else ""
        return scrub("\n".join(rows), secret) + more
    if fmt and isinstance(src, dict):
        return scrub(line(fmt, src), secret) or "(empty answer)"
    return scrub(json.dumps(src, ensure_ascii=False, indent=1), secret)[:3000]
