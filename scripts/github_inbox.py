# keywords: github inbox, github notifications, github issues, github pull requests, my github, github login, github prs
# desc: See your GitHub notifications or a repo's open issues (github login, github inbox, github issues owner/repo). Token asked privately.
# category: developer
# usage: github login | github inbox | github issues <owner/repo> | github forget
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*github\s+(login|inbox|notifications|issues|prs|pulls|forget)\b
# priority: 4
import json, re, urllib.error, urllib.request
from _lib import args_text, fail
from _conn import load_reg, save_reg, ask_secret, local_only_override
t = re.sub(r"^\s*github\s*", "", args_text(), flags=re.I).strip()
parts = t.split()
cmd = parts[0].lower() if parts else "inbox"
reg = load_reg("github")


def api(path):
    req = urllib.request.Request(local_only_override("JEEG_GITHUB_API", "https://api.github.com") + path, headers={"Accept": "application/vnd.github+json", "User-Agent": "JeeG",
                                 **({"Authorization": "Bearer " + reg["token"]} if reg.get("token") else {})})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read(2_000_000).decode("utf-8", "replace"))
    except urllib.error.HTTPError as ex:
        fail({401: "GitHub refused the token. Run:  github login", 403: "GitHub refused (rate limit or missing permission).", 404: "Not found (or the token cannot see it)."}.get(ex.code, f"GitHub answered {ex.code}."))
    except (urllib.error.URLError, OSError, ValueError) as ex:
        fail(f"Could not reach GitHub: {getattr(ex, 'reason', ex)}")


if cmd == "login":
    tok = ask_secret("GitHub personal access token (typing is hidden; give it only 'notifications' and read access): ")
    if not re.fullmatch(r"[A-Za-z0-9_\-]{20,255}", tok):
        fail("That does not look like a token. Nothing was saved.")
    save_reg("github", {"token": tok})
    print("Saved privately. Try:  github inbox")
elif cmd == "forget":
    save_reg("github", {})
    print("GitHub token removed.")
elif cmd in {"inbox", "notifications"}:
    if not reg.get("token"):
        fail("Run  github login  first.")
    items = api("/notifications?per_page=15")
    print(f"{len(items)} unread notification(s)." if items else "No unread notifications.")
    for n in items:
        print(f"  {n['repository']['full_name']:<32} {n['subject']['type']:<12} {n['subject']['title'][:70]}")
elif cmd in {"issues", "prs", "pulls"}:
    if len(parts) < 2 or not re.fullmatch(r"[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+", parts[1]):
        fail("Usage: github issues <owner/repo>")
    items = api(f"/repos/{parts[1]}/issues?state=open&per_page=15")
    want_pr = cmd in {"prs", "pulls"}
    items = [i for i in items if ("pull_request" in i) == want_pr]
    print(f"{len(items)} open {'pull request(s)' if want_pr else 'issue(s)'} in {parts[1]}:" if items else f"No open {'pull requests' if want_pr else 'issues'}.")
    for i in items:
        print(f"  #{i['number']:<5} {i['title'][:75]}  ({i['user']['login']})")
else:
    fail("Use:  github login | inbox | issues <owner/repo> | prs <owner/repo> | forget")
