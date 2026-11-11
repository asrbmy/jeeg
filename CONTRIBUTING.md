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

## A worked example: `rupees_to_paise`

```python
# keywords: paise, rupees to paise, convert to paise
# desc: Convert rupees to paise (rupees to paise 12.5)
# category: money
# usage: rupees to paise <amount>
# rawargs: yes
import re, sys
n = re.findall(r"\d+(?:\.\d+)?", " ".join(sys.argv[1:]))
if not n:
    sys.exit("Usage: rupees to paise 12.5")
print(f"{float(n[0]):g} rupees = {round(float(n[0]) * 100):,} paise")
```

This one uses only the standard library, so it works anywhere: in `~/.jeeg/plugins/` for yourself, or in `scripts/` as a built-in (built-in tasks can also use the helpers in `scripts/_lib.py`, `_money.py` and so on; plugins cannot). Save it as `rupees_to_paise.py`, then add this line to `tests/phrases.txt`:

```
rupees to paise 12.5 => rupees_to_paise | 12.5
```

The text after `|` is what the task should receive as arguments. Run `python tests/test_routing.py` and `python jeeg.py selftest`. If another task starts winning for common words, rename your task or add `# patterns:` and `# priority: 2` (see `explain <phrase>`).

Use it from Python too: `jeeg.rupees_to_paise(12.5)`.

## Releasing (automatic)

1. Change `__version__` in `jeeg.py` (for example `2.16.1`) and add a `## 2.16.1` section at the top of `CHANGELOG.md`. That section becomes the release notes.
2. Commit and push to `main`.
3. The `publish` workflow runs the tests, builds the package, creates the tag `v2.16.1`, makes the GitHub release with the files attached, and uploads to PyPI.

Pushes that do not change the version do nothing: a version that already has a tag is skipped. PyPI upload needs the one-time setup in `.github/workflows/publish.yml` (trusted publisher on pypi.org, an environment named `pypi`, and the repository variable `PUBLISH_PYPI` = `true`). You can also run the workflow by hand from the Actions tab.
