# Changelog

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
