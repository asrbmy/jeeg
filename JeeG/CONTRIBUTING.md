# Contributing to JeeG

Thank you. JeeG stays small on purpose: standard-library Python, no background processes, no accounts, no network unless a task is about the network.

## Add a task in five minutes

1. `jeeg plugin new my_task` creates `~/.jeeg/plugins/my_task.py`, or copy any file in `scripts/` as a model.
2. Fill the header at the top of the file:

```
# keywords: words people would say, separated by commas
# desc: One line: what it does (example input)
# category: money
# usage: my task <thing>
```

3. Say a phrase in your terminal. `explain <phrase>` shows which tasks match and why.
4. To make it a built-in task: put the file in `scripts/`, add 2-4 example phrases to `tests/phrases.txt` (`phrase => script_name`), run the tests.

## Rules for tasks

- Standard library only. If a task needs something optional (for example `pypdf`), say so in `fail(...)` with the pip command.
- Windows, macOS and Linux: use `_lib.py` helpers (`open_url`, `open_path`, `launch`, `data_dir`) rather than OS-specific commands.
- Never write outside the data folder or a folder the user named. Anything that deletes or overwrites needs `# confirm: yes`.
- No calls to AI services and no tracking. A task that goes online must say so in its description, for example "(needs internet)".
- Use plain, short output. A person should understand it without reading code.

## Run the tests

```
python jeeg.py selftest
python tests/test_routing.py
python tests/test_parsers.py
python tests/test_engine.py
python tests/test_cmds.py
python tests/test_security.py
```

All must pass. The routing test matters most: new keywords can make a common word "generic" and quietly break other tasks, so add your phrases and run it.

## Reporting a security problem

Please do not open a public issue. Use GitHub's "Report a vulnerability" button on the Security tab, and include the command you typed and what happened.
