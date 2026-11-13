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
