# Security policy

## Reporting a problem
Please do not open a public issue for a security problem. Report it privately:

- **GitHub:** https://github.com/asrbmy/jeeg/security/advisories/new  (or the **Security** tab, then **Report a vulnerability**)

Include what you typed, what happened, and your system (`jeeg --version`; `doctor` shows more). Do not include real passwords, tokens or personal files.

### What to expect
| Step | Target time |
|---|---|
| We confirm we received it | within 3 days |
| First assessment (real issue or not, how serious) | within 7 days |
| Fix released for a confirmed high-severity problem | within 30 days |
| Fix released for lower-severity problems | next regular release |
| Public note in `CHANGELOG.md` and the GitHub advisory | when the fix is out, crediting you if you wish |

This is a small project run by volunteers, so these are goals, not guarantees. If you hear nothing in a week, write again on the same advisory.

### Scope
In scope: the `jeeg` code and scripts in this repository, the plugin library and its fingerprints, the local web page, the local API (`--serve-api`, `--stdio`, `--mcp`), and the release workflow. Out of scope: problems that need you to install a plugin or run a script you did not trust, and issues in Python, your operating system or other software.

## The network-facing parts (2.9)
- **Connectors (CONNECTORS.md):** all off until set up. `telegram start` is outbound-only (long polling to the Telegram servers); a chat can use it only after pairing with a one-time 6-digit code shown on the computer (5 wrong codes lock pairing; only private chats); modes, request limit, non-safe cap and session log are the same as AI mode; the token is sent only to the Telegram host (an address override is accepted only if it points at this computer, for tests). `hook listen` serves `/<256-bit secret>/<name>` on 127.0.0.1 behind your tunnel: it runs only the saved task, ignores the request body, refuses confirmation tasks, allows 12 calls a minute and 2 at once, and answers a wrong secret with the same 404. Connector tasks keep secrets in 0600 `conn_*.json` files, ask for passwords and tokens through a hidden prompt (never the command line), never print them, accept plain http only for this computer or private addresses, require private addresses for devices, pass ssh targets after `--` and quote the remote task, validate every adb/serial/MQTT argument, and send mail to exactly one validated recipient with a single-line subject. `mcp call` starts the server command you saved and asks first.
- `connect ai` (AI mode): a server on 127.0.0.1 only, reached through a tunnel program you start. The link holds a 256-bit random secret (constant-time compare, identical 404 for wrong guesses); browser requests (Origin) and unknown Host names are refused; time limit (30 minutes default, 240 max); 4 parallel requests, 120 per minute, 16 KB request bodies. Modes: `safe` (fixed list, no chaining), `read` (safe list minus writers, plus look-only tasks),  `ask` (safe list automatic, everything else needs your y in the terminal, no terminal or no answer = no), `god` (all tasks; tasks that need confirmation still need your y). `limit` caps requests per session (default 100) and at most 5 non-safe tasks run per minute; "allow always" is per task name, per session, and never for confirmation questions; `notify` (opt-in) sends a fixed message with no details to the ntfy server you name; `install mcp` edits only the `mcpServers.jeeg` entry of an AI app's settings, keeps a backup, refuses broken files, and defaults to the safe list. `phone` adds an approval page under a separate 192-bit secret path with a 6-digit PIN (5 wrong = locked, strict CSP, same-origin only, answers must be a real JSON boolean); the AI is never given that path or PIN, and it closes with the AI link. `keep` stores the link secret in a 0600 file (delete it with `connect ai forget`). Calls are logged to a 0600 session log. Terminal-only commands are blocked. Risks you accept: whoever has the link can use the allowed tasks; the tunnel provider and the AI service can see requests and answers; task output goes to the AI and could contain text that tries to steer it (prompt injection), which is why `ask` is the default.
- `web lan god` (phone page, god mode): every task except the terminal-only commands; needs the secret link AND a 6-digit PIN shown only in the terminal; 5 wrong PINs lock it; a time limit (30 minutes by default, 240 at most) ends it; confirmation tasks need a button press; each command is printed in the terminal. Anyone with link and PIN can use JeeG on your computer as you, over plain http, so use it only on a trusted Wi-Fi and stop it when you are done.
- `web lan` (phone page, safe mode): off unless you ask; secret link plus a per-session token, Host and Origin checks, a fixed list of about 70 safe tasks (by name), no chaining, 4 requests at once, 30 s timeouts, plain http (use only on a trusted network).
- Browser extensions: `--allow-origin` accepts only `chrome-extension://` and `moz-extension://` addresses you name; web pages are always refused.
- Updates (`update now`, standalone program only): https only (redirects to http are refused), the file must match its published SHA-256, and nothing is replaced if the check fails. The hash comes from the same release, so it protects against corruption and mix-ups, not against someone who controls your GitHub release.

## Supported versions
Only the latest release is supported.

## What JeeG protects
- Links: only `http`, `https`, `mailto`, `tel`, `sms` and `whatsapp` links are opened.
- Files: archives cannot write outside the folder they are extracted to; imports and backups are validated; file moves and renames can be undone and never overwrite.
- Data: the data folder is private to you on Mac and Linux; private tasks are not written to history.
- Input: control characters are removed and very long lines are refused.
- Plugins: size limit, built-in names protected, fingerprint check for library plugins, a risk scan and a confirmation before installing.
- Web page (`web`): listens only on `127.0.0.1`, needs a random token, rejects unknown Host and Origin headers, declines tasks that need confirmation.
- Local API (`--serve-api`): `127.0.0.1` only, token required, refuses web pages, size/time/parallel limits, optional `--only` / `--except` allow-lists and a content-free `--log`. `--stdio` and `--mcp` use the same rules. Tasks that ask for confirmation never run unless you start with `--allow-confirm`.
- Piped input and `autorun`: piped text is capped at 1 MB and never run as a command; scheduled phrases are quoted for cron and Task Scheduler and cannot be `update`, `plugin` or `setup`.

## What is not protected
- Plugins and extra script folders run with your permissions. Only install ones you trust.
- JeeG does not sandbox the tasks it runs. A task that deletes things asks first (`confirm`), but you are responsible for what you confirm.

## Verifying a release
Releases uploaded to PyPI by the `publish` workflow carry build provenance. Check one with:

    gh attestation verify jeeg-X.Y.Z-py3-none-any.whl --repo asrbmy/jeeg

(download the wheel from the GitHub release first). The workflow also uploads the files and their SHA-256 sums to the release page.
