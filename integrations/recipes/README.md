# Recipes: JeeG from other launchers and automation tools

Everything here talks to JeeG on this computer only. Two ways in, pick the simpler one your tool supports:

| Your tool can... | Use |
|---|---|
| run a program or shell command | `jeeg <phrase>` (add `--json` for JSON). Text on standard input works for text tasks. |
| send an HTTP request | the local API: `jeeg --serve-api`, then `POST http://127.0.0.1:8766/v1/run` with `Authorization: Bearer <token>` |

Recipes in this folder:

- `alfred/` Alfred (macOS) workflow steps
- `autohotkey/jeeg.ahk` AutoHotkey v2 (Windows): a hotkey box, and a hotkey that runs a task on the clipboard
- `shortcuts/README.md` Apple Shortcuts (macOS)
- `curl/` curl, PowerShell and Node examples for the local API

Already elsewhere: Raycast (`../raycast/`), Home Assistant (`../homeassistant/`), Windows "Send to" menu (`../sendto/`),
JavaScript library (`../js/`), Python (`../../PYTHON_GUIDE.md`).

For the other direction (something outside tells JeeG to act when an event happens) use the bridge's webhook source,
see `../../BRIDGE.md`.

Honest note: these recipes were written from each tool's documentation and checked for syntax where a checker exists here.
They were not run in Alfred, AutoHotkey or Shortcuts themselves.
