# Changelog

## 2.16.0

- **Connectors** (see `CONNECTORS.md`). Everything is off until you set it up; secrets are asked for privately and kept in files only you can read.
  - **Telegram bot:** `telegram setup`, `telegram start [safe|read|ask|god]`. Outbound only (no tunnel). Chats must be paired with a one-time code shown on the computer; 5 wrong codes lock pairing; groups ignored; same modes and limits as AI mode.
  - **Incoming hooks:** `hook add name = task`, `hook listen`. A link starts one saved task and nothing else; confirmation tasks are refused; rate limited.
  - **Tasks:** `webhook` (Slack, Discord, Zapier, n8n ...), `wake` (Wake-on-LAN), `computer` and `on <name> run <task>` (ssh), `device` (Shelly Gen1/Gen2, Tasmota), `mqtt`, `android` (adb), `serial`, `peer` (JeeG to JeeG), `mcp add/tools/call` (JeeG as an MCP client), `mail setup/inbox/send`, `github login/inbox/issues/prs`, `calendar feed` (Google/Outlook/Apple private iCal links, read only).
  - **Other languages:** `integrations/openapi/jeeg-openapi.json` (OpenAPI 3 description of the local API) and `integrations/js` (a dependency-free JavaScript/TypeScript client with types).
- Routing: a task whose header says `priority: 4` or more now gets double pattern weight, so command-like forms (`on pi run ...`) beat a plain keyword match. `send mail ...` now goes to `compose email`.
- Tests: `tests/test_connect.py` (134+ checks against fake Telegram, webhook, plug, MQTT, mail, GitHub, adb and ssh servers on this computer, two JeeGs talking to each other, JeeG using its own MCP server, and the JavaScript client). `tests/phrases.txt` has 21 more routing phrases.

## 2.15.0

- **`selfcheck`:** real, harmless checks on your own computer (runs a task, two tasks in one line, a file task, unicode, a bad command, a local server, AI mode locally, tunnel program, Pillow, data folder). Uses a throw-away data folder. The CI now runs it on Windows, Mac and Linux, and the standalone programs run it before release. `MANUAL_TEST.md` lists what only a person can check.
- **AI mode:**
  - "Allow always (this task, this session)": a button on the phone page, or `a` in the terminal. It covers only that one task name and only until AI mode closes; confirmation questions never get it.
  - `limit N` (default 100, max 1000 requests per session) and a fixed cap of 5 non-safe tasks per minute.
  - `notify ntfy.sh/TOPIC` sends a short ping (no details, at most one per 30 seconds) to the free ntfy app when the AI is waiting. Opt-in: it contacts the ntfy server you name.
  - `ai log` / `ai log list` shows saved session logs.
  - `install mcp claude-desktop|cursor [read|full] yes` writes JeeG into that app's MCP settings (safe tasks only by default; a backup is kept; a broken settings file is never overwritten; `remove` takes it out). No tunnel needed.
- **New tasks:** `payment reminder` (polite message from your ledger or from a name and amount; copies it), `action items` (to-do lines from meeting notes, simple rules), `screen text` (screenshot, read the text, copy it; the screenshot is not saved).
- **Preview mode** (`preview` as a word) for `clean temp files`, `empty trash`, `shred file` and `replace in files`: shows what would happen and changes nothing, without the confirmation question.
- **Fuzz test** (`tests/test_fuzz.py`, fixed seed, also runs in CI): thousands of odd phrases, option strings, JSON messages and HTTP requests against the router, AI mode and the server; none may crash it.
- **Packaging:** winget manifest templates and `tools/fill_packaging.py` (fills version and hashes from a release); notes on signing in `packaging/winget/README.md`.

## 2.14.0

- **Approve from your phone.** `connect ai phone` (ask or god mode) also shows each y/n question on a phone page, with big Allow and Deny buttons. The first answer wins: the phone or the terminal. The page has its own secret link and a 6-digit PIN that are shown only in the terminal (the AI is never told them); 5 wrong PINs lock it; it closes with the AI link; no answer in 60 seconds still means no. It works from anywhere the tunnel link reaches (mobile data included). With `no tunnel` only this computer can open it.
- Tests: `tests/test_remote.py` now has 113 checks. The page was also driven in a real headless browser (PIN, question, Allow, task ran).

## 2.13.0

- **AI mode upgrades.**
  - `connect ai read`: safe tasks plus look-only tasks (disk space, file lists, git status, system info ...). Nothing that changes anything.
  - `connect ai allow files,system`: let whole task categories run without asking (unknown category names are refused).
  - `connect ai keep`: the secret part of the link is saved (private file in your JeeG folder) and reused, so a fixed address (for example your own cloudflared/Tailscale tunnel with `url ...` and `port ...`) needs adding to the AI only once. `connect ai forget` deletes it.
  - Session log: every call is also written to `ai-sessions/<date>.log` in your JeeG folder (only you can read it). `connect ai no log` turns it off.
- **New tasks:** `health check` (one-screen disk, memory, CPU, battery, uptime with warnings), `contact sheet <folder>` (one picture of thumbnails, needs Pillow), and `search clipboard history <word>`.
- The web page has a light/dark button (remembers your choice).
- Tests: `tests/test_remote.py` now has 85 checks; 7 new routing phrases.

## 2.12.0

- **AI mode: `connect ai`.** Lets an AI assistant (Claude.ai, ChatGPT, any agent that can open a link) use JeeG on your computer. JeeG starts a small server that listens on 127.0.0.1 only, starts a tunnel program you already have (`cloudflared`, `ngrok`, or `ssh` to localhost.run) and prints a temporary https link. Paste the link into the AI (for Claude.ai: Settings > Connectors > Add custom connector > paste the MCP link).
  - The link contains a 43-character random secret; every wrong guess gets the same plain 404; browsers (Origin header) and unknown Host names are refused; it closes after 30 minutes (`for 90 minutes`, maximum 240) or on Ctrl+C.
  - Three modes: `connect ai safe` (only the fixed safe list), `connect ai` (**ask**, the default: safe tasks run at once, anything else waits for your y/n in the terminal, no answer in 60 s = no), `connect ai god` (every task; tasks that change or delete things still need your y).
  - Speaks MCP (`jeeg_run`, `jeeg_find`, `jeeg_list`) and a plain URL API (`/run?q=...`) for AIs that can only open links.
  - Terminal-only commands (`web`, `setup`, `update`, `plugin`, `autorun`, `report`, `share`, `connect`) stay blocked. At most 4 requests at once, 120 per minute, 16 KB bodies, 30 KB answers. Every call is printed in the terminal.
  - `connect ai no tunnel` gives a local link only; `connect ai url https://...` uses an address you already have (for example Tailscale Funnel).
  - JeeG has no AI in it and sends nothing itself. The tunnel provider and the AI service see what passes through the link, and task output goes back to the AI.
- Tests: `tests/test_remote.py` (63 checks, using fake tunnel programs). The real Claude.ai connection and real tunnels could not be tested in the build sandbox.

## 2.11.0

- **Phone page, two modes.** `web lan` is **safe mode** (a fixed list of about 70 calculators, converters and small lists). `web lan god` is **god mode**: every task can run from the phone, including opening apps, reading and changing files, chaining with `then`, and tasks that ask for confirmation (a "Yes, run it" button appears first). Add `for 60 minutes` to change the default 30-minute limit (maximum 240).
  - God mode needs the secret link **and** a 6-digit PIN that is shown only in the terminal; 5 wrong PINs lock it; it closes by itself when the time is up; every command is printed in the terminal with the phone's address; the page shows a red GOD MODE banner and a countdown.
  - Terminal-only commands (`web`, `setup`, `update`, `plugin`, `autorun`, `report`, `share`) stay blocked in both modes, because they change JeeG itself.
  - Still plain http on your Wi-Fi: use it only on a network you trust.
- Tests: `tests/test_phone.py` (41 checks).

## 2.10.0

- **Your own variables:** `set var rate = 18`, then use `$rate` (or `${rate}`) in any phrase: `gst 1000 $rate`. `vars` lists them, `remove var rate` deletes one. Unknown `$names` are left as typed, so `$5` still means five dollars.
- **`ans`:** `calculate` remembers its last answer; use `calculate ans * 2`, or `$ans` in any other task (`gst $ans 18`).
- **Spelled-out numbers:** `calculate five thousand times 3`, `emi five lakh 8.5 5 years` (tasks that use the shared number reader).
- **`batch <file>`:** run a text file of phrases, one per line (`#` comments, up to 200 lines); stops at the first failure unless you add `keep going`. Terminal-only commands such as `web`, `update` and `setup` are skipped.
- **Local search index:** `index folder Documents` builds a full-text index (SQLite FTS5) of text, notes, code, HTML and Word files; `search index invoice march` finds them, best match first, with a snippet. `index update` re-reads only what changed; `index remove` forgets a folder (your files are never touched). Files that look like secrets (.env, keys, passwords, tokens), hidden folders, `node_modules`, links and binary files are never indexed, and the index file is private to you. Nothing leaves your computer.
- **Spending analytics:** `spending trends` (6 months, what grew or shrank, same-day comparison), `spending forecast` (month-end projection against your budgets), `spending anomalies` (unusually large or double-entered expenses).
- A closed pipe (`jeeg ... | head`) no longer prints a Python error.
- Tests: `tests/test_v210.py` (116 checks).

## 2.9.0

- **10 new tasks (488 after that release):** `csv to json`, `chart csv` (HTML bar chart), `readability` (accepts piped text), `replace in files` (asks first, keeps backups), `strip exif` (optional Pillow), `profit margin`, `compare loans`, `freelance rate`, `toml to json` (Python 3.11+), `watch folder` (asks first).
- **Remembers your pick** when "More than one task fits" (short phrases only; `alias remove` undoes it).
- **Routine variables:** `{today}`, `{date}`, `{month}`, `{year}`, `{weekday}`, `{week}`, `{time}`.
- **`web lan`:** phone page with a secret link, host and origin checks, a fixed list of about 70 safe tasks, and at most 4 requests at once.
- **`update now` for the standalone program:** downloads the release file, checks its SHA-256, replaces the program. `report` writes a bug-report file; `share plugin/routines/aliases` writes one shareable file.
- **API:** `--allow-origin chrome-extension://ID` lets named browser extensions call the local API (CORS preflight handled); web pages are still refused.
- **Standalone program (no Python needed):** `python tools/build_exe.py`; the `build-exe` workflow attaches Windows, Mac and Linux files and `.sha256` files to each release. `DISTRIBUTION.md` explains publishing to PyPI, Homebrew, Scoop, winget, Chocolatey, AUR, conda-forge, VS Code, Docker and GitHub Pages; ready files in `packaging/scoop` and `packaging/docker`.
- **Integrations:** browser extension (`integrations/browser`), Send to JeeG for Windows/Linux/macOS (`integrations/sendto`), Raycast and Alfred, Home Assistant example.
- `tools/make_guide_appendix.py` rebuilds the task table in USER_GUIDE.md (it was missing 10 tasks from 2.8).
- **Security fixes found by review before release:** the phone page now uses a fixed list of task names (whole categories also held tasks that read files or the clipboard or open websites on the computer); downloads and the update check refuse redirects to plain http; `replace in files`, `report` and `share` never write through a symbolic link; the phone page limits parallel requests and times out stalled connections; Send to JeeG on Linux protects file names that start with a dash; `strip exif` handles damaged or huge images.
- Tests: `tests/test_v29.py` (134 checks).

## 2.8.0

- **Use JeeG from Python:** `import jeeg`, then `jeeg.run("gst 2500 18")`, `jeeg.gst_amount(1000, 18)`, `jeeg.find(...)`, `jeeg.tasks()`, and `jeeg.JeeG(home=...)` for your own data folder. Results carry `.ok`, `.output`, `.exit`, `.task`. Calls never prompt, are not added to history, and are thread-safe.
- `jeeg.run_many([...])` for several phrases at once and `await jeeg.arun(...)` for asyncio programs.
- 15 new tasks (478 in all): `cgpa`, `marks` percentage, `study plan`, `heart rate zones`, `macros`, `trip budget`, `income tax` (new vs old regime), `ppf`, `hra`, `attendance` (how many classes you can skip), `electricity bill`, `subscriptions`, `json diff`, `cron` explainer, `jwt` decoder.
- Fixed: "what is the date today" now shows the time and date; `add bill ...` no longer clashes with `electricity bill`; symbols such as `*` are kept for tasks that read the whole sentence.
- **Work with other programs:** `jeeg --serve-api` (local HTTP API with a token), `jeeg --stdio` (JSON lines for any language), `jeeg --mcp` (MCP server for apps such as Claude Desktop), `jeeg --api-token`, `--allow-confirm`. See INTEGRATIONS.md and `examples/other_languages/`.
- **Limits for outside callers:** `--only` / `--except` (categories or task names), `--log` (private call log with no content), at most 8 calls at once, 30-second client timeout, short or weak tokens refused, token file permissions re-tightened, bad UTF-8 on stdin no longer crashes the pipe.
- Tested every task against 26 hostile inputs each (path tricks, shell characters, huge numbers, emoji, control characters): no crashes found.
- **22 more tasks (478 in all):** `salary breakup`, `interest tax`, `severance`, credit card dues (`add card`), `sip goal`, `rotate pdf`, `compress pdf`, `watermark pdf`, `pdf to images` (the PDF tasks need `pip install pypdf`; pictures also need `pypdfium2 Pillow`), `gpa planner`, `cite`, `medicine stock`, `bp` / `sugar` / `health summary`, `fast start`, `cylinder changed`, `milk` / `maid absent`, `flat` (flatmate split), `regex explain`, `color`, `env check`, `verify checksum`, `http headers`, `my habits`.
- **Chaining:** `gst 2500 18 then save it to a note` (also copy, speak).
- **Piped input:** `type notes.txt | jeeg word count` for the text tools (1 MB limit).
- **autorun:** schedule a phrase or routine with Task Scheduler or cron (`autorun add ... at 9:00 weekdays`).
- **Typo fixing** tries every close spelling of each word; **plugin update / outdated**; five more library plugins (`morse`, `workdays`, `anagram`, `recipe scale`, `allowance split`).
- Fixed: counting or hashing very long text no longer fails with "name too long"; `reading time` accepts piped text; dates without a year in logs mean the most recent one.
- Project: `tests/test_quality.py` (every task well formed, size and speed budgets), a searchable task page (`docs/tasks.html`), terminal pictures in the README, VS Code starter extension, security policy timelines, bug report template asks for `doctor`.
- **Automatic releases:** push a new `__version__` to main and the tag, GitHub release and PyPI upload happen by themselves (see CONTRIBUTING.md, "Releasing").
- Library: `jeeg.on("before"/"after", fn)` hooks, `jeeg.watch(phrase, every=300, callback=...)`. Command line: `jeeg --list-json` lists every task as JSON for programs in other languages.
- New `examples/` folder and `tests/test_api.py`.

## 2.7.0
- `--json` and `--output FILE` for use from other programs; the tour is offered once on first run; `misses export` / `misses clear`.
- Money ledger (`lend`, `borrow`, `ledger`, `settle`); warranty, vehicle and vaccine due dates (included in `what is due`); weight log (and a trend in `life report`); reading list.
- A speed guard test; plugin sharing guide and issue templates.

## 2.6.0
- Files: `pdf to text`, `read text from <picture>` (OCR), `compress pictures`, `rename files ... as <pattern>` (preview, undo).
- Tracking: `life report` (visual page), `study log`, medicines (`add medicine`, `medicine today/taken/remind`), `what is due`, `journal prompt`.
- Plugin library (`plugin search`, `plugin get`) with SHA-256 fingerprints; four starter plugins in `library/`.
- `routines export/import`, `alias export/import`, `doctor fix`, `learn` tour, short-form fallback (`mail` -> `email`).
- `privacy` command and `[online]` marks; `PRIVACY.md`, `SECURITY.md`, `tests/test_privacy.py`.
- Reach: GitHub Pages site (`docs/`), demo GIF, Homebrew template, signed-release workflow (`publish.yml`).

## 2.5.0
- `pip install jeeg` (package with a `jeeg` command); `setup` wizard.
- `update` / `update now` checks GitHub releases (only when asked).
- Plugin tools: `plugin new | install | export | remove | list`, with size limit, built-in name protection and a risk scan.
- Typo repair when nothing matches; `completion bash|zsh|powershell`.
- `web`: a private local page (127.0.0.1 only, token, host and origin checks).
- New tasks: `invoice`, `rd` (recurring deposit), `save clipboard`, `clipboard history`.
- No traceback when output is piped (`jeeg list | head`).
- CI also builds and installs the wheel; 64 new command tests.

## 2.4.1
- Security hardening: safe link types, safe archive extraction, validated import, private data folder, input limits, friendly error line.

## 2.4.0
- `undo`, contacts and email, budgets, countdowns, `search my data`, file and text tools, `plugins` folder.
