#!/usr/bin/env python3
"""
JeeG - say a task in plain words, the matching script runs.

    python jeeg.py open youtube
    python jeeg.py search python tutorial          (extra words become arguments)
    python jeeg.py open gmail and open calendar    (several tasks in one line)
    python jeeg.py                                  (interactive mode)

Commands (interactive or one-shot):
    list [category]   show tasks          again    repeat the last task
    history           recent tasks        reindex  rebuild the cache
    selftest          verify every script resolves correctly
    alias add wa = send whatsapp to     your own short words (alias list / alias remove wa)
    explain <words>   show which tasks match and why        misses   phrases it could not match
    stats             what you use most                     doctor   check this computer
    update [now]      check GitHub for a newer version      setup    first-run wizard
    learn             a 7-step guided tour                  doctor fix   repair common problems
    routines export|import <file>    alias export|import <file>   share your setup
    plugin search|get <name>          shared plugin library
    plugin new|install|export|remove|list   your own tasks    web   a local page in your browser
    completion bash|zsh|powershell          tab completion
    tips              suggest a task you have not used      pack list / pack off <category> / pack on <category>
    exit              quit

Options:
    --dir PATH   extra scripts folder (repeatable; also TASK_SCRIPTS_DIR)
    -y, --yes    do not ask before risky tasks
    --dry-run    show what would run, run nothing
    --json       print the result as JSON (task, exit code, output) for other programs
    --output F   save what the task prints to a new file F (never overwrites)
    --timeout S  stop a script after S seconds

Script header (first 15 lines of any script, comment style of that language):
    # keywords: chrome, internet, web
    # desc:     Open the default web browser
    # category: web
    # confirm:  yes          <- ask before running (shutdown, delete, ...)
    # priority: 1            <- wins ties against equally good matches
    # rawargs:  yes          <- keep keyword words in the arguments (timers, maths)
    # rawargs:  full         <- pass the whole sentence (date maths)
    # patterns: regex ;; regex   <- phrases that identify this task
    # private:  yes          <- never write what you typed to history (passwords)
    # usage:    search <words>

Exit codes: 0 ok, 1 error / no match, 2 ambiguous, 3 declined.
Standard library only. Index is cached, so start-up stays fast.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

__version__ = "2.7.0"

HERE = Path(__file__).resolve().parent
def _state_dir() -> Path:
    """Data folder: JEEG_HOME (or the older TASKRUNNER_HOME), else ~/.jeeg; an existing ~/.taskrunner is still used."""
    env = os.environ.get("JEEG_HOME") or os.environ.get("TASKRUNNER_HOME")
    if env:
        return Path(env)
    new, old = Path.home() / ".jeeg", Path.home() / ".taskrunner"
    return old if (old.exists() and not new.exists()) else new


STATE = _state_dir()


def _ensure_state() -> None:
    """Create the data folder, readable only by you (your notes, journal and history are private)."""
    STATE.mkdir(parents=True, exist_ok=True)
    if os.name == "posix":
        try:
            if STATE.stat().st_mode & 0o077 and STATE.stat().st_uid == os.getuid():
                STATE.chmod(0o700)
        except OSError:
            pass

IS_WIN = os.name == "nt"

RUNNERS = {
    ".py": lambda p: [sys.executable, str(p)],
    ".js": lambda p: ["node", str(p)],
    ".ps1": lambda p: [
        "powershell" if IS_WIN else "pwsh", "-NoProfile",
        "-ExecutionPolicy", "Bypass", "-File", str(p),
    ],
}
if IS_WIN:
    RUNNERS[".bat"] = RUNNERS[".cmd"] = lambda p: ["cmd", "/c", str(p)]
else:
    RUNNERS[".sh"] = lambda p: ["bash", str(p)]

FILLER = frozenset("""
a an the my me i you we it its is are was be to for of on in at by with
please pls can could would will shall just kindly hey
run start launch execute do want need like lets let tell give get go
now this that so then also
how much many have has does did what whats which who whom whose where when why been being am
""".split())

HEADER_RE = re.compile(r"^\s*(?:#|//|::|REM\b)\s*(\w+)\s*:\s*(.*?)\s*$", re.I)
SPLIT_RE = re.compile(r"\s*(?:&|;|\band then\b|\bthen\b|\band\b)\s*", re.I)
SPLIT_MIN_SCORE = 1.2   # every part must clearly name a task

INDEX_VERSION = 9    # bump when index format / tokenising changes
MIN_SCORE = 0.7      # below this a script is not considered a match
TIE_MARGIN = 0.04    # scores this close count as a tie
MENU_MAX = 8


# ---------------------------------------------------------------- text utils
NO_STEM = frozenset("news series lens canvas atlas bias chess maths physics mathematics ethics politics species".split())


def norm(word: str) -> str:
    """Lower-case, strip symbols, crude plural stemming."""
    w = re.sub(r"[^a-z0-9]", "", word.lower())
    if (len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is")) and w not in NO_STEM):
        w = w[:-1]
    return w


def norm_list(text: str) -> list[str]:
    return [t for t in (norm(x) for x in re.split(r"[^A-Za-z0-9]+", text)) if t]


# --------------------------------------------------------------------- index
def parse_header(path: Path) -> dict:
    meta = {}
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            for _ in range(15):
                line = f.readline()
                if not line:
                    break
                m = HEADER_RE.match(line)
                if m:
                    meta[m.group(1).lower()] = m.group(2)
    except OSError:
        pass
    return meta


def name_tokens(stem: str) -> list[str]:
    toks = norm_list(stem)
    return [t for t in toks if t not in FILLER] or toks     # "copy_to_clipboard" -> copy, clipboard


def make_entry(path: Path) -> dict:
    meta = parse_header(path)
    desc = meta.get("desc") or meta.get("description") or ""
    return {
        "path": str(path),
        "name": path.stem,
        "name_t": name_tokens(path.stem),
        "kw_t": norm_list(meta.get("keywords", meta.get("keyword", ""))),
        "desc_t": norm_list(desc),
        "desc": desc,
        "cat": (meta.get("category") or "general").lower(),
        "confirm": meta.get("confirm", "").lower() in {"yes", "true", "1", "y"},
        "usage": meta.get("usage", ""),
        "raw": 2 if meta.get("rawargs", "").lower() == "full" else int(meta.get("rawargs", "").lower() in {"yes", "true", "1", "y"}),
        "private": meta.get("private", "").lower() in {"yes", "true", "1", "y"},
        "net": meta.get("network", "").lower() in {"yes", "true", "1", "y"},
        "pat": [x.strip() for x in meta.get("patterns", "").split(";;") if x.strip()],
        "prio": int(meta["priority"]) if meta.get("priority", "").lstrip("-").isdigit() else 0,
    }


def script_dirs(cli_dirs: list[str]) -> list[Path]:
    cands = list(cli_dirs)
    cands += [d for d in os.environ.get("TASK_SCRIPTS_DIR", "").split(os.pathsep) if d]
    cands += [str(HERE / "scripts"), str(HERE / "jeeg_scripts")]      # jeeg_scripts: the pip-installed copy
    cands += [str(STATE / "plugins")]
    seen, out = set(), []
    for c in cands:
        p = Path(c).expanduser()
        if p.is_dir():
            r = p.resolve()
            if r not in seen:
                seen.add(r)
                out.append(r)
    return out


def load_index(dirs: list[Path], rebuild: bool = False) -> list[dict]:
    cache_file = STATE / "index.json"
    cache = {}
    if not rebuild:
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            cache = data.get("files", {}) if data.get("v") == INDEX_VERSION else {}
        except (OSError, ValueError):
            cache = {}
    files, entries, names, changed = {}, [], set(), False
    for d in dirs:
        try:
            listing = sorted(os.scandir(d), key=lambda e: e.name.lower())
        except OSError:
            continue
        for de in listing:
            p = Path(de.path)
            if (not de.is_file() or p.suffix.lower() not in RUNNERS
                    or p.name.startswith(("_", "."))):
                continue
            if p.stem.lower() in names:       # first folder wins on duplicates
                continue
            st = de.stat()
            key = str(p)
            hit = cache.get(key)
            if hit and hit["mtime"] == st.st_mtime and hit["size"] == st.st_size:
                entry = hit["entry"]
            else:
                entry = make_entry(p)
                changed = True
            files[key] = {"mtime": st.st_mtime, "size": st.st_size, "entry": entry}
            entries.append(entry)
            names.add(p.stem.lower())
    if changed or set(files) != set(cache):
        try:
            _ensure_state()
            cache_file.write_text(json.dumps({"v": INDEX_VERSION, "files": files}), encoding="utf-8")
        except OSError:
            pass
    return entries


# ------------------------------------------------------------------ matching
_ratio = None


def fuzzy(a: str, b: str) -> float:
    global _ratio
    if len(a) < 4 or len(b) < 4 or a[0] != b[0] or abs(len(a) - len(b)) > 2:
        return 0.0
    if len(a) == len(b) and a[0] == b[0] and sorted(a) == sorted(b):
        return 0.9                                   # swapped letters: "taems" -> "teams"
    if _ratio is None:
        from difflib import SequenceMatcher
        _ratio = lambda x, y: SequenceMatcher(None, x, y).ratio()
    r = _ratio(a, b)
    return r if r >= 0.8 else 0.0


GENERIC_DF = 6   # a word shared by this many scripts ("open", "search" keyword...) is generic
QUESTION = frozenset("what whats which who whom whose how where tell show display".split())
POLITE = frozenset("please pls plz thanks thank kindly".split())
KEEP_END = frozenset("me it us him her them".split())   # "near me", "send it"
QUOTE_RE = re.compile(r'"([^"]+)"|\u201c([^\u201d]+)\u201d')


def generic_sets(entries: list[dict]):
    from collections import Counter
    nd, kd = Counter(), Counter()
    for e in entries:
        nd.update(set(e["name_t"]))
        kd.update(set(e["kw_t"]) - set(e["name_t"]))
    return ({t for t, c in nd.items() if c >= GENERIC_DF},
            {t for t, c in kd.items() if c >= GENERIC_DF})


def score_entry(words: list[str], e: dict, gen):
    """Return (score, matched_flags, strong) for query words vs one script.
    Generic words are consumed but weigh little, so 'open' alone never decides."""
    gn, gk = gen
    total, flags, name_hit, strong = 0.0, [], set(), False
    nt, kt, dt = e["name_t"], set(e["kw_t"]), set(e["desc_t"])
    for w in words:
        wt, matched, hit = 0.0, False, None
        if w in nt:
            wt, matched, hit = (0.5 if w in gn else 1.0), True, w
        elif w in kt:
            wt, matched = (0.3 if (w in gk or w in gn) else 0.9), True
        else:
            for t in nt:
                r = fuzzy(w, t) * 0.9
                if r > wt and t not in gn:
                    wt, hit = r, t
            for t in kt:
                r = fuzzy(w, t) * 0.8
                if r > wt and t not in gk:
                    wt, hit = r, None
            matched = wt >= 0.6
            if not matched:
                wt, hit = (0.1 if w in dt else 0.0), None
        if matched and wt > 0.5:
            strong = True
        total += wt
        flags.append(2 if hit else 1 if matched else 0)
        if hit:
            name_hit.add(hit)
    core = [t for t in nt if t not in gn]          # specific words in the script name
    cov = len(name_hit & set(core)) / len(core) if core else 0.0
    return total * (0.85 + 0.15 * cov), flags, strong


PATTERN_BONUS = 1.5
_pat_cache: dict = {}


def pattern_hit(patterns, query):
    for p in patterns:
        rx = _pat_cache.get(p)
        if rx is None:
            try:
                rx = _pat_cache[p] = re.compile(p, re.I)
            except re.error:
                rx = _pat_cache[p] = False
        if rx and rx.search(query):
            return True
    return False


def rank(query: str, entries: list[dict]):
    literals = [next(g for g in m.groups() if g) for m in QUOTE_RE.finditer(query)]
    raw = QUOTE_RE.sub(" ", query).split()
    idx = [(i, norm(r)) for i, r in enumerate(raw) if norm(r) and norm(r) not in FILLER]
    if not idx:
        idx = [(i, norm(r)) for i, r in enumerate(raw) if norm(r)]
    words = [n for _, n in idx]
    gen = generic_sets(entries)
    out = []
    for e in entries:
        s, flags, strong = score_entry(words, e, gen)
        if e.get("pat") and pattern_hit(e["pat"], query):
            s, strong = s + PATTERN_BONUS, True          # the phrase itself says what the task is
        if not strong or s < MIN_SCORE:
            continue
        need = 2 if e.get("raw") else 1      # rawargs: only drop words that matched the name
        used = {i for (i, _), f in zip(idx, flags) if f >= need}
        if e.get("raw") == 2:
            used = set()                     # rawargs: full -> the task reads the whole sentence
        args = [r for i, r in enumerate(raw) if i not in used]
        full = e.get("raw") == 2
        if full:
            args = query.split()             # whole sentence, quotes left where the user put them
        lead = POLITE if e.get("raw") else FILLER | QUESTION    # free-text tasks keep their own words
        while args and (norm(args[0]) in lead or not norm(args[0])):
            args.pop(0)
        if e.get("raw"):                     # free text (messages, timers): only drop politeness at the end
            while args and (norm(args[-1]) in POLITE or not norm(args[-1])):
                args.pop()
        else:
            while args and ((norm(args[-1]) in FILLER and norm(args[-1]) not in KEEP_END) or not norm(args[-1])):
                args.pop()
        if args and not e["usage"] and not e["raw"] and 2 not in flags:
            s *= 0.7                         # keyword-only hit with unexplained words: weak
            if s < MIN_SCORE:
                continue
        out.append((s + 0.05 * e.get("prio", 0), e, args if full else args + literals))
    out.sort(key=lambda x: (-x[0], x[1]["name"]))
    return out


def resolve(query: str, entries: list[dict]):
    """Return ('ok', hit) | ('ambiguous', hits) | ('none', None)."""
    ranked = rank(query, entries)
    if not ranked:
        return "none", None
    top = ranked[0][0]
    close = [r for r in ranked if top - r[0] <= TIE_MARGIN]
    return ("ok", close[0]) if len(close) == 1 else ("ambiguous", close)


# ------------------------------------------------- your data: aliases, logs
RESERVED = {"list", "help", "history", "again", "repeat", "redo", "reindex", "selftest", "exit", "quit", "alias",
            "explain", "misses", "stats", "doctor", "tasks", "pack", "tips", "tip", "plugins", "plugin", "update", "setup",
            "web", "ui", "completion", "learn", "tour", "routines", "privacy"}


def _load_json(name: str, default):
    try:
        return json.loads((STATE / name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _save_json(name: str, data) -> None:
    _ensure_state()
    tmp = STATE / (name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, STATE / name)


def _append_line(name: str, line: str, keep: int = 300, limit: int = 300_000) -> None:
    try:
        _ensure_state()
        f = STATE / name
        with open(f, "a", encoding="utf-8") as fh:
            fh.write(line.replace("\n", " ") + "\n")
        if f.stat().st_size > limit:
            lines = f.read_text(encoding="utf-8").splitlines()[-keep:]
            f.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError:
        pass


def expand_alias(q: str) -> str:
    """'wa mom hi' -> 'send whatsapp to mom hi' when you saved  alias add wa = send whatsapp to."""
    al = _load_json("aliases.json", {})
    if not al:
        return q
    words = q.split()
    for n in (3, 2, 1):
        if len(words) >= n:
            key = " ".join(words[:n]).lower()
            if key in al:
                return (al[key] + " " + " ".join(words[n:])).strip()
    return q


def cmd_alias(q: str, entries: list[dict]) -> int:
    rest = q[5:].strip()
    low = rest.lower()
    al = _load_json("aliases.json", {})
    if low in {"", "list", "show"}:
        if not al:
            print("No aliases yet. Example:  alias add wa = send whatsapp to")
        for k, v in sorted(al.items()):
            print(f"  {k:<14} = {v}")
        return 0
    if low == "export":
        if not al:
            print("You have no aliases yet.")
            return 1
        dst = Path.cwd() / "jeeg-aliases.json"
        if dst.exists():
            print(f"{dst} already exists; move it first.")
            return 1
        dst.write_text(json.dumps({"jeeg": 1, "kind": "aliases", "aliases": al}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {len(al)} alias(es) to {dst}. Others can add them with:  alias import jeeg-aliases.json")
        return 0
    if low.startswith("import "):
        src = Path(rest[7:].strip().strip("\"'")).expanduser()
        try:
            if not src.is_file() or src.stat().st_size > 100_000:
                raise ValueError("file not found or too large")
            data = json.loads(src.read_text(encoding="utf-8"))
            if data.get("kind") != "aliases" or not isinstance(data.get("aliases"), dict):
                raise ValueError("not a JeeG aliases file")
        except (OSError, ValueError, UnicodeDecodeError, AttributeError) as ex:
            print(f"Could not import: {ex}.")
            return 1
        added, skipped = 0, []
        for k, v in list(data["aliases"].items())[:200]:
            k2, v2 = " ".join(str(k).lower().split()), " ".join(str(v).split())
            if (not k2 or not v2 or len(k2.split()) > 3 or len(v2) > 200 or k2 in RESERVED or k2.split()[0] in RESERVED
                    or re.search(r"[\x00-\x1f\x7f]", k2 + v2) or resolve(v2, entries)[0] == "none"):
                skipped.append(k2 or "?")
                continue
            al[k2] = v2
            added += 1
        _save_json("aliases.json", al)
        print(f"Added {added} alias(es)." + (f" Skipped {len(skipped)} that were not valid here: {', '.join(skipped[:8])}." if skipped else ""))
        return 0
    if low.startswith(("remove ", "delete ", "del ")):
        key = " ".join(rest.split()[1:]).lower()
        if key in al:
            del al[key]
            _save_json("aliases.json", al)
            print(f"Removed alias '{key}'.")
            return 0
        print(f"No alias named '{key}'.")
        return 1
    if low.startswith("add "):
        body = rest[4:].strip()
        key, sep, val = body.partition("=")
        if not sep:
            parts = body.split(None, 1)
            key, val = (parts[0], parts[1]) if len(parts) == 2 else ("", "")
        key, val = " ".join(key.lower().split()), " ".join(val.split())
        if not key or not val or len(key.split()) > 3:
            print("Usage: alias add <short word> = <what to run>     e.g.  alias add wa = send whatsapp to")
            return 1
        if key in RESERVED or key.split()[0] in RESERVED:
            print(f"'{key}' is a built-in command; choose another short word.")
            return 1
        st, _ = resolve(val, entries)
        if st == "none":
            print(f"'{val}' does not match any task, so the alias would never work. Check it with:  explain {val}")
            return 1
        al[key] = val
        _save_json("aliases.json", al)
        print(f"Saved: '{key}' now means '{val}'.")
        return 0
    print("Usage: alias add <short> = <task words> | alias list | alias remove <short> | alias export | alias import <file>")
    return 1


def cmd_explain(q: str, entries: list[dict]) -> int:
    phrase = q[7:].strip()
    if not phrase:
        print("Usage: explain <what you would type>")
        return 1
    shown = expand_alias(phrase)
    if shown != phrase:
        print(f"alias    -> {shown}")
    ranked = rank(shown, entries)
    if not ranked:
        print("No task matches. (Fallbacks: maths-looking text goes to the calculator, 'open <site.com>' opens the website, 'open <app>' tries to launch the app.)")
        return 1
    top = ranked[0][0]
    for i, (sc, e, args) in enumerate(ranked[:6]):
        tag = "  <- would run" if i == 0 and (len(ranked) == 1 or top - ranked[1][0] > TIE_MARGIN) else "  <- tied (menu)" if top - sc <= TIE_MARGIN else ""
        print(f"  {sc:5.2f}  {e['name'].replace('_', ' '):<24} args: {' '.join(args) or '-'}{tag}")
    return 0



def active(entries: list[dict]) -> list[dict]:
    """Entries minus categories you switched off with  pack off <category>."""
    off = set(_load_json("disabled.json", []))
    return [e for e in entries if e["cat"] not in off] if off else entries


def cmd_plugins(entries: list[dict]) -> int:
    d = STATE / "plugins"
    mine = [e for e in entries if Path(e["path"]).resolve().parent == d.resolve()] if d.is_dir() else []
    print(f"Plugin folder: {d}")
    print("Put extra task scripts there (same header format as the built-in ones) and they are found automatically.")
    print("Plugins are ordinary Python programs that run with your permissions: only add ones you trust.")
    if not mine:
        print("No plugins installed.")
    for e in sorted(mine, key=lambda x: x["name"]):
        print(f"  {e['name'].replace('_', ' '):<24}{e['desc'][:70]}")
    return 0


def cmd_pack(q: str, entries: list[dict]) -> int:
    parts = q.split()
    cats: dict[str, int] = {}
    for e in entries:
        cats[e["cat"]] = cats.get(e["cat"], 0) + 1
    off = set(_load_json("disabled.json", []))
    sub = parts[1].lower() if len(parts) > 1 else "list"
    if sub == "list":
        for c in sorted(cats):
            print(f"  {'off' if c in off else 'on ':<4} {c:<14}{cats[c]:>3} tasks")
        print("Switch one with:  pack off <category>   /   pack on <category>")
        return 0
    if sub in {"on", "off"} and len(parts) > 2:
        want = parts[2].lower()
        if want == "all" and sub == "on":
            _save_json("disabled.json", [])
            print("All categories are on.")
            return 0
        if want not in cats:
            print(f"No category '{want}'. Type 'pack list' to see them.")
            return 1
        if sub == "off":
            if len(off | {want}) >= len(cats):
                print("At least one category must stay on.")
                return 1
            off.add(want)
        else:
            off.discard(want)
        _save_json("disabled.json", sorted(off))
        print(f"{want}: {'off' if sub == 'off' else 'on'} ({cats[want]} tasks).")
        return 0
    print("Usage: pack list | pack off <category> | pack on <category> | pack on all")
    return 1


def cmd_tips(entries: list[dict]) -> int:
    import random
    used = set()
    try:
        for l in (STATE / "log.jsonl").read_text(encoding="utf-8").splitlines():
            try:
                used.add(json.loads(l)["s"])
            except (ValueError, KeyError):
                pass
    except OSError:
        pass
    fresh = [e for e in entries if e["name"] not in used and not e["confirm"] and e["desc"]]
    if not fresh:
        print("You have tried every task that is safe to suggest. Type 'list' to browse.")
        return 0
    e = random.choice(fresh)
    print(f"Try:  {e['name'].replace('_', ' ')}   [{e['cat']}]")
    print(f"      {e['desc']}")
    if e["usage"]:
        print(f"      usage: {e['usage']}")
    return 0


def closest(query: str, entries: list[dict], n: int = 3) -> list[dict]:
    """Tasks that share words with the query or look like it, best first."""
    import difflib
    qt = set(norm_list(query))
    q = query.lower().strip()
    scored = []
    for e in entries:
        name = e["name"].replace("_", " ")
        s = difflib.SequenceMatcher(None, q, name).ratio()
        pool = set(e["name_t"]) | set(e["kw_t"]) | set(e["desc_t"])
        s += 0.25 * len(qt & pool)
        if s > 0.45:
            scored.append((s, e))
    scored.sort(key=lambda x: -x[0])
    return [e for _, e in scored[:n]]


def nudge_backup() -> None:
    """Once a day, mention a backup if you have personal data and have not exported it for 30 days."""
    try:
        mine = [f for f in STATE.iterdir() if f.name not in {"index.json", "log.jsonl", "history.jsonl", "misses.log",
                                                              "last_backup.json", "nudge.json", "disabled.json"} and f.is_file()]
        if not mine:
            return
        today = time.strftime("%Y-%m-%d")
        if _load_json("nudge.json", {}).get("d") == today:
            return
        last = _load_json("last_backup.json", {}).get("t")
        days = (time.time() - last) / 86400 if last else None
        if days is None or days > 30:
            _save_json("nudge.json", {"d": today})
            print("Tip: " + ("your data has never been backed up." if days is None else f"your last backup was {int(days)} days ago.") + "  Type: export data")
    except OSError:
        pass


def log_run(e: dict, rc: int, dt: float) -> None:
    _append_line("log.jsonl", json.dumps({"t": int(time.time()), "s": e["name"], "rc": rc, "dt": round(dt, 2)}))


def log_miss(query: str, why: str) -> None:
    _append_line("misses.log", f"{time.strftime('%Y-%m-%d %H:%M')}\t{why}\t{query}", keep=200, limit=100_000)


def cmd_misses(sub: str = "") -> int:
    f = STATE / "misses.log"
    if sub == "clear":
        try:
            f.unlink()
        except OSError:
            pass
        print("Cleared the list of missed phrases.")
        return 0
    try:
        lines = f.read_text(encoding="utf-8").splitlines()
    except OSError:
        lines = []
    if sub == "export":
        if not lines:
            print("Nothing missed so far, so there is nothing to export.")
            return 1
        dst = Path.cwd() / "jeeg-misses.txt"
        if dst.exists():
            print(f"{dst} already exists; move it first.")
            return 1
        rows = [l.split("\t")[-1] for l in lines[-100:]]
        dst.write_text("Phrases JeeG did not understand (newest last).\nREAD AND EDIT BEFORE SHARING: remove anything personal such as names or numbers.\n"
                       "Share them as a GitHub issue ('A phrase JeeG did not understand') so they can be taught.\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
        print(f"Wrote {len(rows)} phrase(s) to {dst}. Nothing was sent anywhere; check the file, then share what you are comfortable with.")
        return 0
    if not lines:
        print("Nothing missed so far.")
        return 0
    print("Phrases that matched nothing (or were ambiguous). Teach one with:  alias add <short> = <task words>")
    print("To help improve JeeG: 'misses export' writes them to a file you can review and share; 'misses clear' empties the list.")
    for l in lines[-20:]:
        print("  " + l.replace("\t", "  "))
    return 0


def cmd_stats() -> int:
    from collections import Counter
    rows = []
    try:
        for l in (STATE / "log.jsonl").read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(l))
            except ValueError:
                continue
    except OSError:
        pass
    if not rows:
        print("No runs recorded yet.")
        return 0
    cnt = Counter(r["s"] for r in rows)
    fails = Counter(r["s"] for r in rows if r.get("rc"))
    print(f"{len(rows)} recent runs, {sum(fails.values())} failed. Most used:")
    for name, n in cnt.most_common(10):
        ts = [r["dt"] for r in rows if r["s"] == name]
        print(f"  {name.replace('_', ' '):<24}{n:>4}x   avg {sum(ts) / len(ts):.2f}s" + (f"   {fails[name]} failed" if fails[name] else ""))
    often = [(nm, fails[nm], cnt[nm]) for nm in cnt if cnt[nm] >= 3 and fails[nm] / cnt[nm] >= 0.5]
    if often:
        print("Often failing (check these first):")
        for nm, f_, c_ in sorted(often, key=lambda x: -x[1]):
            print(f"  {nm.replace('_', ' '):<24}{f_} of {c_} runs failed")
    return 0


def cmd_doctor(dirs, entries: list[dict]) -> int:
    ok = True

    def line(good: bool, text: str, fatal: bool = True) -> None:
        nonlocal ok
        print(("  ok    " if good else ("  FAIL  " if fatal else "  note  ")) + text)
        ok = ok and (good or not fatal)
    line(sys.version_info >= (3, 9), f"Python {sys.version.split()[0]} (needs 3.9 or newer)")
    line(True, f"JeeG {__version__} on {sys.platform}")
    line(bool(entries), f"{len(entries)} tasks from {', '.join(str(d) for d in dirs)}")
    try:
        _ensure_state()
        t = STATE / ".write_test"
        t.write_text("x")
        t.unlink()
        line(True, f"data folder writable: {STATE}")
    except OSError as ex:
        line(False, f"cannot write to data folder {STATE}: {ex}")
    bad = [e["name"] for e in entries if e["path"].endswith(".py") and not os.access(e["path"], os.R_OK)]
    line(not bad, "all scripts readable" if not bad else f"unreadable scripts: {', '.join(bad[:5])}")
    for tool, what in (("git", "git tasks"), ("ffmpeg", "video/audio tasks"), ("node", "JavaScript scripts")):
        line(bool(shutil.which(tool)), f"{tool} {'found' if shutil.which(tool) else 'not found'} (needed for {what})", fatal=False)
    for mod, what in (("PIL", "picture tasks: pip install pillow"), ("pypdf", "PDF tasks: pip install pypdf"),
                      ("qrcode", "QR codes: pip install qrcode[pil]"), ("psutil", "extra system detail: pip install psutil")):
        try:
            __import__(mod)
            line(True, f"{mod} installed")
        except ImportError:
            line(False, f"{mod} not installed ({what})", fatal=False)
    try:
        import socket
        socket.create_connection(("1.1.1.1", 53), timeout=2).close()
        line(True, "internet reachable")
    except OSError:
        line(False, "internet not reachable (online tasks will say so)", fatal=False)
    print("Everything required is fine." if ok else "Some required checks failed - see FAIL lines above.")
    return 0 if ok else 1


SYNONYMS = {"mail": "email", "mails": "email", "gmail": "gmail", "pic": "picture", "pics": "picture", "img": "image", "imgs": "image",
            "vid": "video", "vids": "video", "pwd": "password", "passwd": "password", "pass": "password", "calc": "calculator",
            "bday": "birthday", "bdays": "birthday", "txt": "text", "msg": "message", "msgs": "message", "doc": "document",
            "docs": "documents", "cal": "calendar", "mins": "minutes", "min": "minutes", "hrs": "hours", "temp": "temperature",
            "info": "information", "config": "settings", "wifi": "wifi", "wi-fi": "wifi", "ip": "ip", "sys": "system",
            "mem": "memory", "ram": "memory", "dl": "downloads", "dls": "downloads", "app": "app", "apps": "programs",
            "shot": "screenshot", "ss": "screenshot", "snap": "screenshot", "notes": "note", "remember": "remind",
            "alarm": "alarm", "tv": "video", "tablet": "medicine", "pill": "medicine", "pills": "medicine"}


def apply_synonyms(query: str) -> str:
    """Last-chance rewrite of short forms ('mail' -> 'email'); only used when nothing matched at all."""
    return " ".join(SYNONYMS.get(w, w) for w in query.lower().split())


def cmd_doctor_fix(dirs) -> int:
    """Repair the usual problems: damaged data files, stray temp files, dead reminders, open permissions, stale index."""
    fixed = 0
    _ensure_state()
    for f in sorted(STATE.glob("*.json")):
        try:
            json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            bad = f.with_suffix(".json.bad")
            n = 1
            while bad.exists():
                bad = f.with_suffix(f".json.bad{n}")
                n += 1
            f.rename(bad)
            print(f"  fixed  {f.name} was damaged; moved to {bad.name} so JeeG can start fresh")
            fixed += 1
    for f in list(STATE.glob("*.tmp")) + list(STATE.glob(".lib_*.py")):
        try:
            f.unlink()
            print(f"  fixed  removed leftover file {f.name}")
            fixed += 1
        except OSError:
            pass
    try:
        rem = json.loads((STATE / "reminders.json").read_text(encoding="utf-8"))
        live = []
        for r in rem:
            try:
                os.kill(int(r["pid"]), 0) if os.name == "posix" else None
                live.append(r)
            except (OSError, KeyError, ValueError, TypeError):
                pass
        if len(live) != len(rem):
            (STATE / "reminders.json").write_text(json.dumps(live), encoding="utf-8")
            print(f"  fixed  removed {len(rem) - len(live)} finished reminder(s) from the list")
            fixed += 1
    except (OSError, ValueError, TypeError):
        pass
    if os.name == "posix":
        try:
            if STATE.stat().st_mode & 0o077:
                STATE.chmod(0o700)
                print("  fixed  made your data folder private to you")
                fixed += 1
        except OSError:
            pass
    try:
        (STATE / "index.json").unlink()
        print("  fixed  rebuilt the task index")
        fixed += 1
    except OSError:
        pass
    load_index(dirs, rebuild=True)
    print(f"Done. {fixed} thing(s) repaired." if fixed else "Nothing needed repairing.")
    return 0


def did_you_mean(query: str, entries: list[dict]) -> list[str]:
    import difflib
    out = []
    vocab = sorted({t for e in entries for t in e["name_t"] + e["kw_t"] if len(t) > 2})
    words = query.lower().split()
    vs = set(vocab)
    fixed = [w if (norm(w) in vs or not w.isalpha() or len(w) < 3)
             else (difflib.get_close_matches(norm(w), vocab, n=1, cutoff=0.8) or [w])[0] for w in words]
    if fixed != words and all(norm(w) in vs or not w.isalpha() or len(w) < 3 for w in fixed):   # "opne youtub" -> "open youtube"
        cand = " ".join(fixed)
        st, hit = resolve(cand, entries)
        if st == "ok":
            out.append(cand)
    names = [e["name"].replace("_", " ") for e in entries]
    out += [n for n in difflib.get_close_matches(query.lower().strip(), names, n=3, cutoff=0.6) if n not in out]
    return out[:3]


# ----------------------------------------------------------------- execution
def history_add(query: str, name: str, private: bool = False) -> None:
    try:
        _ensure_state()
        f = STATE / "history.jsonl"
        with open(f, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"t": int(time.time()), "q": "(private - not saved)" if private else query, "s": name}) + "\n")
        if f.stat().st_size > 200_000:
            lines = f.read_text(encoding="utf-8").splitlines()[-300:]
            f.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError:
        pass


def history_read(n: int = 15) -> list[dict]:
    try:
        lines = (STATE / "history.jsonl").read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out = []
    for ln in lines[-n:]:
        try:
            out.append(json.loads(ln))
        except ValueError:
            pass
    return out


def run_entry(e: dict, args: list[str], opt: dict) -> int:
    path = Path(e["path"])
    cmd = RUNNERS[path.suffix.lower()](path) + args
    label = e["name"].replace("_", " ")
    if shutil.which(cmd[0]) is None and not os.path.isabs(cmd[0]):
        print(f"!! {label}: '{cmd[0]}' is not installed or not on PATH.")
        return 1
    if opt["dry"]:
        print(f"[dry-run] {' '.join(cmd)}")
        return 0
    safe_preview = any(a.lower() in {"preview", "dry-run", "dryrun"} for a in args)
    if e["confirm"] and not opt["yes"] and not safe_preview:
        if not sys.stdin.isatty() or opt.get("quiet"):
            print(f"!! '{label}' needs confirmation; re-run with --yes.")
            return 3
        if input(f"Run '{label}'? [y/N] ").strip().lower() not in {"y", "yes"}:
            print("Cancelled.")
            return 3
    if opt.get("quiet"):                      # --json / --output: capture what the task prints, no headers
        t0 = time.perf_counter()
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=opt["timeout"], stdin=subprocess.DEVNULL)
            rc, text = r.returncode, (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired:
            rc, text = 1, f"{label} timed out after {opt['timeout']}s.\n"
        except OSError as ex:
            rc, text = 1, f"could not start {label}: {ex}\n"
        dt = time.perf_counter() - t0
        log_run(e, rc, dt)
        opt.setdefault("_tasks", []).append({"name": e["name"], "args": list(args), "exit": rc, "seconds": round(dt, 3)})
        sys.stdout.write(text if text.endswith("\n") or not text else text + "\n")
        return 0 if rc == 0 else 1
    print(f">> {label}" + (f"  ({' '.join(args)})" if args else ""))
    t0 = time.perf_counter()
    try:
        rc = subprocess.run(cmd, timeout=opt["timeout"]).returncode
    except subprocess.TimeoutExpired:
        print(f"!! {label} timed out after {opt['timeout']}s.")
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 1
    except OSError as ex:
        print(f"!! could not start {label}: {ex}")
        return 1
    dt = time.perf_counter() - t0
    log_run(e, rc, dt)
    print(f"{'ok' if rc == 0 else 'failed (exit %d)' % rc} in {dt:.2f}s")
    return 0 if rc == 0 else 1


def show_menu(hits) -> list:
    hits = hits[:MENU_MAX]
    for i, (_, e, _) in enumerate(hits, 1):
        d = f" - {e['desc']}" if e["desc"] else ""
        print(f"  {i}. {e['name'].replace('_', ' ')}{d}")
    return hits


MATH_WORDS = frozenset("""plus minus times divided by multiplied over of percent power to the squared
cubed mod sqrt square root x pi e what whats is sin cos tan log ln abs factorial""".split())


def looks_like_math(q: str) -> bool:
    """'25 * 4', 'what is 15% of 200', '2 plus 2' -> True (no keyword needed)."""
    t = q.lower().strip().rstrip("?=")
    if not re.search(r"\d", t) or not re.fullmatch(r"[\w\s.,+\-*/^()%x\u00d7\u00f7=?]+", t):
        return False
    alpha = re.findall(r"[a-z]+", t)
    ops = re.search(r"[+\-*/^%\u00d7\u00f7]", t) or any(a in MATH_WORDS - {"what", "whats", "is", "the", "to", "of", "by"} for a in alpha)
    return bool(ops) and all(a in MATH_WORDS for a in alpha)


def run_query(query: str, entries: list[dict], opt: dict) -> int:
    parts = [p for p in SPLIT_RE.split(query) if p.strip()]
    if len(parts) > 1:                       # "open gmail and open calendar"
        plan = []
        for p in parts:
            st, hit = resolve(p, entries)
            if st != "ok" or hit[0] < SPLIT_MIN_SCORE or hit[1].get("raw"):
                plan = None                  # unclear part, or a free-text task: the 'and' belongs to the text
                break
            plan.append((p, hit))
        if plan and len({h[1]["name"] for _, h in plan}) < len(plan):
            plan = None                      # same task twice => it is one sentence, not two tasks
        if plan:
            rc = 0
            for p, (_, e, args) in plan:
                history_add(p, e["name"], e.get("private"))
                rc = max(rc, run_entry(e, args, opt))
            return rc

    st, hit = resolve(query, entries)
    if st == "none":
        words = query.split()
        calc = next((e for e in entries if e["name"] == "calculate"), None)
        if calc and looks_like_math(query):
            history_add(query, calc["name"])
            return run_entry(calc, words, opt)
        site = next((e for e in entries if e["name"] == "open_website"), None)
        if (site and len(words) >= 2 and words[0].lower() in {"open", "go", "visit", "browse", "launch"}
                and re.fullmatch(r"(https?://)?[\w\-]+(\.[\w\-]+)+(:\d+)?([/?#]\S*)?", words[-1])):
            history_add(query, site["name"])        # "open github.com"
            return run_entry(site, [words[-1]], opt)
        fb = next((e for e in entries if e["name"] == "open_app"), None)
        if fb and len(words) >= 2 and words[0].lower() in {"open", "launch", "start", "run"}:
            history_add(query, fb["name"])      # "open vlc" -> try launching an installed app
            return run_entry(fb, words[1:], opt)
        alt = apply_synonyms(query)
        if alt != query.lower().strip():
            st2, hit2 = resolve(alt, entries)
            if st2 == "ok":
                print(f"(understood as: {alt})")
                return run_query(alt, entries, opt)
        near = did_you_mean(query, entries)
        log_miss(query, "no match")
        if near and sys.stdin.isatty() and not opt.get("quiet"):
            ans = input(f"No exact match. Did you mean '{near[0]}'? [y/N] ").strip().lower()
            if ans in {"y", "yes"}:
                if len(query.split()) <= 3 and query.lower() not in RESERVED:
                    al = _load_json("aliases.json", {})
                    al[query.lower().strip()] = near[0]
                    _save_json("aliases.json", al)
                    print(f"(remembered: '{query.strip().lower()}' = '{near[0]}'; undo with: alias remove {query.strip().lower()})")
                return run_query(near[0], entries, opt)
            return 3
        print("No matching task." + (f" Did you mean: {', '.join(near)}?" if near else "") + " Type 'list' to see what is available.")
        cl = [e for e in closest(query, entries) if e["name"].replace("_", " ") not in near]
        if cl:
            print("Closest tasks:")
            for e in cl:
                print(f"  {e['name'].replace('_', ' '):<24}{e['usage'] or e['desc']}")
        return 1
    if st == "ok":
        _, e, args = hit
        history_add(query, e["name"], e.get("private"))
        return run_entry(e, args, opt)

    print("More than one task fits:")
    hits = show_menu(hit)
    if not sys.stdin.isatty():
        log_miss(query, "ambiguous")
        return 2
    pick = input("Pick a number (Enter to cancel): ").strip()
    if pick.isdigit() and 1 <= int(pick) <= len(hits):
        _, e, args = hits[int(pick) - 1]
        history_add(query, e["name"], e.get("private"))
        return run_entry(e, args, opt)
    print("Cancelled.")
    return 3


# -------------------------------------------------------------- housekeeping
def cmd_list(entries: list[dict], cat: str = "") -> None:
    groups: dict[str, list[dict]] = {}
    for e in entries:
        if not cat or cat.lower() in e["cat"]:
            groups.setdefault(e["cat"], []).append(e)
    if not groups:
        print("No tasks found.")
        return
    for c in sorted(groups):
        print(f"\n[{c}]")
        for e in groups[c]:
            flag = (" *" if e["confirm"] else "") + (" [online]" if e.get("net") else "")
            d = f"  {e['desc']}" if e["desc"] else ""
            print(f"  {e['name'].replace('_', ' '):<24}{d}{flag}")
    print(f"\n{len(entries)} tasks. (* asks before running, [online] can use the internet; see 'privacy')")


def cmd_privacy(entries: list[dict]) -> int:
    online = sorted((e for e in entries if e.get("net")), key=lambda e: e["name"])
    print(f"Your data lives only in {STATE} (readable only by you). JeeG has no account and no telemetry, and nothing runs in the background except reminders you set yourself.")
    print(f"{len(entries) - len(online)} of {len(entries)} tasks never touch the network. These {len(online)} can, and only when you run them:")
    for e in online:
        print(f"  {e['name'].replace('_', ' '):<22}{e['desc'][:70]}")
    print("Tasks named 'open <site>' only ask your own browser to open that site; JeeG itself sends nothing.")
    print("Tasks from plugins are not covered by this list: read a plugin before you install it.")
    return 0


def cmd_selftest(entries: list[dict]) -> int:
    bad = 0
    for e in entries:
        problems = []
        if not e["desc"]:
            problems.append("missing '# desc:'")
        if not e["kw_t"]:
            problems.append("missing '# keywords:'")
        for pt in e.get("pat", []):
            try:
                re.compile(pt)
            except re.error as ex:
                problems.append(f"bad pattern {pt!r}: {ex}")
        st, hit = resolve(e["name"].replace("_", " "), entries)
        got = hit[1]["name"] if st == "ok" else st
        if got != e["name"]:
            problems.append(f"name resolves to {got!r}")
        p = Path(e["path"])
        if p.suffix == ".py":
            try:
                compile(p.read_text(encoding="utf-8"), str(p), "exec")
            except SyntaxError as ex:
                problems.append(f"syntax error line {ex.lineno}")
        if problems:
            bad += 1
            print(f"FAIL {e['name']}: " + "; ".join(problems))
    print(f"selftest: {len(entries) - bad}/{len(entries)} ok")
    return 1 if bad else 0


def handle(line: str, dirs, opt) -> int | None:
    """Return exit code, or None to quit."""
    q = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", line).strip()      # no control or terminal-escape characters
    if len(q) > 2000:
        print("That line is too long (over 2000 characters). Please shorten it.")
        return 1
    low = q.lower()
    if not q:
        return 0
    if low in {"exit", "quit", "q"}:
        return None
    all_entries = load_index(dirs, rebuild=(low == "reindex"))
    entries = active(all_entries)
    if low == "pack" or low.startswith("pack "):
        return cmd_pack(q, all_entries)
    if low in {"tips", "tip"}:
        return cmd_tips(entries)
    if low.startswith(("plugin ", "plugins ")) or low in {"plugins", "plugin"}:
        import jeeg_cmds
        return jeeg_cmds.cmd_plugin(q.split(None, 1)[1] if " " in q else "list", STATE / "plugins", all_entries, parse_header,
                                    opt.get("yes", False))
    if re.fullmatch(r"(?:(?:jeeg\s+)?(?:update|upgrade)(?:\s+jeeg)?(?:\s+now)?|(?:update|upgrade)\s+now)", low):
        import jeeg_cmds
        return jeeg_cmds.cmd_update(low, HERE, __version__, opt.get("yes", False))
    if low in {"setup", "setup jeeg", "jeeg setup", "setup wizard", "first run"}:
        import jeeg_cmds
        return jeeg_cmds.cmd_setup(HERE, STATE, all_entries, opt.get("yes", False))
    if low in {"learn", "tour", "tutorial", "jeeg tour", "learn jeeg"}:
        import jeeg_cmds
        def _run(cmd_line: str) -> None:
            import shlex
            subprocess.run([sys.executable, str(HERE / "jeeg.py")] + shlex.split(cmd_line), env=dict(os.environ, JEEG_HOME=str(STATE)))
        return jeeg_cmds.cmd_learn(_run, sys.stdin.isatty() and sys.stdout.isatty())
    if re.match(r"routines\s+(export|import)\b", low):
        import jeeg_cmds
        return jeeg_cmds.cmd_routines_io(q.split(None, 1)[1], STATE, opt.get("yes", False))
    if low == "doctor fix" or low == "doctor --fix":
        return cmd_doctor_fix(dirs)
    if low.startswith("completion"):
        import jeeg_cmds
        parts = low.split()
        if len(parts) == 1:
            print(jeeg_cmds.COMPLETION_HELP)
            return 0
        return jeeg_cmds.cmd_completion(parts[1], all_entries)
    m = re.fullmatch(r"(?:web|ui|web page|web ui)(?:\s+(\d{4,5}))?", low)
    if m:
        import jeeg_cmds
        return jeeg_cmds.serve(HERE, STATE, int(m.group(1) or 8765))
    if low == "alias" or low.startswith("alias "):
        return cmd_alias(q, entries)
    if low == "explain" or low.startswith("explain "):
        return cmd_explain(q, entries)
    if low in {"privacy", "what goes online", "network tasks"}:
        return cmd_privacy(entries)
    if low in {"misses", "misses export", "misses clear"}:
        return cmd_misses(low.split()[1] if " " in low else "")
    if low == "stats":
        return cmd_stats()
    if low == "doctor":
        return cmd_doctor(dirs, all_entries)
    if low == "reindex":
        print(f"Indexed {len(entries)} tasks.")
        return 0
    cats = {e["cat"] for e in entries}
    if low in {"list", "help", "?", "tasks"} or (low.startswith("list ") and low[5:].strip() in cats):
        st, hit = resolve(q, entries) if low != "list" else ("none", None)
        if not (st == "ok" and "list" in hit[1]["name_t"]):     # "list links" is a task; "list web" is a category
            cmd_list(entries, q[5:].strip() if low.startswith("list ") else "")
            return 0
    if low == "history":
        for h in history_read():
            print(f"  {time.strftime('%m-%d %H:%M', time.localtime(h['t']))}  {h['q']}  -> {h['s']}")
        return 0
    if low == "selftest":
        return cmd_selftest(all_entries)
    if low in {"again", "repeat", "redo"}:
        last = history_read(1)
        if not last:
            print("Nothing to repeat yet.")
            return 1
        print(f"Repeating: {last[0]['q']}")
        return run_query(last[0]["q"], entries, opt)
    return run_query(expand_alias(q), entries, opt)


def offer_tour(dirs, opt) -> None:
    """The very first time JeeG starts in a terminal, offer the guided tour once."""
    marker = STATE / ".toured"
    try:
        if marker.exists() or not (sys.stdin.isatty() and sys.stdout.isatty()):
            return
        _ensure_state()
        marker.write_text("1", encoding="utf-8")                    # ask only once, whatever the answer
        ans = input("First time here? Take the 1-minute tour? [Y/n] ").strip().lower()
        if ans in {"", "y", "yes"}:
            handle("learn", dirs, opt)
    except (OSError, EOFError, KeyboardInterrupt):
        print()


def run_captured(line: str, dirs, opt) -> int:
    """--json / --output: run one line, collect the text, and write it as JSON or to a file."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = handle(line, dirs, opt)
    rc = 0 if rc is None else rc
    text = buf.getvalue()
    if opt["json"]:
        text = json.dumps({"jeeg": __version__, "input": line, "tasks": opt.get("_tasks", []), "exit": rc, "output": text.rstrip("\n")},
                          indent=2, ensure_ascii=False) + "\n"
    if opt["out"]:
        dest = Path(opt["out"]).expanduser()
        try:
            if "\0" in str(dest) or dest.is_dir() or not dest.parent.is_dir():
                raise OSError("that is not a usable file path")
            if dest.exists():
                raise OSError(f"{dest} already exists (JeeG never overwrites; choose another name)")
            if len(text) > 5_000_000:
                raise OSError("the output is too large")
            with open(dest, "x", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
        except OSError as ex:
            print(f"Could not save the output: {ex}")
            return 1
        print(f"Saved to {dest}")
    else:
        sys.stdout.write(text)
    return rc


def main(argv: list[str]) -> int:
    opt = {"yes": False, "dry": False, "timeout": None, "json": False, "out": None, "quiet": False}
    cli_dirs, words, i = [], [], 0
    while i < len(argv):
        a = argv[i]
        if a in {"-y", "--yes"}:
            opt["yes"] = True
        elif a == "--dry-run":
            opt["dry"] = True
        elif a == "--json":
            opt["json"] = opt["quiet"] = True
        elif a == "--output" and i + 1 < len(argv):
            i += 1
            opt["out"] = argv[i]
            opt["quiet"] = True
        elif a == "--dir" and i + 1 < len(argv):
            i += 1
            cli_dirs.append(argv[i])
        elif a == "--timeout" and i + 1 < len(argv):
            i += 1
            try:
                opt["timeout"] = float(argv[i])
            except ValueError:
                print("--timeout needs a number of seconds.")
                return 1
        elif a in {"-h", "--help"}:
            print(__doc__)
            return 0
        elif a == "--version":
            print(f"JeeG {__version__}")
            return 0
        else:
            words.append(a)
        i += 1

    dirs = script_dirs(cli_dirs)
    if not dirs:
        print("No scripts folder found. Create 'scripts' next to jeeg.py, "
              "or use --dir PATH / TASK_SCRIPTS_DIR.")
        return 1

    if words:
        if opt["quiet"]:
            return run_captured(" ".join(words), dirs, opt)
        rc = handle(" ".join(words), dirs, opt)
        return 0 if rc is None else rc
    if opt["quiet"]:
        print("--json and --output need a task, for example:  jeeg --json gst 2500 18")
        return 1

    try:
        import readline  # noqa: F401  (arrow-key history where available)
    except ImportError:
        pass
    n = len(load_index(dirs))
    print(f"JeeG {__version__} - {n} tasks. Say what to do ('list' for help, 'exit' to quit).")
    offer_tour(dirs, opt)
    nudge_backup()
    while True:
        try:
            line = input("task> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if handle(line, dirs, opt) is None:
            return 0


def cli() -> None:
    """Entry point for the pip-installed 'jeeg' command."""
    try:
        code = main(sys.argv[1:])
        sys.stdout.flush()
    except BrokenPipeError:                          # e.g.  jeeg list | head
        try:
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        except OSError:
            pass
        code = 0
    sys.exit(code)


if __name__ == "__main__":
    cli()
