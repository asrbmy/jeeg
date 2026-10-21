# JeeG 2.3 - How It Works

You type what you want in plain words ("open youtube", "set timer 10 minutes", "send whatsapp to mom hi").
JeeG finds the matching script in the `scripts` folder and runs it.

- Pure Python 3.9+, nothing to install. Works on Windows, macOS and Linux.
- Light: about 16 MB of memory, about 65 ms per command, nothing running in the background (except reminders and alarms you set yourself).
- 399 ready-made tasks. You can add your own by dropping in a file.

---

## 1. Quick start

1. Install Python 3.9 or newer (python.org). Unzip this folder anywhere.
2. Open a terminal in the folder and run:

       python jeeg.py

3. At the `task>` prompt, type a task and press Enter:

       task> open youtube
       task> weather in mumbai
       task> 25 * 4
       task> exit

One-shot (no prompt): `python jeeg.py "open youtube"`.
Shortcuts: `./jeeg open youtube` (Mac/Linux) or `jeeg.bat open youtube` (Windows) from this folder.
To run it from any folder, run `python install.py` once. That creates the command `jeeg` (`jeeg open youtube`). Use `python install.py --name go` for another name (not `tr`: Mac and Linux already have a program called `tr`) and `python install.py --uninstall` to remove it.
Use quotes when your text has `*` or `?`, for example `python jeeg.py "25 * 4"`.

Type `list` any time to see every task, grouped by category.

The full manual is in `USER_GUIDE.md` (how it works, every feature with examples, adding your own tasks, troubleshooting, and a list of all tasks).

---

## 2. What is inside

    JeeG/
      jeeg.py        the engine (reads what you type, picks the script, runs it)
      scripts/             one small script per task (open_youtube.py, set_timer.py, ...)
        _lib.py _sys.py    helper code shared by the scripts (names starting with _ are not tasks)
        _files.py _dates.py _text.py _money.py _info.py _net.py _time.py _store.py _routine.py _worker.py
      tests/               checks that your phrases pick the right script
      jeeg / jeeg.bat      short launchers
      README.md            this file

Your own data (to-dos, notes, journal, expenses, shopping list, links, snippets, habits, birthdays, routines, reminders, history) is stored in a folder named `.jeeg` in your home folder. Files are written safely (a crash cannot half-write them). Set `JEEG_HOME` to keep that data somewhere else. If you used an earlier version, your old `.taskrunner` folder is still found and used automatically (`TASKRUNNER_HOME` also still works).

---

## 3. How a command is handled, step by step

When you type `search youtube lofi beats`:

**Step 1 - Read the scripts folder (fast).**
The engine looks at every script in `scripts/`. Each script starts with a few comment lines that describe it:

    # keywords: video, videos, watch, search
    # desc: Open YouTube or search it
    # category: entertainment

The engine remembers these in a small cache file, so the next start only re-reads scripts that changed.

**Step 2 - Clean up what you typed.**
Filler words ("please", "the", "can you", "how", "what") are ignored. Plurals are simplified ("downloads" = "download").

**Step 3 - Score every script.**
Each script earns points for matching your words:

| Match | Points |
|---|---|
| A word in the script's file name (`open_youtube`: "youtube") | highest |
| A word in its `keywords:` line | slightly lower |
| A close spelling (a typo like "brwoser", or swapped letters like "taems") | slightly lower again |
| Very common words ("open", "folder", "search") | very low, so they never decide alone |

The best score wins. This is why "open youtube" opens YouTube and not Gmail: the word "open" is shared by more than 110 scripts and counts for little, while "youtube" is unique.

**Step 4 - Decide.**
- One clear winner: it runs.
- Two scripts fit equally well: you get a numbered menu and choose. It never guesses on a tie.
- Nothing fits: it says so. (Special cases: `open <app name>` tries to launch that installed app, `open github.com` opens the website, and plain maths like `25 * 4` goes to the calculator.)

**Step 5 - Pass your extra words to the script.**
Words that were not used to find the script become its arguments:

    search youtube lofi beats   ->  script open_youtube.py gets:  lofi beats
    weather in mumbai           ->  script check_weather.py gets: mumbai

Put text in double quotes to keep it exactly as typed: `search "to be or not to be"`.

**Step 6 - Safety check, then run.**
Risky tasks (shutdown, restart, kill a program, delete, git push, pip install...) ask `Run 'shutdown pc'? [y/N]` first.
If JeeG is started by another program (no keyboard), it refuses these unless you add `--yes`.

**Step 7 - Report.** You see `ok in 0.05s` or `failed (exit 1)` and the script's own message.
The task is saved to history so you can type `again` to repeat it.

---

## 3b. Several tasks in one line

    open gmail and open calendar
    open youtube, then set timer 20 minutes

JeeG splits on "and", "then", ";" and "&" (not commas, so `random choice pizza, burger or pasta` and `1,200.50` stay whole). It only runs the parts as separate tasks if every part clearly matches a *different* script and none of them is a free-text task (messages, timers, notes). Otherwise your line is treated as one task, so `search tom and jerry` is still one search.

---

## 4. Everything you can type

| Command | What it does |
|---|---|
| `list` / `list web` | Show all tasks / only a category |
| `again` | Repeat the last task |
| `history` | Recent tasks |
| `reindex` | Rebuild the script cache |
| `selftest` | Check every script (has a description, keywords, valid code, and is found by its own name) |
| `alias add wa = send whatsapp to` | Your own short word for any task (then `wa mom hi`). Also `alias list`, `alias remove wa` |
| `explain <words>` | Show which tasks match what you typed, their scores, and which one would run |
| `misses` | Phrases that matched nothing, so you can teach them with an alias |
| `stats` | Which tasks you use most, how fast, and how often they fail |
| `doctor` | Check Python, the data folder, scripts, optional tools and internet |
| `exit` | Quit |

Options (put before your words):

| Option | Meaning |
|---|---|
| `--dry-run` | Show what would run, run nothing |
| `-y` / `--yes` | Do not ask for confirmation |
| `--timeout 30` | Stop a script after 30 seconds |
| `--dir PATH` | Also read scripts from another folder (can repeat; also `TASK_SCRIPTS_DIR`) |

Exit codes: 0 ok, 1 error or no match, 2 ambiguous, 3 declined.

---

## 4b. Teaching it

- **Aliases.** `alias add wa = send whatsapp to` saves a short word. It only accepts an alias that points at a real task (so a typo cannot create a dead alias), and it refuses names of built-in commands. Aliases are stored in `aliases.json` in your data folder; you can also edit that file.
- **Did you mean.** If nothing matches but something is close ("opne youtub"), it asks `Did you mean 'open youtube'? [y/N]`. Answer `y` and it runs that task and remembers your wording as an alias (the message tells you how to undo it). Without a keyboard it only prints the suggestion.
- **Why did it pick that?** `explain open youtube` prints the top matches with their scores. A line marked `tied` means you would get a menu.
- **Logs stay on your computer.** `history.jsonl` (what you typed; skipped for private tasks), `log.jsonl` (task name, result, seconds), `misses.log` (phrases that failed) are all in `.jeeg`. Delete them any time.

## 5. Examples by category

| Area | Examples |
|---|---|
| Web and services | `open youtube`, `search cats`, `images of golden retriever`, `weather in mumbai`, `directions to taj mahal`, `translate good morning`, `open github.com`, `compose email`, `add event dentist` |
| Music and messages | `play shape of you`, `play blinding lights on spotify`, `play` (pause/resume), `add contact mom 9876543210`, `send whatsapp to mom see you at 5` |
| Apps | `open chrome`, `open vscode`, `open task manager`, `open settings`, `open vlc`, `open app <any installed app>` |
| Folders and files | `open downloads`, `find file invoice`, `folder size downloads`, `large files`, `find duplicates`, `organize downloads preview`, `backup folder documents`, `zip folder x`, `unzip file x.zip` |
| System | `system info`, `memory usage`, `cpu usage`, `battery status`, `disk space`, `running processes`, `kill process notepad` |
| Network | `check internet`, `show ip`, `wifi info`, `ping host google.com`, `dns lookup x.com`, `port check host 443`, `check website github.com` |
| Power and hardware | `lock screen`, `shutdown pc`, `restart pc`, `cancel shutdown`, `schedule shutdown 45 minutes`, `volume up`, `set volume 40`, `mute`, `next song`, `set brightness 60`, `take screenshot`, `toggle dark mode` |
| Utilities | `25 * 4`, `15% of 200`, `convert 5 km to miles`, `generate password 20`, `roll 2d6`, `set timer 10 minutes tea`, `random choice a, b, c`, `hash text hello` |
| Productivity | `add todo buy milk`, `todo list`, `todo done 1`, `add note call dentist`, `show notes`, `days until 25 dec 2026`, `age calculator 14 aug 2001` |
| Developer | `git status`, `git commit fix bug`, `git stash`, `git stash pop`, `git checkout new feature-x`, `undo last commit`, `serve folder`, `create venv`, `pip install requests`, `kill port 3000`, `docker ps`, `check versions`, `http get https://example.com`, `new project demo flask`, `lines of code myproject`, `json to csv data.json`, `csv preview sales.csv`, `create gitignore python`, `env variables`, `show path` |

### More tasks (added in version 2.1)

| Area | Examples |
|---|---|
| Routines | `start work day`, `end work day`, `study mode`, `meeting mode`, `night mode`, `run routine <name>`, `list routines`, `edit routines` (routines live in an editable `routines.json`) |
| Reminders and time | `remind me in 20 minutes to call mom`, `set alarm 6:30 am`, `show reminders`, `stop reminders`, `water reminder`, `eye break`, `stretch reminder`, `pomodoro`, `daily briefing` (reminders run in a small background process and survive closing the terminal; a time like `5:30` without am/pm is read as 24-hour) |
| Personal records | `journal add had a great day`, `journal show 7`, `add expense 250 lunch`, `show expenses`, `expense total`, `undo expense`, `shopping add milk`, `shopping list`, `save link <name> <url>`, `open link <name>`, `habit done gym`, `habit streak gym`, `add birthday mom 12 mar`, `upcoming birthdays`, `save snippet`, `paste snippet` |
| Money (Indian grouping, lakh/crore) | `emi loan 25 lakh 8.5% 20 years`, `sip growth 5000 12% 15 years`, `compound interest ...`, `gst amount 1000 18%`, `split bill 2450 among 4`, `percentage change 80 to 100`, `discount price 2999 30%`, `currency convert 100 usd to inr`, `crypto price bitcoin` |
| Live information (needs internet) | `weather in pune`, `wiki summary python`, `define serendipity`, `news headlines`, `pincode 560001`, `cricket score`, `stock price tcs`, `lyrics <song>`, `recipe <dish>`, `movie info <title>`, `restaurants near me`, `pharmacy near me`, `flight status 6E 204`, `train status 12951`, `pnr status <10 digits>` |
| Dates and time | `time in london and tokyo`, `what day is 15 aug 2027`, `add 45 days to 1 jan 2027`, `10 days ago`, `days between 1 jan 2027 and 25 dec 2027`, `week number`, `unix timestamp 1700000000` |
| Files and media | `bulk rename downloads replace img with photo` (preview first; add `apply` to do it), `delete empty folders <folder> preview`, `delete old downloads 90 days` (moves them to a holding folder, deletes nothing), `find text invoice in documents`, `file types in downloads`, `open last download`, `copy path of report.pdf`, `folder tree documents depth 3`, `move file a.txt to documents`, `copy file a.txt to desktop`, `resize image photo.jpg to 800`, `convert image a.png to jpg`, `images to pdf <folder>`, `merge pdf a.pdf b.pdf`, `split pdf report.pdf pages 2-4`, `compress video movie.mp4`, `extract audio movie.mp4` |
| System extras | `keep awake 2 hours`, `startup programs`, `installed programs chrome`, `check updates`, `screen resolution`, `usb devices`, `gpu info`, `cpu temperature`, `listening ports`, `restart explorer`, `turn off screen`, `live network speed` |
| Security | `password strength "..."`, `breach check "..."` (only the first 5 characters of a hash are sent; what you type is never saved to history), `compare files a.txt b.txt`, `shred file secret.txt` |
| Text tools | `uppercase hello`, `lowercase`, `title case`, `reverse text`, `sort lines pear, apple`, `remove duplicates a, b, a`, `word frequency notes.txt`, `number to words 1234567` (Indian and international), `roman numeral 2026`, `binary 1010`, `hex ff`, `lorem ipsum 3 paragraphs`, `qr code https://example.com` (text tools copy their result to the clipboard) |
| Fun and learning | `guess the number`, `rock paper scissors`, `typing test`, `multiplication table 7 up to 20`, `quiz me` (from a `question \| answer` notes file) |

Notes:
- Tasks that change or remove things (`delete empty folders`, `delete old downloads`, `shred file`, `undo last commit`, `check updates`, `restart explorer`) ask first. Add the word `preview` to the delete tasks to only list what would happen.
- `undo last commit` keeps your changes and refuses if the commit is already pushed.
- Some tasks need an optional tool: `pip install pillow pypdf qrcode[pil]` for pictures, PDFs and QR codes; `ffmpeg` for video and audio; `psutil` for extra detail. The task tells you exactly what is missing.
- Tasks that need the internet say so plainly when you are offline; they never hang.

Notes on three popular tasks:
- **Play a song** opens a search (YouTube Music by default). A browser cannot press play for you, so click the first result.
- **WhatsApp** opens a chat with your message already typed; you press send. WhatsApp does not allow silent sending. Ten-digit numbers are assumed to be India (+91).
- **Opening websites** uses your normal browser, so you stay signed in. JeeG never reads your passwords or data.

---

### New in version 2.3

| Area | Examples |
|---|---|
| Data safety | `export data`, `import data backup.zip`, `backup status` (a gentle reminder appears if you have not backed up for a while), `export records expenses` |
| Summaries | `weekly summary`, `monthly summary` |
| Daily life | `water log 500 ml`, `sleep log 7 hours`, `bmi 70 kg 175 cm`, `tip 1200 10%`, `unit price 500g 45 vs 1kg 80`, `fuel cost 250 km 18 kmpl 105`, `add bill electricity 15 1200`, `upcoming bills`, `add class maths mon 9:00`, `todays classes` |
| Time and sky | `meeting time 9 am india in london`, `sunrise delhi`, `moon phase`, `public holidays india 2026` |
| Files and developer | `old large files`, `rename photos by date <folder>`, `compare folders a b`, `zip with password <folder>`, `file hash <file>`, `json to yaml`, `run tests`, `who uses port 3000`, `regex test`, `git contributors` |
| Engine | `pack off <category>` / `pack on <category>`, `tips`, routines that take words (`run routine morning Asha`), closest-task suggestions, failing-task flags in `stats` |

Optional extras for a few of these: `pip install pyzipper pyyaml`.

## 6. Adding your own task

1. Create a file in `scripts/` named after the task, for example `open_notes_app.py`. The file name is what people will say ("open notes app"), so use words, joined by underscores.
2. Put a header at the top (first 15 lines) and then your code:

       # keywords: notes, notebook, jot
       # desc: Open my notes app
       # category: apps
       from _lib import launch
       launch(win=[("start", "onenote")], mac=[("open", "-a", "Notes")], linux=[("gnome-notes",)], name="Notes")

3. Type `selftest`. It confirms the new script is found by its own name.

Any language works: `.py`, `.bat`, `.cmd`, `.ps1`, `.sh`, `.js`.
You can also keep your personal scripts in another folder and use `--dir`, so updates never touch them.

Header options:

| Line | Meaning |
|---|---|
| `# keywords:` | Extra words that should find this script |
| `# desc:` | One-line description shown by `list` |
| `# category:` | Group name in `list` |
| `# usage:` | Marks that the task accepts words after its name (like `search <words>`) |
| `# confirm: yes` | Ask before running |
| `# priority: 1` | Wins ties against equally good matches |
| `# rawargs: yes` | Pass your words through untouched (used by timers, calculator, messages) |
| `# rawargs: full` | Pass the whole sentence, including the task words and quotes where you typed them (used by date maths and `find text`) |
| `# patterns: regex ;; regex` | Phrases that identify this task even when single words are ambiguous (for example `\d+ days ago`) |
| `# private: yes` | Never write what you typed to history (used by the password tasks) |

Helpers you can use inside Python scripts (from `_lib.py`): `args_text()` (the words after the task), `open_url(url)`, `launch(...)` (open an app on any OS), `fail("message")`, `call([...])` (run a program), `data_dir()` (a place to save data).

---

## 7. Safety summary

- Dangerous tasks always ask first (see step 6).
- Nothing is deleted without confirmation; temp cleaning only touches files older than 24 hours.
- Zip extraction refuses archives that try to write outside their folder.
- Host names, ports and package names are checked before being passed to other programs.
- Critical system processes cannot be killed with `kill process`.
- No task sends your files or personal data anywhere. Web tasks only open a page in your browser.

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| `python` not found | Install Python from python.org (tick "Add to PATH"), or use `py jeeg.py` on Windows |
| "No matching task" | Type `list`. Try the words from the task name, or add keywords to the script |
| A menu appears | Two tasks fit equally; pick a number, or be more specific ("open youtube music") |
| "needs confirmation; re-run with --yes" | You are running without a keyboard; add `--yes` if you really want it |
| A task says a tool is missing | Some tasks use optional tools (Linux: `playerctl`, `brightnessctl`, `xclip`, `espeak-ng`). The message names what to install |
| Changed a script but nothing changed | Type `reindex` |
| Check everything is healthy | `selftest`, then `python tests/test_routing.py` |

Optional extras: `pip install pillow psutil pypdf qrcode[pil]` (screenshots, process details, picture/PDF/QR tasks). `ffmpeg` is needed for the video and audio tasks.

## 9. Checking it yourself

    python jeeg.py selftest        every script: header, valid code, found by its own name
    python tests/test_routing.py         over 250 phrases and multi-task lines must pick the right script
    python tests/test_parsers.py         the online tasks against sample API replies (no internet needed)
    python tests/test_engine.py          aliases, explain, did-you-mean, logs, installer

The folder includes `.github/workflows/test.yml`. If you put this project on GitHub, it runs all four test files on Windows, macOS and Linux with Python 3.9 and 3.12 on every change, which is the easiest way to find problems on systems you do not have at hand.

## 10. What was and was not tested

- Routing, maths (EMI, SIP, GST and so on), dates, file, text, PDF, picture, git and personal-record tasks are tested automatically on Linux, including typo and polite-wording variants of every task name.
- Online tasks (weather, Wikipedia, news, currency, crypto, dictionary, pincode, breach check, public holidays, exchange rates, gold price) are tested against sample replies shaped like the real services, not the live services. If a provider changes its format, that one task will say it could not read the answer.
- Not built, on purpose: a pop-up launcher window (needs Tk, which I could not run here) and recurring scheduled tasks through cron or Windows Task Scheduler (could not be tested here). Both are best added once they can be tried on your own computer.
- Windows- and macOS-specific parts (volume keys, startup list, installed programs, screen off, restart explorer, and similar) were written carefully but have not been run on real Windows or macOS machines here. Report any that misbehave and they are quick to fix.
