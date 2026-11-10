# Connectors: JeeG with other software, services, devices and languages

Everything here is **off until you set it up**, one connector at a time. Secrets (tokens, passwords, links) are asked for privately, never typed in the command, never printed, and kept in files only you can read in your JeeG folder (`conn_*.json`, `telegram.json`). JeeG itself still has no AI and no account. Tasks that send something out or control something are never in the "safe" list.

## Talk to JeeG from elsewhere

| From | How |
|---|---|
| Telegram on your phone | `telegram setup`, then `telegram start` (below) |
| A web address, GitHub, Zapier, cron | `hook add` and `hook listen` (below) |
| Claude.ai or any AI | `connect ai` (REMOTE_AI.md) |
| Claude Desktop / Cursor | `install mcp claude-desktop yes` |
| Another JeeG | `peer` (below) |
| JavaScript / TypeScript | `integrations/js` (`const { run } = require("./index.js")`) |
| Go, Rust, Java, C#, Swift ... | `integrations/openapi/jeeg-openapi.json` with any OpenAPI generator, against `jeeg --serve-api` |
| Python | `import jeeg_api` |

### Telegram bot (no tunnel needed)
1. In Telegram talk to **@BotFather**, send `/newbot`, copy the token.
2. `telegram setup` and paste the token (hidden).
3. `telegram start` (or `telegram start read`, `ask`, `god`, `for 60 minutes`, `limit 50`). JeeG prints a 6-digit code.
4. Open your bot and send `/pair 123456`. Only chats paired this way can use it; 5 wrong codes lock pairing; groups are ignored.
5. Message tasks in plain words. `/mode` shows what is allowed, `/stop` ends it. `telegram forget` deletes the token.

Modes are the same as AI mode: `safe`, `read`, `ask` (default: anything else waits for your y/n at the computer), `god`. JeeG calls Telegram's servers outbound only. Telegram, and anyone who can read the chat, can see what is said.

### Incoming hooks
`hook add backup = backup folder documents` saves a named task. `hook listen` prints one link per hook. Anyone with a link can start **that one saved task**, nothing else (the caller cannot change it); tasks that ask for confirmation are refused; 12 calls a minute. Use `keep` for stable links, `no tunnel` for local only. Good for GitHub webhooks, Zapier, IFTTT, cron.

## JeeG reaching out

| Task | What it does |
|---|---|
| `webhook add team <https address>` then `webhook send team deploy done` | Slack, Discord, Zapier, n8n and anything that takes a JSON POST (text is sent as `text`, `content` and `message`). `http` only to your own network. |
| `wake add nas AA:BB:CC:DD:EE:FF`, `wake nas` | Wake-on-LAN. |
| `computer add pi pi@192.168.1.20`, `on pi run disk space` | Run a JeeG task on another computer over ssh (key login only; asks first). |
| `device add lamp shelly 192.168.1.50`, `device on lamp` | Shelly (Gen1 and Gen2) and Tasmota plugs on your home network. Addresses must be private. |
| `mqtt add home 192.168.1.2 [user]`, `mqtt publish home lights/kitchen on`, `mqtt listen home sensors/#` | Minimal MQTT 3.1.1 (TLS on port 8883). Password asked privately. |
| `android devices`, `android battery`, `android screenshot`, `android open <url>` | An Android phone over adb. |
| `serial ports`, `serial send COM3 hello` | Arduino and other serial devices (needs `pip install pyserial`). |
| `peer add office <link>`, `peer run office disk space` | Use another computer's JeeG through its `connect ai` link. Its own mode applies. |
| `mcp add files = npx -y @modelcontextprotocol/server-filesystem ~/Documents`, `mcp tools files`, `mcp call files read_file {"path":"a.txt"}` | JeeG as an MCP **client**: use tools from other MCP servers (asks first). |

## Services (your own account needed)

| Task | What it does |
|---|---|
| `mail setup you@gmail.com imap.gmail.com smtp.gmail.com`, `mail inbox`, `mail send bob@x.com \| Subject \| Body` | Mail over IMAP/SMTP with an **app password** (asked privately). `mail inbox` reads only the headers and marks nothing read. `mail send` asks first. |
| `github login`, `github inbox`, `github issues owner/repo`, `github prs owner/repo` | GitHub with a personal access token (give it only read and notifications). |
| `calendar feed add work <secret iCal address or file.ics>`, `calendar feed upcoming 14` | Google, Outlook, Apple calendars through their private iCal link: no sign-in, read only. Repeating events show only on their first date. |

Not included (they need a sign-in flow that cannot be done safely in a small standard-library tool): Google Calendar write access, Notion, Slack/Discord *bots* (use `webhook` to post), Philips Hue (needs a pairing button flow).

## Safety rules for every connector
- Nothing runs until you set it up and start it. Stop with Ctrl+C or `forget`/`remove`.
- Secrets never appear in output, logs or an AI's view; files are mode 600.
- Anything that sends data out or controls a device is outside the safe list, so AI mode asks you first.
- Local-network devices must have private addresses; plain `http` only to this computer or your home network.
- A connector token is only ever sent to the service it belongs to (Telegram to Telegram, GitHub to GitHub).
- What the tunnel provider, Telegram, GitHub, your mail provider or a webhook receiver sees is up to them; PRIVACY.md lists what JeeG sends.
