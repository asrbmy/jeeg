# AI Mode and MCP

JeeG has no AI inside. But AI apps can use JeeG as a **tool**, and JeeG can use **other MCP servers**. In both directions you stay in control.

## A. Let an AI use JeeG: `connect ai`

1. Install a tunnel program once (JeeG does not bundle one): `cloudflared` (free, no account) or `ngrok`. Or `connect ai via ssh`, or `connect ai no tunnel` (link works only on this computer).
2. Type `connect ai`. JeeG prints links ending in `/mcp` and `/`.
3. **Claude.ai:** Settings > Connectors > Add custom connector, paste the `/mcp` link, start a new chat and say "Use my JeeG to check disk space." Other AIs: paste the short message JeeG prints.
4. Watch the terminal; answer `y` when asked. Ctrl+C closes it and the link stops working at once.

### Modes

| Command | The AI can |
|---|---|
| `connect ai safe` | only calculators, converters, small lists; no chaining |
| `connect ai read` | safe tasks plus look-only tasks (disk space, file lists, git status) |
| `connect ai` (ask) | safe tasks at once; everything else waits for your `y` here (60 s no answer = no) |
| `connect ai god` | every task; delete/change tasks still ask |

Options: `for 90 minutes` (default 30, max 240), `allow files,system`, `keep` / `forget`, `limit 50`, `no log`, `phone` (answer on your phone), `notify ntfy.sh/TOPIC`, `port 8800`, `url https://...`, `via cloudflared|ngrok|ssh`, `preview only`. `ai log` shows the session log.

### Controls on apps (2.20)
`app ai allow|deny <app>`, `app ai dry on` (previews only), "always allow" for one action in ask mode (`a`). All set by you, in a terminal; an AI cannot change them. Details: `REMOTE_AI.md`, [Linked Apps](Linked-Apps).

### The browser
`connect ai ... allow browser` lets an AI use [Real Web Browser](Real-Web-Browser) with extra limits.

## B. Connect your AI app to JeeG: `install mcp`

    install mcp <app>            shows what would change
    install mcp <app> yes        does it (the old file is saved as a backup)
    install mcp <app> read yes   also look-only tasks      full yes = every task
    install mcp <app> remove yes

| Kind | Apps |
|---|---|
| Edited for you | Claude Desktop, Claude Code, Cursor, Windsurf, VS Code, Gemini CLI, Amazon Q Developer CLI |
| Shown, you paste | Zed, OpenAI Codex CLI, Goose, Continue, Cline, Roo Code, JetBrains IDEs, Warp, Replit, Cherry Studio, LibreChat, Witsy, Open WebUI, Sourcegraph Cody, NextChat |
| Web link (`connect ai ask`) | Claude.ai, ChatGPT, Google Gemini web, Microsoft Copilot, Perplexity |

Settings locations come from each app's documentation and may be out of date; use the "paste" form if a path is wrong. By default an app gets only the safe list; writes ask you.

## C. Use other MCP servers from JeeG

    mcp catalog                      31 ready-made servers
    mcp add filesystem ~/Documents
    mcp add files = npx -y some-server /path
    mcp add webby = https://example.com/mcp
    mcp login <name> [ENV_VAR]       a token if needed (hidden, private)
    mcp tools <name>                 [read ] only looks, [WRITE] changes things
    mcp mark <name> <tool> read      only if it really only reads
    mcp look <name> <tool> {json}    use a tool marked read
    mcp call <name> <tool> {json}    any tool: asks first; add preview to see the request
    mcp list | logout <name> | remove <name>

Safety: only you add, log in, mark and remove (in a terminal); `mcp look` runs only tools you marked read; web servers must be https to a public address; a shell is refused as a server; logins go to that server only. Per-server AI rules: `app ai deny mcp:files`. Full detail: `MCP.md`.

## What was not tested
Settings paths of other AI apps, the servers in the catalog (not started from here), and real Windows/macOS. Check `mcp tools <name>` after adding a server.
