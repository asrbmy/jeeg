# AI mode: let an AI use JeeG on your computer

JeeG has no AI in it. AI mode lets an AI **you already use** (Claude.ai, ChatGPT, an agent) call JeeG over a temporary link.

## Quick start

1. Install a tunnel program once (JeeG does not bundle one): `cloudflared` (free, no account) or `ngrok`.
2. In JeeG type `connect ai` and press Enter.
3. JeeG prints two links ending in `/mcp` and `/`.
4. **Claude.ai:** Settings > Connectors > Add custom connector > paste the `/mcp` link. Start a new chat and say: "Use my JeeG to check disk space."
   **Other AIs:** paste the short message JeeG prints (works for AIs that can open web links).
5. Watch the terminal. In ask mode type `y` when JeeG asks. Press Ctrl+C to close.

## Modes

| Command | What the AI can do |
|---|---|
| `connect ai safe` | Only calculators, converters, small lists. Nothing else, no chaining. |
| `connect ai read` | Safe tasks that only read, plus look-only tasks: disk space, file lists, git status, system info. Nothing is changed. |
| `connect ai` (ask) | Safe tasks at once. Anything else waits for your `y` here; no answer in 60 s = no. |
| `connect ai god` | Every task. Tasks that delete or change things still need your `y`. |

Options: `allow files,system` (let those categories run without asking), `keep` (same link every time; `forget` deletes it), `no log`, `for 90 minutes` (default 30, max 240), `no tunnel`, `via cloudflared|ngrok|ssh`, `url https://your.address`, `port 8800`.

## Safety notes

- Anyone with the link can use JeeG as allowed by the mode until it closes. Do not post it.
- The link has a 256-bit secret, expires, and works only through the tunnel to a server bound to 127.0.0.1.
- The tunnel provider and the AI service can see what passes through. Task output goes to the AI.
- Text inside task output (a file, a web page) may try to instruct the AI. Keep ask mode on unless you need more.
- `web`, `setup`, `update`, `plugin`, `autorun`, `report`, `share` and `connect` cannot be started by the AI.

## If it does not work

- "No tunnel program found": install cloudflared or ngrok, or use `via ssh`.
- Claude.ai says it cannot connect: your plan or organization may not allow custom connectors; try the plain link in a chat that can open web pages.
- Not tested by the author against real Claude.ai or real tunnels (only against fake tunnel programs); tell us what you see with `report`.

## Approve from your phone

`connect ai phone` (ask or god mode) prints a second link and a 6-digit PIN just for you. Open it on your phone, type the PIN, and each time the AI asks for something beyond the safe list you see the request with **Allow** and **Deny**. You can also still answer in the terminal; the first answer counts, and no answer in 60 seconds means no.

- The link and PIN are never given to the AI. Do not paste them into the chat.
- It uses the same tunnel, so it works on mobile data. With `no tunnel` it opens only on this computer.
- 5 wrong PINs lock it (terminal still works). It closes when the AI link closes.

## One link you add only once

1. Run your own named tunnel (for example cloudflared with a free Cloudflare account, or Tailscale Funnel) that points to `http://127.0.0.1:8767`.
2. Start JeeG with `connect ai keep url https://your-address` (add `read`, `ask` ... as you like).
3. Add `https://your-address/<secret>/mcp` to the AI once. The secret is saved by `keep`, so it is the same next time.
4. Run `connect ai forget` if the link ever leaks; the next `keep` makes a new one.

## The session log

Each call is written to `ai-sessions/` in your JeeG folder (mode, request, allowed or denied). Only you can read it. It can contain what the AI asked for, so delete old logs you do not need.
