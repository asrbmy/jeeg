# Changelog

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
