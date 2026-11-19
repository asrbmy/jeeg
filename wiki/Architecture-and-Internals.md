# Architecture and Internals

How JeeG is built, so you can read it, extend it and trust it. Everything is Python's standard library; there is no server, no database and no background service (except reminders you set).

## 1. The big picture

```
 you type a line
      |
      v
 jeeg.py  (the engine)  ──────────────►  handles built-in commands itself:
      |                                   list, explain, alias, again, history, doctor, pack, reindex,
      |                                   selftest, misses, stats, tips, vars, batch, ...
      |  otherwise: rank the tasks
      v
 scripts/*.py|sh|bat|cmd|ps1|js   (one file = one task, a separate process)
      |   uses shared helpers: scripts/_lib.py, _store.py, _dates.py, _money.py, ...
      v
 your data folder  ~/.jeeg   (small JSON/JSONL files, written atomically)
```

A task always runs as its **own process**. That is deliberate: a crash, a hang or a bug in one task cannot take down the engine, a timeout can kill it (`--timeout`), and tasks can be written in any language.

## 2. Files in the project

| Path | What it is |
|---|---|
| `jeeg.py` | The engine: reads headers, scores phrases, runs tasks, built-in commands, aliases, variables, batch, history, logs |
| `jeeg_cmds.py` | Extra commands kept apart so the engine stays small: `update`, `plugin ...`, `setup`, `completion`, the local web page, `report`, `share`, routine import/export, the plugin library, the tour |
| `jeeg_api.py` | The Python library (`import jeeg`): `run`, `find`, `plan`, `tasks`, `run_task`, results, hooks |
| `jeeg_bridge.py` | The local HTTP API (`--serve-api`), the JSON-lines pipe (`--stdio`) and the MCP server (`--mcp`) |
| `jeeg_remote.py` | AI mode (`connect ai`): modes, approvals, tunnels, `install mcp`, the safe/read lists, per-app rules |
| `jeeg_connect.py` | Long-running connectors: the Telegram bot and incoming hooks |
| `jeeg_autorun.py` | `autorun`: cron / Task Scheduler entries |
| `scripts/` | The tasks (files not starting with `_`) and the helper modules (files starting with `_`) |
| `library/` | The plugin library (`index.json` with SHA-256 fingerprints, and the plugins) |
| `integrations/` | VS Code, browser extension, Send To, Raycast/Alfred, Home Assistant, JavaScript, OpenAPI description |
| `examples/` | Python and other-language examples |
| `tests/` | The automatic checks, plus `phrases.txt` (phrase => expected task) |
| `tools/` | Build and docs generators: `build_exe.py`, `make_guide_appendix.py`, `make_site.py`, `make_wiki.py`, `fill_packaging.py` |
| `docs/` | The static project page and the searchable task list |
| `packaging/` | Homebrew, Scoop, winget, Chocolatey, AUR, conda recipes (filled from the release) |
| `wiki/` | This wiki |

## 3. What a task is

A task is one file in `scripts/` (or a plugin folder or a `--dir`). Its **name** is the file name without the extension, words joined with underscores: `emi_loan.py` is the task "emi loan". The first lines hold a **header**:

```
# keywords: loan, emi, mortgage
# desc: Monthly instalment for a loan (emi loan 25 lakh 8.5% 20 years)
# category: money
# usage: emi <amount> <rate%> <years>
```

`parse_header` reads the comment lines at the top (the first 15 lines) of any supported language. The recognised keys are:

| Key | Meaning |
|---|---|
| `keywords` | extra words that find the task |
| `desc` | one-line description shown in `list` |
| `category` | group for `list`, packs and AI rules |
| `usage` | the shape of the arguments (marks that the task takes words) |
| `confirm: yes` | ask `[y/N]` before running |
| `priority` | breaks ties |
| `rawargs: yes` / `full` | pass your words untouched / the whole sentence |
| `patterns` | regular expressions (separated by `;;`) that identify the task |
| `private: yes` | never write what you typed to history |
| `network: yes` | the task touches the network (shown by `privacy`; enforced by a test) |
| `stdin: yes` | the task reads piped text |

Runners by extension: `.py` with the same Python that runs JeeG, `.js` with `node`, `.sh` with `bash` (macOS and Linux), `.bat`/`.cmd` with `cmd` (Windows), `.ps1` with PowerShell. Tasks get the shared helpers on their import path, so scripts in your own folders can use `from _lib import args_text` too.

## 4. The index

On start, JeeG reads every script header and keeps the result in `index.json` in your data folder (`{"v": version, "files": {path: entry}}`). Each entry records the name, tokens, keywords, description, category, usage and flags, plus the file's modification time and size. Only files that changed are re-read. `reindex` rebuilds it; deleting it is safe. `--dir` folders, `TASK_SCRIPTS_DIR`, the plugins folder and `scripts/` are all searched; the first copy of a name wins.

## 5. From a line to a run

`run_query` in `jeeg.py`:

1. **Refuse** lines over 2000 characters; strip terminal control characters.
2. **Expand** an alias (only at the start, up to three words) and variables (`$name`, `ans`).
3. **Split a chain** on `and`, `then`, `;`, `&` — but only if every part clearly resolves to a different task and none is a free-text task.
4. **Normalise**: lower-case, drop filler words ("please", "the", "can you"), simplify plurals, apply short-form synonyms.
5. **Score** each task (`score_entry`): words in the task name weigh most, `keywords` slightly less, close spellings less again, and *very common words* (a word shared by many tasks) almost nothing, so they cannot decide alone. A matching `patterns` entry adds a bonus. Words are weighted by how rare they are across all tasks, which is why `open youtube` opens YouTube.
6. **Resolve** (`resolve`): one clear winner runs; an exact tie becomes a numbered menu (exit code 2 without a keyboard); no score becomes "No matching task" with closest suggestions, or a fallback (maths text goes to the calculator, `open <site.com>` opens the site, `open <app>` tries to launch it); typo repair offers "Did you mean...?".
7. **Arguments**: the words that were not used to find the task become its arguments.
8. **Confirm** if the task says `confirm: yes` (unless `--yes`, or the words include `preview` / `dry-run`). With no keyboard, a confirmation task returns exit code 3.
9. **Run** as a subprocess with the timeout; print `>> task (args)`, then the task's output, then `ok in 0.05s` or `failed (exit 1)`.
10. **Record**: append to `history.jsonl` unless the task is `private`; append to `log.jsonl` (task name, exit, seconds; no typed text); on a miss append to `misses.log`.

`explain` runs steps 1-6 and prints the ranking instead of running.

## 6. Exit codes

| Code | Meaning |
|---|---|
| 0 | ok |
| 1 | error or no match |
| 2 | ambiguous (a menu was needed but there was no keyboard) |
| 3 | needs confirmation, or you declined |

## 7. The data folder

Default `~/.jeeg` (`JEEG_HOME` overrides; the old `.taskrunner` is still read). Created with owner-only permissions on macOS and Linux. All writes go through a temporary file and an atomic swap. Helpers in `_store.py` load and save JSON safely; a damaged file is moved aside by `doctor fix`. Plain JSON means a record file can be read, edited and backed up with ordinary tools.

| Kind | Files |
|---|---|
| Engine | `index.json`, `history.jsonl`, `log.jsonl`, `misses.log`, `aliases.json`, `vars.json`, `packs` state |
| Your records | `todos.json`, notes, journal, expenses, budgets, habits, birthdays, contacts, bills, medicines, ledger, stock, ... one file each |
| Automation | `routines.json`, `reminders.json`, autorun entries |
| Connections | registries for webhooks, devices, computers, mail, MCP servers, linked apps (mode `0600`), `app_policy.json`, `browser_policy.json`, `browser-profile/` |
| Housekeeping | `trash/`, `plugins/`, `real test` history |

## 8. Helper modules (`scripts/_*.py`)

| Module | Job |
|---|---|
| `_lib` | argument helpers, `open_url`, `launch`, `fail`, `call`, `data_dir`, `notify`, `need` |
| `_store` | safe JSON storage and period parsing |
| `_dates`, `_time`, `_zones`, `_astro` | forgiving dates, clock parsing and background reminders, city time zones, sunrise and moon maths |
| `_money` | money parsing, Indian digit grouping, live rates |
| `_files`, `_undo`, `_backup`, `_text`, `_sys` | file helpers, the undo log, export/import, text helpers, OS helpers (memory, battery, volume, clipboard) |
| `_net`, `_web`, `_info`, `_netdoc`, `_watch` | tiny HTTP helper (returns `None` when offline), safe public-web fetching, parsers for online services (tested against sample data), network diagnosis, watch lists |
| `_conn`, `_mqtt`, `_device`, `_keystore` | connector helpers (secrets asked privately, private-network checks), a small MQTT client, RFC 8628 device login, system keychain |
| `_adapters`, `_presets`, `_apps`, `_policy` | the linked-app framework, 27 presets, program-to-package names, per-app AI rules |
| `_mcpclient`, `_mcpsaved`, `_mcpcatalog` | MCP client (stdio and https), saved servers, the catalog of 31 servers |
| `_cdp` | the real-browser driver (WebSocket + DevTools protocol) |
| `_realtest`, `_routine`, `_dues`, `_worker` | the real-PC test, routines, due-date lists, the reminder process |

Files named `_*` are never tasks. A privacy test (`tests/test_privacy.py`) lists exactly which helpers may import network modules.

## 9. Safety design

- **One process per task**, a timeout, no shell for external programs (argument lists, never a command string).
- **Input is untrusted**: lines are length-limited and cleaned; text is URL-encoded before it goes into addresses; host names, ports and package names are validated.
- **Allow-lists**: only `http`, `https`, `mailto`, `tel`, `sms`, `whatsapp` links are opened; archives cannot write outside their folder.
- **Confirmation** for tasks that can lose data, with `preview` to look first; destructive tasks move rather than delete.
- **Declared network use**: a task that touches the network must say `network: yes`; `privacy` is generated from that and a test keeps it honest.
- **Private by default**: no account, no telemetry; sensitive tasks (`private`) are not written to history.
- **Secrets** are asked privately, never taken from the command line, stored `0600` or in the system keychain.
- **Reads and writes are separate** for anything an AI or another program can reach.

## 10. AI mode and MCP in one picture

```
 AI app (Claude.ai, Cursor, ...)  ──MCP/HTTP──►  jeeg_remote / jeeg_bridge
                                                     │ mode: safe | read | ask | god
                                                     │ policy: app allow/deny, preview-only, per-action always-allow
                                                     ▼
                                                 run_for_ai ──► jeeg.py ──► task
                                                     ▲
                                  you, in the terminal: answer y/n (or on your phone)
```

- `jeeg_bridge.py` offers three front ends (HTTP, stdio, MCP) over one `dispatch`. They listen on 127.0.0.1 only and refuse web pages, unless you name an origin.
- `jeeg_remote.py` wraps it for an AI: a fixed **safe list**, an optional **read list**, an **approver** that asks you (terminal or phone) with a timeout and a rate limit, a session **log**, and optional tunnels (`cloudflared`, `ngrok`, `ssh`). The environment flag `JEEG_VIA_AI` marks a call as coming from an AI so tasks can apply stricter rules (for example the browser, and linked-app policy).
- Chains are refused in preview-only mode so the preview always covers the whole request.

## 11. Linked apps and MCP clients

A **definition** (`_adapters.py`) names an app's base address, its login style and its actions. A web action has a method and path; a **command** app has one fixed argument list. `GET` actions (and POST marked `read=yes`, and command actions marked `read=yes`) are reads; everything else is a write. `build` fills `{placeholders}` (URL-quoted), `send` talks to the service with size and time limits, and `send_auto` refreshes an expired login once. Logins live in private files or the keychain; the AI never sees them.

MCP servers come in two kinds: a program started over stdio (`Server`) or an https address (`HTTPServer`, streamable HTTP with bearer token, session id, JSON or event-stream replies, public addresses only). Whether a tool only reads is **your** decision (`mcp mark`), never the server's claim.

## 12. The real browser

`_cdp.py` starts a browser with its own profile and `--remote-debugging-port=0`, finds the port in `DevToolsActivePort`, and speaks the DevTools protocol over a hand-written WebSocket (handshake, masked client frames, ping/pong, fragments). Each task connects for a moment; the browser stays running between tasks. `look` stamps elements with `data-jeeg-id` numbers; clicks and keys are real input events. Policy checks (`check_url`, `guard`) apply to an AI before and after every navigation.

## 13. Tests

`tests/` holds the suites; each prints `N passed, M failed`. Routing is tested from `phrases.txt` (every task is also asked by its own name, with typos and polite variants). `selftest` checks that every task is described, compiles and resolves to itself. Servers, programs and keychains are faked locally, so the suites need no internet. The GitHub workflow runs them on Windows, macOS and Linux. Details: [Testing and Releasing](Testing-and-Releasing).

## 14. Packaging

`pyproject.toml` builds a wheel with the engine, helpers and scripts (`jeeg_scripts` is the installed copy). `tools/build_exe.py` makes standalone programs (PyInstaller) in the workflow; releases carry build-provenance attestations. `tools/fill_packaging.py` fills version and hashes for Homebrew, Scoop, winget, Chocolatey, AUR and conda.

## 15. Extending safely: the checklist

When you add a task to JeeG itself:

1. Name it in distinct words (not only very common ones); add `keywords`, `desc`, `category`, `usage`.
2. Say `confirm: yes` if it can lose data; support `preview` if you can.
3. Say `private: yes` for anything personal; say `network: yes` if it touches the network.
4. Add a line to `tests/phrases.txt`; run `selftest` and the routing and privacy tests.
5. Update the task counts (README, USER_GUIDE, PRIVACY) and regenerate docs and this wiki.
