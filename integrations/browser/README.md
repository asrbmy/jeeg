# JeeG browser extension (Chrome, Edge, Firefox)

Select text on a page, click the JeeG icon, type a task (for example `word count`, `readability`, `uppercase`),
press Run. The answer shows in the popup. It only talks to JeeG on this computer (`127.0.0.1`).

## Install (developer mode, no store needed)
1. **Chrome / Edge:** open `chrome://extensions`, switch on *Developer mode*, choose *Load unpacked* and pick this folder.
   Copy the extension **ID** shown on its card.
   **Firefox:** open `about:debugging#/runtime/this-firefox`, *Load Temporary Add-on*, pick `manifest.json`.
2. Click the JeeG icon > **Settings**. It shows the exact command to start JeeG, for example:

       jeeg --serve-api --allow-origin chrome-extension://<the ID> --only text,money,utility,time

   Browser extensions are the only web origin JeeG accepts, and only the ones you name with `--allow-origin`.
   Web pages are still refused. `--only` limits which kinds of tasks the extension may run.
3. Paste the token (`jeeg --api-token`) into Settings and Save.

Tasks that ask for confirmation are not available here. The extension has no network access to anything but `127.0.0.1`.
