"""Content for tools/make_wiki.py: scenarios (really run, output captured) and the text between them.

A scenario is run in a fresh temporary home. `setup` items: ("write", relative path, text), ("sh", shell command), ("mkdir", path).
`steps` are phrases run as one argument each (a step starting with "--" is split into options). {HOME} is the temporary home.
"""

SC = {}


def sc(key, setup=None, steps=(), cwd=""):
    SC[key] = {"setup": setup or [], "steps": list(steps), "cwd": cwd}


# ---------------------------------------------------------------- tutorial
sc("t_calc", steps=["25 * 4", "15% of 200", "sqrt 144", "calculate five thousand times 3", "convert 5 km to miles"])
sc("t_explain", steps=["explain open youtube", "explain play shape of you", "explain gibberish qwxz"])
sc("t_records", steps=["add todo buy milk", "add todo call dentist", "todo list", "todo done 1", "todo list", "add note idea for the weekend", "show notes", "search my data dentist"])
sc("t_money", steps=["add expense 250 lunch", "add expense 1200 groceries", "add expense 90 tea", "show expenses", "expense total", "set budget groceries 1000", "add expense 300 groceries", "budget report"])
sc("t_dates", steps=["what day is 15 aug 2027", "add 45 days to 1 jan 2027", "days between 1 jan 2027 and 25 dec 2027", "age calculator 14 aug 2001", "week number 25 dec 2026"])
sc("t_own", setup=[("write", "myjobs.txt", "# a batch file: one phrase per line\nset var rate = 18\ngst 1000 $rate\nsplit bill 900 among 3\n")],
   steps=["alias add tp = todo list", "tp", "alias list", "set var rate = 12", "vars", "gst 1000 $rate", "batch myjobs.txt"])

# ---------------------------------------------------------------- recipes
sc("r_month", steps=["add expense 12000 rent", "add expense 3500 groceries", "add expense 800 transport", "add expense 2200 eating-out", "set budget groceries 3000", "set budget eating-out 2000", "budget report", "expense total", "spending forecast"])
sc("r_loan", steps=["emi loan 25 lakh 8.5% 20 years", "emi loan 25 lakh 8.5% 15 years", "compare loans 2500000 8.5% 20y vs 9% 15y", "compound interest 100000 7% 10 years", "percentage change 80 to 100"])
sc("r_save", steps=["sip growth 5000 12% 15 years", "sip goal 50 lakh in 15 years at 12%", "rd 5000 6.5 2 years", "ppf 150000 15", "income tax 1200000"])
sc("r_downloads", setup=[("mkdir", "Downloads"), ("write", "Downloads/img_001.jpg", "a"), ("write", "Downloads/img_002.jpg", "b"), ("write", "Downloads/report.pdf", "pdf"),
                         ("write", "Downloads/notes.txt", "hello"), ("write", "Downloads/copy of notes.txt", "hello"), ("mkdir", "Downloads/empty_folder")],
   steps=["file types in downloads", "find duplicates downloads", "bulk rename downloads replace img with photo", "delete empty folders downloads preview"])
sc("r_health", steps=["water log 500 ml", "water log 2 glasses", "water today", "sleep log 7.5 hours", "weight 72.5 kg", "weight goal 70", "bmi 72.5 kg 175 cm", "add medicine vitamin-d at 8am", "medicine today", "medicine taken vitamin-d", "medicine today"])
sc("r_study", steps=["add class maths mon 9:00", "add class physics tue 11:00", "show timetable", "study log maths 45 min", "study log physics 30 min", "study report", "attendance 42 of 50 need 75", "cgpa 8.4 out of 10", "marks 412 out of 500"])
sc("r_people", steps=["add contact mom 9876543210", "add contact asha 9123456780", "find contact mom", "add birthday mom 12 mar", "add birthday asha 3 nov", "lend 500 to ravi for lunch", "borrow 300 from asha", "ledger", "settle ravi 200", "ledger ravi"])
sc("r_shop", steps=["invoice seller Sharma Stationers", "stock add rice 20 min 5", "stock add sugar 8 min 5", "stock sell rice 3", "stock sell sugar 4", "low stock", "stock list", "invoice Ravi Traders: 3 pens at 10, 2 books at 150 gst 18"])
sc("r_text", steps=["uppercase hello world", "title case the quick brown fox", "reverse text hello", "sort lines pear, apple, fig", "remove duplicates a, b, a, c", "word frequency the cat and the hat and the bat",
                    "number to words 100 crore", "roman numeral 2026", "255 in binary", "hex ff", "encode base64 hello", "decode base64 aGVsbG8=", "hash text hello", "url encode a b&c"])
sc("r_routine", setup=[("write", ".jeeg/routines.json", '{"morning": ["say:Good morning {1}!", "todo list", "show notes"], "end_day": ["say:Wrapping up", "expense total", "wait:1", "say:Done"]}')],
   steps=["add todo write report", "list routines", "run routine morning Asha", "run routine end_day"])
sc("r_backup", setup=[("mkdir", "backups")], steps=["add todo something worth keeping", "add note an important note", "backup status", "export data {HOME}/backups"])
sc("r_git", setup=[("sh", "git init -q repo && cd repo && git config user.email a@b.c && git config user.name Demo && echo hi > a.txt && git add . && git commit -qm 'first' && echo more >> a.txt")],
   steps=["git status", "git diff", "git log", "git branch", "git contributors", "git recent changes"], cwd="repo")
sc("r_task", setup=[("mkdir", "mytasks"), ("write", "mytasks/tea_timer.py",
   "# keywords: tea, brew, steep\n# desc: Say how long to brew tea (tea timer green)\n# category: fun\n# usage: tea timer [black|green]\nfrom _lib import args_text\nkind = args_text().lower()\nprint('Brew green tea for 2 minutes at 80 C.' if 'green' in kind else 'Brew black tea for 4 minutes at 100 C.')\n")],
   steps=["--dir {HOME}/mytasks reindex", "--dir {HOME}/mytasks explain tea timer green", "--dir {HOME}/mytasks tea timer green", "--dir {HOME}/mytasks tea timer", "--dir {HOME}/mytasks selftest"])
sc("r_safe", setup=[("mkdir", "Downloads/empty_one")],
   steps=["--dry-run shutdown pc", "delete empty folders downloads preview", "privacy"])

# ---------------------------------------------------------------- gallery (independent one-liners)
sc("g_math", steps=["2 plus 2", "sqrt 144", "15% of 200", "calculate 2 ** 10", "convert 5 kg to lb", "cooking convert 2 cups flour to grams", "multiplication table 7 up to 10"])
sc("g_money", steps=["gst 2500 18", "gst 1180 18 inclusive", "discount 2999 30", "split bill 2450 among 4 tip 10", "tip 1200 10% split 3", "unit price 500g 45 vs 1kg 80", "fuel cost 250 km 18 kmpl 105", "profit margin cost 80 price 100", "hra basic 40000 hra 16000 rent 15000 metro", "salary breakup 1200000 a year tax 10 pension 12"])
sc("g_time", steps=["time in london and tokyo", "meeting time 9 am india in london", "unix timestamp 1700000000", "what day is 25 dec 2026", "days between 1 jan 2027 and 1 jan 2028", "sunrise delhi", "moon phase"])
sc("g_util", steps=["flip coin", "roll 2d6", "random number 1 100", "random choice pizza, burger, pasta", "generate password 16", "generate uuid", "count words the quick brown fox"])
sc("g_health", steps=["bmi 70 kg 175 cm", "calorie calculator male 30 years 70 kg 175 cm moderate", "heart rate zones age 30", "macros 2200 high protein"])
sc("g_study", steps=["gpa planner current 7.5 credits 60 target 8 next 20 scale 10", "study plan 5 subjects 10 days 4 hours", "attendance 30 of 40 need 75", "cgpa 8.4 out of 10", "marks 412 out of 500"])
sc("g_home", steps=["electricity bill 250 units at 6.5 fixed 100", "add warranty laptop 12 mar 2027", "warranties", "add vehicle due insurance bike 15 dec 2026", "vehicle dues", "trip budget 4 days 2 people 3000 a day fare 8000"])


# ---------------------------------------------------------------- reference page groups (category -> page)
GROUPS = [
    ("Reference-Money-and-Business", "Money and business", "Calculators for loans, savings, tax, bills and splitting, your expense records and budgets, a lending ledger, a small stock list and invoices.", ["money"]),
    ("Reference-Files-and-Folders", "Files, folders, backups and the clipboard", "Finding, organising, renaming and cleaning files; folders; backups; the clipboard; snippets; data files.", ["files", "folders", "backup", "clipboard", "snippets", "data", "security"]),
    ("Reference-System-and-Hardware", "System, power, hardware and home", "Status of your computer, power and screen control, volume and brightness, devices, and household helpers.", ["system", "power", "hardware", "home", "selfcheck"]),
    ("Reference-Network-Web-and-Search", "Network, web, search and travel", "Network checks, watching pages, feeds, looking things up, maps, travel, mail and the real browser.", ["network", "web", "search", "maps", "travel", "info", "email", "links", "browser"]),
    ("Reference-Developer-Tools", "Developer tools", "Git, projects, packages, data formats, HTTP, ports, containers and testing helpers.", ["developer"]),
    ("Reference-Apps-and-Launchers", "Apps, launchers and linked apps", "Opening apps and websites, workspace shortcuts, social and AI sites, and the linked-app and MCP tasks.", ["apps", "apps_setup", "apps_write", "workspace", "social", "ai", "entertainment", "tools", "reference", "food", "utility"]),
    ("Reference-Time-Reminders-and-Records", "Time, reminders and personal records", "Dates, time zones, reminders and timers, routines, to-dos, notes, journal, habits, birthdays, lists and reports.", ["time", "reminders", "routines", "productivity", "lists", "shopping", "journal", "habits", "birthdays", "personal", "work"]),
    ("Reference-Health-Study-and-Fun", "Health, study, media and fun", "Health logs and calculators, study tools, pictures, PDF and video, learning sites, games and quizzes.", ["health", "study", "learning", "media", "fun", "text"]),
]

# ---------------------------------------------------------------- hand-written pages built around the scenarios
PAGES = {}

PAGES["Tutorial-Your-First-Hour"] = ("Tutorial: Your First Hour", [
"""Every block of output below was captured by **really running JeeG** (version {version}) in a fresh, empty home folder, on {date}. Your output will match except for things that depend on the day, the time or chance. Lines starting `>>` show which task JeeG chose and which words it passed on as arguments.

You will need JeeG installed ([Install and First Run](Install-and-First-Run)). You can type each line at the `task>` prompt (`jeeg`), or one at a time as `jeeg "<line>"`.

## Step 1: Maths needs no keyword (5 minutes)

JeeG treats anything that looks like arithmetic as a calculation. It also understands percentages, square roots, number words and units.
""",
("scn", "t_calc"),
"""Notice `calculate five thousand times 3`: number words need the word `calculate` in front, because `five thousand` alone could mean many things. Anything that looks like a number in the line goes to the maths engine; the rest is matched against task names.

**Try:** `2 plus 2`, `20% of 450`, `convert 5 kg to lb`, `calculate 2 ** 10`.

## Step 2: See how JeeG chooses (5 minutes)

`explain` shows the ranking instead of running anything. The number is the score; the first line is what would run, and `args` are the leftover words handed to that task.
""",
("scn", "t_explain"),
"""Read the second example: "shape of you" is not a task, so those words become the song name (`args: shape of you`). The third example shows what a miss looks like. JeeG never guesses: no match means no run. Details: [How JeeG Understands You](How-JeeG-Understands-You).

## Step 3: Keep a to-do list and notes (10 minutes)

Your records live in small files in `~/.jeeg`. Task ids are numbers; `todo done 1` ticks by number. `search my data` looks across all your records.
""",
("scn", "t_records"),
"""## Step 4: Track money (10 minutes)

Expenses are `add expense <amount> <category> [note]`. The category is **one word** (use `eating-out`, not `eating out`). `show expenses` lists the month, `expense total` draws bars, and once you set a budget JeeG warns you when you go over.
""",
("scn", "t_money"),
"""## Step 5: Dates without a calendar (5 minutes)

Date arithmetic is forgiving about wording and handles month ends correctly.
""",
("scn", "t_dates"),
"""## Step 6: Make it yours (10 minutes)

Aliases give a short word to any phrase. Variables (`$name`) get filled into any later phrase. A batch file is just one phrase per line; here the file `myjobs.txt` contains a comment, `set var rate = 18`, `gst 1000 $rate` and `split bill 900 among 3`.

`myjobs.txt`:

```text
# a batch file: one phrase per line
set var rate = 18
gst 1000 $rate
split bill 900 among 3
```
""",
("scn", "t_own"),
"""Aliases and variables are saved in your data folder (`aliases.json`, `vars.json`), so they are still there tomorrow.

## Step 7: Find your way around (10 minutes)

    list                 every task, grouped (a * means it asks first, [online] means it may use the internet)
    list money           one category
    tips                 one task you may not have tried
    stats                what you use, how long it takes, what fails
    misses               phrases JeeG did not understand, to turn into aliases
    doctor               check Python, your data folder, scripts and optional tools
    privacy              the exact list of tasks that can touch the network
    learn                a 7-step guided tour inside the program

The complete list of tasks is in the [Task Catalog](Task-Catalog); long descriptions with usage, flags and script files are in the reference pages linked from [Home](Home).

## Where next

* Real-life walk-throughs: [Recipes and Workflows](Recipes-and-Workflows).
* A big list of one-liners with output: [Examples Gallery](Examples-Gallery).
* How it all works inside: [Architecture and Internals](Architecture-and-Internals).
* Write your own task: [Plugins and Writing Your Own Tasks](Plugins-and-Writing-Your-Own-Tasks) and the recipe "Make your own task" below.
"""])

PAGES["Recipes-and-Workflows"] = ("Recipes and Workflows", [
"""Longer, realistic sequences. Every transcript is real output captured from JeeG {version} on {date} in a clean temporary home folder (so lists start empty). Dates, "days left" figures and anything random depend on when you run it. Files used in the examples are created for the demo; **the folder `~` below stands for the temporary home**.

Contents: [Month of spending](#recipe-1-a-month-of-spending) | [Compare two loans](#recipe-2-compare-two-loans) | [Save for a goal](#recipe-3-save-for-a-goal) | [Tidy Downloads safely](#recipe-4-tidy-downloads-safely) | [Daily health log](#recipe-5-a-daily-health-log) | [Student week](#recipe-6-a-student-week) | [People and money owed](#recipe-7-people-birthdays-and-who-owes-whom) | [Small shop](#recipe-8-a-small-shop) | [Text tricks](#recipe-9-text-tricks) | [Your own routine](#recipe-10-your-own-routine) | [Backup](#recipe-11-back-up-your-data) | [Git without leaving JeeG](#recipe-12-git-without-leaving-jeeg) | [Make your own task](#recipe-13-make-your-own-task) | [Preview before you act](#recipe-14-see-what-would-happen-first)

## Recipe 1: A month of spending

**Goal:** know where the money goes and whether you will overspend.
**How:** add expenses as they happen (one-word category), set budgets for the categories you care about, then ask for a report and a forecast.
""",
("scn", "r_month"),
"""**Things to notice:** the budget report lists categories with a budget first and then says which categories have none; the forecast projects the month end from your pace so far, and names the categories likely to go over. These are hints, not promises.

**Extend it:** `spending trends` (six months, what grew), `spending anomalies` (unusually large expenses or double entries), `weekly summary`, `monthly summary`, `life report` (an HTML page in `Documents/JeeG-reports`), `export records expenses` (CSV for a spreadsheet).

## Recipe 2: Compare two loans

**Goal:** decide between a longer, cheaper-per-month loan and a shorter one.
""",
("scn", "r_loan"),
"""The comparison table shows both the monthly payment and the total interest, and says in words which loan is cheaper overall and which has the lower payment. Amounts and years can be written `25 lakh`, `2500000`, `20 years` or `20y`. Indian digit grouping (lakh, crore) is used for results.

## Recipe 3: Save for a goal

**Goal:** work out how much to put away each month and what you end with.
""",
("scn", "r_save"),
"""All of these are estimates that assume a constant rate; every output says so. `income tax` uses the slabs of the stated financial year and tells you which regime is cheaper; always check the latest rules.

## Recipe 4: Tidy Downloads safely

**Goal:** see what is in Downloads and clean it up **without deleting anything by accident**. The demo folder was created with two pictures, a PDF, a text file, a copy of that text file and an empty folder.

The rule of thumb: **look first, then preview, then act.** Every cleaning task has a preview, and the destructive ones ask before running.
""",
("scn", "r_downloads"),
"""To really do it, add `apply` to `bulk rename ...`; `delete empty folders downloads` asks first; `delete old downloads 90 days` **moves** files to a holding folder inside your data folder instead of deleting them. `undo` puts back your last move or rename (the last 20 are remembered) and never overwrites a file that already exists.

## Recipe 5: A daily health log

**Goal:** a few seconds a day, and a trend over time. Water accepts `ml`, `glasses` or `bottles`.
""",
("scn", "r_health"),
"""`medicine today` shows `(missed?)` for a dose time that has passed and you have not ticked; `medicine remind` raises alerts for the rest of today (add it to a morning routine for every day). Medicine, weight and sleep tasks never write what you typed into your command history. This is a reminder helper, not medical advice; BMI is a rough screen.

## Recipe 6: A student week

**Goal:** a timetable, a study log and quick checks for attendance and marks.
""",
("scn", "r_study"),
"""`todays classes` / `tomorrows classes` read the timetable; `study report` shows hours per subject for the last 7 days; `flashcards <file>` and `quiz me` test you from a text file of `question | answer` lines.

## Recipe 7: People, birthdays and who owes whom

**Goal:** contacts you can message, dates you will not forget, and a private ledger of lending.
""",
("scn", "r_people"),
"""Ten-digit numbers are assumed Indian (+91). `send whatsapp to mom see you at 5` opens a WhatsApp chat with the message typed and **you** press Send. The ledger tasks (`lend`, `borrow`, `settle`) are private: they are never written to command history. `upcoming birthdays` and `what is due` pull these dates onto one list.

## Recipe 8: A small shop

**Goal:** stock levels, low-stock alerts and a printable invoice, all offline.
""",
("scn", "r_shop"),
"""The invoice is an HTML page you can open in a browser and print or save as PDF; it is written to `Documents/JeeG-invoices` (shown above as `~/JeeG-invoices` in the demo). The total includes GST: 3 pens at 10 and 2 books at 150 is 330 before tax; with 18% GST that is 389.40 (59.40 of it GST).

## Recipe 9: Text tricks

**Goal:** the small conversions people open a web page for. Most of these take text after the task name, or use your clipboard when you give none, and copy the result back to the clipboard when one is available.
""",
("scn", "r_text"),
"""## Recipe 10: Your own routine

**Goal:** one phrase that runs several. A routine is a named list in `routines.json`. Steps can be task phrases, `say:text`, or `wait:seconds`, and may use `{1}`, `{2}` for words you give when you run it. Here `~/.jeeg/routines.json` was extended with two routines (`morning` and `end_day`); the built-in ones are listed too.

```json
{"morning": ["say:Good morning {1}!", "todo list", "show notes"],
 "end_day": ["say:Wrapping up", "expense total", "wait:1", "say:Done"]}
```
""",
("scn", "r_routine"),
"""Use `edit routines` to open the file in your editor. Date variables (`{today}`, `{date}`, `{month}`, `{year}`, `{weekday}`, `{week}`, `{time}`) are filled in when the routine runs. To run a routine every morning by itself: `autorun add "run routine morning Asha" at 8:00 weekdays` (see [Routines, Aliases, Variables and Automation](Routines-Aliases-Variables-and-Automation)).

## Recipe 11: Back up your data

**Goal:** a zip of every record you keep. Everything is plain JSON, so the backup is easy to inspect. Restore with `import data <file.zip>`; your current data is first saved in `trash/before-import-...`, and archives with unsafe paths are refused.
""",
("scn", "r_backup"),
"""## Recipe 12: Git without leaving JeeG

**Goal:** the everyday read-only git questions in plain words. The demo ran in a small repository with one commit and one uncommitted change. Tasks that change things (`git commit`, `git push`, `undo last commit`, `git pull`) ask first; `undo last commit` keeps your changes staged and refuses if that commit was already pushed.
""",
("scn", "r_git"),
"""## Recipe 13: Make your own task

**Goal:** add a task in minutes, without touching JeeG's own files. We create a folder `mytasks` containing one file, `tea_timer.py`:

```python
# keywords: tea, brew, steep
# desc: Say how long to brew tea (tea timer green)
# category: fun
# usage: tea timer [black|green]
from _lib import args_text
kind = args_text().lower()
print('Brew green tea for 2 minutes at 80 C.' if 'green' in kind else 'Brew black tea for 4 minutes at 100 C.')
```

The first four lines are the **header**: they are how JeeG finds the task. Everything after is ordinary Python (any language works: `.sh`, `.bat`, `.ps1`, `.js` too). We point JeeG at the folder with `--dir`, rebuild the index, check how a phrase would be chosen, and run it.
""",
("scn", "r_task"),
"""`reindex` rebuilt the cache (one more task than before); `explain` showed the new task winning; the run printed our line; `selftest` confirmed every task, including the new one, is described, compiles, and is found by its own name. To keep a folder of your own tasks permanently, set `TASK_SCRIPTS_DIR` or start with `--dir` each time (see [Plugins and Writing Your Own Tasks](Plugins-and-Writing-Your-Own-Tasks)).

## Recipe 14: See what would happen first

**Goal:** never be surprised. Three ways to look before you leap:

* `--dry-run <phrase>` shows which script would run, runs nothing.
* the word `preview` on tasks that change files (delete, rename, install ...).
* `privacy` lists exactly which tasks can touch the network.
""",
("scn", "r_safe"),
"""(The list printed by `privacy` is long; the demo shows only its start.)
"""])

PAGES["Examples-Gallery"] = ("Examples Gallery", [
"""A gallery of one-liners with their **real output**, captured from JeeG {version} on {date}. Each group was run in a fresh temporary home. Anything that depends on the date, the time or chance (coin flips, random numbers, passwords, "days left") will differ when you run it. For the complete list of tasks see the [Task Catalog](Task-Catalog).

## Maths, units and tables
""",
("scn", "g_math"),
"""## Money helpers
""",
("scn", "g_money"),
"""## Dates, time zones, sun and moon

Time-zone and astronomy tasks work **offline**: sunrise and moon phase are calculated (about 2 minutes and about a day of accuracy, as the output says).
""",
("scn", "g_time"),
"""## Small utilities
""",
("scn", "g_util"),
"""## Health calculators

These are estimates with plain-language caveats, not medical advice.
""",
("scn", "g_health"),
"""## Study helpers
""",
("scn", "g_study"),
"""## Home, vehicles and trips

`warranties` and `vehicle dues` keep a soonest-first list with "in N days" and flag overdue items; `what is due` combines them with birthdays, bills, countdowns and missed medicine.
""",
("scn", "g_home"),
])
