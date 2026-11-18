# Reminders and Personal Records

Everything here is stored as small files in your data folder (`~/.jeeg`). Nothing leaves your computer.

## Reminders, alarms, timers
- `remind me in 20 minutes to call mom`, `set alarm 6:30 am`, `set timer 10 minutes tea`, `stopwatch`.
- `5:30` with no am/pm means 24-hour time; write `5:30 pm` for evening.
- `show reminders`, `stop reminders`.
- Habits of the day: `water reminder`, `eye break`, `stretch reminder`, `pomodoro` (25/5; `pomodoro 4 rounds`), `daily briefing`.
- Reminders run in a small background process, so they fire after you close the terminal. **They do not survive a computer restart.** For recurring jobs use `autorun` ([Routines, Aliases, Variables and Automation](Routines-Aliases-Variables-and-Automation)).

## Everyday records

| What | Examples |
|---|---|
| To-dos | `add todo buy milk`, `todo list`, `todo done 1`, `todo clear` |
| Notes | `add note call dentist`, `show notes`, `meeting notes <title>` |
| Journal | `journal add had a great day`, `journal show 7`, `journal show gym`, `journal prompt` |
| Expenses | `add expense 250 lunch`, `show expenses`, `expense total`, `undo expense` |
| Shopping | `shopping add milk`, `shopping list`, `shopping remove milk`, `shopping clear` |
| Links | `save link <name> <url>`, `open link <name>`, `list links` |
| Habits | `habit done gym`, `habit streak gym` |
| Birthdays | `add birthday mom 12 mar`, `upcoming birthdays` |
| Snippets | `save snippet`, `paste snippet`, `list snippets` |
| Contacts | `add contact mom 9876543210`, `add email mom mom@example.com`, `find contact mom` |
| Clipboard | `save clipboard`, `clipboard history`, `clipboard history 2` |

## Money tracking
- Budgets: `set budget food 5000`, `budget report`. `add expense` warns at 80% and when over.
- Insight: `spending trends`, `spending forecast`, `spending anomalies` (hints, not verdicts).
- Who owes whom (private, never in history): `lend 500 to ravi for lunch`, `borrow 300 from asha`, `ledger`, `settle ravi 200`.
- Bills: `add bill electricity 15 1200`, `upcoming bills`.

## Dates you should not miss
`add countdown exam 12 dec 2026`, `add warranty laptop 12 mar 2027`, `add vehicle due insurance bike 15 dec 2026`, `add vaccine asha polio 12 nov 2026`. **`what is due`** shows and pops up birthdays, bills, countdowns, warranties, vehicle dues and missed medicine; overdue items are flagged.

## Health and daily life
`water log 500 ml`, `sleep log 7.5 hours`, `weight 72.5 kg`, `weight goal 70`, `bmi 70 kg 175 cm`, `calorie calculator`, `bp and sugar log`, `fasting timer`. **Medicines:** `add medicine metformin at 8am and 8pm`, `medicine today`, `medicine taken metformin`, `medicine remind` (never written to history; a reminder helper, not medical advice).

## School and work
`add class maths mon 9:00`, `show timetable`, `todays classes`, `study log maths 45 min`, `study report`, `gpa planner`, `add book Atomic Habits`, `finished book ...`, `books`.

## Reports and search
- `weekly summary`, `monthly summary`, `life report` (a page in `Documents/JeeG-reports` with spending bars, a 12-week habit heat-map, water, sleep, to-dos, weight trend).
- `search my data dentist` searches notes, journal, to-dos, expenses and other lists.
- `export records expenses` writes one record type to CSV.

## Backups
`export data [folder]` zips every record; `import data file.zip` restores (your current data is saved first in `trash/before-import-...`; unsafe archives are refused); `backup status` reminds you if it has been long. `doctor fix` repairs damaged files.
