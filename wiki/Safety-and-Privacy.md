# Safety and Privacy

## What is private
- Everything runs on your computer. No account, no telemetry, no AI model inside.
- Online tasks (weather, news, currency, Wikipedia, dictionary, `check website`, `ping host`, `git pull`, connectors, installs, feeds, watches ...) are listed by `privacy` and marked `[online]` in `list`. Everything else works with the network unplugged. Count: 65 of 548 tasks.
- Web tasks open a page in your normal browser; JeeG never reads your passwords.
- `breach check` sends only the first 5 characters of a password hash to the Have I Been Pwned range service; the password never leaves.
- Password, medicine and money-ledger tasks are `private`: never written to history. The log keeps task names and results, not what you typed.
- Update checks and plugin library lookups contact GitHub only when you ask.

## Confirmations
Tasks that can lose data or change the system ask `[y/N]` first (shutdown, restart, kill process/port, delete tasks, shred, `undo last commit`, `git push`, `pip install`, empty trash, installs ...). They carry a `*` in `list`.
- Add `preview` to see what would happen. Preview needs no confirmation.
- Started by another program with no keyboard? Confirmation tasks refuse unless you add `--yes`.
- Nothing is deleted outright: `delete old downloads` moves files to a holding folder and tells you where.
- `bulk rename` previews first; `apply` does it; it refuses name collisions. `undo` reverses.

## Built-in protections
- Zip/tar extraction refuses paths that escape the folder and unsafe tar entries.
- Links with schemes other than http, https, mailto, tel, sms, whatsapp are never opened.
- Typed text is URL-encoded before it goes into addresses.
- Host names, ports and package names are validated before reaching other programs.
- Lines over 2000 characters are refused; terminal control characters are stripped.
- Writes are atomic (temp file then swap): a crash cannot leave half a file.
- Your data folder is readable only by you on macOS and Linux.
- `import data` checks every file and backs up current data first.
- Unexpected problems print one plain line; `JEEG_DEBUG=1` shows details.

## Where your data lives (`~/.jeeg`)

| Item | Contents |
|---|---|
| `index.json` | script cache (safe to delete) |
| `history.jsonl` | what you typed (not private tasks) |
| `log.jsonl` | task, result, seconds (no typed text) |
| `misses.log` | phrases that matched nothing |
| `aliases.json`, `routines.json` | editable |
| `reminders.json` | background reminders |
| one file per record type | to-dos, notes, journal, expenses, shopping, links, habits, birthdays, snippets, contacts |
| `trash/` | files moved by delete tasks |
| `browser-profile/` | the real browser's own profile |
| login and policy files | `0600`, mode private; see [Linked Apps](Linked-Apps) |

Back up by copying the folder or `export data`. Reset one thing by deleting its file.

## Trust model for extensions
Scripts, plugins and extra folders run with **your** permissions, like any program. Install only ones you trust. `plugin install` shows what a plugin says it does, its size and a scan for risky features before asking.

## When an AI is involved
An AI can never link apps, add MCP servers, log in, mark tools as read-only or change policy; only you do that, in a terminal. Reads and writes are separate; writes always ask. See [AI Mode and MCP](AI-Mode-and-MCP).

## Honest limits
Parts specific to Windows and macOS were written carefully but were tested on Linux only. Online tasks were tested against sample replies, not live services. `real test run all` on your own computer is how to check.
