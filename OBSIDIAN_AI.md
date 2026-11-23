# Edit your Obsidian notes with Claude.ai, DeepSeek, ChatGPT and other AI websites

JeeG has no AI in it. It is the safe hand between a website AI and your notes. Everything changes only on your computer,
only inside your vault, and every change can be undone.

One-time setup (in JeeG): `vault set` (finds your Obsidian vault; or `vault set <folder>`).

## Route 1: Claude.ai website (live connection)
1. In JeeG: `connect ai ask`. It prints a link ending in `/mcp` (this needs a tunnel program, see `REMOTE_AI.md`).
2. Claude.ai > Settings > Connectors > Add custom connector > paste the link. (Anthropic says custom connectors are on all
   plans, with one connector on the free plan. The address has to be public HTTPS on port 443, which the tunnel gives.)
3. In a chat: "Use my JeeG to search my vault for the beta launch and add a line to the Project Plan note."
4. In the default mode (`connect ai`, "ask"), JeeG asks you in its terminal window before running each vault task: type `y`
   (no answer in 60 seconds means no). For reading only, use `connect ai read`: searching and reading your notes then go
   straight through, and every change is refused. Press Ctrl+C in JeeG to close the link; it also stops by itself after
   30 minutes (change with `for 90 minutes`) or 100 requests. `connect ai forget` makes a saved link invalid.

## Route 2: any website, including DeepSeek and ChatGPT (copy and paste)
This works with every chat website, because nothing connects to anything: you carry the text.
1. Put your notes and a short set of instructions on the clipboard:
   - `vault copy Project Plan` (up to 5 notes: `vault copy Project Plan | Ideas`),
   - `vault copy find beta launch` (the 3 best-matching notes),
   - `vault copy` on its own (just the list of note names, so the AI can pick notes or make new ones).
2. Paste into the chat, write what you want at the end ("add a risks section and fix the date to April") and send.
3. The AI answers with a block like:

       ```jeeg
       [{"op":"replace","note":"Project Plan","find":"March","with":"April"},
        {"op":"append","note":"Project Plan","text":"## Risks\n- Budget"}]
       ```
4. Copy that block (the site's copy button is fine). **Easiest:** leave `vault listen` running in a JeeG window; the moment you copy a block it shows what would change and asks `Apply? y/N/u` (u = undo). Or do it by hand:
   - `vault plan` shows exactly what would change (nothing is changed yet),
   - `vault apply` makes the changes after you confirm,
   - `vault undo` puts everything back (the last 30 changes are kept in `.jeeg-backup` inside the vault).

## What an edit block can do
`new`, `append`, `prepend`, `insert_under` (add to the end of a heading's section), `replace` (the old text must appear exactly once), `remove_text`, `trash`.
Up to 20 changes at once, and either all are applied or none (if one cannot be done, nothing changes).
"Removing" a note moves it to the vault's `.trash` folder, as Obsidian does; JeeG never deletes for good.

## Safety, in plain words
- Nothing outside the vault and nothing in hidden folders (like `.obsidian`) can be read or written.
- Notes are data. The copy-paste instructions tell the AI not to follow orders written inside a note, but a clever note can
  still fool some AIs, which is why `vault plan` exists: read it before you apply.
- An AI connected through `connect ai` cannot read or overwrite your clipboard; it has to include the edit block itself.
- Only the text you paste into a website goes to that website. Claude.ai connected live sees what its search and read
  calls return.

## Honest limits
- The Claude.ai connection was not tried against the real website; the tunnel and approval parts were only tested with
  stand-ins (see `REMOTE_AI.md`). Your plan or organisation may restrict custom connectors.
- I could not confirm that the DeepSeek website can add connectors, so for it (and any site without them) use Route 2.
  An AI can write a wrong edit block; `vault plan` and `vault undo` are your protection.
- Obsidian Sync or other sync tools may sync `.jeeg-backup` and `.trash`; exclude them if you do not want that.
