"""Saved MCP servers: where they live and how to open one. Not a task itself."""
import re

from _conn import clean_name, load_reg, save_reg
import _mcpclient

SHELL = re.compile(r"^(?:(?:ba|z|k|c|tc|fi|da|a)?sh|cmd|powershell|pwsh)(?:\.exe)?$", re.I)


def servers():
    reg = load_reg("mcp")
    return {k: v for k, v in reg.items() if isinstance(v, list) and v and all(isinstance(x, str) for x in v)}


def env_vars(name):
    """The login variables of a server: [] (none), ['@bearer'] (web) or one or more names."""
    return [x for x in env_name(name).split(",") if x]


def _key(name, var):
    return name if len(env_vars(name)) <= 1 else f"{name}:{var}"


def token(name, var=None):
    """The saved login. For a server with several variables, say which one."""
    var = var or (env_vars(name) or [""])[0]
    v = load_reg("mcpsecrets").get(_key(name, var), "")
    return v if isinstance(v, str) else ""


def logged_in(name):
    vs = env_vars(name)
    return bool(vs) and all(token(name, v) for v in vs)


def drop_logins(name):
    for v in env_vars(name) or [""]:
        put("mcpsecrets", _key(name, v), None)
    put("mcpsecrets", name, None)


def env_name(name):
    v = load_reg("mcpenv").get(name, "")
    return v if isinstance(v, str) else ""


def read_tools(name):
    v = load_reg("mcpread").get(name, [])
    return set(x for x in v if isinstance(x, str)) if isinstance(v, list) else set()


def put(reg_name, name, value):
    r = load_reg(reg_name)
    if value is None:
        r.pop(name, None)
    else:
        r[name] = value
    save_reg(reg_name, r)


def open_saved(name, timeout=60):
    """-> a connected server object. Raises _mcpclient.MCPError with a plain-words reason."""
    sv = servers()
    if name not in sv:
        raise _mcpclient.MCPError(f"No server named '{name}'. Saved: {', '.join(sorted(sv)) or 'none'}")
    vs = env_vars(name)
    if vs and vs != ["@bearer"] and not logged_in(name):
        raise _mcpclient.MCPError(f"'{name}' needs a login first:  mcp login {name}")
    env = {v: token(name, v) for v in vs} if vs and vs != ["@bearer"] else None
    return _mcpclient.open_server(sv[name], timeout, env, token(name, "@bearer") if vs == ["@bearer"] else "")


def text_of(res):
    import json
    return "\n".join(c.get("text", "") for c in res.get("content", []) if isinstance(c, dict) and c.get("type") == "text") or json.dumps(res)[:3000]
