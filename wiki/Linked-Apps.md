# Linked Apps

Linked apps let JeeG (and, if you allow it, an AI) reach things that live on your own accounts and devices. **Reads and writes are separate. Writes always ask. Only you, in a terminal, can link or change anything.**

## Quick start

    apps                              what is linked
    apps github                       the actions of one app
    app login github                  paste a token once (hidden; stays on this computer)
    app read github issues            look: never changes anything
    app do github comment repo=owner/name number=12 text="Thanks"
    app do telegram send chat=123456789 text="Build finished"
    app do ... preview                shows exactly what would be sent, sends nothing

## Built in

| App | Login | Read | Write |
|---|---|---|---|
| GitHub | personal access token (or `github login`) | me, issues, notifications, repo_issues, pulls | comment, create_issue |
| Telegram (your bot) | token from @BotFather | me | send |
| Discord | channel webhook address | none | send |
| Slack | incoming webhook address | none | send |
| WhatsApp | none | none | message (opens the chat; **you** press Send) |

## Add any web API in three lines

    app add trello https://api.trello.com/1 query:key
    app action trello boards GET /members/me/boards format="{name}"
    app action trello add_card POST /cards params=list,name body='{"idList":"{list}","name":"{name}"}'
    app login trello
    app read trello boards
    app do trello add_card list=abc123 name="Buy milk"

- Login styles: `bearer`, `basic`, `header:NAME`, `query:NAME`, `none`.
- `params=a,b` names the words an action takes; `a:int` digits only, `a:word` letters/digits/`_.-`, `a:text` long text.
- `format="{field}"` shapes results; `list=items` says where the list is.
- `GET` actions are reads. POST/PUT/PATCH/DELETE are writes and ask first.
- Plain `http://` only for your own computer or home network; the internet needs `https://`.
- `read=yes` (set by you) marks a POST as read-only, for search and query APIs such as Notion and GraphQL.

## Presets (27)
`app preset list`, `app preset add gitlab`, `app preset add homeassistant base=http://homeassistant.local:8123/api`. GitLab, Bitbucket, Notion, Linear, Todoist, Asana, Box, monday.com, Jira, Confluence, Stripe (look only), Shopify, Salesforce, Cloudflare, Vercel, Grafana, Home Assistant, Spotify, X (look only), Gmail, Google Drive, Google Calendar (look only), Outlook (look only), and local programs `git`, `docker`, `kubectl`, `adb`. Written from public documentation and **not tried against the live services**: after login, run one read first.

## Programs on this computer (command apps)
For tools with no web API: `app add box command`, `app action box logs RUN docker logs {name} params=name:word read=yes`. One fixed argument list, never a shell; shells, interpreters, `sudo`, `ssh`, `rm` and similar are refused as the program; values starting with `-` are refused; 30 s and 20,000-character limits. Without `read=yes` an action is a write.

## Logins
- Stored in private files (`0600`), never in the definition.
- **Keychain:** `app keystore on|off|status` moves logins into Linux secret-tool, macOS Keychain or Windows Credential Manager, only after reading back an identical value. Off by default. The Windows path is untested on a real machine.
- **Device login:** `app login github device client_id=...` (approve in the browser; page address must be https).
- **Refresh:** logins that expire (for example Outlook) are refreshed automatically when a refresh token was saved.

## Event rules
    rule add issues when github issues changes then gst 100 18
    rules list     rules run once     rules run     rule remove issues
A rule watches a **read** action; the first look only remembers; each new line starts the task (`{new}`, `{count}`). Terminal only; new text is cleaned so strangers' issue titles cannot become commands; confirmation tasks are skipped.

## Letting an AI use your apps

| Mode | AI can use apps? |
|---|---|
| safe | no |
| read | no, unless `connect ai read allow apps` (reads only) |
| ask | reads and writes both ask |
| god | reads run; writes still ask |

Rules (terminal only): `app ai allow github telegram`, `app ai deny whatsapp`, `app ai dry on`, `app ai list`, `app ai reset`. The AI never sees tokens. In preview-only mode, messages with `and`, `then`, `;`, `&` are refused so the preview covers the whole request. MCP tools for your apps: `jeeg_apps`, `jeeg_app_read`, `jeeg_app_do`.

## Safety recap
Host and port checks, no shells, URL-quoted values, size and time limits, private files. Full guide: `APPS.md`.
