# JeeG plugins and extensions

All of these talk to JeeG on **this computer only**. None needs an account, and none sends anything to the internet by itself. The one exception you choose yourself: the Obsidian plugin's "Ask an AI" commands, and `ai/local/jeeg_chat.py` with a remote provider, send text to the AI company you pick, only when you run them.

| For | Folder | How it connects |
|---|---|---|
| Chrome, Edge, Firefox | `browser/` | local API (`jeeg --serve-api --allow-origin ...`) |
| Claude Desktop, any MCP app | `ai/claude/` | `jeeg --mcp` (`install mcp <app>` sets it up) |
| ChatGPT, OpenAI tools, Gemini | `ai/openai/` | tool lists + OpenAPI file |
| Ollama, LM Studio, local models | `ai/local/` | `jeeg_chat.py` (standard library only) |
| VS Code | `vscode/` | starts the `jeeg` command |
| Obsidian (+ ask Claude, ChatGPT, DeepSeek and more about notes) | `obsidian/` | local API; your own API keys for the AI commands |
| Raycast, Alfred, AutoHotkey, Shortcuts, curl, PowerShell | `raycast/`, `recipes/` | command line or local API |
| n8n, Node-RED, Kestra, Prefect, Sim Studio, Python runners | `workflows/` | local API (they call JeeG) and `rest post` (JeeG calls them) |
| Home Assistant | `homeassistant/` | local API |
| JavaScript | `js/` | `jeeg --json` |

The one rule for everything that uses the local API: **the token is a password.** Keep it out of web pages, shared
folders and GitHub, and limit what a plugin may run with `--only` (for example `--only text,money,utility,time`).
Tasks that ask first are refused unless you start the API with `--allow-confirm`, which plugins should not need.

Full details: `../INTEGRATIONS.md`, `../MCP.md`, `../REMOTE_AI.md`.
