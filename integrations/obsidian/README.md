# JeeG for Obsidian (desktop)

Two ways to connect AIs (Claude, ChatGPT, DeepSeek, Gemini and more) with your notes:

**A. Ask an AI from inside Obsidian** (this plugin). Commands: *Ask an AI about the selection*, *about this note*,
*Summarize this note with an AI*, *Ask an AI (no note text sent)*. The answer is added as a collapsed callout.
Providers: OpenAI (ChatGPT), Anthropic (Claude), DeepSeek, Google (Gemini), OpenRouter (hundreds of models), Groq, Mistral,
Ollama and LM Studio (on your computer), or any OpenAI-style address. You paste your own API key and the model name in
Settings > JeeG. Text is sent only when you run one of these commands, only the selection or up to 12,000 characters of the
note, and only to the provider you picked (Ollama and LM Studio keep it on this computer). Your provider's own terms and
prices apply. Notes are marked as data to the model, so text inside a note cannot give it orders.

**B. Let an AI app read your notes through JeeG.** In a terminal: `jeeg`, then `vault set` (finds your Obsidian vault) .
After that `vault search <words>`, `vault read <note>`, `vault list`, `vault recent` work, and are read-only.
Claude Desktop (and other MCP apps, run `install mcp claude desktop read yes`) can then answer "search my notes for the
beta launch". Local models can do the same with `ai/local/jeeg_chat.py --only notes`. `vault append` and `vault new`
add text but never overwrite or delete, always ask first, and cannot reach outside the vault or into hidden folders.

**C. Claude.ai, DeepSeek and ChatGPT websites editing your notes** (add, change, remove, with undo): see `../../OBSIDIAN_AI.md`.


Adds three commands to the command palette (Ctrl/Cmd+P):

- **Run a task on the selection and replace it** (e.g. select a list, task `sort lines`)
- **Run a task on the selection and add the answer below**
- **Run a task and insert the answer** (e.g. `gst 2500 18`, `convert 5 km to miles`)

## Install by hand
1. Make the folder `<your vault>/.obsidian/plugins/jeeg/` and copy `manifest.json` and `main.js` into it.
2. In Obsidian: Settings > Community plugins > turn on **JeeG**.
3. In a terminal, keep this running: `jeeg --serve-api --only text,money,utility,time`
4. In the plugin's settings, paste the token from `jeeg --api-token`.

Only `127.0.0.1` is contacted. Tasks that ask for confirmation are refused. The token is stored in the plugin's `data.json`
inside the vault, so exclude that file if you sync the vault with other people or a public repository.

Not tested inside a real Obsidian, and the AI commands were tested against stand-in servers, not the live services: it was syntax-checked and its logic is the same as the browser extension's, which
was run in Chromium. Obsidian's API can change between versions.
