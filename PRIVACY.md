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
Only when you run a task that needs it. Say `privacy` to see the list; `list` marks those tasks with `[online]`. Today that is 62 of 545 tasks: weather, exchange rates, news, dictionary and Wikipedia look-ups, `check website`, `ping host`, `git pull`, the connector tasks you set up yourself (webhooks, mail, GitHub, MQTT, peers ...), installing programs (your package manager contacts its own servers), watches, RSS feeds, `save page`, `network doctor` and similar. Everything else (calculators, files, notes, reminders, reports, invoices, medicines) works with the network cable unplugged.

Besides tasks, the engine contacts these addresses, only when you type the matching command:

| Address | When | What is sent |
|---|---|---|
| `api.github.com` | `update` | a request for the latest release (no personal data) |
| `raw.githubusercontent.com` | `plugin search`, `plugin get` | a request for the library list or one plugin file |
| any `https` address you give | `plugin install <link>` | a request for that file |
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
