# Using JeeG in your own Python programs

A step-by-step guide. You need Python 3.9 or newer. JeeG uses only the standard library and runs entirely on your computer.

## 1. Install

```
pip install jeeg
```

Check it works:

```
python -c "import jeeg; print(jeeg.__version__)"
```

(Not on PyPI yet? Put the `jeeg.py`, `jeeg_cmds.py`, `jeeg_api.py` files and the `scripts` folder next to your program and `import jeeg` works the same way.)

## 2. Your first call

```python
import jeeg

r = jeeg.run("gst 2500 18")
print(r.output)
```

`run` takes the same words you would type at the JeeG prompt and returns a **Result**:

| You want | Use |
|---|---|
| The printed text | `r.output` (or `str(r)`) |
| Did it work? | `r.ok` (True when the exit code is 0) or just `if r:` |
| The exit code | `r.exit` (0 ok, 1 error or no match, 2 several tasks fit, 3 needs confirmation) |
| Which task ran | `r.task`, and details in `r.runs` |
| Output line by line | `r.lines` |
| Output that is JSON | `r.json()` |

## 3. Call a task by name

Saying words is friendly; naming the task is predictable. In a program, prefer this:

```python
jeeg.gst_amount(1000, 18)             # same as jeeg.run_task("gst_amount", 1000, 18)
jeeg.convert_units("5 km to miles")
```

Find task names with `jeeg.tasks()` (below) or the **Task list** in USER_GUIDE.md. A wrong name raises `UnknownTaskError` with close suggestions.

## 4. Look before you run

```python
for m in jeeg.find("open youtube", limit=3):
    print(m.name, m.score)            # runs nothing

for t in jeeg.tasks(category="money"):
    print(t.name, "-", t.description)

jeeg.categories()                      # {"apps": 26, "money": ...}
jeeg.task_info("gst_amount").usage     # how to word it
jeeg.tasks(online=True)                # tasks that can use the internet
```

## 5. Keep your own data separate

By default JeeG stores notes, expenses, reminders and so on in `~/.jeeg`. A program usually wants its own folder:

```python
j = jeeg.JeeG(home="my_app_data", timeout=30)
j("add expense 250 food lunch")
print(j("show expenses").output)
j.gst_amount(1000, 18)                 # tasks are methods too
```

`JeeG(...)` takes: `home`, `yes`, `timeout`, `dirs` (extra folders of your own task scripts) and `history`.

## 6. Handle problems

```python
r = jeeg.run("some phrase")
if r.ambiguous:
    print("Did you mean one of:", r.candidates)
elif r.needs_confirmation:
    print("This task asks first (shutdown, delete ...). Pass yes=True to allow it.")
elif not r.ok:
    print("Failed:", r.output)

jeeg.run("qzxqzx", check=True)         # raises jeeg.JeeGError instead
```

Calls **never prompt** for input, so they cannot hang your program. Tasks that normally ask "are you sure?" return exit code 3 unless you pass `yes=True`:

```python
jeeg.run("shutdown pc", yes=True)   # really shuts down - be careful
```

## 7. Several at once, and async

```python
results = jeeg.run_many(["gst 100 5", "disk space", "show time"])
for r in results:
    print(r.task, r.ok)

import asyncio
async def main():
    r = await jeeg.arun("gst 2500 18")
    print(r.output)
asyncio.run(main())
```

`run_many(..., stop_on_error=True)` stops after the first failure.

## 8. Settings that matter

| Option | Meaning | Default |
|---|---|---|
| `timeout` | Stop a task after this many seconds (`None` = no limit) | 60 |
| `yes` | Allow tasks that ask for confirmation | False |
| `home` | Data folder | `~/.jeeg` |
| `dirs` | Extra folders with your own task scripts | none |
| `history` | Also record the call in command history | False |
| `check` | Raise `JeeGError` on failure | False |

## 9. Add your own tasks

Put a script in a folder and pass it with `dirs`:

```python
# my_tasks/say_hello.py
# keywords: hello, greet
# desc: Say hello
print("hello from my task")
```

```python
j = jeeg.JeeG(dirs=["my_tasks"])
j("say hello")
j.say_hello()
```

## 10. Good to know

- **Safe by design:** control characters are removed from input, over 2,000 characters is refused, and `web`, `setup`, `update` and `plugin` are only available in the terminal.
- **Threads:** you can call from several threads; calls run one at a time.
- **Private:** nothing is sent anywhere unless a task is marked online (it needs the internet to answer, like weather). Run `jeeg privacy` to see which.
- **Not in your history:** library calls do not fill your `history` or "misses" list.
- **Examples:** see the `examples/` folder (`use_from_python.py`, `daily_report.py`).

## 11. Quick cheat sheet

```python
import jeeg
jeeg.run("phrase")                 # words
jeeg.task_name(arg, ...)           # by name
jeeg.run_many([...])               # list
await jeeg.arun("phrase")          # async
jeeg.find("phrase")                # which task? (no run)
jeeg.tasks(category="money")       # what exists
jeeg.JeeG(home="data")("phrase")   # own data folder
```
