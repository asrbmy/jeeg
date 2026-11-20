# Reference: Time, reminders and personal records

Dates, time zones, reminders and timers, routines, to-dos, notes, journal, habits, birthdays, lists and reports.

69 tasks. Each entry shows the **usage** (`<x>` you fill in, `[x]` optional), what the task does, how it behaves, other words that also find it, and the script file you can read or edit. Say the task name, or the usage with your words filled in. `explain <words>` shows how any phrase is matched; `<task> preview` or `--dry-run` shows what would happen without doing it.

Categories on this page: [time](#time), [reminders](#reminders), [routines](#routines), [productivity](#productivity), [lists](#lists), [shopping](#shopping), [journal](#journal), [habits](#habits), [birthdays](#birthdays), [personal](#personal), [work](#work)

## time

### add days

**Usage:** `add <n> days to <date>`  
**What it does:** Date arithmetic (add 45 days to 1 jan 2027, 3 months from today, 10 days ago)  
**Also found by:** `add weeks`, `add months`, `days from now`, `days ago`, `weeks from`, `months after`, `date after`, `date before`, `subtract days`, `plus days`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/add_days.py`

### age calculator

**What it does:** Work out an age from a birth date  
**Also found by:** `age`, `birthday`, `how old`, `born`, `date of birth`, `dob`  
**Script:** `scripts/age_calculator.py`

### convert time zone

**Usage:** `meeting time <time> <place> in <place>[, <place>]`  
**What it does:** Convert a meeting time between places (meeting time 9 am india in london, 3 pm new york to mumbai)  
**Also found by:** `meeting time`, `convert time`, `time zone converter`, `time difference`, `what time will it be in`, `convert timezone`, `9 am in london is what time`, `meeting planner`, `schedule across time zones`  
**Your words:** passed through untouched  
**Script:** `scripts/convert_time_zone.py`

### date difference

**Usage:** `days between <date> and <date>`  
**What it does:** Days between two dates (days between 1 jan 2027 and 25 dec 2027)  
**Also found by:** `days between`, `difference between dates`, `how many days between`, `working days`, `business days`, `weeks between`, `between dates`, `duration between`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/date_difference.py`

### days until

**What it does:** Days until a date (days until 25 dec 2026)  
**Also found by:** `countdown`, `days left`, `how many days`, `until`, `date difference`, `days to`  
**Script:** `scripts/days_until.py`

### set timer

**Usage:** `set timer <duration> [label]`  
**What it does:** Countdown timer with a beep (set timer 10 minutes tea)  
**Also found by:** `timer`, `countdown`, `after`, `minutes`, `seconds`, `minute`, `second`, `hours`  
**Your words:** passed through untouched  
**Script:** `scripts/set_timer.py`

### show calendar

**What it does:** Show a month calendar (show calendar march 2027)  
**Also found by:** `calendar`, `month`, `dates`, `this month`, `month view`  
**Script:** `scripts/show_calendar.py`

### show time

**What it does:** Show the current time and date  
**Also found by:** `time`, `date`, `today`, `clock`, `day`, `what time`, `current time`  
**Script:** `scripts/show_time.py`

### stopwatch

**What it does:** Start a stopwatch (press Enter to stop)  
**Also found by:** `stop watch`, `measure time`, `lap`, `elapsed`  
**Script:** `scripts/stopwatch.py`

### unix timestamp

**Usage:** `unix timestamp [number|date]`  
**What it does:** Unix timestamp now, or convert one (unix timestamp 1700000000, or a date)  
**Also found by:** `timestamp`, `unix time`, `epoch`, `unix epoch`, `epoch time`, `convert timestamp`, `timestamp to date`, `date to timestamp`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/unix_timestamp.py`

### week number

**Usage:** `week number [date]`  
**What it does:** ISO week number, day of year and quarter (week number, week number 25 dec 2026)  
**Also found by:** `which week`, `week of year`, `day of year`, `quarter`, `what week is it`, `iso week`, `current week`, `fiscal quarter`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/week_number.py`

### weekday of

**Usage:** `what day is <date>`  
**What it does:** Which weekday a date falls on (what day is 15 aug 2027)  
**Also found by:** `what day is`, `weekday`, `which day`, `day of week`, `day of the week`, `what weekday`, `day on`, `was it a`, `will it be a`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/weekday_of.py`

### world time

**Usage:** `time in <city>[, <city>]`  
**What it does:** Current time in cities (time in london, tokyo and new york)  
**Also found by:** `time in`, `world clock`, `timezone`, `time zone`, `current time in`, `clock in`, `what time in`, `time at`, `local time`, `time difference`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/world_time.py`


## reminders

### add countdown

**Usage:** `add countdown <event> <date>`  
**What it does:** Count the days to an event (add countdown exam 12 dec 2026)  
**Also found by:** `countdown`, `days left until`, `days until`, `event countdown`, `how many days until`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/add_countdown.py`

### calendar feed

**Usage:** `calendar feed add <name> <https address | file.ics> | calendar feed upcoming [name] [days] | calendar feed list | calendar feed remove <name>`  
**What it does:** Show upcoming events from a calendar link or .ics file (calendar feed add work <secret iCal address>, calendar feed upcoming). Works with Google/Outlook secret iCal links, no sign-in.  
**Behaviour:** can use the internet; never saved in history.  
**Also found by:** `ics`, `ical`, `upcoming events`, `google calendar feed`, `calendar events from link`, `agenda from calendar`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/calendar_feed.py`

### eye break

**Usage:** `eye break [minutes]`  
**What it does:** 20-20-20 eye break reminder every 20 minutes  
**Also found by:** `eye`, `eyes`, `eye strain`, `rest eyes`, `screen break`  
**Script:** `scripts/eye_break.py`

### notify due

**Usage:** `notify due`  
**What it does:** Pop up a notification for what is due: birthdays, bills, countdowns, medicine (what is due, notify due)  
**Also found by:** `what is due`, `due today`, `due soon`, `check due`, `anything due`, `remind due`, `due items`  
**Script:** `scripts/notify_due.py`

### pomodoro

**Usage:** `pomodoro [rounds] [N work] [N break]`  
**What it does:** Pomodoro focus timer: 25 min work / 5 min break (pomodoro 4 rounds)  
**Also found by:** `pomo`, `focus timer`, `work timer`, `work sessions`, `study timer`, `productivity timer`  
**Your words:** passed through untouched  
**Script:** `scripts/pomodoro.py`

### remind me

**Usage:** `remind me <when> <what>`  
**What it does:** Background reminder (remind me at 5:30pm to call mom / in 20 minutes ... / every 2 hours ...)  
**Also found by:** `remind`, `reminder`, `notify me`, `alert me`, `nudge`, `tell me to`, `minutes`, `hours`, `tomorrow`  
**Your words:** passed through untouched  
**Script:** `scripts/remind_me.py`

### remove countdown

**Usage:** `remove countdown <event>`  
**What it does:** Delete a countdown (remove countdown exam)  
**Also found by:** `delete countdown`, `clear countdown`, `stop countdown`  
**Your words:** passed through untouched  
**Script:** `scripts/remove_countdown.py`

### set alarm

**Usage:** `set alarm <time>`  
**What it does:** Set an alarm for a clock time (set alarm 6:30 am)  
**Also found by:** `alarm`, `wake me`, `wake up`, `alarm clock`, `wake me up at`, `morning alarm`  
**Your words:** passed through untouched  
**Script:** `scripts/set_alarm.py`

### show countdowns

**Usage:** `show countdowns`  
**What it does:** Show the days left for your events (show countdowns)  
**Also found by:** `my countdowns`, `days left`, `list countdowns`, `countdown list`, `how many days left`  
**Script:** `scripts/show_countdowns.py`

### show reminders

**What it does:** List active background reminders and alarms  
**Also found by:** `list reminders`, `my reminders`, `active reminders`, `pending reminders`, `what reminders`, `alarms`  
**Script:** `scripts/show_reminders.py`

### stop reminders

**What it does:** Cancel all background reminders and alarms  
**Also found by:** `cancel reminders`, `clear reminders`, `cancel alarm`, `stop alarm`, `remove reminders`, `delete reminders`, `stop water reminder`  
**Script:** `scripts/stop_reminders.py`

### stretch reminder

**Usage:** `stretch reminder [minutes]`  
**What it does:** Remind you to stand up and stretch every 45 minutes  
**Also found by:** `stretch`, `stand up`, `posture`, `move`, `exercise break`, `walk`, `sitting`  
**Script:** `scripts/stretch_reminder.py`

### water reminder

**Usage:** `water reminder [minutes]`  
**What it does:** Remind you to drink water every 30 minutes  
**Also found by:** `water`, `drink water`, `hydrate`, `hydration`, `drink`, `stay hydrated`, `water break`  
**Script:** `scripts/water_reminder.py`


## routines

### daily briefing

**Usage:** `daily briefing [city]`  
**What it does:** Daily briefing (say: morning briefing): date, weather, to-dos, birthdays, reminders  
**Behaviour:** can use the internet.  
**Also found by:** `briefing`, `brief me`, `agenda`, `summary`, `overview`  
**Script:** `scripts/daily_briefing.py`

### edit routines

**What it does:** Open the routines file to add or change routines  
**Also found by:** `change routine`, `customize routine`, `add routine`, `routines file`, `edit routine`  
**Script:** `scripts/edit_routines.py`

### end work day

**What it does:** Routine: show to-dos then lock the screen after 5 s (editable)  
**Also found by:** `end work`, `finish work`, `end my day`, `end day`, `wrap up`, `shutdown routine`, `going home`, `done for today`  
**Script:** `scripts/end_work_day.py`

### kit install

**Usage:** `kit install <file>`  
**What it does:** Install a kit file made by 'kit export' (kit install file). Asks first; keeps anything you already have; check it first with 'kit show'  
**Behaviour:** asks before running.  
**Also found by:** `install a kit`, `add someone else routines`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/kit_install.py`

### kit share

**Usage:** `kit export <name> | kit show <file>`  
**What it does:** Share your routines, aliases and variables as one file, or look inside someone else's (kit export mykit, kit show file)  
**Also found by:** `kit export`, `kit show`, `share my routines`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/kit_share.py`

### list routines

**What it does:** List your routines and their steps  
**Also found by:** `show routines`, `my routines`, `routines`, `what routines`, `macros`  
**Script:** `scripts/list_routines.py`

### meeting mode

**What it does:** Routine: open Meet and your calendar (editable)  
**Also found by:** `meeting`, `call mode`, `join meeting`, `video call mode`  
**Script:** `scripts/meeting_mode.py`

### night mode

**What it does:** Routine: dark mode, dim screen, low volume (editable)  
**Also found by:** `night`, `bedtime`, `sleep mode`, `evening`, `wind down`  
**Script:** `scripts/night_mode.py`

### run routine

**Usage:** `run routine <name> [words]`  
**What it does:** Run any routine from your routines file (run routine <name> [words]; steps can use {1} {2} {args})  
**Also found by:** `routine`, `my routine`, `custom routine`, `macro`, `workflow`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/run_routine.py`

### start work day

**What it does:** Routine: open mail and calendar, show your to-dos (editable)  
**Also found by:** `start work`, `work day`, `begin work`, `start my day`, `start day`, `work mode`, `morning routine`  
**Script:** `scripts/start_work_day.py`

### study mode

**What it does:** Routine: notes app, low volume, 25-minute study timer (editable)  
**Also found by:** `study`, `focus`, `focus mode`, `exam`, `homework`, `concentrate`  
**Script:** `scripts/study_mode.py`


## productivity

### life report

**Usage:** `life report [last month | year]`  
**What it does:** A visual page of your month: spending bars, habit heat-map, water, sleep, to-dos (life report, life report last month, life report year)  
**Also found by:** `visual report`, `report page`, `my month chart`, `habit heatmap`, `spending chart`, `progress page`, `dashboard of my life`  
**Your words:** passed through untouched  
**Script:** `scripts/life_report.py`

### my data lookup

**Usage:** `search my data <words>`  
**What it does:** Search your notes, journal, to-dos, expenses and other saved records (search my data milk)  
**Also found by:** `look in my data`, `dig through my notes`, `where did i write`, `dig my records`  
**Your words:** passed through untouched  
**Script:** `scripts/my_data_lookup.py`

### note add

**Usage:** `add note <text>`  
**What it does:** Save a quick note (note add call dentist at 5)  
**Behaviour:** reads piped text.  
**Also found by:** `note`, `add note`, `take note`, `save note`, `remember`, `jot`, `write down`, `memo`, `new note`  
**Script:** `scripts/note_add.py`

### note list

**Usage:** `show notes [word]`  
**What it does:** Show your recent notes (optionally filter by a word)  
**Also found by:** `notes`, `show notes`, `list notes`, `my notes`, `read notes`, `search notes`, `find note`, `recent notes`  
**Script:** `scripts/note_list.py`

### study log

**Usage:** `study log <subject> <time> | study report`  
**What it does:** Log study time and see where it goes (study log maths 45 min, study report)  
**Also found by:** `log study`, `studied`, `study time`, `study report`, `hours studied`, `track study`, `study hours`  
**Your words:** passed through untouched  
**Script:** `scripts/study_log.py`

### todo add

**Usage:** `add todo <text>`  
**What it does:** Add a to-do item (add todo buy milk)  
**Also found by:** `todo`, `to do`, `add todo`, `new task`, `add task`, `remember to`, `task list`, `add item`  
**Script:** `scripts/todo_add.py`

### todo clear

**What it does:** Remove finished items from the to-do list  
**Also found by:** `clear todos`, `clear done`, `remove completed`, `clean todo`, `delete done todos`, `tidy`  
**Script:** `scripts/todo_clear.py`

### todo done

**Usage:** `todo done <number|text>`  
**What it does:** Mark a to-do done (todo done 3, or part of its text)  
**Also found by:** `done`, `finish`, `complete`, `completed`, `tick`, `mark done`, `check off`, `finished`  
**Script:** `scripts/todo_done.py`

### todo list

**What it does:** Show your to-do list  
**Also found by:** `show todos`, `my todos`, `pending`, `things to do`, `what do i have to do`, `to do list`, `my list`, `show tasks`  
**Script:** `scripts/todo_list.py`

### weekly summary

**Usage:** `weekly summary | monthly summary`  
**What it does:** One-page summary of your week or month: spending, habits, journal, to-dos, water and sleep (weekly summary, monthly summary)  
**Also found by:** `week summary`, `monthly summary`, `month summary`, `my week`, `weekly report`, `review my week`, `summary of my week`, `how was my week`, `progress report`  
**Your words:** passed through untouched  
**Script:** `scripts/weekly_summary.py`

### work tracker

**Usage:** `track start <task> | track stop | track status | track report [today|week]`  
**What it does:** Track how long you work on things (track start report, track stop, track status, track report week)  
**Also found by:** `track start`, `track stop`, `track status`, `track report`, `start tracking`, `stop tracking`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/work_tracker.py`


## lists

### document expiry

**Usage:** `add document <name> <expiry date> | documents | remove document <name>`  
**What it does:** Remember when passports, licences and IDs expire (add document passport 12 mar 2031, documents, remove document passport)  
**Also found by:** `passport expiry`, `licence expiry`, `license expiry`, `add document`, `my documents`, `remove document`, `id expiry`, `document expires`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/document_expiry.py`

### meal planner

**Usage:** `meal plan <day> <meals> | meal plan | meal today | meal clear`  
**What it does:** Plan the week's meals (meal plan monday dal rice, meal plan, meal today, meal clear)  
**Also found by:** `meal plan`, `weekly meals`, `what to cook`, `menu plan`, `dinner plan`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/meal_planner.py`

### my calendar

**Usage:** `calendar file <title> <date> [time] [for <minutes>]`  
**What it does:** Make a .ics calendar event file that opens in any calendar app (calendar file dentist 25 dec 4pm)  
**Also found by:** `calendar file`, `ics file`, `make ics`, `calendar event file`, `save event calendar`, `add to calendar file`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/my_calendar.py`

### shopping add

**Usage:** `shopping add <items>`  
**What it does:** Add items to the shopping list (shopping add milk, eggs and bread)  
**Also found by:** `shopping`, `shopping list`, `add to shopping list`, `need to buy`, `add item`  
**Your words:** passed through untouched  
**Script:** `scripts/shopping_add.py`

### shopping clear

**What it does:** Clear the whole shopping list  
**Behaviour:** asks before running.  
**Also found by:** `clear shopping list`, `empty shopping list`, `clear groceries`, `reset shopping`, `start over`  
**Script:** `scripts/shopping_clear.py`

### shopping list

**What it does:** Show the shopping list  
**Also found by:** `show shopping list`, `grocery list`, `what to buy`, `my groceries`, `show groceries`, `list shopping`  
**Script:** `scripts/shopping_list.py`

### shopping remove

**Usage:** `shopping remove <n|name>`  
**What it does:** Cross an item off (shopping remove 2, or shopping remove milk)  
**Also found by:** `remove from shopping`, `bought`, `got it`, `cross off`, `shopping done`, `delete item`, `remove item`  
**Your words:** passed through untouched  
**Script:** `scripts/shopping_remove.py`


## shopping

### open amazon

**Usage:** `open amazon <words>`  
**What it does:** Open Amazon India or search it  
**Also found by:** `shop`, `buy`, `order`, `shopping`, `search`  
**Script:** `scripts/open_amazon.py`

### open flipkart

**Usage:** `open flipkart <words>`  
**What it does:** Open Flipkart or search it  
**Also found by:** `shop`, `buy`, `order`, `shopping`, `search`  
**Script:** `scripts/open_flipkart.py`

### open myntra

**Usage:** `open myntra <words>`  
**What it does:** Open Myntra or search it  
**Also found by:** `clothes`, `fashion`, `shoes`, `shop`, `search`  
**Script:** `scripts/open_myntra.py`


## journal

### journal add

**Usage:** `journal add <text>`  
**What it does:** Add a dated diary entry (journal had a great day)  
**Also found by:** `journal`, `diary`, `dear diary`, `log my day`, `write journal`, `daily log`, `journal entry`, `add journal`  
**Your words:** passed through untouched  
**Script:** `scripts/journal_add.py`

### journal prompt

**Usage:** `journal prompt`  
**What it does:** Give a question to write about in your journal (journal prompt)  
**Also found by:** `writing prompt`, `what to write`, `diary prompt`, `journal idea`, `reflect`, `reflection question`  
**Script:** `scripts/journal_prompt.py`

### journal show

**Usage:** `journal show [days|word]`  
**What it does:** Read your journal (last 7 days; or a number of days, or a word to search)  
**Also found by:** `show journal`, `read journal`, `my journal`, `past entries`, `diary entries`, `journal history`, `search journal`  
**Your words:** passed through untouched  
**Script:** `scripts/journal_show.py`


## habits

### habit done

**Usage:** `habit done <name>`  
**What it does:** Tick a habit for today (habit done gym)  
**Also found by:** `habit`, `did`, `done today`, `completed`, `check in`, `tick`, `i did`, `workout done`, `log habit`, `habit tracker`  
**Your words:** passed through untouched  
**Script:** `scripts/habit_done.py`

### habit streak

**What it does:** Show all habits with current streak and the last 14 days  
**Also found by:** `habits`, `my habits`, `streaks`, `habit list`, `habit progress`, `show habits`, `habit report`  
**Script:** `scripts/habit_streak.py`


## birthdays

### add birthday

**Usage:** `add birthday <name> <date>`  
**What it does:** Save a birthday (add birthday mom 14 aug, add birthday raj 3 march 1999)  
**Also found by:** `birthday`, `save birthday`, `remember birthday`, `anniversary`, `born on`, `new birthday`  
**Your words:** passed through untouched  
**Script:** `scripts/add_birthday.py`

### remove birthday

**Usage:** `remove birthday <name>`  
**What it does:** Delete a saved birthday  
**Also found by:** `delete birthday`, `forget birthday`, `remove anniversary`  
**Your words:** passed through untouched  
**Script:** `scripts/remove_birthday.py`

### upcoming birthdays

**What it does:** Show birthdays in the next 60 days  
**Also found by:** `birthdays`, `birthday list`, `whose birthday`, `next birthday`, `birthdays soon`, `show birthdays`  
**Script:** `scripts/upcoming_birthdays.py`


## personal

### reading list

**Usage:** `add book <title> | books | finished book <title> | remove book <title>`  
**What it does:** Keep a list of books to read and finished (add book Atomic Habits, books, finished book atomic habits)  
**Also found by:** `add book`, `books`, `book list`, `finished book`, `finished reading`, `read book`, `books to read`, `my books`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/reading_list.py`


## work

### action items

**Usage:** `action items <notes file | text>`  
**What it does:** Pull the to-do lines out of meeting notes (action items notes.txt, or paste text after it). Simple rules, no AI.  
**Also found by:** `find action items`, `extract action items`, `to dos from notes`, `tasks from notes`, `what do i need to do from notes`, `follow ups from meeting`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/action_items.py`

### meeting notes

**Usage:** `meeting notes [title]`  
**What it does:** Create a dated meeting-notes file from a template (meeting notes weekly sync)  
**Also found by:** `new meeting notes`, `minutes of meeting`, `mom template`, `notes for meeting`, `meeting minutes`, `create meeting notes`, `agenda template`  
**Your words:** passed through untouched  
**Script:** `scripts/meeting_notes.py`


Back to [Home](Home) | [Task Catalog](Task-Catalog).
