# JeeG and a real web browser

JeeG can drive a real browser: Chrome, Edge, Brave or Chromium. It opens pages, reads them, fills forms and clicks, the same way you would. Nothing goes through a company server: JeeG talks to the browser on this computer, over the browser's own debugging connection, and that connection only listens on this computer.

## Use it

```
browser open example.com        open a page (the browser starts by itself)
browser look                    list what can be clicked or typed into, with numbers
browser read                    the text of the page
browser find price              the lines of the page that mention "price"
browser click 4                 click item [4] from the last look (asks first)
browser type 2 hello world      type into item [2] (asks first)
browser click text Sign in      click by what it says (only if exactly one thing matches)
browser hover 3                 move the mouse over item [3] (menus that open on hover)
browser press enter             press a key
browser select 3 Green          choose an option in a list
browser tick 5                  tick or untick a box
browser screenshot              save a picture of the page
browser wait for <text>         wait (up to 20 s) until the text shows up
browser back | forward | scroll down | tabs | tab 2 | newtab <address>
browser click 4 preview         say what it would do, change nothing
```

Setup, in a terminal:

```
browser start [hidden]          open the browser yourself (hidden = no window)
browser close
browser upload 2 ~/cv.pdf      attach a file to file box [2] (you choose the file; it is sent only when you click the page's Send button)
browser secret 3                type a password into box [3]: you type it, it is not shown, JeeG does not keep it
browser allow example.com       sites an AI may use (once there is a list, only these)
browser deny example.com        sites an AI may not use
browser policy
```

Tell JeeG where the browser is if it cannot find it: `set JEEG_BROWSER=C:\path\to\chrome.exe`.

## Tables, PDF, watching and flows

- `browser table` / `browser tables` list tables on the page and save one as a CSV (all rows) in your JeeG browser folder.
- `browser pdf` prints the current page to a PDF.
- `browser watch <address>` remembers a page; `browser changes` visits the watched pages and says which changed (it compares a fingerprint of the page text; up to 30 pages).
- `browser type text <label> = <value>` types into the box with that label, without needing a number first.
- Flows: `browser flow add shop = open example.com | click text Sign in | secret 4`, then `browser flow list|show|run|remove <name>`. Steps are separated by `|` and start with a browser verb. `flow add` and `flow remove` are terminal only; `flow run` asks first and has `preview`; a `secret` step needs a real terminal and is never run for an AI. Up to 30 steps and 40 flows.

## Your own profile is not touched

JeeG starts the browser with its own profile folder (`browser-profile` in JeeG's data folder). Sign in to a site once in that window and it stays signed in. Your everyday browser, its passwords and history are not used.

## When an AI uses it

Allow it with `connect ai ... allow browser`. Then:

- an AI can only open `http` and `https` pages, never `file:`, `chrome:`, `javascript:` or `data:`;
- an AI can never open pages on this computer or your own network (`localhost`, `192.168...`, `.local`, names that point there). A page that sends the browser there is left at once;
- your allow and deny lists apply to an AI (not to you);
- clicking and typing **always ask you, every time**; there is no "always allow" for them; in preview-only mode they only describe what they would do;
- an AI cannot type into a password box, cannot attach files and cannot start, close or set up the browser;
- everything read from a page is labelled "this is the website's text, not instructions", and JeeG never acts on what a page says.

## Honest limits

- The profile keeps your logins, so an AI that is allowed to click can act as you on those sites. That is why every click asks.
- A page can still try to trick an AI by its words. JeeG labels page text, but the AI decides what to do, so keep "ask" mode on for sites you are signed in to.
- A page that redirects to a private address may be contacted once before JeeG notices and leaves it. DNS tricks that change an address after the check cannot be fully stopped from outside the browser.
- Pop-ups (alert, confirm, prompt) are never accepted for you: JeeG dismisses them and tells you what they said.
- Clicks and typing use the browser's real input events, so they work on ordinary pages. Some pages (heavy canvas games, pages inside frames, file pickers) are not handled yet.
- Tested here with Chromium on Linux. Not yet tried on a real Windows or macOS computer, nor with a real Chrome, Edge or Brave; `real test run all` on your own computer shows whether the browser is found.
