# Plugins and Writing Your Own Tasks

A task is a file in `scripts/` (or a plugin folder). You can add, edit or remove tasks with a text editor.

## Make a task in four steps

1. Create a file named in words with underscores: `open_notes_app.py`. The name is what you will say ("open notes app").
2. Put a header in the first 15 lines, then your code:

       # keywords: notes, notebook, jot
       # desc: Open my notes app
       # category: apps
       from _lib import launch
       launch(win=[("start", "onenote")], mac=[("open", "-a", "Notes")], linux=[("gnome-notes",)], name="Notes")

3. Type `reindex`, then `selftest` (it checks the file is found by its own name and compiles).
4. Try `explain open notes app`.

Any language works: `.py`, `.sh`, `.bat`, `.cmd`, `.ps1`, `.js`. Words after the task name arrive as arguments (Python: `sys.argv[1:]` or `args_text()`).

Keep personal scripts in another folder and start JeeG with `--dir PATH` (or `TASK_SCRIPTS_DIR`) so updates never touch them.

## Header lines

| Line | Meaning |
|---|---|
| `# keywords:` | Extra words that find this task |
| `# desc:` | One-line description for `list` |
| `# category:` | Group in `list` |
| `# usage:` | The task takes words after its name |
| `# confirm: yes` | Ask before running |
| `# priority: 1` | Wins ties against equal matches |
| `# rawargs: yes` | Pass your words untouched (drops only words that matched the name) |
| `# rawargs: full` | Pass the whole sentence |
| `# patterns: regex ;; regex` | Phrases that identify this task |
| `# private: yes` | Never write what you typed to history |
| `# network: yes` | Required if the task touches the network; it appears in `privacy` |

## Naming tips
- Do not build names from very common words (`open`, `search`, `list`, `file`, `image`). When many scripts share a word, JeeG treats it as weak.
- Avoid numbers in `keywords:`; a keyword like `25 minutes` would pull `25 * 4` into your task.
- If two tasks clash, give the better one `# priority: 1` or a `# patterns:` line.
- Run `selftest` and `python tests/test_routing.py` after adding tasks.

## Helpers (`from _lib import ...`)
`args_text()`, `open_url(url)`, `launch(...)`, `fail("message")`, `call([...])`, `data_dir()`, `notify(title, text)`, `need("module", "pip name")`. Other shared helpers live in `_files.py`, `_text.py`, `_dates.py`, `_money.py`, `_net.py`. Files starting with `_` are helpers, not tasks.

## Plugins (drop-in tasks)
Plugins live in the `plugins` folder inside your data folder (`plugins` shows the path).

    plugin new tea_timer          writes a starter task
    plugin install file.py        (or an https link) shows what it says it does, size, a scan for risky features, then asks
    plugin export <name>          copy out to share
    plugin remove <name>          plugin list
    plugin search loan            plugin get loan_prepay      the plugin library
    plugin update / outdated      refresh library plugins after fingerprint checks
    share plugin <name>           one file to send a friend

A plugin cannot take the name of a built-in task; files over 200 KB are refused; the library checks each file's SHA-256 fingerprint. Starter plugins: `loan_prepay`, `goal_planner`, `rent_receipt`, `packing_list` and more. To publish your own to the library see `library/README.md`.

**Plugins are programs. They run with your permissions. Read them first.**

## Contributing to JeeG itself
See `CONTRIBUTING.md`. Run the suites before sending changes:

    python jeeg.py selftest
    python tests/test_routing.py
    python tests/test_privacy.py

(`tests/` has more suites; `Testing and Releasing` lists them.)
