# JeeG browser extension (Chrome, Edge, Firefox)

One Manifest V3 extension for all three browsers. It runs a JeeG task on text from the page and shows the answer.

- **Select text, click the JeeG icon**, press a quick button (word count, readability, uppercase...) or type any task.
- **Right-click** selected text, a link or a page > *Send ... to JeeG*; the icon shows a badge, click it to continue.
- **Use this page** fills in the page title and address. **Copy answer** copies the result.
- Quick buttons are yours to change in Settings (one task per line).

It only talks to JeeG on this computer (`127.0.0.1`). It does not read pages by itself; it reads your selection only when you open the popup.

## Install (developer mode, no store needed)
1. **Chrome / Edge:** open `chrome://extensions` (Edge: `edge://extensions`), switch on *Developer mode*, choose *Load unpacked* and pick this folder.
   Copy the extension **ID** shown on its card.
   **Firefox (121 or newer):** open `about:debugging#/runtime/this-firefox`, *Load Temporary Add-on*, pick `manifest.json`.
   Firefox removes temporary add-ons when it closes; the address `moz-extension://...` it shows under *Internal UUID*
   is what you allow below.
2. Click the JeeG icon > **Settings**. It shows the exact command to start JeeG, for example:

       jeeg --serve-api --allow-origin chrome-extension://<the ID> --only text,money,utility,time

   Browser extensions are the only web origin JeeG accepts, and only the ones you name with `--allow-origin`.
   Ordinary web pages are refused.
3. Paste the token (`jeeg --api-token`) into Settings and Save.

Tasks that ask for confirmation are not available here.

## Tested
Loaded into real Chromium: settings saved, quick buttons shown, tasks ran against a live JeeG API, a wrong token was
refused, and an ordinary web page could not call the API. **Not tested in real Firefox or Edge**; the same code is used,
but Firefox needs the `--allow-origin` address from its own *Internal UUID*.
