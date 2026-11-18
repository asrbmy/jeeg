# Phone, Web Page and Connectors

## Local web page
`web` (or `web 8800`) opens a small page on your computer for people who prefer a text box. It listens on 127.0.0.1 only, rejects other hosts and sites, needs a random token created at start, and declines tasks that ask for confirmation. Ctrl+C stops it.

## Phone page
- `web lan` (**safe mode**): prints a secret link for a phone on the same Wi-Fi. Only about 70 safe tasks work (calculators, converters, shopping/notes/expenses, reminders). No app launching, file access, clipboard, or chains.
- `web lan god` (**god mode**): every task, including opening apps and files and `then` chains. Confirmation tasks show a "Yes, run it" button. It needs a 6-digit PIN shown only in the terminal, allows 5 wrong tries, closes itself after 30 minutes (`for 60 minutes`, max 240), shows a red countdown banner and prints every command.
- It is plain http: only on your own Wi-Fi, never public Wi-Fi.
- `web`, `setup`, `update`, `plugin`, `autorun`, `report` and `share` stay terminal-only.

## Telegram (no tunnel needed)
1. Talk to **@BotFather**, `/newbot`, copy the token.
2. `telegram setup`, paste the token (hidden).
3. `telegram start` (`read`, `ask`, `god`, `for 60 minutes`, `limit 50`). JeeG shows a 6-digit code.
4. Send `/pair 123456` to your bot. Only paired chats work; 5 wrong codes lock pairing; groups are ignored.
5. Message tasks in plain words. `/mode` shows what is allowed, `/stop` ends it, `telegram forget` deletes the token.

## Incoming hooks
`hook add backup = backup folder documents`, then `hook listen` prints one link per hook. Anyone with a link can start **that one saved task**; the caller cannot change it; confirmation tasks are refused; 12 calls a minute. Good for GitHub webhooks, Zapier, IFTTT, cron.

## Outgoing
| Task | Does |
|---|---|
| `webhook add team <https address>`, `webhook send team deploy done` | Slack, Discord, Zapier, n8n, any JSON POST |
| `wake add nas AA:BB:...`, `wake nas` | Wake-on-LAN |
| `computer add pi pi@192.168.1.20`, `on pi run disk space` | Another computer over ssh (key login; asks first) |
| `device add lamp shelly 192.168.1.50`, `device on lamp` | Shelly and Tasmota plugs on your home network |
| `mqtt add home 192.168.1.2`, `mqtt publish home lights/kitchen on` | Minimal MQTT 3.1.1 |
| `android devices`, `android battery`, `android screenshot` | Android over adb |
| `serial ports`, `serial send COM3 hello` | Serial devices (`pip install pyserial`) |
| `peer add office <link>`, `peer run office disk space` | Another computer's JeeG via its `connect ai` link |

## Services (your own account)
- Mail: `mail setup you@gmail.com imap.gmail.com smtp.gmail.com` (app password), `mail inbox` (headers only), `mail send bob@x.com | Subject | Body` (asks).
- GitHub: `github login`, `github inbox`, `github issues owner/repo`, `github prs owner/repo`.
- Calendars: `calendar feed add work <secret iCal link>`, `calendar feed upcoming 14` (read only).

## Safety rules for every connector
Secrets are asked privately, never typed in a command, kept in files only you can read. Links stop working when you close them. See `CONNECTORS.md`. Not included: Google Calendar write access, Notion API sign-in flows, Slack/Discord bots (use `webhook`), Philips Hue.
