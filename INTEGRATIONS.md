# Using JeeG with other programs

JeeG can be called from any language and any app, all on your own computer. Pick the way that fits:

| You are using | Use | Needs a port? |
|---|---|---|
| Python | `import jeeg` (see PYTHON_GUIDE.md) | no |
| Any language, simplest | `jeeg --json <phrase>` once per call | no |
| Any language, many calls | `jeeg --stdio` (JSON lines) | no |
| Any language, like a web service | `jeeg --serve-api` (local HTTP) | yes, 127.0.0.1 only |
| An app that supports MCP (for example Claude Desktop) | `jeeg --mcp` | no |

## 1. One call: `--json`

```
jeeg --json gst 2500 18
```
prints JSON with the output, the exit code and the task name. `jeeg --list-json` prints every task.

## 2. Many calls: `--stdio`

Start `jeeg --stdio` once. Send one JSON object per line; you get one JSON line back per request. Add an `"id"` and it is echoed back.

```
{"id": 1, "query": "gst 2500 18"}
{"id": 2, "op": "find", "query": "open youtube", "limit": 3}
{"id": 3, "op": "task", "name": "gst_amount", "args": [1000, 18]}
```

Answer shape: `{"ok": true, "result": {...}, "id": 1}` or `{"ok": false, "error": "..."}`. A run result has `query`, `exit`, `ok`, `task`, `output`, `needs_confirmation`, `ambiguous`, `candidates`.

Operations (`op`): `run` (needs `query`), `task` (`name`, `args`), `find` (`query`, `limit`), `tasks` (`category` optional), `categories`, `info` (`name`), `ping`. Optional on run and task: `timeout` in seconds (1 to 300, default 60).

## 3. Local web API: `--serve-api`

```
jeeg --serve-api            # port 8766; or: jeeg --serve-api 8800
```

It prints a token (also saved as `api_token` in your JeeG data folder; `jeeg --api-token` prints it). Send it on every request as `Authorization: Bearer <token>`.

| Request | Does |
|---|---|
| `GET /v1/health` | check it is running |
| `GET /v1/find?q=open+youtube&limit=3` | which tasks match |
| `GET /v1/tasks?category=money` | list tasks |
| `GET /v1/categories` | categories with counts |
| `GET /v1/info?name=gst_amount` | one task's details |
| `POST /v1/run` with `{"query": "gst 2500 18"}` | run a phrase |
| `POST /v1/task` with `{"name": "gst_amount", "args": [1000, 18]}` | run one task by name |

```
curl -H "Authorization: Bearer $(jeeg --api-token)" -d '{"query":"gst 2500 18"}' http://127.0.0.1:8766/v1/run
```

Examples for Node.js, curl and Python are in `examples/other_languages/`.

## 4. MCP: let an app use JeeG as a tool

`jeeg --mcp` is a Model Context Protocol server over stdio with three tools: `jeeg_run`, `jeeg_find` and `jeeg_list`. In Claude Desktop add this to its config file (see `examples/other_languages/claude_desktop_mcp.json`) and restart the app:

```json
{ "mcpServers": { "jeeg": { "command": "jeeg", "args": ["--mcp"] } } }
```

JeeG itself still uses no AI model. MCP just lets an app you already use call JeeG's tasks.

## Limit what outside programs may do: `--only`, `--except`, `--log`

Give a program (or an AI app) only the tasks it needs:

```
jeeg --mcp --only money,text,time          # only these categories (or exact task names)
jeeg --serve-api --except files,system     # everything except these
jeeg --serve-api --log                     # keep a private call log
```

- Names and categories both work (`money`, `gst_amount`). See categories with `jeeg --list-json` or `GET /v1/categories`.
- With `--only` or `--except`, a phrase must match exactly one allowed task. Multi-task sentences ("do X and Y") and built-in commands (history, alias ...) are refused, so they cannot be used to get around the limit. Listings and searches show only allowed tasks.
- `--log` writes `api.log` in your JeeG data folder: time, which interface, the task name and the exit code. It never stores what was asked or the output. It keeps about 1 MB, then starts a fresh file.

## Safety rules (all four ways)

- Everything runs on your computer. The API listens on `127.0.0.1` only, never on the network.
- The API needs the token, checks the Host header, and refuses requests from web pages (any `Origin` header), so a website you visit cannot call it.
- Tasks that ask for confirmation (shutdown, delete, empty trash ...) are **refused** unless you start the server with `--allow-confirm`. Callers cannot turn this on themselves. Think carefully before using `--allow-confirm` with MCP.
- Terminal-only commands (`web`, `setup`, `update`, `plugin` ...) are refused.
- Requests are limited in size (64 KB), time (300 s), output (100,000 characters) and parallel calls (8 at once; more get a 503). A client that stalls for 30 seconds is dropped.
- Calls are not added to your command history.
- Keep the token private. To change it, delete `api_token` in your JeeG data folder and start again, or set `JEEG_API_TOKEN` yourself.
