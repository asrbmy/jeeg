"""Use JeeG from your own Python programs.

    import jeeg

    r = jeeg.run("gst 2500 18")          # say it in words, like at the terminal
    print(r.output)                       # the text the task printed
    if r.ok: ...                          # True when the task finished with exit code 0

    jeeg.gst_amount(2500, 18).output      # or call a task by name, with its arguments
    jeeg.find("open youtube")             # which task would run, and how sure JeeG is
    jeeg.tasks(category="money")          # what is available

    j = jeeg.JeeG(home="my-data", yes=False, timeout=30)    # your own settings and data folder
    j("add expense 250 food lunch")

Everything runs on your computer. Calls never ask questions: a task that wants confirmation returns exit code 3
(pass yes=True to allow it). Library calls are not written to your command history. Calls are serialised with a lock,
so they are safe to make from several threads, but they run one at a time. Standard library only.
"""
from __future__ import annotations

import contextlib
import difflib
import io
import json
import os
import re
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

import jeeg as _engine

__all__ = ["run", "run_many", "arun", "run_task", "find", "tasks", "categories", "task_info", "JeeG", "Result", "TaskRun", "TaskInfo", "Match",
           "JeeGError", "UnknownTaskError"]

MAX_LINE = 2000
# Commands that are interactive, long-running or that install code: only available in the terminal.
TERMINAL_ONLY = frozenset({"web", "ui", "learn", "tour", "tutorial", "setup", "exit", "quit", "q", "update", "upgrade",
                           "plugin", "plugins", "routines", "completion", "first"})
_LOCK = threading.RLock()
_CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


class JeeGError(RuntimeError):
    """Raised by run(..., check=True) when a task did not finish. The Result is in .result."""

    def __init__(self, result: "Result"):
        self.result = result
        first = (result.output.strip().splitlines() or ["no output"])[0]
        super().__init__(f"{result.query!r} failed (exit {result.exit}): {first}")


class UnknownTaskError(KeyError, AttributeError):
    """No task has that name. .suggestions lists close names."""

    def __init__(self, name: str, suggestions: Iterable[str] = ()):
        self.name, self.suggestions = name, list(suggestions)
        hint = f" Did you mean: {', '.join(self.suggestions)}?" if self.suggestions else ""
        super().__init__(f"no task named {name!r}.{hint}")

    def __str__(self) -> str:
        return self.args[0]


@dataclass(frozen=True)
class TaskRun:
    name: str
    args: tuple
    exit: int
    seconds: float


@dataclass(frozen=True)
class Result:
    """What came back from running a task."""
    query: str
    exit: int
    output: str
    runs: tuple = ()
    candidates: tuple = ()

    @property
    def ok(self) -> bool:
        return self.exit == 0

    def __bool__(self) -> bool:
        return self.ok

    def __str__(self) -> str:
        return self.output

    @property
    def task(self) -> Optional[str]:
        """Name of the first task that ran, or None (nothing matched, or a built-in command)."""
        return self.runs[0].name if self.runs else None

    @property
    def matched(self) -> bool:
        return bool(self.runs) or self.exit == 0

    @property
    def needs_confirmation(self) -> bool:
        return self.exit == 3

    @property
    def ambiguous(self) -> bool:
        """More than one task fits equally well. .candidates names them."""
        return self.exit == 2

    @property
    def lines(self) -> list:
        return self.output.splitlines()

    def json(self) -> Any:
        """The output parsed as JSON (for tasks that print JSON). Raises ValueError otherwise."""
        return json.loads(self.output)

    def raise_for_status(self) -> "Result":
        if not self.ok:
            raise JeeGError(self)
        return self


@dataclass(frozen=True)
class Match:
    name: str
    score: float
    args: tuple
    description: str = ""


@dataclass(frozen=True)
class TaskInfo:
    name: str
    description: str
    category: str
    usage: str
    online: bool
    confirm: bool
    private: bool


# ------------------------------------------------------------------ plumbing
@contextlib.contextmanager
def _redirect_stdin(stream):
    old = sys.stdin
    sys.stdin = stream
    try:
        yield
    finally:
        sys.stdin = old


@contextlib.contextmanager
def _session(home, history: bool):
    """Point the engine at `home` for the duration of one call; restore everything afterwards."""
    with _LOCK:
        old = (_engine.STATE, os.environ.get("JEEG_HOME"), _engine.NOLOG)
        try:
            if home is not None:
                h = Path(os.fspath(home)).expanduser()
                if "\0" in str(h):
                    raise ValueError("home contains a NUL character")
                _engine.STATE = h
                os.environ["JEEG_HOME"] = str(h)
            _engine.NOLOG = not history
            yield
        finally:
            _engine.STATE, env, _engine.NOLOG = old
            if env is None:
                os.environ.pop("JEEG_HOME", None)
            else:
                os.environ["JEEG_HOME"] = env


def _clean_text(text: Any, what: str) -> str:
    if not isinstance(text, str):
        raise TypeError(f"{what} must be a string, not {type(text).__name__}")
    t = _CONTROL.sub("", text).strip()
    if len(t) > MAX_LINE:
        raise ValueError(f"{what} is too long (over {MAX_LINE} characters)")
    return t


def _entries(dirs):
    dl = _engine.script_dirs([str(d) for d in dirs])
    return _engine.active(_engine.load_index(dl)), dl


def _opt(yes: bool, timeout) -> dict:
    if timeout is not None and (not isinstance(timeout, (int, float)) or timeout <= 0):
        raise ValueError("timeout must be a positive number of seconds or None")
    return {"yes": bool(yes), "dry": False, "timeout": timeout, "json": False, "out": None, "quiet": True}


def _result(query: str, rc: int, text: str, opt: dict, candidates=()) -> Result:
    runs = tuple(TaskRun(t["name"], tuple(t["args"]), t["exit"], t["seconds"]) for t in opt.get("_tasks", []))
    return Result(query=query, exit=int(rc), output=text.rstrip("\n"), runs=runs, candidates=tuple(candidates))


# ------------------------------------------------------------------ public functions
def run(query: str, *, yes: bool = False, timeout: Optional[float] = 60, home=None, dirs: Iterable = (),
        history: bool = False, check: bool = False) -> Result:
    """Run what you would type at the JeeG prompt, e.g. run("gst 2500 18") or run("open gmail and open calendar").

    yes      allow tasks that ask for confirmation (shutdown, delete ...). Without it they return exit code 3.
    timeout  stop a task after this many seconds (None = no limit).
    home     use this data folder instead of ~/.jeeg (your own isolated notes, expenses, aliases ...).
    dirs     extra folders of task scripts.
    history  also write the call to your command history (off by default).
    check    raise JeeGError when the task did not finish.
    """
    q = _clean_text(query, "query")
    words = q.lower().split()
    opt = _opt(yes, timeout)
    if not words:
        res = _result(q, 1, "Say something to run.", opt)
    elif words[0] in TERMINAL_ONLY or (words[0] == "jeeg" and len(words) > 1 and words[1] in TERMINAL_ONLY):
        res = _result(q, 1, f"'{words[0]}' is only available in the terminal, not from Python.", opt)
    else:
        with _session(home, history):
            dl = _engine.script_dirs([str(d) for d in dirs])
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf), _redirect_stdin(io.StringIO("")):
                    rc = _engine.handle(q, dl, opt)
            except SystemExit as ex:
                rc = ex.code if isinstance(ex.code, int) else 1
            rc = 0 if rc is None else rc
            cands = []
            if rc == 2:
                ranked = _engine.resolve(_engine.expand_alias(q), _engine.active(_engine.load_index(dl)))
                if ranked[0] == "ambiguous":
                    cands = [h[1]["name"] for h in ranked[1]]
        res = _result(q, rc, buf.getvalue(), opt, cands)
    if check:
        res.raise_for_status()
    return res


def run_many(queries: Iterable[str], *, stop_on_error: bool = False, **kw) -> list:
    """Run several phrases in order and return a list of Results. stop_on_error=True stops after the first failure."""
    if isinstance(queries, str):
        raise TypeError("run_many needs a list of phrases, not one string (use run for one)")
    out = []
    for q in queries:
        r = run(q, **kw)
        out.append(r)
        if stop_on_error and not r.ok:
            break
    return out


async def arun(query: str, **kw) -> Result:
    """Async version of run() for asyncio programs: r = await jeeg.arun("gst 2500 18"). Runs in a worker thread."""
    import asyncio
    return await asyncio.get_running_loop().run_in_executor(None, lambda: run(query, **kw))


def run_task(name: str, *args: Any, yes: bool = False, timeout: Optional[float] = 60, home=None, dirs: Iterable = (),
             history: bool = False, check: bool = False) -> Result:
    """Run one task by its exact name, passing arguments as they are: run_task("gst_amount", 2500, 18).

    Skips the word matching entirely, so it is predictable in programs. Raises UnknownTaskError for a bad name.
    """
    if not isinstance(name, str):
        raise TypeError("task name must be a string")
    key = name.strip().lower().replace(" ", "_").replace("-", "_")
    argv = [_clean_text(str(a), "argument") for a in args]
    if sum(len(a) for a in argv) > MAX_LINE:
        raise ValueError(f"arguments are too long (over {MAX_LINE} characters in all)")
    opt = _opt(yes, timeout)
    with _session(home, history):
        entries, _ = _entries(dirs)
        entry = next((e for e in entries if e["name"] == key), None)
        if entry is None:
            near = difflib.get_close_matches(key, [e["name"] for e in entries], n=3, cutoff=0.6)
            raise UnknownTaskError(name, near)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf), _redirect_stdin(io.StringIO("")):
            rc = _engine.run_entry(entry, argv, opt)
        res = _result(f"{entry['name']} {' '.join(argv)}".strip(), rc, buf.getvalue(), opt)
    if check:
        res.raise_for_status()
    return res


def find(query: str, limit: int = 5, *, home=None, dirs: Iterable = ()) -> list:
    """Which tasks would handle this phrase, best first: [Match(name, score, args, description)]. Runs nothing."""
    q = _clean_text(query, "query")
    with _session(home, False):
        entries, _ = _entries(dirs)
        ranked = _engine.rank(_engine.expand_alias(q), entries) if q else []
    return [Match(e["name"], round(sc, 3), tuple(args), e["desc"]) for sc, e, args in ranked[:max(1, int(limit))]]


def _info(e: dict) -> TaskInfo:
    return TaskInfo(e["name"], e["desc"], e["cat"], e["usage"], bool(e.get("net")), bool(e["confirm"]), bool(e["private"]))


def tasks(category: Optional[str] = None, online: Optional[bool] = None, *, home=None, dirs: Iterable = ()) -> list:
    """All available tasks as TaskInfo, optionally filtered by category or by whether they can use the internet."""
    with _session(home, False):
        entries, _ = _entries(dirs)
    out = [_info(e) for e in entries if (category is None or e["cat"] == category.lower())
           and (online is None or bool(e.get("net")) == online)]
    return sorted(out, key=lambda t: (t.category, t.name))


def categories(*, home=None, dirs: Iterable = ()) -> dict:
    """{category: number of tasks}."""
    out: dict = {}
    for t in tasks(home=home, dirs=dirs):
        out[t.category] = out.get(t.category, 0) + 1
    return dict(sorted(out.items()))


def task_info(name: str, *, home=None, dirs: Iterable = ()) -> TaskInfo:
    key = name.strip().lower().replace(" ", "_").replace("-", "_")
    for t in tasks(home=home, dirs=dirs):
        if t.name == key:
            return t
    raise UnknownTaskError(name, difflib.get_close_matches(key, [t.name for t in tasks(home=home, dirs=dirs)], n=3, cutoff=0.6))


def task_function(name: str):
    """The callable behind jeeg.<task_name>(...). Raises AttributeError when there is no such task."""
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name) or not any(t.name == name for t in tasks()):
        raise AttributeError(f"module 'jeeg' has no attribute or task {name!r}")

    def call(*args, **kw):
        return run_task(name, *args, **kw)
    call.__name__ = name
    call.__doc__ = task_info(name).description
    return call


class JeeG:
    """Your own settings in one place: JeeG(home="data", yes=False, timeout=30, dirs=["my_tasks"]).

    j = JeeG(home="data"); j("add expense 250 food lunch"); j.gst_amount(1000, 18); j.find("weather"); j.tasks()
    """

    def __init__(self, home=None, *, yes: bool = False, timeout: Optional[float] = 60, dirs: Iterable = (), history: bool = False):
        self.home, self.yes, self.timeout, self.dirs, self.history = home, yes, timeout, tuple(dirs), history
        _opt(yes, timeout)                      # validate now

    def _kw(self, **over) -> dict:
        kw = dict(yes=self.yes, timeout=self.timeout, home=self.home, dirs=self.dirs, history=self.history)
        kw.update(over)
        return kw

    def run(self, query: str, **over) -> Result:
        return run(query, **self._kw(**over))

    __call__ = run

    def run_many(self, queries: Iterable[str], **over) -> list:
        return run_many(queries, **self._kw(**over))

    async def arun(self, query: str, **over) -> Result:
        return await arun(query, **self._kw(**over))

    def run_task(self, name: str, *args: Any, **over) -> Result:
        return run_task(name, *args, **self._kw(**over))

    def find(self, query: str, limit: int = 5) -> list:
        return find(query, limit, home=self.home, dirs=self.dirs)

    def tasks(self, category: Optional[str] = None, online: Optional[bool] = None) -> list:
        return tasks(category, online, home=self.home, dirs=self.dirs)

    def categories(self) -> dict:
        return categories(home=self.home, dirs=self.dirs)

    def task_info(self, name: str) -> TaskInfo:
        return task_info(name, home=self.home, dirs=self.dirs)

    def __getattr__(self, name: str):
        if name.startswith("_") or not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise AttributeError(name)
        if not any(t.name == name for t in self.tasks()):
            raise AttributeError(f"no task named {name!r}")
        return lambda *args, **over: self.run_task(name, *args, **over)

    def __dir__(self):
        return sorted(set(super().__dir__()) | {t.name for t in self.tasks()})

    def __repr__(self) -> str:
        return f"JeeG(home={self.home!r}, yes={self.yes}, timeout={self.timeout})"
