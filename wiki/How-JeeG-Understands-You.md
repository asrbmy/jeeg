# How JeeG Understands You

JeeG does not "understand" language the way an AI chat does. It **matches your words to scripts** you can see. That makes it fast, predictable and private.

## The steps for `search youtube lofi beats`

1. **Read the scripts.** Each script starts with header comments (`keywords`, `desc`, `category` ...). JeeG caches them in `index.json` and only re-reads scripts that changed.
2. **Clean the line.** Filler words ("please", "the", "can you", "how", "what") are ignored; plurals are simplified.
3. **Score every script.** Each word of yours earns points:

| Match | Weight |
|---|---|
| A word in the script's file name (`open_youtube`: "youtube") | highest |
| A word in its `keywords:` line | slightly lower |
| A close spelling (typo or swapped letters) | lower again |
| A very common word ("open", "folder", "search") | very low: can never decide alone |
| A phrase pattern (for example `10 days ago`) | bonus |

4. **Decide.** One clear winner runs. A tie gives a numbered menu. No match gives "No matching task" (plus "Did you mean...?" when something is close). Special cases when nothing fits: maths-looking text goes to the calculator, `open github.com` opens that site, `open <app>` tries to launch that app.
5. **Pass the rest as arguments.** `search youtube lofi beats` gives `lofi beats` to the YouTube script.
6. **Safety check.** Risky tasks ask `Run 'shutdown pc'? [y/N]`.
7. **Report.** `ok in 0.05s` or `failed (exit 1)`. The task is saved to history so `again` repeats it (private tasks are not saved).

## Why `open youtube` opens YouTube
"open" is shared by 110+ scripts, so it is nearly worthless; "youtube" is rare, so it wins.

## Typing tips
- Say it naturally: `please open the youtube` works.
- One typo is usually fine; JeeG asks "Did you mean...?" before running a repaired line. Answer `y` and it remembers your wording as an alias.
- Put exact text in double quotes: `search "to be or not to be"`.
- Several tasks in one line: `open gmail and open calendar`, `open youtube then set timer 20 minutes`. JeeG splits on `and`, `then`, `;`, `&` only when every part clearly matches a different task and none is a free-text task (messages, timers, notes). Otherwise it is one task (`search tom and jerry` stays one search).
- Maths works without a keyword: `25 * 4`, `2 plus 2`, `15% of 200`, `sqrt 144`, numbers in words (`five thousand times 3`).
- Free-text tasks keep your words untouched.
- Short forms are repaired (`mail` = email, `pwd` = password, `pic` = picture) with a note of what it understood.

## See the ranking: `explain`

    explain play shape of you
      1.02  play song      args: shape of you  <- would run
      0.92  play pause     args: shape

`<- tied (menu)` means you would get a menu. Make your wording more specific, or add an alias.

## When it picks wrong or asks too much
- Be specific: `open youtube music`.
- `alias add yt = open youtube` (see [Routines, Aliases, Variables and Automation](Routines-Aliases-Variables-and-Automation)).
- `misses` lists what matched nothing: the best clues for aliases.
- When you choose from a menu, a short phrase is remembered as an alias; `alias remove <phrase>` undoes it.
