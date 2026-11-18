# Routines, Aliases, Variables and Automation

## Aliases
    alias add wa = send whatsapp to
    wa mom see you at 5
    alias list      alias remove wa
    alias export    alias import file.json

Up to three words, expanded only at the start of a line. An alias that points at nothing is refused, and so are names of built-in commands. Choosing from a menu saves a phrase as an alias automatically.

## Routines
A routine is a named list of phrases run in order.
- Built in: `start work day`, `end work day`, `study mode`, `meeting mode`, `night mode`.
- `list routines`, `run routine <name>`, `edit routines` (opens `routines.json`).
- Steps: plain strings are phrases; `say:text` prints; `wait:5` pauses 5 seconds.

      "start_work_day": ["say:Starting...", "open gmail", "open calendar", "todo list"]

- Parameters: write `{1}`, `{2}` in a step, give words when you run: `run routine morning Asha london`.
- Date variables in steps: `{today}`, `{date}`, `{month}`, `{year}`, `{weekday}`, `{week}`, `{time}`.
- Share: `routines export`, `routines import file.json` (validated, asks first).

## Variables
    set var rate = 18
    gst 1000 $rate        (also ${rate})
    vars       remove var rate

Up to 100 variables, values up to 120 characters. An undefined `$name` stays as typed. `ans` holds the last `calculate` answer: `calculate ans * 2`, `gst $ans 18`.

## Batch files
One phrase per line, blank lines and `#` comments ignored:

    batch myjobs.txt              stops at the first failure
    batch myjobs.txt keep going   continues

Variables work inside; terminal-only commands (`web`, `update`, `setup`, `plugin`...) are skipped.

## Chains and pipes
`gst 2500 18 then save it to a note`; `type notes.txt | jeeg word count`. See [Commands and Options](Commands-and-Options).

## Autorun (schedules)
    autorun add "start work day" at 9:00 weekdays
    autorun list
    autorun remove 1

Uses Task Scheduler on Windows and cron on macOS and Linux. Untested on real Windows and macOS machines.

## Watching and rules
- `watch folder <folder> move <types> to <folder>` (asks first; add `once` for one pass).
- `watch price <url>` then `check watches`.
- Event rules for linked apps: `rule add ... when <app> <read-action> changes then <task>` ([Linked Apps](Linked-Apps)).

## Packs
`pack off games` turns a whole category off so it is never matched; `pack on games` brings it back.
