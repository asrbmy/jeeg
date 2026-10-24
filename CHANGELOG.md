# Changelog

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
