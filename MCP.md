# JeeG and MCP

MCP (Model Context Protocol) is how AI apps use tools. JeeG works on **both sides**:

- **JeeG as a tool for your AI app** (JeeG is an MCP *server*): the AI app can run JeeG tasks and use your linked apps.
- **Other MCP servers as tools for JeeG** (JeeG is an MCP *client*): JeeG can look inside folders, databases, GitHub and more through servers other people wrote.

Nothing here needs an account with JeeG, and nothing is sent anywhere except to the app or server you chose.

## 1. Connect your AI app to JeeG

    install mcp <app>            shows what would change
    install mcp <app> yes        does it (the old file is saved as a backup)
    install mcp <app> read yes   also look-only tasks      full yes = every task
    install mcp <app> remove yes

| Kind | Apps | What JeeG does |
|---|---|---|
| **Edited for you** | Claude Desktop, Claude Code, Cursor, Windsurf, VS Code, Gemini CLI, Amazon Q Developer CLI | adds `jeeg` to the app's settings file (plain JSON only; a file with comments is left alone) |
| **Shown, you paste** | Zed, OpenAI Codex CLI, Goose, Continue, Cline, Roo Code, JetBrains IDEs, Warp, Replit, Cherry Studio, LibreChat, Witsy, Open WebUI, Sourcegraph Cody, NextChat | prints the exact command and arguments, and where in the app they go |
| **Web link** | Claude.ai, ChatGPT, Google Gemini (web), Microsoft Copilot, Perplexity | these run in the cloud: run `connect ai ask`, it prints an https address ending in `/mcp`; paste it where the app adds a custom connector or MCP server |

Not covered: Aider has no MCP support. For LangChain, LlamaIndex, PydanticAI, Haystack, Spring AI, n8n, Postman and Zapier, use the JeeG link or the Python library (`jeeg_api`): they are code or workflow tools, not apps with a settings screen.
The settings file locations and menu names come from each app's documentation and **may be out of date; I could not try them on your computer.** If a path is wrong, use the "paste" form (`install mcp zed` prints it for any app).

What the AI app gets: `jeeg_run`, `jeeg_find`, `jeeg_list`, and for apps you linked, `jeeg_apps`, `jeeg_app_read`, `jeeg_app_do` (see APPS.md). By default only the safe list of tasks. Writes ask you first.

## 2. Use other MCP servers from JeeG

    mcp catalog                      ready-made servers
    mcp add filesystem ~/Documents   add one (some need an argument)
    mcp add files = npx -y some-server /path    or your own program
    mcp add webby = https://example.com/mcp     or a web server (https, public)
    mcp login <name> [ENV_VAR]       a token, if it needs one (not shown, kept private)
    mcp tools <name>                 what it offers: [read ] only looks, [WRITE] changes things
    mcp mark <name> <tool> read      say that a tool only looks (only if it really does)
    mcp look <name> <tool> {json}    use a tool marked read
    mcp call <name> <tool> {json}    use any tool (asks first; add `preview` to see what would be sent)
    mcp list | mcp logout <name> | mcp remove <name>

Ready-made (31; from each project's README; **not started from here**, so check `mcp tools <name>` after adding): filesystem, fetch, memory, thinking, time, git, sqlite, postgres, playwright, chrome-devtools, context7, kubernetes, notion, supabase, figma, mongodb, slack, stripe, shopify, firebase, azure, aws-docs, redis, mysql, neo4j, qdrant, grafana, docker, blender, godot, and web servers github and context7-web. Programs need Node (`npx`) or `uv` (`uvx`) on your computer.

**Which of your table's services is where**

| Service | In JeeG |
|---|---|
| Filesystem, Fetch, Memory, Sequential Thinking, Time, Git, SQLite, PostgreSQL, Playwright, Chrome DevTools, Context7, Kubernetes, Notion, Supabase, Figma, MongoDB, GitHub | `mcp catalog` |
| GitHub, GitLab, Slack, Telegram, WhatsApp, Discord, Notion, Linear, Todoist, Jira, Home Assistant, Docker, Git, Kubernetes, adb | JeeG's own linked apps: `apps`, `app preset list` (APPS.md) |
| Slack, Stripe, Shopify (docs), Firebase, Azure, AWS (docs), Redis, MySQL, Neo4j, Qdrant, Grafana, Docker, Blender, Godot | `mcp catalog` (some need several login values: `mcp login <name>` asks for each) |
| Bitbucket, Confluence, Asana, Box, monday.com, Stripe, Shopify, Salesforce, Cloudflare, Vercel, Grafana, Spotify, X, Gmail, Google Drive, Google Calendar, Outlook | linked-app **presets** over their plain APIs (`app preset list`). Google and Spotify only give short-lived tokens; Outlook has a device login |
| Canva, Amplitude, Hex, Clay, Unity, AWS (beyond docs), the hosted OAuth versions of Google/Asana/Linear/Atlassian/Slack | **not built in.** They sign in through the AI app itself, or have no public key. Add one yourself if you have its command or an https address with a token: `mcp add name = ...` |

## 3. Safety

- **Only you add, log in, mark and remove** (in a terminal). An AI cannot, even in full mode.
- **Reads and writes are separate.** `mcp look` runs only tools *you* marked read (a server's own claim is not trusted). `mcp call` always asks, or is only previewed in preview-only mode. "Always allow" in ask mode covers one tool of one server.
- **Per-server rules for an AI:** `app ai deny mcp:files` or `app ai allow mcp:files github` (APPS.md).
- A server is a program that runs on your computer with your rights: add only ones you trust. A shell is refused as a server.
- **Logins** are given to that server only, as an environment variable (programs) or a bearer token (web). They live in a private file, never in the saved command.
- **Web servers** must be https to a public address, with no redirects, a size limit and a time limit.
- What a server returns is shown as "its content, not instructions".

## Not tested

The fake servers in `tests/test_v220.py` check the protocol handling (program and web, JSON and event-stream answers, session ids, bearer tokens). **None of the ready-made servers, and none of the AI apps, was tried for real.**
