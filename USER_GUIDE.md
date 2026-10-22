# JeeG User Guide

JeeG lets you type what you want in plain words, such as `open youtube` or `set timer 10 minutes`, and runs the matching script from the `scripts` folder. This guide explains how to use it, how it decides what to run, and how to extend it.

Contents

1. What JeeG is
2. Install and first run
3. How a line you type is understood
4. Typing tips
5. Built-in commands, options and exit codes
6. Safety and confirmations
7. Where your data lives
8. Feature walkthroughs
9. Teaching and checking JeeG: aliases, explain, did-you-mean, misses, stats, doctor
10. Adding your own task
11. Optional tools
12. Troubleshooting
13. Questions people ask
14. What has and has not been tested
15. Appendix: every task

---

## 1. What JeeG is

- A small launcher written in Python (standard library only). It has no background service and does not need an account.
- It reads every script in `scripts/`, matches your words to a script, and runs it. A script is just a file you can open and edit.
- 417 tasks are included across apps, websites, files, system, network, reminders, personal records, money calculators, text tools, developer tools and quick searches.
- It runs on Windows, macOS and Linux. Python 3.9 or newer is required.
- It is quick (about 56 ms per command including Python start-up, measured on Linux) and light (about 16 MB while a command runs; nothing stays in memory between commands, except reminders and alarms you set).

JeeG does not "understand" language like an AI chat assistant. It matches words against scripts you can see. That makes it fast, predictable and private, but it only knows tasks that have a script. Anything unknown gets a plain "No matching task" instead of a guess.

---

## 2. Install and first run

1. Install Python 3.9 or newer from python.org (on Windows tick "Add Python to PATH").
2. Unzip the JeeG folder anywhere you like.
3. Open a terminal in that folder and check the setup:

       python jeeg.py doctor

   `doctor` confirms Python, the data folder, the scripts and which optional tools are present.
4. Start it:

       python jeeg.py

   You get a `task>` prompt. Type a task and press Enter. Type `exit` to leave.

       task> open youtube
       task> weather in mumbai
       task> 25 * 4
       task> exit

**One-shot use** (no prompt): `python jeeg.py "open youtube"`. Use quotes when your text has symbols the terminal treats specially, such as `*` or `?`.

**Shortcuts from inside the folder:** `./jeeg open youtube` (Mac/Linux) or `jeeg.bat open youtube` (Windows).

**Run it from any folder:** run `python install.py` once. It creates a command named `jeeg`, so you can then type `jeeg open youtube` anywhere.
- `python install.py --name go` uses a different command name (avoid `tr`, which already exists on Mac and Linux).
- `python install.py --uninstall` removes it.
- If the installer says its folder is not on your PATH, add that folder to PATH as it shows.
- If you move the JeeG folder later, run the installer again.

---

## 3. How a line you type is understood

Take `search youtube lofi beats`. JeeG goes through these steps.

**Step 1: Read the scripts folder.** Each script starts with a few comment lines that describe it:

    # keywords: video, videos, watch, search
    # desc: Open YouTube or search it
    # category: entertainment

JeeG caches this information in `index.json` in your data folder, so the next start only re-reads scripts that changed.

**Step 2: Clean the line.** Filler words ("please", "the", "can you", "how", "what") are ignored. Plurals are simplified, so "downloads" matches "download".

**Step 3: Score every script.** A script earns points for each of your words:

| Match | Weight |
|---|---|
| A word in the script's file name (`open_youtube`: "youtube") | highest |
| A word in its `keywords:` line | slightly lower |
| A close spelling (a typo like "brwoser", or swapped letters like "taems") | slightly lower again |
| A very common word ("open", "folder", "search") | very low, so it can never decide alone |
| A phrase pattern that identifies the task (for example `10 days ago`) | a bonus |

Common words count for little. That is why `open youtube` opens YouTube and not Gmail: "open" is shared by more than 110 scripts, while "youtube" is unique.

**Step 4: Decide.**
- One clear winner: it runs.
- Two scripts fit equally well: you get a numbered menu. JeeG never guesses on a tie.
- Nothing fits: you get "No matching task", plus a "Did you mean...?" suggestion if something is close.
- Special cases when nothing fits: maths-looking text (`25 * 4`, `15% of 200`) goes to the calculator, `open github.com` opens that website, and `open <app name>` tries to launch that installed app.

**Step 5: Pass the extra words to the script.** Words that were not used to find the script become its arguments:

    search youtube lofi beats   ->  open_youtube.py gets:  lofi beats
    weather in mumbai           ->  check_weather.py gets: mumbai

**Step 6: Safety check, then run.** Risky tasks ask `Run 'shutdown pc'? [y/N]` first (see section 6).

**Step 7: Report.** You see `ok in 0.05s` or `failed (exit 1)` and the script's own message. The task is saved to history so you can type `again` to repeat it.

---

## 4. Typing tips

- **Say it naturally.** `please open the youtube`, `can you check my battery` and `battery status` all work. Politeness words are ignored.
- **Typos are tolerated.** One mistyped word is usually fine (`opne youtub` gets a "Did you mean?"). Two typos in a short word may not match.
- **Put exact text in double quotes.** `search "to be or not to be"` keeps the phrase exactly. Quotes are also how you give JeeG a password or any text with special characters.
- **Several tasks in one line.** `open gmail and open calendar`, or `open youtube then set timer 20 minutes`. JeeG splits on `and`, `then`, `;` and `&` (not commas, so `1,200.50` and `random choice pizza, burger or pasta` stay whole). It runs the parts separately only if every part clearly matches a different task and none of them is a free-text task such as a message, timer or note. Otherwise the whole line is one task, so `search tom and jerry` stays a single search.
- **Free-text tasks keep your words.** Messages, notes, timers and the calculator pass your words through untouched.
- **Maths works without a keyword.** `25 * 4`, `2 plus 2`, `15% of 200`, `sqrt 144`.
- **Be specific when a menu appears.** `open youtube music` instead of `open youtube`. Or create an alias (section 9).
- **See why a task was chosen.** `explain <your words>` shows the ranking.

---

## 5. Built-in commands, options and exit codes

Commands (typed at the prompt or after `jeeg.py`):

| Command | What it does |
|---|---|
| `list` / `list web` | Show all tasks / only one category. A `*` marks tasks that ask before running |
| `again` | Repeat the last task |
| `history` | Recent tasks |
| `alias add wa = send whatsapp to` | Save your own short word. Also `alias list`, `alias remove wa` |
| `explain <words>` | Show which tasks match, their scores, and which would run |
| `misses` | Phrases that matched nothing, to teach as aliases |
| `stats` | Which tasks you use most, how long they take, how often they fail |
| `doctor` | Check Python, the data folder, scripts, optional tools and internet |
| `pack list` / `pack off <category>` / `pack on <category>` | Turn whole categories of tasks off or on (for example `pack off games`). Turned-off tasks are never matched |
| `plugins` | Show the plugin folder and any plugins in it (see 10) |
| `tips` | Show one task you may not have tried yet |
| `reindex` | Rebuild the script cache (after you edit a script's header) |
| `selftest` | Check every script: it has a description and keywords, its code compiles, and it is found by its own name |
| `exit` | Quit |

Options (put them before your words):

| Option | Meaning |
|---|---|
| `--dry-run` | Show what would run without running it |
| `-y`, `--yes` | Do not ask for confirmation |
| `--timeout 30` | Stop a script after 30 seconds |
| `--dir PATH` | Also read scripts from another folder (can repeat; also the `TASK_SCRIPTS_DIR` variable) |
| `--version`, `-h` | Version / help |

Exit codes: `0` ok, `1` error or no match, `2` ambiguous (menu with no keyboard), `3` declined.

---

## 6. Safety and confirmations

- Tasks that can lose data or change the system ask first: shutdown, restart, sleep/log out, kill a process or port, delete empty folders, delete old downloads, shred file, undo last commit, git push, pip install, check updates, restart explorer, empty trash and similar. In `list` they have a `*`.
- Add the word `preview` to the delete tasks to only list what would happen (for example `delete empty folders downloads preview`). Preview runs without asking.
- If JeeG is started by another program (no keyboard), confirmation-needing tasks refuse unless you add `--yes`.
- Nothing is deleted without confirmation. `delete old downloads` does not delete: it moves files into a holding folder inside your data folder, and tells you where.
- `bulk rename` only previews. Add the word `apply` to really rename. It refuses if two files would end up with the same name.
- Zip and tar extraction refuse archives that try to write outside their folder, and tar files with links or device entries.
- Only `http`, `https`, `mailto`, `tel`, `sms` and `whatsapp` links are ever opened, so a changed saved link cannot launch a program or open a local file. `http get` accepts only web addresses.
- Text you type is put into web addresses safely (encoded), never pasted in raw.
- Your data folder is readable only by you on Mac and Linux. (On Windows it lives in your user profile, which other accounts cannot normally read.)
- `import data` checks every file in a backup before writing anything, and saves your current data first.
- `clean temp files` only removes your own old files, never other users' or the system's.
- Lines over 2000 characters are refused, and terminal control characters are removed.
- If a task hits an unexpected problem it prints one plain line instead of a Python error. Set `JEEG_DEBUG=1` to see the full details.
- Plugins and extra script folders (`--dir`) run with your permissions, like any program you install: only use ones you trust.
- Host names, ports and package names are checked before being passed to other programs.
- Critical system processes cannot be killed with `kill process`.
- No task sends your files or personal data anywhere. Web tasks open a page in your normal browser, so you stay signed in; JeeG never reads your passwords.
- Password tasks (`password strength`, `breach check`) never write what you typed to history. `breach check` sends only the first 5 characters of a hash of the password to the public Have I Been Pwned range service; the password never leaves your computer. Your terminal itself may still keep its own command history, so for real passwords type them at the `jeeg` prompt rather than in a one-shot shell command.

---

## 7. Where your data lives

Everything personal is stored in a folder named `.jeeg` in your home folder (`~/.jeeg`, or `C:\Users\<you>\.jeeg` on Windows). If you used an earlier version, your old `.taskrunner` folder is still found and used automatically. Set the `JEEG_HOME` environment variable to keep the data somewhere else.

| File | Contents |
|---|---|
| `index.json` | the script cache (safe to delete) |
| `history.jsonl` | what you typed (private tasks are not recorded) |
| `log.jsonl` | task name, result and seconds for each run (no text you typed) |
| `misses.log` | phrases that matched nothing |
| `aliases.json` | your aliases (you can edit it) |
| `routines.json` | your routines (you can edit it) |
| `reminders.json` | background reminders and alarms |
| to-dos, notes, journal, expenses, shopping list, saved links, habits, birthdays, snippets, contacts | one small file each |
| `trash/` | files moved by `delete old downloads` |

Files are written safely (written to a temporary file, then swapped in), so a crash cannot leave a half-written file. To back everything up, copy the folder. To reset one thing, delete its file. You can delete the logs at any time.

---

## 8. Feature walkthroughs

The examples below are things you can type. Use `list` or the appendix for the exact usage of each task.

### 8.1 Opening things
- Websites: `open youtube`, `open gmail`, `open github.com`, `open maps`, `search cats`, `search images golden retriever`, `search news election`.
- Apps: `open chrome`, `open vscode`, `open task manager`, `open settings`, `open vlc`, or `open <any installed app>`.
- Folders: `open downloads`, `open documents`, `open desktop`.

### 8.2 Music and messages
- `play shape of you` opens a search on YouTube Music (a browser cannot press play for you, so click the first result). `play shape of you on spotify` uses Spotify. Plain `play` toggles pause/resume. `next song`, `previous song`.
- `add contact mom 9876543210`, then `send whatsapp to mom see you at 5`. WhatsApp opens a chat with the message already typed and you press send; WhatsApp does not allow silent sending. Ten-digit numbers are assumed to be Indian (+91).

### 8.3 Routines
A routine is a named list of task phrases JeeG runs in order.
- Built in: `start work day`, `end work day`, `study mode`, `meeting mode`, `night mode`.
- `list routines` shows them, `run routine <name>` runs one, `edit routines` opens `routines.json`.
- In `routines.json` each routine is a list. Plain strings are task phrases. `say:text` prints a message and `wait:5` pauses 5 seconds. Example:

      "start_work_day": ["say:Starting...", "open gmail", "open calendar", "todo list"]

- Routines can take words. Write `{1}`, `{2}` ... in a step, then give the words when you run it: `run routine morning Asha london`. If you give too few, JeeG stops and says how many it needs.
- Add your own routine by adding a new key, then run it with `run routine <name>`.

### 8.4 Reminders, alarms and timers
- `remind me in 20 minutes to call mom`, `set alarm 6:30 am`, `set timer 10 minutes tea`, `stopwatch`.
- A time like `5:30` without am/pm is read as 24-hour time, so write `5:30 pm` when you mean the evening.
- `show reminders` lists active ones, `stop reminders` cancels them all.
- Habits of the day: `water reminder`, `eye break`, `stretch reminder`, `pomodoro` (25 minutes work, 5 break; `pomodoro 4 rounds`), `daily briefing`.
- Reminders run in a small background process, so they still fire after you close the terminal. They do not survive a computer restart.

### 8.5 Your own records
| What | Examples |
|---|---|
| To-dos | `add todo buy milk`, `todo list`, `todo done 1`, `todo clear` |
| Notes | `add note call dentist`, `show notes` |
| Journal | `journal add had a great day`, `journal show 7` (last 7 days) or `journal show gym` (search) |
| Expenses | `add expense 250 lunch`, `show expenses`, `expense total`, `undo expense` |
| Shopping | `shopping add milk`, `shopping list`, `shopping remove milk`, `shopping clear` |
| Links | `save link <name> <url>`, `open link <name>`, `list links`, `remove link <name>` |
| Habits | `habit done gym`, `habit streak gym` |
| Birthdays | `add birthday mom 12 mar`, `upcoming birthdays`, `remove birthday mom` |
| Snippets | `save snippet`, `paste snippet`, `list snippets`, `remove snippet` |
| Contacts | `add contact mom 9876543210`, `show contacts` |

### 8.6 Money calculators
These use Indian digit grouping (lakh and crore) and were checked against independent calculations.
- `emi loan 25 lakh 8.5% 20 years`
- `sip growth 5000 12% 15 years`
- `compound interest ...`
- `gst amount 1000 18%`
- `split bill 2450 among 4`
- `percentage change 80 to 100`
- `discount price 2999 30%`
- `currency convert 100 usd to inr` and `crypto price bitcoin` need internet.
- Plain maths and units: `15% of 200`, `convert 5 km to miles`.

### 8.7 Dates and time
- `time in london and tokyo`, `time in mumbai`, `what time is it in dubai`
- `what day is 15 aug 2027`, `week number 25 dec 2026`
- `add 45 days to 1 jan 2027`, `3 months from today`, `10 days ago`
- `days between 1 jan 2027 and 25 dec 2027` (also counts working days Monday to Friday; public holidays are not excluded)
- `days until 25 dec 2026`, `age calculator 14 aug 2001`
- `unix timestamp` (now), `unix timestamp 1700000000`
- Month and year arithmetic clamps to the last day of a month (1 year after 29 Feb 2028 is 28 Feb 2029).

### 8.8 Files and media
- Find and inspect: `find file invoice`, `find text invoice in documents`, `folder size downloads`, `large files`, `find duplicates`, `file types in downloads`, `folder tree documents depth 3`, `recent files`.
- Organise: `organize downloads preview`, `backup folder documents`, `zip folder x`, `unzip file x.zip`, `move file a.txt to documents`, `copy file a.txt to desktop`, `open last download`, `copy path of report.pdf`.
- Clean up: `bulk rename downloads replace img with photo` (preview, then add `apply`), also `prefix`, `suffix`, `number <base>`, `lowercase`, `uppercase`, `underscores`; `delete empty folders downloads`; `delete old downloads 90 days`.
- Pictures: `resize image photo.jpg to 800` (or `800x600`, or `50%`), `convert image a.png to jpg`, `images to pdf <folder or files>`. These write a new file next to the original and never overwrite.
- PDF: `merge pdf a.pdf b.pdf`, `split pdf report.pdf pages 2-4` (without pages it writes one file per page into a new folder).
- Video: `compress video movie.mp4`, `extract audio movie.mp4` (needs ffmpeg).
- Bare file names are looked up in the current folder, then Downloads, Desktop and Documents. Put names with spaces in "quotes".

### 8.9 System and network
- Status: `system info`, `memory usage`, `cpu usage`, `battery status`, `disk space`, `running processes`, `show uptime`, `cpu temperature`, `gpu info`, `screen resolution`, `usb devices`, `startup programs`, `installed programs chrome`.
- Control: `lock screen`, `shutdown pc`, `restart pc`, `sleep pc`, `cancel shutdown`, `schedule shutdown 45 minutes`, `volume up`, `set volume 40`, `mute`, `set brightness 60`, `take screenshot`, `toggle dark mode`, `turn off screen`, `keep awake 2 hours`, `restart explorer` (Windows), `check updates`.
- Network: `check internet`, `show ip`, `wifi info`, `ping host google.com`, `dns lookup x.com`, `port check host 443`, `check website github.com`, `listening ports`, `live network speed 10`, `trace route x.com`.
- Process control: `kill process notepad`, `kill port 3000` (both ask first).

### 8.10 Security
- `password strength "MyPass123"` rates a password offline with a rough crack-time estimate and explains the weaknesses it found. Always put the password in quotes. The estimate is a guide, not a guarantee.
- `breach check "MyPass123"` checks whether a password appears in known leaks (needs internet; see section 6 for what is sent).
- `compare files a.txt b.txt` says same or different and shows what changed for text files.
- `shred file secret.txt` overwrites a file with random data and deletes it. On SSDs and cloud-synced folders overwriting cannot be guaranteed; full-disk encryption is the real protection.
- `generate password 20` creates a random password.

### 8.11 Text tools
Most accept text after the task name or use your clipboard if you give none, and copy the result to the clipboard when one is available.
- `uppercase hello`, `lowercase HELLO`, `title case the quick fox`, `reverse text hello`
- `sort lines pear, apple, fig` (add `reverse` for Z-A; numbers sort numerically), `remove duplicates a, b, a`
- `word frequency notes.txt` (or pass text)
- `number to words 1234567` writes the number in Indian and international words; it also accepts `100 crore`, `2.5 lakh`, decimals and negatives. `roman numeral 2026` and `roman numeral MCMXC` convert both ways.
- `binary 1010`, `hex ff`, `255 in binary`, `0xff` show a number in decimal, binary, hex and octal.
- `lorem ipsum 3 paragraphs` or `lorem ipsum 50 words`, `qr code https://example.com` (saves a PNG in the current folder), `count words`, `encode base64`, `decode base64`, `hash text hello`, `json format`.

### 8.12 Developer
- Git: `git status`, `git diff`, `git log`, `git commit fix bug`, `git pull`, `git push`, `git branch`, `git clone <url>`, `git stash`, `git stash pop`, `git stash list`, `git checkout main`, `git checkout new feature-x`, `undo last commit`. `undo last commit` keeps your changes staged and refuses if that commit is already pushed.
- Projects: `new project demo flask` (also `python`, `node`, `html`), `create gitignore python`, `create venv`, `pip install requests`, `pip list`, `serve folder`, `lines of code myproject`, `check versions`.
- Data: `json to csv data.json`, `csv preview sales.csv`, `http get https://example.com`, `env variables [filter]` (secrets are hidden), `show path`.
- Docker and ports: `docker ps`, `docker stop all`, `kill port 3000`, `open localhost`.

### 8.13 Fun and learning
- `guess the number` (`guess number 1000` for a bigger range), `rock paper scissors`, `typing test`, `multiplication table 7 up to 20`.
- `quiz me` quizzes you from a text file of lines like `Capital of India | New Delhi`. Run `quiz notes myfile.txt` to use a file of your own. With no file it creates a sample at `~/.jeeg/quiz.txt`.
- `tell joke`, `daily quote`, `random fact`, `flip coin`, `roll 2d6`, `random number 1 100`, `random choice a, b, c`.

### 8.14 Looking things up (needs internet)
- `weather in pune`, `wiki summary python`, `define serendipity`, `news headlines`, `pincode 560001`, `translate good morning`.
- These open a search in your browser: `cricket score india`, `stock price tcs`, `lyrics <song>`, `recipe <dish>`, `movie info <title>`, `restaurants near me`, `restaurants in pune`, `pharmacy near me`, `flight status 6E 204`, `train status 12951`, `pnr status <10 digits>`, `directions to taj mahal`.
- Offline, these tasks say so plainly and do not hang.

---

### 8.15 New in version 2.3
- **Data safety:** `export data [folder]` zips all your JeeG records; `import data <file.zip>` restores them (your current data is first saved in a `trash/before-import-...` folder; zips with unsafe paths are refused). `backup status` shows when you last backed up, and JeeG gently reminds you if it has been a long time. `export records expenses` writes one record type to a CSV file.
- **Summaries:** `weekly summary` / `monthly summary` bring spending, habits, journal, to-dos, water and sleep onto one page.
- **Health and daily life:** `water log 500 ml`, `sleep log 7.5 hours`, `bmi 70 kg 175 cm`, `calorie calculator ...`, `fuel cost 250 km 18 kmpl 105`, `tip 1200 10%`, `unit price 500g 45 vs 1kg 80`, `cooking convert 2 cups flour to grams`.
- **Bills and classes:** `add bill electricity 15 1200`, `upcoming bills`, `remove bill ...`, `add class maths mon 9:00`, `show timetable`, `todays classes`, `remove class ...`.
- **Time, sky and money:** `meeting time 9 am india in london`, `sunrise delhi`, `sunset mumbai`, `moon phase`, `public holidays india 2026`, `exchange rates`, `gold price` (the last three need internet).
- **Files:** `old large files 100 mb`, `rename photos by date <folder>` (preview first), `compare folders a b`, `convert encoding old.txt`, `zip with password <folder>` (needs `pip install pyzipper`), `file hash setup.exe`, `json to yaml` / `yaml to json` (needs `pip install pyyaml`), `reading time notes.txt`, `meeting notes <title>`, `flashcards <file>`.
- **Developer:** `run tests`, `who uses port 3000`, `regex test "a+" on "caaat"` (runs in a separate process with a time limit), `git contributors`, `git recent changes`.
- **When nothing matches:** JeeG shows the closest tasks instead of just failing, and `stats` flags tasks that keep failing.

### 8.16 New in version 2.4
- **Undo:** `undo` puts back your last file move, rename or Downloads tidy (`move file`, `bulk rename ... apply`, `rename photos by date ... apply`, `organise downloads`). It remembers the last 20 and never overwrites a file that is already there; anything it cannot restore is listed as skipped.
- **Contacts:** `add contact mom 9876543210`, `add email mom mom@example.com`, `find contact mom` (or `whose number is mom`), `remove contact mom`, `email mom about dinner` (opens a Gmail draft; you press send), plus the existing `send whatsapp to mom hello`.
- **Budgets:** `set budget food 5000`, `budget report`, `remove budget food`. `add expense` now warns you at 80% of a category budget and when you go over.
- **Countdowns:** `add countdown exam 12 dec 2026`, `show countdowns`, `remove countdown exam`.
- **Search your own records:** `search my data dentist` looks through your notes, journal, to-dos, expenses and other saved lists.
- **Files and data:** `large folders downloads` (what is taking space), `csv summary data.csv`, `text diff a.txt b.txt`, `json minify data.json`, `url encode ...`, `url decode ...`.
- **Plugins:** drop extra task scripts into the `plugins` folder inside your JeeG data folder (type `plugins` to see where). They use the same header lines as the built-in tasks. Plugins are ordinary programs that run with your permissions, so only add ones you trust.
- Timings: `stats` already shows the average run time of each task and which ones fail.

## 9. Teaching and checking JeeG

**Aliases: your own short words**

    alias add wa = send whatsapp to
    wa mom see you at 5          ->  send whatsapp to mom see you at 5
    alias list
    alias remove wa

An alias can be up to three words and is expanded only at the start of a line. JeeG refuses an alias that points at nothing (so a typo can never create a dead alias) and refuses names of built-in commands such as `list`. Aliases are stored in `aliases.json`.

**Did you mean?** If nothing matches but something is close, it asks `Did you mean 'open youtube'? [y/N]`. Answer `y` and it runs that task and remembers your wording as an alias (the message says how to undo it). Without a keyboard it only prints the suggestion.

**explain** shows the ranking for any line:

    explain play shape of you
      1.02  play song      args: shape of you  <- would run
      0.92  play pause     args: shape
      ...

A line marked `<- tied (menu)` means you would get a menu; make your wording more specific or add an alias.

**misses** lists the phrases that matched nothing or were ambiguous. These are your best clues for aliases or for a keyword to add to a script.

**stats** shows your most used tasks, their average time and how many failed.

**doctor** checks your setup and is the first thing to run when something seems wrong.

---

## 10. Adding your own task

1. Create a file in `scripts/` whose name is the task, with words joined by underscores: `open_notes_app.py`. The file name is what people will say ("open notes app"), so name it in words.
2. Put a header in the first 15 lines, then your code:

       # keywords: notes, notebook, jot
       # desc: Open my notes app
       # category: apps
       from _lib import launch
       launch(win=[("start", "onenote")], mac=[("open", "-a", "Notes")], linux=[("gnome-notes",)], name="Notes")

3. Type `reindex`, then `selftest`. It confirms the script is found by its own name and that its code compiles.
4. Try it with `explain open notes app`.

Any language works: `.py`, `.sh`, `.bat`, `.cmd`, `.ps1`, `.js`. Words after the task name arrive as command-line arguments (in Python: `sys.argv[1:]`, or `args_text()` from `_lib`).

Keep personal scripts in another folder and start JeeG with `--dir PATH` (or set `TASK_SCRIPTS_DIR`), so updates to JeeG never touch them.

**Header lines**

| Line | Meaning |
|---|---|
| `# keywords:` | Extra words that should find this script |
| `# desc:` | One-line description shown by `list` |
| `# category:` | Group name in `list` |
| `# usage:` | Marks that the task takes words after its name (like `search <words>`) |
| `# confirm: yes` | Ask before running |
| `# priority: 1` | Wins ties against equally good matches |
| `# rawargs: yes` | Pass your words through untouched, dropping only words that matched the name (timers, calculator, messages) |
| `# rawargs: full` | Pass the whole sentence, quotes where you typed them (date maths, `find text`) |
| `# patterns: regex ;; regex` | Phrases that identify this task even when single words are ambiguous |
| `# private: yes` | Never write what you typed to history |

**Naming tips** (these avoid the most common problems)
- Do not give your task a name made of very common words (`open`, `search`, `list`, `file`, `image`). When too many scripts share a word, JeeG treats that word as weak, and other tasks can start matching less well. Run `selftest` and `python tests/test_routing.py` after adding tasks; they catch this.
- Avoid numbers in `keywords:`. A keyword like `25 minutes` would make a plain `25 * 4` route to your task.
- If two tasks clash, give the better one `# priority: 1`, or add a `# patterns:` line.

**Helpers for Python scripts** (`from _lib import ...`): `args_text()` (the words after the task), `open_url(url)`, `launch(...)` (open an app on any OS), `fail("message")`, `call([...])` (run a program), `data_dir()` (a place to save data), `notify(title, text)`, `need("module", "pip name")` (import an optional module or print an install hint). Other shared helpers live in `_files.py`, `_text.py`, `_dates.py`, `_money.py`, `_net.py` and others; files starting with `_` are helpers, not tasks.

---

## 11. Optional tools

JeeG needs nothing installed beyond Python. A few tasks use extras, and each tells you exactly what is missing:

| For | Install |
|---|---|
| Picture tasks | `pip install pillow` |
| PDF tasks | `pip install pypdf` |
| QR codes | `pip install "qrcode[pil]"` |
| Faster screenshots, process and temperature detail | `pip install psutil` |
| Video and audio tasks | ffmpeg (Windows `winget install ffmpeg`, Mac `brew install ffmpeg`, Linux `sudo apt install ffmpeg`) |
| Clipboard on Linux | `wl-clipboard`, `xclip` or `xsel` |
| Media keys on Linux | `playerctl` |
| Brightness on Linux | `brightnessctl` |
| Speaking text on Linux | `espeak-ng` |
| Timezone names on Windows | `pip install tzdata` |
| Password-protected zips | `pip install pyzipper` |
| JSON/YAML conversion | `pip install pyyaml` |

`doctor` shows which of these you already have.

---

## 12. Troubleshooting

| Problem | What to do |
|---|---|
| `python` not found | Install Python from python.org and tick "Add Python to PATH", or use `py jeeg.py` on Windows |
| "No matching task" | Type `list`. Use the words in the task name, or run `explain <your words>`, or make an alias |
| A menu appears | Two tasks fit equally; pick a number, or be more specific (`open youtube music`) |
| "needs confirmation; re-run with --yes" | You started JeeG without a keyboard; add `--yes` if you really want it |
| A task says a tool is missing | Install the tool it names (section 11) |
| You changed a script but nothing changed | Type `reindex` |
| A script's header is ignored | Headers must be in the first 15 lines and start with `#` |
| A web task fails | The task could not open a browser, or you are offline. Check with `check internet` |
| A reminder never fired | Reminders need the background process to start; check `show reminders`. They do not survive a computer restart |
| `jeeg` command not found after install | Add the folder the installer printed to your PATH and open a new terminal |
| Not sure what is wrong | `doctor`, then `selftest`, then `python tests/test_routing.py` |

---

## 13. Questions people ask

**Is it private?** Yes. Everything runs on your computer. Web tasks only open a page in your browser, and a few online tasks (weather, news, currency and so on) fetch public data. Nothing is sent to any AI service.

**Does it work offline?** Yes, except the online lookups, which say so when you are offline.

**Why does it ask me to choose sometimes?** Because two tasks fit equally well and guessing wrong could do the wrong thing. It is deliberate.

**Why did it not understand my sentence?** It matches words to scripts. Rephrase using the task's words, check with `explain`, or add an alias.

**Can I use it by voice?** Not in this version.

**Can I change what a task does?** Yes. Scripts are plain files in `scripts/`. Edit one and type `reindex` if you changed its header.

**Can I share my tasks?** Copy the script file. Only run scripts from people you trust, because a script can do anything you can do.

**How do I update?** Replace the program files (`jeeg.py`, `scripts/` and so on) with the new ones. Your data folder is separate and is kept. If you have edited built-in scripts, keep a copy first, or put your own scripts in a separate `--dir` folder.

---

## 14. What has and has not been tested

- Routing, maths, dates, files, text, PDF, picture, git and personal-record tasks are tested automatically on Linux. That includes typo and polite-wording variants of every task name.
- Online tasks (weather, Wikipedia, news, currency, crypto, dictionary, pincode, breach check, public holidays, exchange rates, gold price) were tested against sample replies shaped like the real services, not the live services. If a provider changes its format, that one task will say it could not read the answer.
- Parts that are specific to Windows or macOS (volume keys, startup list, installed programs, screen off, restart explorer and similar) were written carefully but have not been run on real Windows or macOS machines. The included `.github/workflows/test.yml` runs the test suite on all three systems if you put the project on GitHub.
- Not included in this version: a pop-up launcher window, recurring scheduled tasks through the system scheduler, remote control from a phone, and voice input.

Run the checks yourself any time:

    python jeeg.py selftest
    python tests/test_routing.py
    python tests/test_parsers.py
    python tests/test_engine.py
    python tests/test_security.py

---

## 15. Appendix: every task

417 tasks. In the Usage column, `<...>` is something you fill in and `[...]` is optional. A star means the task asks before running.


### ai

| Task | Usage | What it does |
|---|---|---|
| open chatgpt |  | Open ChatGPT |
| open claude |  | Open Claude |
| open gemini |  | Open Google Gemini |
| open perplexity | `open perplexity <words>` | Open Perplexity (or ask it) |

### apps

| Task | Usage | What it does |
|---|---|---|
| open app | `open app <name>` | Open any installed app by name (open app <name>) |
| open bluetooth settings |  | Open Bluetooth settings |
| open brave |  | Open Brave browser |
| open calculator |  | Open the calculator |
| open camera |  | Open the camera |
| open chrome |  | Open Google Chrome |
| open clock |  | Open the Clock / alarms app |
| open control panel |  | Open the classic Control Panel |
| open device manager |  | Open Device Manager |
| open edge |  | Open Microsoft Edge |
| open excel |  | Open Microsoft Excel / a spreadsheet app |
| open firefox |  | Open Firefox |
| open incognito |  | Open a private / incognito browser window |
| open notepad |  | Open a simple text editor |
| open paint |  | Open Paint / an image editor |
| open powerpoint |  | Open PowerPoint / a presentation app |
| open powershell |  | Open PowerShell |
| open resource monitor |  | Open Resource Monitor |
| open settings |  | Open system Settings |
| open snipping tool |  | Open the snipping / screenshot tool |
| open taskmanager |  | Open Task Manager / system monitor |
| open terminal |  | Open a terminal / command prompt |
| open vlc |  | Open VLC media player |
| open vscode |  | Open Visual Studio Code |
| open wifi settings |  | Open Wi-Fi settings |
| open word |  | Open Microsoft Word / a word processor |

### backup

| Task | Usage | What it does |
|---|---|---|
| backup info |  | Show when your data was last backed up and how much data you have |
| export data | `export data [folder]` | Back up all your JeeG data (to-dos, notes, expenses, journal...) into one zip file (export data) |
| export records | `export records <expenses\|journal\|todos\|habits\|birthdays\|notes>` | Save one list as a CSV file for Excel (export records expenses \| journal \| todos \| habits \| birthdays \| notes) |
| import data * | `import data <backup.zip>` | Restore your data from a backup zip made by 'export data' (current data is saved first) |

### birthdays

| Task | Usage | What it does |
|---|---|---|
| add birthday | `add birthday <name> <date>` | Save a birthday (add birthday mom 14 aug, add birthday raj 3 march 1999) |
| remove birthday | `remove birthday <name>` | Delete a saved birthday |
| upcoming birthdays |  | Show birthdays in the next 60 days |

### clipboard

| Task | Usage | What it does |
|---|---|---|
| clear clipboard |  | Clear the clipboard |
| copy to clipboard | `copy to clipboard <text>` | Copy text to the clipboard (copy hello world) |
| show clipboard |  | Show what is on the clipboard |
| speak text | `speak <text>` | Read text aloud (speak hello there) |

### developer

| Task | Usage | What it does |
|---|---|---|
| check versions |  | Show installed versions of Python, Node, Git, Docker, Java |
| count lines of code | `lines of code [folder]` | Count lines of code by language in a folder (lines of code myproject) |
| create gitignore | `create gitignore [python\|node\|java]` | Create or extend a .gitignore for a language (create gitignore python \| node \| java) |
| create venv |  | Create a Python virtual environment (.venv) here |
| csv preview | `csv preview <file.csv>` | Show the first rows of a CSV file as a table (csv preview data.csv) |
| csv summary | `csv summary <file.csv>` | Summarise a CSV: rows, columns, number totals and common values (csv summary data.csv) |
| docker ps |  | List running Docker containers |
| docker stop all * |  | Stop all running Docker containers |
| git branch |  | List git branches |
| git checkout | `git checkout <branch> \| git checkout new <branch>` | Switch to a git branch, or create one (git switch main, git checkout new feature-x) |
| git clone | `git clone <url>` | Clone a repository (git clone https://github.com/user/repo) |
| git commit * | `git commit <message>` | Stage everything and commit (git commit fix login bug) |
| git contributors |  | Who has committed to this git project, and how much (git contributors) |
| git diff |  | Summarise uncommitted git changes |
| git log |  | Show the last 10 git commits |
| git pull |  | Pull the latest changes (fast-forward only) |
| git push * |  | Push commits to the remote |
| git recent changes | `git recent changes [days]` | What changed in this git project recently (git recent changes, git recent changes 14 days) |
| git stash | `git stash [pop\|list\|save <note>]` | Stash or restore uncommitted changes (git stash, git stash pop, git stash list) |
| git status |  | Show git status of the current folder |
| git undo commit * |  | Undo the last commit but keep your changes (git undo last commit) |
| http get | `http get <url>` | Fetch a URL and show status, headers and the start of the body (http get https://example.com) |
| json minify | `json minify <file.json>` | Shrink a JSON file onto one line (json minify data.json) |
| json to csv | `json to csv <file.json>` | Convert a JSON file (a list of records) to CSV (json to csv data.json) |
| json to yaml | `json to yaml <file.json>` | Convert a JSON file to YAML (json to yaml config.json) |
| kill port * | `kill port <number>` | Stop whatever is listening on a port (kill port 3000) |
| new project | `new project <name> [python\|node\|html\|flask]` | Create a starter project folder (new project myapp python \| node \| html \| flask) |
| open codepen |  | Open CodePen |
| open dockerhub | `open dockerhub <words>` | Open Docker Hub |
| open github | `open github <words>` | Open GitHub or search it |
| open gitlab |  | Open GitLab |
| open huggingface | `open huggingface <words>` | Open Hugging Face |
| open kaggle | `open kaggle <words>` | Open Kaggle |
| open leetcode | `open leetcode <words>` | Open LeetCode |
| open localhost | `open localhost [port]` | Open http://localhost:<port> in the browser |
| open mdn | `open mdn <words>` | Open MDN Web Docs or search it |
| open npm | `open npm <words>` | Open npm or search Node packages |
| open pypi | `open pypi <words>` | Open PyPI or search Python packages |
| open stackoverflow | `open stackoverflow <words>` | Open Stack Overflow or search it |
| open vscode here |  | Open the current folder in VS Code |
| open w3schools |  | Open W3Schools |
| pip install * | `pip install <packages>` | Install Python packages (pip install requests) |
| pip list |  | List installed Python packages |
| pip outdated |  | List Python packages that have updates |
| regex tester | `regex test "<pattern>" on "<text>"` | Try a regular expression on some text and see the matches (regex test "\d+" on "abc 123 def 45") |
| run tests |  | Run the tests of the project in this folder (run tests): pytest, unittest, npm, go or cargo is detected |
| serve folder | `serve folder [port]` | Serve the current folder at http://localhost:8000 |
| show env variables | `env variables [filter]` | List environment variables (secrets hidden); add a word to filter (env variables java) |
| show path |  | Show the folders in your PATH, one per line, marking missing ones |
| text diff | `text diff <file1> <file2>` | Show the differences between two text files (text diff a.txt b.txt) |
| yaml to json | `yaml to json <file.yaml>` | Convert a YAML file to JSON (yaml to json config.yaml) |

### email

| Task | Usage | What it does |
|---|---|---|
| compose email | `compose email <words>` | Compose a Gmail message (words become the subject) |
| email to | `email <contact\|address> [about <subject>]` | Start an email to a saved contact or address (email mom about dinner) |
| open gmail |  | Open Gmail |

### entertainment

| Task | Usage | What it does |
|---|---|---|
| movie info | `movie info <title>` | Look up a movie or show on IMDb (movie info inception) |
| open hotstar |  | Open JioHotstar |
| open jiosaavn | `open jiosaavn <words>` | Open JioSaavn music |
| open netflix | `open netflix <words>` | Open Netflix |
| open primevideo |  | Open Amazon Prime Video |
| open spotify | `open spotify <words>` | Open Spotify web player or search it |
| open twitch | `open twitch <words>` | Open Twitch |
| open youtube | `open youtube <words>` | Open YouTube or search it |
| open youtube music | `open youtube music <words>` | Open YouTube Music or search it |
| play song | `play <song name> [on spotify\|youtube]` | Play a song: searches YouTube Music (or 'on spotify' / 'on youtube'); plain 'play' toggles play/pause |
| recipe lookup | `recipe <dish>` | Find a recipe (recipe paneer butter masala) |
| song lyrics | `lyrics <song>` | Find the lyrics of a song (lyrics shape of you) |

### files

| Task | Usage | What it does |
|---|---|---|
| backup folder | `backup folder <folder>` | Zip a folder into ~/Backups with a timestamp (backup folder documents) |
| bulk rename | `bulk rename <folder> replace <old> with <new>` | Rename many files at once, with a preview first (bulk rename downloads replace img with photo) |
| clean temp files * |  | Delete temporary files older than 24 hours |
| compare files | `compare files <a> <b>` | Compare two files: same or different, and what changed (compare files a.txt b.txt) |
| compare folders | `compare folders <a> <b>` | Compare two folders: what is only in one, and what differs (compare folders a b) |
| convert encoding | `convert encoding <file>` | Fix garbled text by saving a file as UTF-8 (convert encoding old.txt) |
| copy file | `copy file <file> to <folder>` | Copy a file or folder (copy file report.pdf to desktop) |
| copy path | `copy path of <file>` | Copy a file or folder's full path to the clipboard (copy path of report.pdf) |
| create folder | `create folder <name>` | Create a new folder on your Desktop (create folder projects) |
| delete empty folders * | `delete empty folders <folder>` | Remove empty folders inside a folder (add 'preview' to just list them) |
| delete old downloads * | `delete old downloads [days]` | Move old files from Downloads to a safe holding folder (delete old downloads 90 days) |
| empty trash * |  | Empty the Recycle Bin / Trash permanently |
| file types | `file types in <folder>` | Count files by type in a folder (file types in downloads) |
| find duplicates | `find duplicates [folder]` | Find duplicate files in a folder (read-only report) |
| find file | `find file <name words>` | Find files by name under your home folder (find file invoice pdf) |
| find text | `find text <words> in <folder>` | Search inside text files for a phrase (find text invoice in documents) |
| folder size | `folder size [folder]` | Show how big a folder is (folder size downloads) |
| folder tree | `folder tree [folder] [depth n]` | Show a folder as a tree (folder tree documents, tree depth 3) |
| large files | `large files [folder]` | Find the biggest files (large files downloads) |
| large folders | `large folders [folder]` | Show which sub-folders take the most space (large folders downloads) |
| move file | `move file <file> to <folder>` | Move a file or folder (move file report.pdf to documents) |
| open last download |  | Open the newest file in Downloads |
| organize downloads * | `organize downloads [preview]` | Sort loose files in Downloads into folders by type (add 'preview' to just look) |
| recent files |  | List recently changed files in Documents, Downloads and Desktop |
| rename photos by date | `rename photos by date <folder> [apply]` | Rename photos to their date taken, e.g. 2026-10-21_143005.jpg (preview first; add 'apply') |
| stale files | `old large files [size] [age] [folder]` | Find big files you have not touched for a long time (old large files 100 mb 1 year in downloads) |
| undo files | `undo` | Undo your last file move, rename or Downloads tidy (undo, undo move, undo rename) |
| unzip file | `unzip file <archive>` | Extract a .zip / .tar.gz safely (unzip file archive.zip) |
| zip folder | `zip folder <folder>` | Zip a folder next to itself (zip folder projects) |
| zip with password | `zip with password <file\|folder>` | Make a password-protected AES zip of a file or folder (the password is asked privately, not typed in the command) |

### folders

| Task | Usage | What it does |
|---|---|---|
| open desktop |  | Open the Desktop folder |
| open documents |  | Open the Documents folder |
| open downloads |  | Open the Downloads folder |
| open file explorer |  | Open the file manager at your home folder |
| open music folder |  | Open the Music folder |
| open pictures |  | Open the Pictures folder |
| open scripts folder |  | Open the folder holding these task scripts |
| open trash |  | Open the Recycle Bin / Trash |
| open videos folder |  | Open the Videos folder |

### food

| Task | Usage | What it does |
|---|---|---|
| open swiggy |  | Open Swiggy |
| open zomato |  | Open Zomato |

### fun

| Task | Usage | What it does |
|---|---|---|
| guess number | `guess number [max]` | Play 'guess the number' (guess number, or guess number 1000) |
| multiplication table | `multiplication table <n> [up to <m>]` | Print a multiplication table (table of 7, multiplication table 12 up to 20) |
| quiz notes | `quiz notes [file]` | Quiz yourself from a notes file of 'question \| answer' lines (quiz notes myfile.txt) |
| rock paper scissors |  | Play rock paper scissors against the computer |
| typing test |  | Test your typing speed and accuracy |

### habits

| Task | Usage | What it does |
|---|---|---|
| habit done | `habit done <name>` | Tick a habit for today (habit done gym) |
| habit streak |  | Show all habits with current streak and the last 14 days |

### hardware

| Task | Usage | What it does |
|---|---|---|
| mute volume |  | Mute or unmute the sound |
| next track |  | Skip to the next song |
| play pause |  | Play or pause the current media |
| previous track |  | Go back to the previous song |
| set brightness | `set brightness <0-100>` | Set screen brightness (set brightness 60) |
| set volume | `set volume <0-100>` | Set the volume to a level (set volume 40) |
| show desktop |  | Minimise everything and show the desktop |
| take screenshot |  | Save a screenshot to your Pictures folder |
| toggle dark mode | `dark mode on\|off` | Switch dark/light mode (dark mode on, dark mode off, or toggle) |
| volume down | `volume down [amount]` | Lower the volume |
| volume up | `volume up [amount]` | Raise the volume |

### health

| Task | Usage | What it does |
|---|---|---|
| bmi calculator | `bmi <weight> kg <height> cm` | Body mass index from weight and height (bmi 70 kg 175 cm, bmi 70 5 ft 9 in) |
| calorie calculator | `calorie calculator <male\|female> <age> years <kg> kg <cm> cm [activity]` | Estimate daily calories you burn (calorie calculator male 30 years 70 kg 175 cm moderate) |
| sleep log | `sleep log <hours> \| sleep show` | Log how long you slept and see your recent average (sleep log 7.5 hours, sleep show) |
| water log | `water log <amount> [ml\|glasses\|bottles] \| water today \| water goal <ml>` | Log water you drank and see today's total (water log 500 ml, water log 2 glasses, water today, water goal 3000) |

### info

| Task | Usage | What it does |
|---|---|---|
| check weather | `check weather <words>` | Weather for a city (e.g. weather mumbai) |
| daily quote |  | Show an inspiring quote |
| define word | `meaning of <word>` | Dictionary meaning in the terminal (meaning of ephemeral); opens Google if offline |
| moon phase |  | Today's moon phase and the next new and full moon (moon phase) |
| news headlines | `news headlines [topic]` | Top news headlines in the terminal (news headlines, news cricket) (needs internet) |
| pincode lookup | `pincode <PIN>` | Look up an Indian PIN code (pincode 110001) (needs internet) |
| public holidays | `public holidays [country] [year] \| next holiday` | Public holidays for a country and year (public holidays india 2026, holidays in us) |
| random fact |  | Show an interesting fact |
| sunrise sunset | `sunrise [city] [tomorrow\|date]` | Sunrise, sunset and day length for a city (sunrise delhi, sunset mumbai tomorrow) |
| tell joke |  | Tell a clean joke |
| weather report | `weather report [city]` | Weather as text in the terminal (weather report mumbai) (needs internet) |
| wiki summary | `wiki summary <topic>` | Short Wikipedia summary (wiki summary einstein) (needs internet) |

### journal

| Task | Usage | What it does |
|---|---|---|
| journal add | `journal add <text>` | Add a dated diary entry (journal had a great day) |
| journal show | `journal show [days\|word]` | Read your journal (last 7 days; or a number of days, or a word to search) |

### learning

| Task | Usage | What it does |
|---|---|---|
| open coursera | `open coursera <words>` | Open Coursera |
| open duolingo |  | Open Duolingo |
| open khanacademy | `open khanacademy <words>` | Open Khan Academy |
| open nptel |  | Open NPTEL |
| open udemy | `open udemy <words>` | Open Udemy |

### links

| Task | Usage | What it does |
|---|---|---|
| list links |  | List saved bookmarks |
| open link | `open link <name>` | Open a saved bookmark by name (open link code) |
| remove link | `remove link <name>` | Delete a saved bookmark |
| save link | `save link <url> <name>` | Save a bookmark (save link github.com my code) |

### lists

| Task | Usage | What it does |
|---|---|---|
| shopping add | `shopping add <items>` | Add items to the shopping list (shopping add milk, eggs and bread) |
| shopping clear * |  | Clear the whole shopping list |
| shopping list |  | Show the shopping list |
| shopping remove | `shopping remove <n\|name>` | Cross an item off (shopping remove 2, or shopping remove milk) |

### maps

| Task | Usage | What it does |
|---|---|---|
| get directions | `get directions <words>` | Directions to a place in Google Maps |
| open maps | `open maps <words>` | Open Google Maps or search a place |
| pharmacy near me | `pharmacy near me \| pharmacy in <place>` | Find a medical store or pharmacy near you or in a place (pharmacy near me) |
| restaurants near me | `restaurants near me \| restaurants in <place>` | Find restaurants near you or in a place (restaurants near me, restaurants in pune) |

### media

| Task | Usage | What it does |
|---|---|---|
| compress video | `compress video <file>` | Make a video file smaller with ffmpeg (compress video movie.mp4) |
| convert picture | `convert image <file> to <format>` | Convert a picture to another format (convert image photo.png to jpg) |
| extract audio | `extract audio <video file>` | Save the sound of a video as MP3 (extract audio movie.mp4) |
| merge pdf | `merge pdf <file> <file> ...` | Join PDF files into one (merge pdf a.pdf b.pdf) |
| pictures to pdf | `images to pdf <folder\|files>` | Combine pictures into one PDF (images to pdf <folder or files>) |
| resize picture | `resize image <file> to <width>` | Resize a picture (resize image photo.jpg to 800 wide, or 50%) |
| split pdf | `split pdf <file> [pages 2-4]` | Split a PDF into pages, or pull out some pages (split pdf report.pdf pages 2-4) |

### money

| Task | Usage | What it does |
|---|---|---|
| add bill | `add bill <name> <day> [amount]` | Remember a monthly bill's due day (add bill electricity 15 1200) |
| add expense | `add expense <amount> <category> [note]` | Record spending (spent 450 on groceries, add expense 200 food lunch) |
| budget report | `budget report` | Show this month's spending against your budgets (budget report) |
| compound interest | `compound interest <amount> <rate%> <years>` | Compound interest (compound interest 10000 7 3 years [monthly]) |
| crypto price | `crypto price <coin>` | Live cryptocurrency price (crypto price bitcoin) (needs internet) |
| currency convert | `currency <amount> <from> to <to>` | Live currency conversion (currency 100 usd to inr) (needs internet) |
| discount price | `discount <price> <percent> [more %]` | Price after discount(s) (discount 2000 30% off, discount 2000 30 10) |
| emi loan | `emi <amount> <rate%> <years>` | Loan EMI (emi 5 lakh 8.5 5 years) |
| exchange rates | `exchange rates [base currency]` | Table of today's exchange rates against the rupee (exchange rates, exchange rates eur) |
| expense total | `expense total [month]` | Spending totals by category (expense total, expense total last month) |
| fuel cost | `fuel cost <km> km <mileage> kmpl <price>` | Trip fuel cost from distance, mileage and price (fuel cost 250 km 18 kmpl 105 per litre) |
| gst amount | `gst <amount> [rate] [inclusive]` | GST add or remove (gst 1000 18, gst 1180 18 inclusive) |
| percentage change | `percentage change <old> to <new>` | Percentage change between two numbers (percentage change 80 to 100) |
| remove bill | `remove bill <name>` | Delete a saved bill (remove bill electricity) |
| remove budget | `remove budget <category>` | Remove a category budget (remove budget food) |
| set budget | `set budget <category> <amount>` | Set a monthly spending limit for a category (set budget food 5000) |
| show expenses | `show expenses [category] [month]` | List expenses (show expenses, show expenses food, show expenses last month) |
| sip growth | `sip <monthly> <return%> <years>` | SIP growth (sip 5000 12 10 years: monthly amount, yearly return %, years) |
| split bill | `split bill <amount> among <n> [tip %]` | Split a bill (split bill 2400 among 4 tip 10%) |
| tip calculator | `tip <bill> [percent%] [split <people>]` | Work out a tip and split the bill (tip 1200 10%, tip 2450 12% split 4) |
| undo expense * |  | Remove the last recorded expense |
| unit price | `unit price <qty><unit> <price> vs <qty><unit> <price>` | Which pack is cheaper per kg or litre (unit price 500g 45 vs 1kg 80) |
| upcoming bills | `upcoming bills [days]` | Bills due soon (upcoming bills, upcoming bills 30) |

### network

| Task | Usage | What it does |
|---|---|---|
| check internet |  | Check whether the internet is working |
| check speed |  | Test internet speed (Speedtest) |
| check website | `check website <url>` | Check if a website is up (check website github.com) |
| dns lookup | `dns lookup <domain>` | Look up the IP addresses of a domain |
| flush dns * |  | Clear the DNS cache |
| listening ports |  | Show which programs are listening on network ports |
| live network speed | `live network speed [seconds]` | Watch your current download/upload speed for a few seconds (live network speed) |
| ping host | `ping host <name or ip>` | Ping a host (ping google.com) |
| port check | `port check <host> <port>` | Check if a port is open (port check example.com 443) |
| port owner | `who uses port <number>` | Which program is using a port (who uses port 3000) |
| show ip |  | Show your local and public IP address |
| trace route | `trace route <host>` | Trace the network route to a host |
| wifi info |  | Show the Wi-Fi network you are connected to |

### power

| Task | Usage | What it does |
|---|---|---|
| cancel shutdown |  | Cancel a pending shutdown or restart |
| lock screen |  | Lock the computer |
| log out * |  | Sign out of the current user |
| restart pc * |  | Restart the computer (30 second delay, can be cancelled) |
| schedule shutdown * | `schedule shutdown <minutes>` | Shut down after N minutes (schedule shutdown 45 minutes) |
| shutdown pc * |  | Shut the computer down (30 second delay, can be cancelled) |
| sleep pc * |  | Put the computer to sleep |

### productivity

| Task | Usage | What it does |
|---|---|---|
| my data lookup | `search my data <words>` | Search your notes, journal, to-dos, expenses and other saved records (search my data milk) |
| note add | `add note <text>` | Save a quick note (note add call dentist at 5) |
| note list | `show notes [word]` | Show your recent notes (optionally filter by a word) |
| todo add | `add todo <text>` | Add a to-do item (add todo buy milk) |
| todo clear |  | Remove finished items from the to-do list |
| todo done | `todo done <number\|text>` | Mark a to-do done (todo done 3, or part of its text) |
| todo list |  | Show your to-do list |
| weekly summary | `weekly summary \| monthly summary` | One-page summary of your week or month: spending, habits, journal, to-dos, water and sleep (weekly summary, monthly summary) |

### reference

| Task | Usage | What it does |
|---|---|---|
| open wikipedia | `open wikipedia <words>` | Open Wikipedia or look up an article |

### reminders

| Task | Usage | What it does |
|---|---|---|
| add countdown | `add countdown <event> <date>` | Count the days to an event (add countdown exam 12 dec 2026) |
| eye break | `eye break [minutes]` | 20-20-20 eye break reminder every 20 minutes |
| pomodoro | `pomodoro [rounds] [N work] [N break]` | Pomodoro focus timer: 25 min work / 5 min break (pomodoro 4 rounds) |
| remind me | `remind me <when> <what>` | Background reminder (remind me at 5:30pm to call mom / in 20 minutes ... / every 2 hours ...) |
| remove countdown | `remove countdown <event>` | Delete a countdown (remove countdown exam) |
| set alarm | `set alarm <time>` | Set an alarm for a clock time (set alarm 6:30 am) |
| show countdowns | `show countdowns` | Show the days left for your events (show countdowns) |
| show reminders |  | List active background reminders and alarms |
| stop reminders |  | Cancel all background reminders and alarms |
| stretch reminder | `stretch reminder [minutes]` | Remind you to stand up and stretch every 45 minutes |
| water reminder | `water reminder [minutes]` | Remind you to drink water every 30 minutes |

### routines

| Task | Usage | What it does |
|---|---|---|
| daily briefing | `daily briefing [city]` | Daily briefing (say: morning briefing): date, weather, to-dos, birthdays, reminders |
| edit routines |  | Open the routines file to add or change routines |
| end work day |  | Routine: show to-dos then lock the screen after 5 s (editable) |
| list routines |  | List your routines and their steps |
| meeting mode |  | Routine: open Meet and your calendar (editable) |
| night mode |  | Routine: dark mode, dim screen, low volume (editable) |
| run routine | `run routine <name> [words]` | Run any routine from your routines file (run routine <name> [words]; steps can use {1} {2} {args}) |
| start work day |  | Routine: open mail and calendar, show your to-dos (editable) |
| study mode |  | Routine: notes app, low volume, 25-minute study timer (editable) |

### search

| Task | Usage | What it does |
|---|---|---|
| cricket score | `cricket score [team]` | Open live cricket scores (cricket score india, cricket score csk) |
| gold price | `gold price [city] \| silver price [city]` | Look up gold or silver rates (gold price, silver price delhi) |
| search google | `search google <words>` | Search Google (or open it) |
| search images | `search images <words>` | Search Google Images |
| search news | `search news <words>` | Search Google News / latest headlines |
| search scholar | `search scholar <words>` | Search Google Scholar for papers |
| stock price | `stock price <company>` | Look up a share price (stock price tcs, stock price apple) |
| translate text | `translate text <words>` | Translate text with Google Translate |

### security

| Task | Usage | What it does |
|---|---|---|
| breach check | `breach check "<password>"` | Check if a password has appeared in known data leaks (only a 5-character hash prefix is sent) |
| file hash | `file hash <file> [expected hash]` | Show the SHA-256, SHA-1 and MD5 fingerprint of a file, to check a download (file hash setup.exe) |
| password strength | `password strength "<password>"` | Rate how strong a password is, privately (password strength "MyPass123") |
| shred file * | `shred file <file>` | Overwrite a file with random data and delete it (cannot be undone) |

### shopping

| Task | Usage | What it does |
|---|---|---|
| open amazon | `open amazon <words>` | Open Amazon India or search it |
| open flipkart | `open flipkart <words>` | Open Flipkart or search it |
| open myntra | `open myntra <words>` | Open Myntra or search it |

### snippets

| Task | Usage | What it does |
|---|---|---|
| list snippets |  | List saved snippets |
| paste snippet | `paste snippet <name>` | Copy a saved snippet to the clipboard (paste snippet email) |
| remove snippet | `remove snippet <name>` | Delete a saved snippet |
| save snippet | `save snippet <name> <text>` | Save a reusable text snippet (save snippet email me@example.com) |

### social

| Task | Usage | What it does |
|---|---|---|
| add contact | `add contact <name> <number>` | Save a contact for WhatsApp (add contact mom 9876543210) |
| add email address | `add email <name> <address>` | Save an email address for a contact (add email mom mom@example.com) |
| find contact | `find contact <name>` | Look up a saved contact by name (find contact mom) |
| open discord |  | Open Discord |
| open facebook |  | Open Facebook |
| open instagram |  | Open Instagram |
| open linkedin |  | Open LinkedIn |
| open pinterest | `open pinterest <words>` | Open Pinterest or search it |
| open reddit | `open reddit <words>` | Open Reddit or search it |
| open snapchat |  | Open Snapchat Web |
| open telegram |  | Open Telegram Web |
| open twitter | `open twitter <words>` | Open X (Twitter) |
| open whatsapp |  | Open WhatsApp Web |
| remove contact * | `remove contact <name>` | Delete a saved contact (remove contact mom) |
| send whatsapp | `send whatsapp <contact\|number> <message>` | Start a WhatsApp message to a saved contact or number (send whatsapp to mom hello) |
| show contacts |  | List your saved contacts |

### study

| Task | Usage | What it does |
|---|---|---|
| add class | `add class <subject> <day> <time>` | Add a weekly class or lesson (add class maths mon 9:00, add class physics tue 2:30 pm room 4) |
| flashcards | `flashcards [count] [file]` | Spaced-repetition flashcards from a 'question \| answer' file; cards you miss come back sooner (flashcards, flashcards 5 myfile.txt) |
| reading time | `reading time <file>` | How long a text file or PDF takes to read (reading time notes.txt) |
| remove class | `remove class <subject> [day]` | Remove a class from the timetable (remove class maths mon) |
| show timetable |  | Show your weekly timetable |
| todays classes | `todays classes \| tomorrows classes` | Classes you have today or tomorrow (todays classes, tomorrows classes) |

### system

| Task | Usage | What it does |
|---|---|---|
| battery status |  | Show battery level and charging state |
| check updates * |  | Check which programs and system updates are waiting (does not install) |
| cpu temperature |  | Show processor temperature (where the computer allows it) |
| cpu usage |  | Show current CPU load |
| disk space |  | Show free space on your drives |
| gpu info |  | Show graphics card details |
| installed programs | `installed programs [name]` | List installed programs, or search them (installed programs chrome) |
| keep awake | `keep awake [2 hours]` | Stop the computer sleeping for a while (keep awake 2 hours) |
| kill process * | `kill process <name>` | Close a program by name (e.g. kill process notepad) |
| memory usage |  | Show RAM usage |
| restart explorer * |  | Restart Windows Explorer when the taskbar or desktop freezes |
| running processes |  | List the programs using the most memory |
| screen off |  | Turn the screen off without sleeping |
| screen resolution |  | Show your screen resolution |
| show uptime |  | Show how long the computer has been on |
| startup programs |  | List programs that start with your computer |
| system info |  | Show OS, CPU, memory, disk and uptime |
| usb devices |  | List connected USB devices |

### text

| Task | Usage | What it does |
|---|---|---|
| binary hex | `binary\|hex\|octal <number>` | Convert a number between decimal, binary, hex and octal (binary 1010, hex ff, 255) |
| dedupe lines | `remove duplicates <items>` | Remove duplicate lines or items, keeping the first (remove duplicates a, b, a, c) |
| lorem ipsum | `lorem ipsum [3 paragraphs\|50 words]` | Generate placeholder text (lorem ipsum 3 paragraphs, or 50 words) |
| lowercase text | `lowercase <text>` | lowercase some text (lowercase HELLO World) |
| number to words | `number to words <number>` | Write a number in words, Indian and international style (number to words 1234567) |
| qr code | `qr code <text or link>` | Make a QR code picture from text or a link (qr code https://example.com) |
| reverse text | `reverse text <text>` | Reverse text (reverse text hello) |
| roman numerals | `roman numeral <number\|numeral>` | Convert between Roman numerals and numbers (roman numeral 2026, or roman numeral MCMXC) |
| sort lines | `sort lines <items>` | Sort a list alphabetically or by number (sort lines pear, apple, fig); add 'reverse' for Z-A |
| title case text | `title case <text>` | Title Case Some Text (title case the quick brown fox) |
| uppercase text | `uppercase <text>` | UPPERCASE some text (uppercase hello world); with no text it uses the clipboard |
| url decode | `url decode <text>` | Turn a percent-encoded web address back into readable text (url decode hello%20world) |
| url encode | `url encode <text>` | Make text safe for use in a web address (url encode hello world & more) |
| word frequency | `word frequency <text\|file>` | Most common words in some text or a text file (word frequency notes.txt) |

### time

| Task | Usage | What it does |
|---|---|---|
| add days | `add <n> days to <date>` | Date arithmetic (add 45 days to 1 jan 2027, 3 months from today, 10 days ago) |
| age calculator |  | Work out an age from a birth date |
| convert time zone | `meeting time <time> <place> in <place>[, <place>]` | Convert a meeting time between places (meeting time 9 am india in london, 3 pm new york to mumbai) |
| date difference | `days between <date> and <date>` | Days between two dates (days between 1 jan 2027 and 25 dec 2027) |
| days until |  | Days until a date (days until 25 dec 2026) |
| set timer | `set timer <duration> [label]` | Countdown timer with a beep (set timer 10 minutes tea) |
| show calendar |  | Show a month calendar (show calendar march 2027) |
| show time |  | Show the current time and date |
| stopwatch |  | Start a stopwatch (press Enter to stop) |
| unix timestamp | `unix timestamp [number\|date]` | Unix timestamp now, or convert one (unix timestamp 1700000000, or a date) |
| week number | `week number [date]` | ISO week number, day of year and quarter (week number, week number 25 dec 2026) |
| weekday of | `what day is <date>` | Which weekday a date falls on (what day is 15 aug 2027) |
| world time | `time in <city>[, <city>]` | Current time in cities (time in london, tokyo and new york) |

### tools

| Task | Usage | What it does |
|---|---|---|
| open ilovepdf |  | Open iLovePDF (merge, split, compress PDFs) |
| open removebg |  | Open remove.bg background remover |
| open tinypng |  | Open TinyPNG image compressor |
| open virustotal |  | Open VirusTotal file/URL scanner |

### travel

| Task | Usage | What it does |
|---|---|---|
| flight status | `flight status <number>` | Check a flight's status (flight status 6E 204) |
| open irctc |  | Open IRCTC train booking |
| open makemytrip |  | Open MakeMyTrip |
| open uber |  | Open Uber |
| pnr status | `pnr status <10-digit pnr>` | Check an Indian Railways PNR status (pnr status 1234567890) |
| train status | `train status <number>` | Check a train's live running status (train status 12951) |

### utility

| Task | Usage | What it does |
|---|---|---|
| calculate | `calculate <expression>` | Calculate anything (calculate 15% of 200, 12 * (3+4), sqrt 144) |
| convert units | `convert <n> <unit> to <unit>` | Convert units offline (convert 5 km to miles, 100 f to c); falls back to Google for currency |
| cooking convert | `cooking convert <amount> <unit> [ingredient] to <unit>` | Convert cooking measures, with grams for common ingredients (cooking convert 2 cups flour to grams) |
| count words | `count words <text\|file>` | Count words, lines and characters in text or a file |
| decode base64 | `decode base64 <text>` | Decode Base64 text |
| encode base64 | `encode base64 <text>` | Base64-encode text |
| flip coin |  | Flip a coin |
| generate password | `generate password [length]` | Generate a strong random password (generate password 20) |
| generate uuid |  | Generate a random UUID |
| hash text | `hash text <text\|file>` | SHA-256 / SHA-1 / MD5 of text or a file |
| json format | `json format <file>` | Pretty-print and validate a JSON file |
| random choice | `random choice a, b, c` | Pick one option at random (random choice pizza, burger, pasta) |
| random number | `random number [min] [max]` | Random number (random number 1 to 50) |
| roll dice | `roll <n>d<sides>` | Roll dice (roll dice, roll 2d6, roll d20) |

### web

| Task | Usage | What it does |
|---|---|---|
| open browser |  | Open the default web browser |
| open website | `open website <address>` | Open any website (open website github.com) |

### work

| Task | Usage | What it does |
|---|---|---|
| meeting notes | `meeting notes [title]` | Create a dated meeting-notes file from a template (meeting notes weekly sync) |

### workspace

| Task | Usage | What it does |
|---|---|---|
| add event | `add event <words>` | Add a Google Calendar event (words become the title) |
| new document |  | Create a new Google Doc |
| new meeting |  | Start an instant Google Meet |
| new presentation |  | Create a new Google Slides deck |
| new spreadsheet |  | Create a new Google Sheet |
| open calendar |  | Open Google Calendar |
| open canva |  | Open Canva |
| open classroom |  | Open Google Classroom |
| open docs |  | Open Google Docs |
| open drive |  | Open Google Drive |
| open figma |  | Open Figma |
| open keep |  | Open Google Keep notes |
| open meet |  | Open Google Meet |
| open notion |  | Open Notion |
| open office |  | Open Microsoft Office online |
| open onedrive |  | Open OneDrive |
| open outlook |  | Open Outlook mail |
| open photos |  | Open Google Photos |
| open sheets |  | Open Google Sheets |
| open slack |  | Open Slack |
| open slides |  | Open Google Slides |
| open teams |  | Open Microsoft Teams |
| open trello |  | Open Trello |
| open zoom |  | Open Zoom |
