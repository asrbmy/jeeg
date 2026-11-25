# About JeeG, credits and license

**JeeG** is made and maintained by **asrbmy** and owned by **Link with iQ**.

- asrbmy: https://asrbmy.github.io
- Link with iQ: https://linkwithiq.github.io
- Code: https://github.com/asrbmy/jeeg

## What it is built on
- Python standard library only. No packages to install, no account, no telemetry.
- The optional standalone program is packaged with PyInstaller.
- Plugins and recipes talk to apps that belong to their own makers (Chrome, Edge, Firefox, Obsidian, VS Code, n8n, Node-RED and others).

## License
MIT License; see `LICENSE`. If you share JeeG, keep the `LICENSE` file and the credit with it.

## What is proven and what is not
Everything is tested on Linux with scripted stand-ins (fake AI servers, fake webhooks, real headless Chromium for the extension). Not yet proven on real services or other systems: live Claude, OpenAI, DeepSeek or Gemini, real Ollama or LM Studio, real Obsidian, Firefox, Edge, Alfred, AutoHotkey, Shortcuts, n8n, Node-RED, Kestra, Prefect or Sim Studio, and the Windows and macOS builds. The JeeG link protocol has not had an independent security review. See [Testing and Releasing](Testing-and-Releasing) and [Safety and Privacy](Safety-and-Privacy).

## Where things are written down
`README.md`, `USER_GUIDE.md`, `PRIVACY.md`, `SECURITY.md`, `AGENT.md`, `OBSIDIAN_AI.md`, `CHANGELOG.md` and this wiki.
