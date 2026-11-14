"""Ready-made app definitions you can add with  app preset add <name>.  Not a task itself.
Every preset goes through the same safety check as a hand-made one. They were written from each service's public documentation
and have NOT been tried against the live services: check one with  app read <app> me  (or the first read action) after logging in.
"""
from _adapters import _p

_W = r"[A-Za-z0-9][A-Za-z0-9_.\-]{0,100}"


def _cmd(argv, desc, read=True, **params):
    a = {"kind": "command", "argv": argv, "desc": desc, "read": read}
    if params:
        a["params"] = {k: _p(v) if isinstance(v, str) else v for k, v in params.items()}
    return a


PRESETS = {
    "gitlab": {"title": "GitLab", "base": "https://gitlab.com/api/v4", "auth": "header", "header": "PRIVATE-TOKEN", "needs_base": False,
               "login_help": "GitLab > Preferences > Access tokens: make a token with read_api (add api to comment). For your own server add base=https://your.server/api/v4",
               "actions": {"me": {"method": "GET", "path": "/user", "format": "{username}  {name}", "desc": "who you are"},
                           "issues": {"method": "GET", "path": "/issues?scope=assigned_to_me&state=opened&per_page=15", "format": "#{iid} {title}   ({references.full})", "desc": "issues assigned to you"},
                           "todos": {"method": "GET", "path": "/todos?per_page=15", "format": "{body}", "desc": "your to-do list"},
                           "comment": {"method": "POST", "path": "/projects/{project}/issues/{iid}/notes", "body": {"body": "{text}"}, "format": "sent", "desc": "comment on an issue",
                                       "params": {"project": _p(r"\d{1,12}|[A-Za-z0-9_.\-]{1,100}(?:/[A-Za-z0-9_.\-]{1,100}){0,4}", help="id or group/project"), "iid": _p(r"\d{1,9}"), "text": _p(r"[\s\S]{1,10000}")}}}},
    "notion": {"title": "Notion", "base": "https://api.notion.com/v1", "auth": "bearer", "headers": {"Notion-Version": "2022-06-28"},
               "login_help": "notion.so/my-integrations: create an integration, copy its secret, and share your pages with it.",
               "actions": {"me": {"method": "GET", "path": "/users/me", "format": "{name}", "desc": "the integration"},
                           "search": {"method": "POST", "read": True, "path": "/search", "body": {"query": "{text}", "page_size": 10}, "list": "results", "format": "{object}  {url}",
                                      "desc": "search your pages (only looks)", "params": {"text": _p(r"[^\x00-\x1f\x7f]{1,200}")}}}},
    "linear": {"title": "Linear", "base": "https://api.linear.app", "auth": "header", "header": "Authorization",
               "login_help": "Linear > Settings > API: create a personal API key.",
               "actions": {"me": {"method": "POST", "read": True, "path": "/graphql", "body": {"query": "query { viewer { name email } }"}, "format": "{data.viewer.name}  {data.viewer.email}", "desc": "who you are"},
                           "my_issues": {"method": "POST", "read": True, "path": "/graphql", "body": {"query": "query { viewer { assignedIssues(first: 15) { nodes { identifier title } } } }"},
                                         "list": "data.viewer.assignedIssues.nodes", "format": "{identifier} {title}", "desc": "issues assigned to you"},
                           "comment": {"method": "POST", "path": "/graphql", "format": "sent", "desc": "comment on an issue (give the issue's id)",
                                       "body": {"query": "mutation($i: String!, $b: String!) { commentCreate(input: {issueId: $i, body: $b}) { success } }", "variables": {"i": "{issue}", "b": "{text}"}},
                                       "params": {"issue": _p(r"[A-Za-z0-9\-]{1,64}"), "text": _p(r"[\s\S]{1,10000}")}}}},
    "todoist": {"title": "Todoist", "base": "https://api.todoist.com/rest/v2", "auth": "bearer",
                "login_help": "Todoist > Settings > Integrations > Developer: copy your API token.",
                "actions": {"tasks": {"method": "GET", "path": "/tasks", "format": "{content}   {due.string}", "desc": "your open tasks"},
                            "add_task": {"method": "POST", "path": "/tasks", "body": {"content": "{text}"}, "format": "added: {content}", "desc": "add a task",
                                         "params": {"text": _p(r"[^\x00-\x1f\x7f]{1,500}")}}}},
    "homeassistant": {"title": "Home Assistant", "base": "", "auth": "bearer", "needs_base": "http://homeassistant.local:8123/api",
                      "login_help": "Home Assistant > your profile > Security > Long-lived access tokens. Add it with base=http://homeassistant.local:8123/api (your own network only).",
                      "actions": {"states": {"method": "GET", "path": "/states", "format": "{entity_id}: {state}", "desc": "everything (first 25)"},
                                  "state": {"method": "GET", "path": "/states/{entity}", "format": "{entity_id}: {state}", "desc": "one thing", "params": {"entity": _p(r"[a-z_]+\.[a-z0-9_]{1,60}", help="light.kitchen")}},
                                  "light_on": {"method": "POST", "path": "/services/light/turn_on", "body": {"entity_id": "{entity}"}, "format": "sent", "desc": "switch a light on",
                                               "params": {"entity": _p(r"light\.[a-z0-9_]{1,60}", help="light.kitchen")}},
                                  "light_off": {"method": "POST", "path": "/services/light/turn_off", "body": {"entity_id": "{entity}"}, "format": "sent", "desc": "switch a light off",
                                                "params": {"entity": _p(r"light\.[a-z0-9_]{1,60}", help="light.kitchen")}}}},
    "jira": {"title": "Jira Cloud", "base": "", "auth": "basic", "needs_base": "https://YOURS.atlassian.net/rest/api/3",
             "login_help": "Make an API token at id.atlassian.com, then log in with  your-email:the-token  (one line). Add with base=https://YOURS.atlassian.net/rest/api/3",
             "actions": {"me": {"method": "GET", "path": "/myself", "format": "{displayName}", "desc": "who you are"},
                         "my_issues": {"method": "GET", "path": "/search/jql?jql=assignee%3DcurrentUser()%20AND%20resolution%3DUnresolved&maxResults=15&fields=summary", "list": "issues",
                                       "format": "{key} {fields.summary}", "desc": "your open issues"}}},
    "git": {"title": "git (a folder on this computer)", "local": True, "auth": "none", "base": "", "needs_base": False,
            "actions": {"status": _cmd(["git", "-C", "{dir}", "status", "--short", "--branch"], "what changed in a folder", dir=r"[^\x00-\x1f\x7f]{1,500}"),
                        "log": _cmd(["git", "-C", "{dir}", "log", "--oneline", "-n", "15"], "the last 15 commits", dir=r"[^\x00-\x1f\x7f]{1,500}"),
                        "branches": _cmd(["git", "-C", "{dir}", "branch", "-a"], "branches", dir=r"[^\x00-\x1f\x7f]{1,500}")}},
    "docker": {"title": "Docker (on this computer)", "local": True, "auth": "none", "base": "", "needs_base": False,
               "actions": {"ps": _cmd(["docker", "ps", "-a"], "containers"),
                           "images": _cmd(["docker", "images"], "images"),
                           "logs": _cmd(["docker", "logs", "--tail", "50", "{name}"], "last 50 log lines", name=_W),
                           "restart": _cmd(["docker", "restart", "{name}"], "restart a container", read=False, name=_W),
                           "stop": _cmd(["docker", "stop", "{name}"], "stop a container", read=False, name=_W)}},
    "kubectl": {"title": "kubectl (your cluster)", "local": True, "auth": "none", "base": "", "needs_base": False,
                "actions": {"pods": _cmd(["kubectl", "get", "pods"], "pods"), "nodes": _cmd(["kubectl", "get", "nodes"], "nodes"),
                            "logs": _cmd(["kubectl", "logs", "--tail=50", "{pod}"], "last 50 log lines", pod=_W),
                            "restart": _cmd(["kubectl", "rollout", "restart", "deployment/{name}"], "restart a deployment", read=False, name=_W)}},
    "adb": {"title": "Android phone over USB (adb)", "local": True, "auth": "none", "base": "", "needs_base": False,
            "actions": {"devices": _cmd(["adb", "devices"], "phones connected"), "battery": _cmd(["adb", "shell", "dumpsys", "battery"], "battery state"),
                        "reboot": _cmd(["adb", "reboot"], "restart the phone", read=False)}},
}


# ---- more services (2.20, second batch). Same rule: written from the public documentation, not tried against the live services.
_T = r"[^\x00-\x1f\x7f]{1,200}"
_D = r"\d{1,20}"
_N = r"[A-Za-z0-9][A-Za-z0-9_.\-]{0,100}"


def _g(path, fmt, desc, lst="", **params):
    a = {"method": "GET", "path": path, "format": fmt, "desc": desc}
    if lst:
        a["list"] = lst
    if params:
        a["params"] = {k: _p(v) for k, v in params.items()}
    return a


PRESETS.update({
    "asana": {"title": "Asana", "base": "https://app.asana.com/api/1.0", "auth": "bearer", "login_help": "Asana > My settings > Apps > Developer apps: make a personal access token.",
              "actions": {"me": _g("/users/me", "{data.name}  {data.email}", "who you are"),
                          "workspaces": _g("/workspaces", "{gid}  {name}", "your workspaces", "data"),
                          "my_tasks": _g("/tasks?assignee=me&workspace={workspace}&completed_since=now&limit=15", "{gid}  {name}", "your open tasks (give the workspace id)", "data", workspace=_D),
                          "add_task": {"method": "POST", "path": "/tasks", "body": {"data": {"name": "{text}", "workspace": "{workspace}", "assignee": "me"}}, "format": "added: {data.name}",
                                       "desc": "add a task for yourself", "params": {"workspace": _p(_D), "text": _p(r"[^\x00-\x1f\x7f]{1,500}")}}}},
    "box": {"title": "Box", "base": "https://api.box.com/2.0", "auth": "bearer", "login_help": "Box developer console: make an app and copy a developer token (it lasts about an hour).",
            "actions": {"me": _g("/users/me", "{name}  {login}", "who you are"),
                        "folder": _g("/folders/{id}/items?limit=25", "{type}  {name}", "what is in a folder (0 = the top)", "entries", id=_D),
                        "search": _g("/search?query={q}&limit=15", "{type}  {name}", "search your files", "entries", q=_T)}},
    "monday": {"title": "monday.com", "base": "https://api.monday.com", "auth": "header", "header": "Authorization", "headers": {"API-Version": "2024-10"},
               "login_help": "monday.com > profile > Developers > My access tokens.",
               "actions": {"me": {"method": "POST", "read": True, "path": "/v2", "body": {"query": "query { me { name email } }"}, "format": "{data.me.name}  {data.me.email}", "desc": "who you are"},
                           "boards": {"method": "POST", "read": True, "path": "/v2", "body": {"query": "query { boards(limit: 15) { id name } }"}, "list": "data.boards", "format": "{id}  {name}", "desc": "your boards"}}},
    "bitbucket": {"title": "Bitbucket Cloud", "base": "https://api.bitbucket.org/2.0", "auth": "basic", "login_help": "Make an app password (Personal settings > App passwords) and log in with  your-username:the-app-password",
                  "actions": {"me": _g("/user", "{display_name}  ({username})", "who you are"),
                              "repos": _g("/repositories/{workspace}?pagelen=20", "{full_name}", "repositories of a workspace", "values", workspace=_N),
                              "pulls": _g("/repositories/{workspace}/{repo}/pullrequests?state=OPEN&pagelen=15", "#{id} {title}", "open pull requests", "values", workspace=_N, repo=_N)}},
    "stripe": {"title": "Stripe (look only)", "base": "https://api.stripe.com/v1", "auth": "bearer", "login_help": "Stripe Dashboard > Developers > API keys: make a RESTRICTED key with read-only access. JeeG's Stripe preset has no write actions.",
               "actions": {"balance": _g("/balance", "{amount} {currency}", "your balance", "available"),
                           "customers": _g("/customers?limit=10", "{id}  {email}", "latest customers", "data"),
                           "charges": _g("/charges?limit=10", "{id}  {amount} {currency}  {status}", "latest charges", "data")}},
    "shopify": {"title": "Shopify store", "base": "", "auth": "header", "header": "X-Shopify-Access-Token", "needs_base": "https://YOURS.myshopify.com/admin/api/2024-10",
                "login_help": "Shopify admin > Apps > Develop apps: make a custom app with read scopes and copy its Admin API access token. Add with base=https://YOURS.myshopify.com/admin/api/2024-10",
                "actions": {"shop": _g("/shop.json", "{shop.name}  {shop.domain}", "your store"),
                            "products": _g("/products.json?limit=10", "{id}  {title}", "products", "products"),
                            "orders": _g("/orders.json?limit=10&status=any", "{name}  {total_price}  {financial_status}", "latest orders", "orders")}},
    "cloudflare": {"title": "Cloudflare", "base": "https://api.cloudflare.com/client/v4", "auth": "bearer", "login_help": "Cloudflare > My Profile > API Tokens: make a read-only token.",
                   "actions": {"verify": _g("/user/tokens/verify", "{result.status}", "is the token good"),
                               "zones": _g("/zones?per_page=20", "{id}  {name}  {status}", "your sites", "result")}},
    "vercel": {"title": "Vercel", "base": "https://api.vercel.com", "auth": "bearer", "login_help": "Vercel > Settings > Tokens.",
               "actions": {"me": _g("/v2/user", "{user.username}  {user.email}", "who you are"),
                           "projects": _g("/v9/projects?limit=15", "{name}", "your projects", "projects"),
                           "deployments": _g("/v6/deployments?limit=10", "{name}  {state}  {url}", "latest deployments", "deployments")}},
    "spotify": {"title": "Spotify", "base": "https://api.spotify.com/v1", "auth": "bearer",
                "login_help": "Spotify has no pasteable key. You need an access token from your own Spotify developer app (it lasts one hour); log in again when it ends.",
                "actions": {"me": _g("/me", "{display_name}", "who you are"),
                            "playing": _g("/me/player/currently-playing", "{item.name}", "what is playing"),
                            "playlists": _g("/me/playlists?limit=20", "{name}", "your playlists", "items"),
                            "pause": {"method": "PUT", "path": "/me/player/pause", "format": "paused", "desc": "pause (Premium)"},
                            "next": {"method": "POST", "path": "/me/player/next", "format": "skipped", "desc": "next song (Premium)"}}},
    "twitter": {"title": "X (Twitter), look only", "base": "https://api.x.com/2", "auth": "bearer", "login_help": "developer.x.com: make a project and copy its Bearer Token. What it may read depends on your plan.",
          "actions": {"user": _g("/users/by/username/{name}", "{data.name}  @{data.username}", "look up an account", name=r"[A-Za-z0-9_]{1,15}"),
                      "search": _g("/tweets/search/recent?query={q}&max_results=10", "{id}  {text}", "recent posts (plan dependent)", "data", q=_T)}},
    "salesforce": {"title": "Salesforce", "base": "", "auth": "bearer", "needs_base": "https://YOURS.my.salesforce.com/services/data/v61.0",
                   "login_help": "Log in with an access token (for example from  sf org display ). It ends after a while. Add with base=https://YOURS.my.salesforce.com/services/data/v61.0",
                   "actions": {"limits": _g("/limits", "{DailyApiRequests.Remaining} API calls left today", "limits"),
                               "query": _g("/query?q={soql}", "{Id}  {Name}", "run a SOQL query (read only)", "records", soql=r"[^\x00-\x1f\x7f]{1,500}")}},
    "confluence": {"title": "Confluence Cloud", "base": "", "auth": "basic", "needs_base": "https://YOURS.atlassian.net/wiki/api/v2",
                   "login_help": "Same as Jira: log in with  your-email:api-token . Add with base=https://YOURS.atlassian.net/wiki/api/v2",
                   "actions": {"spaces": _g("/spaces?limit=20", "{key}  {name}", "spaces", "results"), "pages": _g("/pages?limit=10", "{id}  {title}", "latest pages", "results")}},
    "grafana": {"title": "Grafana", "base": "", "auth": "bearer", "needs_base": "https://YOURS.grafana.net/api",
                "login_help": "Grafana > Administration > Service accounts: make one (Viewer) and a token. Add with base=https://YOURS.grafana.net/api",
                "actions": {"health": _g("/health", "{database}  {version}", "is it up"),
                            "search": _g("/search?query={q}", "{type}  {title}", "dashboards and folders", q=_T)}},
    "gmail": {"title": "Gmail (look only)", "base": "https://gmail.googleapis.com/gmail/v1/users/me", "auth": "bearer",
              "login_help": "Google does not allow Gmail over a simple login from here. Paste a short-lived access token (for example from the Google OAuth Playground, scope gmail.readonly). It lasts one hour. For daily use, the AI app's own Gmail connector is better.",
              "actions": {"me": _g("/profile", "{emailAddress}  ({messagesTotal} messages)", "your address"), "labels": _g("/labels", "{name}", "labels", "labels"),
                          "messages": _g("/messages?maxResults=10&q={q}", "{id}", "ids of messages matching a search (ids only)", "messages", q=_T)}},
    "gdrive": {"title": "Google Drive (look only)", "base": "https://www.googleapis.com/drive/v3", "auth": "bearer",
               "login_help": "Paste a short-lived access token with scope drive.readonly (Google OAuth Playground). It lasts one hour.",
               "actions": {"files": _g("/files?pageSize=20&fields=files(id,name,mimeType)", "{name}   ({mimeType})", "latest files", "files"),
                           "search": _g("/files?pageSize=15&fields=files(id,name)&q={q}", "{name}", "search by Drive query, e.g. name contains 'tax'", "files", q=_T)}},
    "gcal": {"title": "Google Calendar (look only)", "base": "https://www.googleapis.com/calendar/v3", "auth": "bearer",
             "login_help": "Paste a short-lived access token with scope calendar.readonly (Google OAuth Playground). It lasts one hour.",
             "actions": {"calendars": _g("/users/me/calendarList", "{summary}", "your calendars", "items"),
                         "events": _g("/calendars/primary/events?maxResults=10&singleEvents=true&orderBy=startTime&timeMin={from}", "{start.dateTime} {summary}", "events from a time on (give it like 2026-11-14T00:00:00Z)", "items", **{"from": r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ"})}},
    "outlook": {"title": "Outlook / Microsoft 365 (look only)", "base": "https://graph.microsoft.com/v1.0", "auth": "bearer",
                "device": {"code_url": "https://login.microsoftonline.com/common/oauth2/v2.0/devicecode", "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                           "scope": "offline_access User.Read Mail.Read Calendars.Read Files.Read"},
                "login_help": "Log in without pasting:  app login outlook device client_id=YOUR_APP_ID   (register an app in the Microsoft Entra portal as a public client and allow device code flow). The login lasts about an hour; run it again after that.",
                "actions": {"me": _g("/me", "{displayName}  {mail}", "who you are"),
                            "mail": _g("/me/messages?$top=10&$select=subject,from,receivedDateTime", "{receivedDateTime}  {subject}", "latest mail (subjects)", "value"),
                            "events": _g("/me/events?$top=10&$select=subject,start", "{start.dateTime}  {subject}", "your next events", "value"),
                            "files": _g("/me/drive/root/children?$top=20", "{name}", "files in OneDrive", "value")}},
})
