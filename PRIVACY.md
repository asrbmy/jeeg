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
Only when you run a task that needs it. Say `privacy` to see the list; `list` marks those tasks with `[online]`. Today that is 29 of 440 tasks: weather, exchange rates, news, dictionary and Wikipedia look-ups, `check website`, `ping host`, `git pull` and similar. Everything else (calculators, files, notes, reminders, reports, invoices, medicines) works with the network cable unplugged.

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
