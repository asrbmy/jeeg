# Manual test checklist (things only a real computer can check)

Automatic tests run on Windows, Mac and Linux in GitHub Actions (`tests` workflow, including `jeeg selfcheck`). These steps cover what a robot cannot: real clicks, real apps, real phones. Takes about 20 minutes. Tick, and report problems with `report` (it makes `jeeg-report.txt`).

## 1. Install and basics (any computer)
- [ ] `jeeg selfcheck` prints "Everything required works."
- [ ] `jeeg "gst 2500 18"` shows a total of 2,950.00
- [ ] `jeeg "open youtube"` opens your browser
- [ ] `jeeg "set timer 1 minute"` pops a notification after a minute
- [ ] `jeeg "health check"` shows your real disk and memory

## 2. Standalone program (Windows .exe / Mac / Linux file from the release)
- [ ] Windows: double-click once; SmartScreen warning is expected (unsigned). "More info > Run anyway" works.
- [ ] Mac: right-click > Open the first time (Gatekeeper). `chmod +x jeeg-macos` first.
- [ ] `jeeg --version` and `jeeg selfcheck` pass without Python installed
- [ ] `jeeg update` says you are up to date (or updates and keeps working)

## 3. Phone page (`web lan`, `web lan god`)
- [ ] The link opens on a phone on the same Wi-Fi; `gst 2500 18` works
- [ ] Safe mode refuses `open youtube`
- [ ] God mode asks for the PIN, runs `open youtube`, and a task that needs confirmation shows a button

## 4. AI mode (needs `cloudflared` or `ngrok`)
- [ ] `connect ai` prints a link within 30 seconds
- [ ] Claude.ai: Settings > Connectors > Add custom connector > paste the `/mcp` link; a new chat can run `gst 100 18` through JeeG
- [ ] Ask something outside the safe list: the terminal asks y/n; `y` runs it, no answer refuses it
- [ ] `connect ai phone`: the approval page opens on your phone, the PIN works, Allow/Deny work, "Allow always" stops further questions for that task
- [ ] Ctrl+C closes it and the old link stops working
- [ ] `ai log` shows what happened

## 4b. Claude Desktop / Cursor (no tunnel)
- [ ] `install mcp claude-desktop` shows what it would change; `install mcp claude-desktop yes` writes it (a backup is kept)
- [ ] Restart Claude Desktop: JeeG tools appear; `gst 100 18` works
- [ ] `install mcp claude-desktop remove yes` takes it out again

## 4c. Connectors (only the ones you use; see CONNECTORS.md)
- [ ] Telegram: `telegram setup` accepts your BotFather token; `telegram start`; `/pair <code>` from your phone works; `gst 100 18` answers 118; a second Telegram account is refused
- [ ] `hook add tax = gst 100 18`, `hook listen`, open the printed link from your phone (mobile data): shows 118; a changed secret gives "Not found"
- [ ] `webhook add team <your Slack or Discord address>`, `webhook send team test` arrives in the channel
- [ ] `wake add pc AA:BB:...`, `wake pc` wakes a computer that has Wake-on-LAN enabled
- [ ] `computer add pi pi@host`, `on pi run disk space` (needs JeeG and an ssh key on the other computer)
- [ ] `device add lamp shelly <ip>`, `device on lamp` / `device off lamp` switch a real plug
- [ ] `mail setup` (app password), `mail inbox` shows your unread mail, `mail send` to yourself arrives
- [ ] `github login`, `github inbox`; `calendar feed add work <secret iCal address>`, `calendar feed upcoming`
- [ ] `android devices` (USB debugging on), `mqtt publish` to your broker

## 5. Browser extension (`integrations/browser`)
- [ ] Load it unpacked in Chrome/Edge; `jeeg --serve-api --allow-origin chrome-extension://<your id>` is running; the popup runs `gst 100 18`

## 6. Windows / Mac extras
- [ ] Right-click a file > Send to > JeeG (Windows `integrations/sendto`)
- [ ] `jeeg "screen text"` (after `pip install pillow pytesseract` and installing Tesseract) copies the text on your screen
- [ ] `jeeg "contact sheet <folder with photos>"` makes `contact_sheet.jpg`

If something fails, run `jeeg report`, attach `jeeg-report.txt`, and say which step number failed.
