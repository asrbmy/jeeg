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

## Letting an AI use your apps

Start AI mode as usual (see REMOTE_AI.md). Then:

| Mode | Can the AI use your apps? |
|---|---|
| safe | No. |
| read | No, unless you add `allow apps`:  `connect ai read allow apps`. Then it can **read** only. |
| ask | Reads and writes both ask you first (press `a` to always allow one kind for this session). |
| god | Reads run; writes still ask you. |

The AI is told which apps exist ("apps" lists them). It never sees your tokens.

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
