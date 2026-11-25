# Tutorial: Your First Hour

Every block of output below was captured by **really running JeeG** (version 2.21.0) in a fresh, empty home folder, on 24 November 2026. Your output will match except for things that depend on the day, the time or chance. Lines starting `>>` show which task JeeG chose and which words it passed on as arguments.

You will need JeeG installed ([Install and First Run](Install-and-First-Run)). You can type each line at the `task>` prompt (`jeeg`), or one at a time as `jeeg "<line>"`.

## Step 1: Maths needs no keyword (5 minutes)

JeeG treats anything that looks like arithmetic as a calculation. It also understands percentages, square roots, number words and units.

```text
task> 25 * 4
>> calculate  (25 * 4)
25 * 4 = 100

task> 15% of 200
>> calculate  (15% of 200)
15% of 200 = 30

task> sqrt 144
>> calculate  (sqrt 144)
sqrt 144 = 12

task> calculate five thousand times 3
>> calculate  (five thousand times 3)
five thousand times 3 = 15,000

task> convert 5 km to miles
>> convert units  (5 km to miles)
5 km = 3.10686 miles
```

Notice `calculate five thousand times 3`: number words need the word `calculate` in front, because `five thousand` alone could mean many things. Anything that looks like a number in the line goes to the maths engine; the rest is matched against task names.

**Try:** `2 plus 2`, `20% of 450`, `convert 5 kg to lb`, `calculate 2 ** 10`.

## Step 2: See how JeeG chooses (5 minutes)

`explain` shows the ranking instead of running anything. The number is the score; the first line is what would run, and `args` are the leftover words handed to that task.

```text
task> explain open youtube
   1.50  open youtube             args: -  <- would run
   1.44  open youtube music       args: -

task> explain play shape of you
   1.02  play song                args: shape of you  <- would run
   0.92  play pause               args: shape
   0.92  share file               args: play shape of you
   0.77  guess number             args: play shape of you

task> explain gibberish qwxz
No task matches. (Fallbacks: maths-looking text goes to the calculator, 'open <site.com>' opens the website, 'open <app>' tries to launch the app.)
[exit code 1]
```

Read the second example: "shape of you" is not a task, so those words become the song name (`args: shape of you`). The third example shows what a miss looks like. JeeG never guesses: no match means no run. Details: [How JeeG Understands You](How-JeeG-Understands-You).

## Step 3: Keep a to-do list and notes (10 minutes)

Your records live in small files in `~/.jeeg`. Task ids are numbers; `todo done 1` ticks by number. `search my data` looks across all your records.

```text
task> add todo buy milk
>> todo add  (buy milk)
Added #1: buy milk

task> add todo call dentist
>> todo add  (call dentist)
Added #2: call dentist

task> todo list
>> todo list
  [ ]   1  buy milk
  [ ]   2  call dentist
(2 open, 0 done)

task> todo done 1
>> todo done  (1)
Done: #1 buy milk

task> todo list
>> todo list
  [ ]   2  call dentist
(1 open, 1 done)

task> add note idea for the weekend
>> note add  (idea for the weekend)
Note saved.

task> show notes
>> note list
2026-11-24 21:11  idea for the weekend

task> search my data dentist
>> my data lookup  (search my dentist)
  todos.json:10  "text": "call dentist",
1 match(es).
```

## Step 4: Track money (10 minutes)

Expenses are `add expense <amount> <category> [note]`. The category is **one word** (use `eating-out`, not `eating out`). `show expenses` lists the month, `expense total` draws bars, and once you set a budget JeeG warns you when you go over.

```text
task> add expense 250 lunch
>> add expense  (250 lunch)
Recorded 250.00 under 'lunch'.

task> add expense 1200 groceries
>> add expense  (1200 groceries)
Recorded 1,200.00 under 'groceries'.

task> add expense 90 tea
>> add expense  (90 tea)
Recorded 90.00 under 'tea'.

task> show expenses
>> show expenses
2026-11-24      250.00  lunch
2026-11-24    1,200.00  groceries
2026-11-24       90.00  tea
-- 3 item(s), total 1,540.00  (November 2026)

task> expense total
>> expense total
Spending - November 2026
  groceries         1,200.00  #######################  78%
  lunch               250.00  #####  16%
  tea                  90.00  ##  6%
  TOTAL             1,540.00

task> set budget groceries 1000
>> set budget  (groceries 1000)
Budget for groceries: 1,000.00 per month.

task> add expense 300 groceries
>> add expense  (300 groceries)
Recorded 300.00 under 'groceries'.
  Warning: over your groceries budget: 1,500.00 of 1,000.00 this month.

task> budget report
>> budget report
Budgets for November 2026:
  groceries         1,500.00 of 1,000.00     150%  OVER
  No budget set for: lunch (250.00), tea (90.00)
```

## Step 5: Dates without a calendar (5 minutes)

Date arithmetic is forgiving about wording and handles month ends correctly.

```text
task> what day is 15 aug 2027
>> weekday of  (what day is 15 aug 2027)
Sunday, 15 August 2027  (day 227 of the year, ISO week 32)

task> add 45 days to 1 jan 2027
>> add days  (add 45 days to 1 jan 2027)
Fri 01 Jan 2027 + 45 days = Monday, 15 February 2027

task> days between 1 jan 2027 and 25 dec 2027
>> date difference  (days between 1 jan 2027 and 25 dec 2027)
01 Jan 2027 -> 25 Dec 2027
  358 days  (51 weeks 1 days)  =  0 years 11 months
  256 working days (Mon-Fri, public holidays not excluded)

task> age calculator 14 aug 2001
>> age calculator  (14 aug 2001)
Age: 25 years, 3 months  (9,233 days old)
Next birthday in 263 days

task> week number 25 dec 2026
>> week number  (week number 25 dec 2026)
Friday, 25 December 2026: week 52 of 2026, day 359 of the year, calendar quarter Q4
```

## Step 6: Make it yours (10 minutes)

Aliases give a short word to any phrase. Variables (`$name`) get filled into any later phrase. A batch file is just one phrase per line; here the file `myjobs.txt` contains a comment, `set var rate = 18`, `gst 1000 $rate` and `split bill 900 among 3`.

`myjobs.txt`:

```text
# a batch file: one phrase per line
set var rate = 18
gst 1000 $rate
split bill 900 among 3
```

```text
task> alias add tp = todo list
Saved: 'tp' now means 'todo list'.

task> tp
>> todo list
Nothing to do - your list is empty.
(0 open, 0 done)

task> alias list
  tp             = todo list

task> set var rate = 12
>> var define  (set var rate = 12)
$rate = 12   (use it in any phrase, for example:  gst 1000 $rate)

task> vars
>> var list
  $rate           = 12
1 variable(s). Use them as $name in any phrase; remove one with: remove var <name>

task> gst 1000 $rate
>> gst amount  (1000 12)
Add GST at 12%
  Base price : 1,000.00
  GST        : 120.00   (CGST 60.00 + SGST 60.00)
  Total      : 1,120.00

task> batch myjobs.txt
[1/3] set var rate = 18
>> var define  (set var rate = 18)
$rate = 18   (use it in any phrase, for example:  gst 1000 $rate)
[2/3] gst 1000 $rate
>> gst amount  (1000 18)
Add GST at 18%
  Base price : 1,000.00
  GST        : 180.00   (CGST 90.00 + SGST 90.00)
  Total      : 1,180.00
[3/3] split bill 900 among 3
>> split bill  (900 among 3)
Bill 900.00, split 3 ways
  Each person pays: 300.00
Batch done: 3 ran, 0 failed.
```

Aliases and variables are saved in your data folder (`aliases.json`, `vars.json`), so they are still there tomorrow.

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


Back to [Home](Home).
