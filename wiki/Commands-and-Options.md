# Commands and Options

## Built-in commands

| Command | What it does |
|---|---|
| `list`, `list <category>` | All tasks / one category. `*` = asks before running, `[online]` = may use the internet |
| `again` | Repeat the last task |
| `history` | Recent tasks |
| `explain <words>` | Show matches, scores and which would run |
| `alias add/list/remove/export/import` | Your own short words |
| `misses`, `misses export`, `misses clear` | What matched nothing |
| `stats`, `my habits` | What you use, how long it takes, what fails |
| `doctor`, `doctor fix` | Check setup; repair damaged data files |
| `pack list/off/on <category>` | Turn whole categories off or on |
| `plugins`, `plugin ...` | See [Plugins and Writing Your Own Tasks](Plugins-and-Writing-Your-Own-Tasks) |
| `tips` | One task you may not have tried |
| `reindex` | Rebuild the script cache after editing a header |
| `selftest` | Check every script is described, compiles and is found by its own name |
| `learn` | Seven-step guided tour |
| `privacy` | Which tasks can use the internet |
| `setup`, `update`, `report` | Wizard; update check; a safe bug-report file |
| `export data`, `import data`, `backup status` | Backups |
| `undo` | Put back your last file move or rename (remembers 20) |
| `vars`, `set var x = 1`, `remove var x` | Variables |
| `batch file.txt` | Run one phrase per line |
| `autorun add/list/remove` | Run a phrase on a schedule |
| `web`, `web lan` | Local page / phone page |
| `connect ai` | AI mode |
| `real test ...` | Test JeeG on your computer |
| `exit` | Quit |

## Options (before your words)

| Option | Meaning |
|---|---|
| `--dry-run` | Show what would run, run nothing |
| `-y`, `--yes` | Do not ask for confirmation |
| `--timeout 30` | Stop a script after 30 seconds |
| `--dir PATH` | Also read scripts from another folder (repeatable; env `TASK_SCRIPTS_DIR`) |
| `--json` | One JSON object with task, exit code and output |
| `--output file` | Save what the task prints to a new file (never overwrites) |
| `--stdio`, `--serve-api`, `--mcp` | Use JeeG from other programs ([Use JeeG From Code](Use-JeeG-From-Code)) |
| `--version`, `-h` | Version, help |

## Exit codes
`0` ok, `1` error or no match, `2` ambiguous (menu with no keyboard), `3` needs confirmation or declined.

## Chaining and piping
- `gst 2500 18 then save it to a note` (also `then copy it`, `then speak it`). Tasks that ask for confirmation are never chained.
- `type notes.txt | jeeg word count`, `cat list.txt | jeeg sort lines` (up to 1 MB; typed words win over piped text).

## Environment variables

| Variable | Use |
|---|---|
| `JEEG_HOME` | Where your data lives |
| `TASK_SCRIPTS_DIR` | Extra scripts folder |
| `JEEG_DEBUG=1` | Show full error details |
| `JEEG_BROWSER` | Full path of the browser program for the `browser` tasks |
