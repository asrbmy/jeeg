# What JeeG never does

JeeG is built so that you can check these statements yourself.

**Never**
- It never asks you to sign in, and has no account or licence server.
- It never sends usage statistics, crash reports or the text you type anywhere. There is no telemetry code in the engine (`tests/test_privacy.py` looks for it).
- It never uses an AI model or calls an AI service. Matching your words to a task is done on your computer with simple scoring rules; `explain <words>` shows exactly why a task was chosen.
- It never runs in the background on its own. The only background processes are reminders, alarms and timers you set yourself, and they stop when they finish or when you say `stop reminders`.
- It never reads your clipboard, files or folders unless you ask for a task that does.

**Where your data lives**
Only in the `.jeeg` folder in your home directory (or `JEEG_HOME`), readable only by you on Mac and Linux. Notes, expenses, journal, medicines, contacts and the rest are plain files you can open, copy or delete. Tasks marked private (passwords, medicines, clipboard) are not written to your command history.

**When JeeG itself uses the internet**
Only when you run a task that needs it. Say `privacy` to see the list; `list` marks those tasks with `[online]`. Today that is 82 of 602 tasks: weather, exchange rates, news, dictionary and Wikipedia look-ups, `check website`, `ping host`, `git pull`, the connector tasks you set up yourself (webhooks, mail, GitHub, MQTT, peers ...), installing programs (your package manager contacts its own servers), watches, RSS feeds, `save page`, `network doctor` and similar. Everything else (calculators, files, notes, reminders, reports, invoices, medicines) works with the network cable unplugged.

Automatic checking is **off** until you say `update auto on`; then JeeG makes one short request a day and prints one line if a newer version exists. It never installs anything by itself.

Besides tasks, the engine contacts these addresses, only when you type the matching command:

| Address | When | What is sent |
|---|---|---|
| `api.github.com` | `update` (clone or standalone program), `update auto on` | a request for the latest release (no personal data) |
| `pypi.org`, `files.pythonhosted.org` | `update` / `update now` (pip install or unzipped folder), `update auto on` | a request for the newest version, then the new files, checked against PyPI's SHA-256 before anything is replaced |
| `raw.githubusercontent.com` | `plugin search`, `plugin get` | a request for the library list or one plugin file |
| any `https` address you give | `plugin install <link>` | a request for that file |
| the computer you pair with, or a relay you choose | `link …` | only encrypted JeeG link messages to that address (see `LINK.md`); the relay sees addresses and amounts, never content; UDP broadcast on your own network for `link find` |
| your own devices (Home Assistant, Modbus, MQTT, TCP/UDP/WebSocket, REST services you saved) | the matching task or a bridge rule | only what you asked it to send to the address you saved; plain `http`/`ws` only to your own network; bridge listeners (webhook, UDP, TCP) accept data from your network |
| `1.1.1.1:53` | `doctor` | one connection test, no data |

The `web` command opens a page on `127.0.0.1` that only your own computer can reach.

**Tasks that open a website** (`open youtube`, `search google ...`, `send whatsapp ...`) only ask your own browser to open an address. What that website learns is between you and the website; JeeG sends nothing.

**Plugins**
Plugins run as normal programs with your permissions, so they could do anything. JeeG checks the fingerprint of library plugins, shows what each plugin says it does and a quick scan for risky features, and asks before installing. Read a plugin before you trust it. Plugins are not covered by the `privacy` list.

**Check it yourself**
- `python tests/test_privacy.py` checks which files can use the network and which web addresses appear in the engine.
- The whole engine is two readable files (`jeeg.py`, `jeeg_cmds.py`) and a folder of small scripts.

## AI mode and the network

`connect ai` starts a server that listens only on this computer. The tunnel program you install (cloudflared, ngrok or ssh) makes it reachable from the internet, and it and the AI service can see requests and answers. If you use `notify ntfy.sh/TOPIC`, JeeG sends one fixed message (no task text) to that ntfy server. JeeG sends nothing otherwise.

## Connectors

`telegram start` contacts api.telegram.org (long polling) while it runs. Connector tasks contact only the service you configured: your webhook address, your mail provider, api.github.com, your calendar link, your MQTT broker or devices on your own network. Nothing is sent until you set a connector up and use it, and tokens go only to the service they belong to. Say `privacy` for the list of tasks that can use the network.

## The real-PC test (2.19)

- `real test` runs harmless checks on this computer and saves the results in your JeeG data folder. Nothing is sent anywhere by JeeG.
- The report removes your user name, computer name, home folder, IP and MAC addresses, e-mail addresses, passwords in web addresses and anything that looks like a secret. Read it before you share it.
- For linked apps it only records whether a read worked; the app's content is never saved or shown.

## Linked apps (2.18)

- `app login` stores your token or webhook address on this computer in a file only your user can read. It is never printed, never saved in history, and removed from every message.
- `app read` and `app do` contact only the app you named, at the address in its definition, and never follow redirects. JeeG has no server in between.
- What you send through `app do` is not saved in the history.

## What 2.20 adds

- **Command apps** run only programs you named, on this computer, with fixed arguments and no shell. They send nothing anywhere by themselves.
- **Keychain** storage (off by default) talks only to your system's own keychain tool.
- **Device login** talks only to the login address of the app you are logging in to (https), and shows you the code.
- **Event rules** look at your linked apps on a timer you started in a terminal, and nothing else; results stay in `rules.json` on this computer (only short fingerprints of what was seen, plus the last status line).
- **MCP servers** (`mcp add ...`) are programs or https addresses you chose; JeeG talks only to them, and gives each only its own login.
- **AI rules** (`app_policy.json`) are only ever changed by you in a terminal.

## Browser (2.20)

`browser ...` tasks talk to a browser on this computer (its debugging connection listens on 127.0.0.1 only) and, through the browser, to the sites you open. JeeG itself sends nothing anywhere else. The browser uses its own profile folder in JeeG's data folder; page text is never saved in history (`private`).

## Network tasks added in 2.17

- `network doctor` opens a TCP connection to 1.1.1.1 and 8.8.8.8 on port 443 (no data is sent) and looks up `example.com`. It pings your router.
- `who is on my wifi` reads your computer's neighbour table; with `scan` it tries a few ports on addresses next to yours, and only on private networks (192.168.x.x, 10.x.x.x, 172.16-31.x.x).
- `send <file> to my phone` listens on your local network address with a random secret link, serves that one file once, then stops (or after 10 minutes). Nothing leaves your network.
- `watch`, `feed` and `save page` fetch only the addresses you give them, and refuse addresses on your own network. Page text is not sent anywhere.
- `check all computers` and `on <name> run <task>` use your own `ssh`.
- Installing programs runs your package manager (winget, choco, brew, apt ...), which contacts its own servers. JeeG itself sends nothing.
- `query database` opens a file on your disk read-only.

## The local API (`--serve-api`, `--stdio`, `--mcp`)

These only run when you start them. The HTTP API listens on 127.0.0.1 (this computer only), needs a secret token kept in your JeeG data folder (readable only by you on Mac/Linux), refuses requests that come from web pages, and refuses tasks that ask for confirmation unless you start it with `--allow-confirm`. Nothing is sent anywhere by the API itself.

## Plugins
The plugins in `integrations/` talk to JeeG on this computer. The only ones that can reach the internet are the Obsidian plugin's "Ask an AI" commands and `jeeg_chat.py` with a remote provider: they send the text you chose (a selection, or up to 12,000 characters of a note) to the AI company you picked, with your own API key, only when you run the command. Ollama and LM Studio keep it on your computer. JeeG itself has no AI model, account or telemetry.

## The agent (optional)
JeeG has no AI model. If you run `agent setup`, you pick a model. With Ollama or LM Studio nothing leaves your computer. With a company's API, each `agent goal` (or Telegram `/goal`) sends your goal, the remembered facts that match it, and what the tasks it runs print to that company, using your own key. Memory (`memory.json`), skills (`skills.json`), run logs (`agent_runs/`) and settings (`conn_agent.json`, private) stay in your JeeG folder; `agent forget` deletes the key and settings.
