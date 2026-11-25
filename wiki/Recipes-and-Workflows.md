# Recipes and Workflows

Longer, realistic sequences. Every transcript is real output captured from JeeG 2.21.0 on 24 November 2026 in a clean temporary home folder (so lists start empty). Dates, "days left" figures and anything random depend on when you run it. Files used in the examples are created for the demo; **the folder `~` below stands for the temporary home**.

Contents: [Month of spending](#recipe-1-a-month-of-spending) | [Compare two loans](#recipe-2-compare-two-loans) | [Save for a goal](#recipe-3-save-for-a-goal) | [Tidy Downloads safely](#recipe-4-tidy-downloads-safely) | [Daily health log](#recipe-5-a-daily-health-log) | [Student week](#recipe-6-a-student-week) | [People and money owed](#recipe-7-people-birthdays-and-who-owes-whom) | [Small shop](#recipe-8-a-small-shop) | [Text tricks](#recipe-9-text-tricks) | [Your own routine](#recipe-10-your-own-routine) | [Backup](#recipe-11-back-up-your-data) | [Git without leaving JeeG](#recipe-12-git-without-leaving-jeeg) | [Make your own task](#recipe-13-make-your-own-task) | [Preview before you act](#recipe-14-see-what-would-happen-first)

## Recipe 1: A month of spending

**Goal:** know where the money goes and whether you will overspend.
**How:** add expenses as they happen (one-word category), set budgets for the categories you care about, then ask for a report and a forecast.

```text
task> add expense 12000 rent
>> add expense  (12000 rent)
Recorded 12,000.00 under 'rent'.

task> add expense 3500 groceries
>> add expense  (3500 groceries)
Recorded 3,500.00 under 'groceries'.

task> add expense 800 transport
>> add expense  (800 transport)
Recorded 800.00 under 'transport'.

task> add expense 2200 eating-out
>> add expense  (2200 eating-out)
Recorded 2,200.00 under 'eating-out'.

task> set budget groceries 3000
>> set budget  (groceries 3000)
Budget for groceries: 3,000.00 per month.

task> set budget eating-out 2000
>> set budget  (eating-out 2000)
Budget for eating-out: 2,000.00 per month.

task> budget report
>> budget report
Budgets for November 2026:
  eating-out        2,200.00 of 2,000.00     110%  OVER
  groceries         3,500.00 of 3,000.00     116%  OVER
  No budget set for: rent (12,000.00), transport (800.00)

task> expense total
>> expense total
Spending - November 2026
  rent             12,000.00  ###################  65%
  groceries         3,500.00  ######  19%
  eating-out        2,200.00  ####  12%
  transport           800.00  #  4%
  TOTAL            18,500.00

task> spending forecast
>> spending forecast
Day 24 of 30: spent 18,500.00
At this pace the month ends near 23,125.00  (about 770.83 a day; 4,625.00 still to come)
Against your budgets (projected):
  eating-out           2,750.00 of 2,000.00       OVER
  groceries            4,375.00 of 3,000.00       OVER
Likely to go over: groceries, eating-out
```

**Things to notice:** the budget report lists categories with a budget first and then says which categories have none; the forecast projects the month end from your pace so far, and names the categories likely to go over. These are hints, not promises.

**Extend it:** `spending trends` (six months, what grew), `spending anomalies` (unusually large expenses or double entries), `weekly summary`, `monthly summary`, `life report` (an HTML page in `Documents/JeeG-reports`), `export records expenses` (CSV for a spreadsheet).

## Recipe 2: Compare two loans

**Goal:** decide between a longer, cheaper-per-month loan and a shorter one.

```text
task> emi loan 25 lakh 8.5% 20 years
>> emi loan  (25 lakh 8.5% 20 years)
Loan 25,00,000.00 (25.00 lakh) at 8.5% for 240 months (20 years)
  Monthly EMI    : 21,695.58
  Total interest : 27,06,939.40
  Total payment  : 52,06,939.40
  First month    : interest 17,708.33, principal 3,987.25

task> emi loan 25 lakh 8.5% 15 years
>> emi loan  (25 lakh 8.5% 15 years)
Loan 25,00,000.00 (25.00 lakh) at 8.5% for 180 months (15 years)
  Monthly EMI    : 24,618.49
  Total interest : 19,31,328.01
  Total payment  : 44,31,328.01
  First month    : interest 17,708.33, principal 6,910.16

task> compare loans 2500000 8.5% 20y vs 9% 15y
>> loan compare  (compare loans 2500000 8.5% 20y vs 9% 15y)
                          Loan A          Loan B
Amount              2,500,000.00    2,500,000.00
Rate                        8.5%            9.0%
Months                       240             180
Monthly payment        21,695.58       25,356.66
Total interest      2,706,939.40    2,064,199.63
Total paid          5,206,939.40    4,564,199.63
Loan B costs less overall by 642,739.77.
Loan A has the lower monthly payment (by 3,661.08).

task> compound interest 100000 7% 10 years
>> compound interest  (100000 7% 10 years)
1,00,000.00 at 7% for 10 years, compounded yearly
  Interest earned: 96,715.14
  Final amount   : 1,96,715.14

task> percentage change 80 to 100
>> percentage change  (80 to 100)
80 -> 100: +25.00%  (increase of 20)
```

The comparison table shows both the monthly payment and the total interest, and says in words which loan is cheaper overall and which has the lower payment. Amounts and years can be written `25 lakh`, `2500000`, `20 years` or `20y`. Indian digit grouping (lakh, crore) is used for results.

## Recipe 3: Save for a goal

**Goal:** work out how much to put away each month and what you end with.

```text
task> sip growth 5000 12% 15 years
>> sip growth  (5000 12% 15 years)
SIP 5,000.00/month for 15 years at 12% a year
  Invested     : 9,00,000.00 (9.00 lakh)
  Estimated gain: 16,22,880.00
  Final value  : 25,22,880.00 (25.23 lakh)
  (an estimate: real returns vary and are not guaranteed)

task> sip goal 50 lakh in 15 years at 12%
>> sip goal  (50 lakh in 15 years at 12%)
To reach 5,000,000 in 15 years at 12% a year:
  Save every month : 10,008.40
  You put in       : 1,801,513
  Growth earns     : 3,198,487
  If you wait 1 year, you would need 11,571.48 a month.
  Returns are not guaranteed; this assumes the same rate every year.

task> rd 5000 6.5 2 years
>> rd maturity  (5000 6.5 2 years)
RD of 5,000.00 a month at 6.5% for 24 months (compounded quarterly)
  You deposit : 1,20,000.00
  Interest    : 8,425.30
  Maturity    : 1,28,425.30
  (Banks differ by a few rupees because of rounding and day counts.)

task> ppf 150000 15
>> ppf maturity  (150000 15)
PPF 1,50,000.00 a year for 15 years at 7.1% (interest is tax free)
  You deposit : 22,50,000.00
  Interest    : 18,18,209.22
  Maturity    : 40,68,209.22
  (Deposit by the 5th of April-month for a full year of interest. The rate is revised every quarter.)

task> income tax 1200000
>> income tax  (1200000)
Yearly income 12,00,000.00
  New regime : tax 0.00  (taxable 11,25,000.00, standard deduction 75,000)
  Old regime : tax 1,63,800.00  (taxable 11,50,000.00, standard deduction 50,000)
  New regime is cheaper by 1,63,800.00. Monthly tax: 0.00
  Salaried slabs of FY 2025-26 with 4% cess; no surcharge. A guide only - check the latest rules or ask a CA.
```

All of these are estimates that assume a constant rate; every output says so. `income tax` uses the slabs of the stated financial year and tells you which regime is cheaper; always check the latest rules.

## Recipe 4: Tidy Downloads safely

**Goal:** see what is in Downloads and clean it up **without deleting anything by accident**. The demo folder was created with two pictures, a PDF, a text file, a copy of that text file and an empty folder.

The rule of thumb: **look first, then preview, then act.** Every cleaning task has a preview, and the destructive ones ask before running.

```text
task> file types in downloads
>> file types  (downloads)
5 files, 15 B in ~/Downloads
  .txt            2   10 B
  .jpg            2   2 B
  .pdf            1   3 B

task> find duplicates downloads
>> find duplicates  (downloads)

5 B x 2
    ~/Downloads/copy of notes.txt
    ~/Downloads/notes.txt

1 duplicate group(s); about 5 B could be freed. Nothing was deleted.

task> bulk rename downloads replace img with photo
>> bulk rename  (downloads replace img with photo)
  img_001.jpg  ->  photo_001.jpg
  img_002.jpg  ->  photo_002.jpg
2 file(s) would change in ~/Downloads. Add 'apply' to do it.

task> delete empty folders downloads preview
>> delete empty folders  (downloads preview)
  would remove ~/Downloads/empty_folder
1 empty folder(s) found in ~/Downloads.
```

To really do it, add `apply` to `bulk rename ...`; `delete empty folders downloads` asks first; `delete old downloads 90 days` **moves** files to a holding folder inside your data folder instead of deleting them. `undo` puts back your last move or rename (the last 20 are remembered) and never overwrites a file that already exists.

## Recipe 5: A daily health log

**Goal:** a few seconds a day, and a trend over time. Water accepts `ml`, `glasses` or `bottles`.

```text
task> water log 500 ml
>> water log  (500 ml)
Logged 500 ml.
Today: 500 ml of your 2,500 ml goal (20%). Change the goal with:  water goal 3000

task> water log 2 glasses
>> water log  (2 glasses)
Logged 500 ml.
Today: 1,000 ml of your 2,500 ml goal (40%). Change the goal with:  water goal 3000

task> water today
>> water log  (today)
Today: 1,000 ml of your 2,500 ml goal (40%). Change the goal with:  water goal 3000

task> sleep log 7.5 hours
>> sleep log  (7.5 hours)
Logged 7.5 hours for 2026-11-24.
Recent nights: 11-24 7.5h
Average of these 1: 7.5 h

task> weight 72.5 kg
>> weight log  (72.5 kg)
Logged 72.5 kg for 2026-11-24.
Recent: 11-24 72.5

task> weight goal 70
>> weight log  (goal 70)
Goal set to 70 kg.

task> bmi 72.5 kg 175 cm
>> bmi calculator  (72.5 kg 175 cm)
BMI 23.7  ->  normal range (WHO adult categories)   [72.5 kg, 175 cm]
Healthy weight range for this height (BMI 18.5-24.9): 56.7 - 76.3 kg
Note: Asian and Indian health guidelines use lower cut-offs (overweight from 23). BMI is a rough screen, not a diagnosis; ask a doctor about your own health.

task> add medicine vitamin-d at 8am
>> add medicine  (vitamin-d at 8am)
Saved vitamin-d: 08:00.  Say 'medicine today' to see it, 'medicine remind' to get alerts today.

task> medicine today
>> medicine today
Medicines for Tuesday 24 November:
  vitamin-d
     08:00  [ ] (missed?)

task> medicine taken vitamin-d
>> medicine today  (taken vitamin-d)
Ticked vitamin-d for 08:00.

task> medicine today
>> medicine today
Medicines for Tuesday 24 November:
  vitamin-d
     08:00  [x]
```

`medicine today` shows `(missed?)` for a dose time that has passed and you have not ticked; `medicine remind` raises alerts for the rest of today (add it to a morning routine for every day). Medicine, weight and sleep tasks never write what you typed into your command history. This is a reminder helper, not medical advice; BMI is a rough screen.

## Recipe 6: A student week

**Goal:** a timetable, a study log and quick checks for attendance and marks.

```text
task> add class maths mon 9:00
>> add class  (maths mon 9:00)
Added: Maths on Mon at 09:00

task> add class physics tue 11:00
>> add class  (physics tue 11:00)
Added: Physics on Tue at 11:00

task> show timetable
>> show timetable
Monday    09:00 Maths
Tuesday   11:00 Physics

task> study log maths 45 min
>> study log  (maths 45 min)
Logged 45 min of maths. Today so far: 0 h 45 min.

task> study log physics 30 min
>> study log  (physics 30 min)
Logged 30 min of physics. Today so far: 1 h 15 min.

task> study report
>> study log  (report)
Last 7 days: 1.2 hours
  maths               0.8 h  ##
  physics             0.5 h  #
Best day: 2026-11-24 (75 min)

task> attendance 42 of 50 need 75
>> attendance percentage  (42 of 50 need 75)
Attendance: 42 of 50 = 84.0%  (minimum 75%)
  You can miss 6 more classes and stay at or above 75%.

task> cgpa 8.4 out of 10
>> cgpa to percentage  (8.4 out of 10)
CGPA 8.4/10 is about 79.8% (CBSE formula: CGPA x 9.5)
  Many universities use CGPA x 10 = 84.0% - check your own university's rule.

task> marks 412 out of 500
>> marks percentage  (412 out of 500)
412 out of 500 = 82.40%  (Distinction)
```

`todays classes` / `tomorrows classes` read the timetable; `study report` shows hours per subject for the last 7 days; `flashcards <file>` and `quiz me` test you from a text file of `question | answer` lines.

## Recipe 7: People, birthdays and who owes whom

**Goal:** contacts you can message, dates you will not forget, and a private ledger of lending.

```text
task> add contact mom 9876543210
>> add contact  (mom 9876543210)
(10-digit number: assuming India, +91)
Saved mom: +919876543210

task> add contact asha 9123456780
>> add contact  (asha 9123456780)
(10-digit number: assuming India, +91)
Saved asha: +919123456780

task> find contact mom
>> find contact  (mom)
  mom                  +919876543210

task> add birthday mom 12 mar
>> add birthday  (mom 12 mar)
Saved Mom: 12 March

task> add birthday asha 3 nov
>> add birthday  (asha 3 nov)
Saved Asha: 03 November

task> lend 500 to ravi for lunch
>> lend money  (500 to ravi for lunch)
Noted: ravi owes you 500.00. Total ravi owes you: 500.00.

task> borrow 300 from asha
>> borrow money  (300 from asha)
Noted: you owe asha 300.00. Total you owe asha: 300.00.

task> ledger
>> show ledger  (ledger)
People who owe you (500.00 in all):
  ravi                    500.00
You owe (300.00 in all):
  asha                    300.00

task> settle ravi 200
>> settle ledger  (ravi 200)
Recorded 200.00 received from ravi. Still owed to you: 300.00.

task> ledger ravi
>> show ledger  (ledger ravi)
ravi: owes you 300.00
  2026-11-24  +500.00  lunch
  2026-11-24  -200.00  settled
```

Ten-digit numbers are assumed Indian (+91). `send whatsapp to mom see you at 5` opens a WhatsApp chat with the message typed and **you** press Send. The ledger tasks (`lend`, `borrow`, `settle`) are private: they are never written to command history. `upcoming birthdays` and `what is due` pull these dates onto one list.

## Recipe 8: A small shop

**Goal:** stock levels, low-stock alerts and a printable invoice, all offline.

```text
task> invoice seller Sharma Stationers
>> make invoice  (invoice seller Sharma Stationers)
Invoices will now show: Sharma Stationers

task> stock add rice 20 min 5
>> inventory  (stock add rice 20 min 5)
rice: 20 in stock (warn at 5)

task> stock add sugar 8 min 5
>> inventory  (stock add sugar 8 min 5)
sugar: 8 in stock (warn at 5)

task> stock sell rice 3
>> inventory  (stock sell rice 3)
rice: 17 left

task> stock sell sugar 4
>> inventory  (stock sell sugar 4)
sugar: 4 left   <-- LOW, time to buy more

task> low stock
>> inventory  (low stock)
1 item(s) to buy:
  sugar                               4   min 5   <-- LOW

task> stock list
>> inventory  (stock list)
2 item(s):
  rice                               17   min 5
  sugar                               4   min 5   <-- LOW

task> invoice Ravi Traders: 3 pens at 10, 2 books at 150 gst 18
>> make invoice  (invoice Ravi Traders: 3 pens at 10, 2 books at 150 gst 18)
INV-0001 for Ravi Traders: total 389.40 (GST 59.40 included)
Saved: ~/JeeG-invoices/INV-0001-Ravi-Traders.html
```

The invoice is an HTML page you can open in a browser and print or save as PDF; it is written to `Documents/JeeG-invoices` (shown above as `~/JeeG-invoices` in the demo). The total includes GST: 3 pens at 10 and 2 books at 150 is 330 before tax; with 18% GST that is 389.40 (59.40 of it GST).

## Recipe 9: Text tricks

**Goal:** the small conversions people open a web page for. Most of these take text after the task name, or use your clipboard when you give none, and copy the result back to the clipboard when one is available.

```text
task> uppercase hello world
>> uppercase text  (hello world)
HELLO WORLD

task> title case the quick brown fox
>> title case text  (the quick brown fox)
The Quick Brown Fox

task> reverse text hello
>> reverse text  (hello)
olleh

task> sort lines pear, apple, fig
>> sort lines  (pear, apple, fig)
apple
fig
pear

task> remove duplicates a, b, a, c
>> dedupe lines  (remove duplicates a, b, a, c)
1 duplicate(s) removed, 3 left:
a
b
c

task> word frequency the cat and the hat and the bat
>> word frequency  (the cat and the hat and the bat)
8 words, 5 different. Top words (common small words ignored):
  cat               1
  hat               1
  bat               1

task> number to words 100 crore
>> number to words  (to 100 crore)
1,00,00,00,000  (Indian grouping)
Indian:        one hundred crore
International: one billion

task> roman numeral 2026
>> roman numerals  (2026)
2026 = MMXXVI

task> 255 in binary
>> binary hex  (255 in binary)
decimal: 255
binary:  11111111
hex:     FF
octal:   377

task> hex ff
>> binary hex  (hex ff)
decimal: 255
binary:  11111111
hex:     FF
octal:   377

task> encode base64 hello
>> encode base64  (hello)
aGVsbG8=

task> decode base64 aGVsbG8=
>> decode base64  (aGVsbG8=)
hello

task> hash text hello
>> hash text  (hello)
SHA256 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
SHA1   aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d
MD5    5d41402abc4b2a76b9719d911017c592

task> url encode a b&c
>> url encode  (url encode a b&c)
a%20b%26c
```

## Recipe 10: Your own routine

**Goal:** one phrase that runs several. A routine is a named list in `routines.json`. Steps can be task phrases, `say:text`, or `wait:seconds`, and may use `{1}`, `{2}` for words you give when you run it. Here `~/.jeeg/routines.json` was extended with two routines (`morning` and `end_day`); the built-in ones are listed too.

```json
{"morning": ["say:Good morning {1}!", "todo list", "show notes"],
 "end_day": ["say:Wrapping up", "expense total", "wait:1", "say:Done"]}
```

```text
task> add todo write report
>> todo add  (write report)
Added #1: write report

task> list routines
>> list routines
end_day:
    say:Wrapping up
    expense total
    wait:1
    say:Done
end_work_day:
    todo list
    say:Locking the screen in 5 seconds - press Ctrl+C to cancel
    wait:5
    lock screen
meeting_mode:
    say:Meeting mode
    open meet
    open calendar
morning:
    say:Good morning {1}!
    todo list
    show notes
night_mode:
    dark mode on
    set brightness 30
    set volume 20
start_work_day:
    say:Starting your work day...
... (8 more lines)

task> run routine morning Asha
>> run routine  (run routine morning Asha)
== morning (3 steps) ==
Good morning Asha!
>> todo list
  [ ]   1  write report
(1 open, 0 done)
>> note list
You have no notes yet. Add one with: add note <text>

task> run routine end_day
>> run routine  (run routine end_day)
== end day (4 steps) ==
Wrapping up
>> expense total
No expenses recorded for November 2026.
Done
```

Use `edit routines` to open the file in your editor. Date variables (`{today}`, `24 November 2026`, `{month}`, `{year}`, `{weekday}`, `{week}`, `{time}`) are filled in when the routine runs. To run a routine every morning by itself: `autorun add "run routine morning Asha" at 8:00 weekdays` (see [Routines, Aliases, Variables and Automation](Routines-Aliases-Variables-and-Automation)).

## Recipe 11: Back up your data

**Goal:** a zip of every record you keep. Everything is plain JSON, so the backup is easy to inspect. Restore with `import data <file.zip>`; your current data is first saved in `trash/before-import-...`, and archives with unsafe paths are refused.

```text
task> add todo something worth keeping
>> todo add  (something worth keeping)
Added #1: something worth keeping

task> add note an important note
>> note add  (important)
Note saved.

task> backup status
>> backup info
5 data file(s), 480 B in total.
Never backed up. Type:  export data

task> export data ~/backups
>> export data  (~/backups)
Backed up 5 file(s) -> ~/backups/jeeg_backup_20261124_2111.zip
Keep it somewhere safe (another drive or cloud folder). Restore with:  import data <file>
```

## Recipe 12: Git without leaving JeeG

**Goal:** the everyday read-only git questions in plain words. The demo ran in a small repository with one commit and one uncommitted change. Tasks that change things (`git commit`, `git push`, `undo last commit`, `git pull`) ask first; `undo last commit` keeps your changes staged and refuses if that commit was already pushed.

```text
task> git status
>> git status
## master
 M a.txt

task> git diff
>> git diff
 a.txt | 1 +
 1 file changed, 1 insertion(+)

task> git log
>> git log
* 7eaad27 (HEAD -> master) first

task> git branch
>> git branch
* master 7eaad27 first

task> git contributors
>> git contributors
     1	Demo <a@b.c>

task> git recent changes
>> git recent changes
7eaad27  2026-11-24  Demo  first

 a.txt | 1 +
 1 file changed, 1 insertion(+)
```

## Recipe 13: Make your own task

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

```text
task> --dir ~/mytasks reindex
Indexed 603 tasks.

task> --dir ~/mytasks explain tea timer green
   2.10  tea timer                args: green  <- would run
   1.07  fasting timer            args: tea timer green
   1.02  set timer                args: tea green
   0.95  show time                args: tea green
   0.77  pomodoro                 args: tea timer green
   0.77  schedule shutdown        args: tea green

task> --dir ~/mytasks tea timer green
>> tea timer  (green)
Brew green tea for 2 minutes at 80 C.

task> --dir ~/mytasks tea timer
>> tea timer
Brew black tea for 4 minutes at 100 C.

task> --dir ~/mytasks selftest
selftest: 603/603 ok
```

`reindex` rebuilt the cache (one more task than before); `explain` showed the new task winning; the run printed our line; `selftest` confirmed every task, including the new one, is described, compiles, and is found by its own name. To keep a folder of your own tasks permanently, set `TASK_SCRIPTS_DIR` or start with `--dir` each time (see [Plugins and Writing Your Own Tasks](Plugins-and-Writing-Your-Own-Tasks)).

## Recipe 14: See what would happen first

**Goal:** never be surprised. Three ways to look before you leap:

* `--dry-run <phrase>` shows which script would run, runs nothing.
* the word `preview` on tasks that change files (delete, rename, install ...).
* `privacy` lists exactly which tasks can touch the network.

```text
task> --dry-run shutdown pc
[dry-run] /usr/local/bin/python3 /home/claude/tr2/scripts/shutdown_pc.py

task> delete empty folders downloads preview
>> delete empty folders  (downloads preview)
  would remove ~/Downloads/empty_one
1 empty folder(s) found in ~/Downloads.

task> privacy
Your data lives only in ~/.jeeg (readable only by you). JeeG has no account and no telemetry, and nothing runs in the background except reminders you set yourself.
520 of 602 tasks never touch the network. These 82 can, and only when you run them:
  agent                 Give JeeG a goal and a model you chose (Ollama, LM Studio, or your own
  ai channel            Shared message boards that people and AIs on different JeeG computers
  backup share          Share a backup zip of your JeeG data to a paired computer over the enc
  breach check          Check if a password has appeared in known data leaks (only a 5-charact
  bridge                Rules that connect things: when a message arrives from MQTT, a webhook
  browser do            Act on a page in the real browser, by the numbers that  browser look
  browser look          Look at websites in a real browser (browser open example.com, browser
  browser setup         Set up the real browser (browser start, browser start hidden, browser
  calendar feed         Show upcoming events from a calendar link or .ics file (calendar feed
  check internet        Check whether the internet is working
  check speed           Test internet speed (Speedtest)
  check updates         Check which programs and system updates are waiting (does not install)
  check website         Check if a website is up (check website github.com)
  configure app         Set up common tools: git name and email, an ssh key, a VS Code extensi
  convert units         Convert units offline (convert 5 km to miles, 100 f to c); falls back
  crypto price          Live cryptocurrency price (crypto price bitcoin) (needs internet)
  currency convert      Live currency conversion (currency 100 usd to inr) (needs internet)
  daily briefing        Daily briefing (say: morning briefing): date, weather, to-dos, birthda
  define word           Dictionary meaning in the terminal (meaning of ephemeral); opens Googl
  dns lookup            Look up the IP addresses of a domain
  event rules           Run a task when something new shows up in a linked app: rule add issue
  exchange rates        Table of today's exchange rates against the rupee (exchange rates, exc
  family board          A shared to-do board for a family or small team. Items sync to the pai
... (61 more lines)
```

(The list printed by `privacy` is long; the demo shows only its start.)


Back to [Home](Home).
