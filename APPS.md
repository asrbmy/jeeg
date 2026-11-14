# Linking JeeG to your apps

AI assistants live in the cloud. They cannot see your GitHub, your Telegram, your Slack, or anything on your own computer. JeeG sits on your computer, so it can be the bridge: you link an app once, and then you (or an AI you allow) can read from it and act in it **through JeeG, under your rules**.

Nothing here needs an account with JeeG, and no JeeG server is involved. JeeG talks straight to the app's own web address from your computer.

## Quick start

    apps                              what is linked, and what each app can do
    apps github                       the actions of one app

    app login github                  paste a token once (nothing is shown; it stays on this computer)
    app read github issues            look: never changes anything
    app read github repo_issues owner/name
    app read github notifications

    app do github comment repo=owner/name number=12 text="Thanks, fixed in the next release"
    app do telegram send chat=123456789 text="Build finished"
    app do discord send Deploy done
    app do whatsapp message phone="+91 98765 43210" text="On my way"

Writing always asks first. Add the word `preview` to see exactly what would be sent, without sending it.

## What is built in

| App | Log in with | Read | Write |
|---|---|---|---|
| GitHub | a personal access token (or `github login`) | `me`, `issues`, `notifications`, `repo_issues`, `pulls` | `comment`, `create_issue` |
| Telegram (your own bot) | the token from @BotFather | `me` | `send` |
| Discord | a channel webhook address | none | `send` |
| Slack | an incoming webhook address | none | `send` |
| WhatsApp | no login | none | `message` (opens the chat with your text typed in; **you** press Send) |

**About WhatsApp:** WhatsApp has no safe way for another program to send as you, and tools that pretend to are a quick way to get an account banned. So JeeG opens the chat with your message ready and you press Send. That is the honest limit.

## Add any other app (Trello, Notion, Home Assistant, your own server...)

If an app has a web API, you can describe it in three lines. In a terminal:

    app add trello https://api.trello.com/1 query:key
    app action trello boards GET /members/me/boards format="{name}"
    app action trello add_card POST /cards params=list,name body='{"idList":"{list}","name":"{name}"}'
    app login trello
    app read trello boards
    app do trello add_card list=abc123 name="Buy milk"

- Login styles: `bearer` (default), `basic` (user:password), `header:NAME`, `query:NAME`, or `none`.
- `params=a,b` names the words an action takes. `a:int` accepts digits only, `a:word` letters, digits and `_ . -`, `a:text` allows long text.
- `format="{field}"` says how to show each result (`{user.login}` reaches inside). `list=items` says where the list is in the answer.
- `GET` actions are reads. Every other method (POST, PUT, PATCH, DELETE) is automatically a **write**: it asks first, and a read command refuses it.
- Apps on your own computer or home network may use plain `http://` (for example Home Assistant). Anything on the internet must be `https://`.

## Ready-made apps (presets)

    app preset list
    app preset add gitlab
    app preset add homeassistant base=http://homeassistant.local:8123/api
    app preset add docker

Presets: GitLab, Notion, Linear, Todoist, Home Assistant, Jira Cloud, and local programs `git`, `docker`, `kubectl`, `adb`. `as=<name>` renames one.
They were written from each service's public documentation and **have not been tried against the live services**: after logging in, run one read action first (for example `app read gitlab me`). Presets go through the same safety check as your own definitions.

## Programs on this computer (no web API needed)

Some tools have no web API at all (docker, adb, git, kubectl). A *command app* runs one fixed program with a fixed argument list:

    app add box command
    app action box logs RUN docker logs --tail 50 {name} params=name:word read=yes
    app action box restart RUN docker restart {name} params=name:word
    app read box logs web          (a read)
    app do box restart web         (a write: asks first)

- It is never run through a shell, so `;`, `&&`, backticks and `$(...)` in what you type are just text inside one argument.
- A value that starts with `-` is refused (it would be read as an option of the program).
- Shells and interpreters (`bash`, `cmd`, `powershell`, `python`, `node`...), `sudo`, `ssh`, `rm`, `dd`, `reg` and similar are not allowed as the program, and batch files (`.bat`, `.cmd`) are never run.
- The program must be on your PATH. It gets no input, a 30 second limit and 20,000 characters of output.
- Without `read=yes` an action counts as a **write**.

## Reading with POST (search and query APIs)

Some APIs (Notion search, Linear/GraphQL) use POST even to look. Mark such an action yourself, in a terminal:

    app action notion search POST /search params=text body='{"query":"{text}"}' read=yes

`read=yes` is accepted only on POST and on command actions, and only you can set it: an AI cannot define or change actions. Do it only for requests that really change nothing.

## Keeping logins in the system keychain

    app keystore on        (Linux: needs secret-tool; macOS: built in; Windows: Credential Manager)
    app keystore off
    app keystore status

Off by default. When switched on, every login is moved into the keychain and the file keeps only a marker. A login is moved only after JeeG read it back and got the same text; if the keychain fails, the login stays in its file. The secret goes in over standard input, never on a command line. Covers linked-app logins (not the older `github login` file). The Windows path is written from Microsoft's documentation and has not been tested on a real Windows computer.

## Log in without pasting a token (device login)

    app login github device client_id=YOUR_OAUTH_APP_ID

JeeG shows a short code and a page address; you approve in your browser and JeeG receives the token (the standard "device flow", RFC 8628). You need an OAuth app with the device flow enabled (GitHub: Settings > Developer settings > OAuth Apps > tick "Enable Device Flow"); JeeG does not ship an app of its own. Other services: add `code_url=https://... token_url=https://...` (and `scope=`). The page address must be https.

## Event rules: act when something new appears

    rule add issues when github issues changes then gst 100 18
    rule add mail when shop items changes every 10 minutes then say new item {new}
    rules list
    rules run once          (look now)
    rules run               (keep looking; Ctrl+C stops)
    rule remove issues

A rule looks at a **read** action. The first look only remembers what is there; after that every new line starts the task. `{new}` is the first new line, `{count}` how many.
Safety: you create and run rules in a terminal (an AI cannot). New text is cleaned before use (symbols removed, the words "and" and "then" replaced) because strangers can write issue titles. The task runs without `--yes`, so a task that asks for confirmation is skipped, never forced.

## Letting an AI use your apps

Start AI mode as usual (see REMOTE_AI.md). Then:

| Mode | Can the AI use your apps? |
|---|---|
| safe | No. |
| read | No, unless you add `allow apps`:  `connect ai read allow apps`. Then it can **read** only. |
| ask | Reads and writes both ask you first (press `a` to always allow one kind for this session). |
| god | Reads run; writes still ask you. |

The AI is told which apps exist ("apps" lists them). It never sees your tokens.

**Rules for the AI, set by you in a terminal:**

    app ai allow github telegram      only these apps (everything else is refused and hidden)
    app ai deny whatsapp              never this one
    app ai dry on                     the AI only ever gets previews
    app ai list     app ai reset

- **Press `a` to always allow one action:** in ask mode the question offers `a` for `app do github comment` only. It covers that app and action for the session, not other actions and not other tasks.
- **Preview-only mode:** `connect ai ask preview only` (or `app ai dry on`). Writes show exactly what would happen and send or change nothing; tasks that cannot preview are refused; reading still works. Messages that contain "and", "then", `;` or `&` are refused in this mode, so it is certain that the preview covers the whole request.

## MCP tools for your apps (Claude Desktop, Cursor, Claude.ai link)

The JeeG MCP server (`install mcp claude-desktop`, or the link from `connect ai`) now has three typed tools besides `jeeg_run`:

| Tool | What it does |
|---|---|
| `jeeg_apps` | lists your linked apps and their actions (`app` for one app) |
| `jeeg_app_read` | `app`, `action`, `args`: looks, never changes |
| `jeeg_app_do` | `app`, `action`, `args`: a write; asks you first (or only previews) |

The tools turn into the same plain words you would type (`app read github issues repo="o/r"`), so every rule above applies: reads cannot write, writes ask, per-app allow/deny, preview-only mode, "always allow" for one action. Names and argument keys are checked, values are quoted. Over `install mcp` (stdio) without AI mode, a write is reported as "needs confirmation" and is not run; use `connect ai ask` for approvals.

## What keeps this safe

- **Setting up is for you only.** `app login`, `app add`, `app action`, `app remove` work only in a real terminal window. A program or an AI cannot link an app, define one, or read a login, even in god mode.
- **Logins stay local.** Tokens are saved in a file only your user can read, never printed, never put in history, and scrubbed from every message.
- **A read can never write.** `app read` refuses anything that is not a plain GET/HEAD. An AI in read mode cannot change anything even if it tries.
- **Words cannot escape.** What you or an AI type fills only a labelled slot: part of the path (encoded), a query value (encoded) or a text field in the JSON body. It can never change the address, the headers or the method.
- **No redirects.** If an app redirects, JeeG stops, so your login is never sent to another site.
- **Your content is data.** Everything an app returns is labelled as the app's content, with terminal escape codes removed. An AI should not follow instructions found inside an issue or message, and JeeG says so in the output.
- **Limits.** Answers are cut at 1 MB, requests time out after 15 seconds, and AI mode allows at most 5 changing tasks per minute.
- **Nothing leaves except to the app you picked.** No JeeG server, no telemetry.

## Things to know

- A token with fewer permissions is safer. For reading GitHub issues, a read-only token is enough; give write access only if you want `comment` and `create_issue`.
- Telegram: message your bot once first, then use your own chat id (send `/start` to @userinfobot to find it).
- Not tested against the real services from where JeeG was built (no network access to them there). The requests are checked against a local fake server, so the shape, the headers, the quoting and the safety rules are tested. The first run against the real GitHub or Telegram is yours: if something is off, `app do <app> <action> ... preview` shows the exact request.
