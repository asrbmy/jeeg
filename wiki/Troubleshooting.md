# Troubleshooting

Start with `doctor`, then `selftest`. Set `JEEG_DEBUG=1` to see full error details.

| Problem | What to do |
|---|---|
| `python` not found | Install Python from python.org and tick "Add Python to PATH"; on Windows try `py jeeg.py` |
| `jeeg` command not found after install | Add the folder the installer printed to PATH and open a new terminal |
| "No matching task" | `list`, use the words in the task name, `explain <words>`, or make an alias |
| A menu appears | Two tasks fit equally; pick a number or be more specific (`open youtube music`) |
| It picked the wrong task | `explain <words>`; make the wording more specific; `alias add` |
| "needs confirmation; re-run with --yes" | JeeG was started without a keyboard; add `--yes` only if you mean it |
| A task says a tool is missing | Install what it names ([Install and First Run](Install-and-First-Run)) |
| You edited a script and nothing changed | `reindex` |
| A script's header is ignored | Headers must be in the first 15 lines and start with `#` |
| A web task fails | You may be offline: `check internet`. Online tasks say so plainly |
| A reminder never fired | Check `show reminders`. Reminders do not survive a computer restart |
| Data looks damaged | `doctor fix` moves damaged files aside and rebuilds the index |
| Restore from backup | `import data file.zip` (current data is saved first) |
| Undo a file move or rename | `undo` |
| Something kept failing | `stats` flags tasks that fail often |

## Specific areas

**AI mode / tunnels.** `connect ai` needs `cloudflared` or `ngrok` (or `via ssh`, or `no tunnel` for this computer only). If the AI cannot reach the link, make sure the program is running and the link is the one ending `/mcp`. `ai log` shows what happened. See `REMOTE_AI.md`.

**`install mcp` did nothing.** Run it without `yes` first to see the file it would edit. Files with comments are left alone (plain JSON only). Use the "paste" form (`install mcp zed`).

**Linked apps.** After login run one read action. A 401 means the token is wrong or expired; log in again. Presets are untested against live services.

**Browser.** "Could not find Chrome..." means set `JEEG_BROWSER` to the full program path. If the browser closes straight away, another window may be using JeeG's profile: `browser close` and retry. "There is no element [n]": run `browser look` again, numbers change when a page changes. An AI that says "address is not allowed": the site is local/private or against your lists (`browser policy`).

**Windows/macOS-only tasks** (volume keys, startup list, keychain, autorun) were not run on real machines. Run `real test run all` and `real test report`, then report problems with `report` (a safe file with no personal data).

**Still stuck?** `report` writes `jeeg-report.txt` (version, system, doctor result; your home path and user name hidden). Read it, then attach it to an issue.
