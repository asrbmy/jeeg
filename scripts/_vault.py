"""Obsidian vault helpers: find the vault, find notes safely, plan edits, apply them with a backup, undo.
Edits never leave the vault, never touch hidden folders, never delete for good (removed notes go to the vault's .trash folder,
like Obsidian's own), and every change can be undone with `vault undo`."""
import difflib, json, os, re, shutil, time
from pathlib import Path
from _lib import data_dir, fail

MAX_OPS, MAX_TEXT, KEEP_BACKUPS = 20, 20000, 30
TRASH = object()


def vault_root():
    try: p = Path(json.loads((data_dir() / "vault.json").read_text())["path"])
    except (OSError, ValueError, KeyError): fail("No vault chosen yet. Say:  vault set   (or  vault set <folder>)")
    if not p.is_dir(): fail(f"The saved vault folder is missing: {p}. Say:  vault set <folder>")
    return p.resolve()


def notes(v):
    for d, dirs, files in os.walk(v, followlinks=False):
        dirs[:] = sorted(x for x in dirs if not x.startswith(".") and x != "node_modules")
        for f in sorted(files):
            p = Path(d) / f
            if f.lower().endswith(".md") and not p.is_symlink() and v.resolve() in p.resolve().parents: yield p   # links that lead outside are ignored


def find_note(v, name):
    name = str(name).strip().strip("[]").removesuffix(".md").replace("\\", "/")
    if not name: fail("Which note?")
    allp = list(notes(v))
    for p in allp:
        if str(p.relative_to(v)).removesuffix(".md").replace("\\", "/").lower() == name.lower(): return p
    hits = [p for p in allp if p.stem.lower() == name.lower()] or [p for p in allp if name.lower() in p.stem.lower()]
    if len(hits) == 1: return hits[0]
    if not hits: fail(f"No note called '{name}'.")
    fail("Several notes match: " + ", ".join(str(p.relative_to(v)) for p in hits[:8]) + ". Use more of the name.")


def new_target(v, name):
    rel = str(name).strip().strip("[]").replace("\\", "/").removesuffix(".md")
    if not rel or re.search(r"[<>:\"|?*\x00-\x1f]", rel) or any(p in ("", ".", "..") or p.startswith(".") for p in rel.split("/")):
        fail(f"'{name}' has characters or folders that are not allowed in a note name.")
    t = (v / (rel + ".md")).resolve()
    if v not in t.parents: fail("That note would be outside the vault.")
    return t


# ---- reading edit instructions (from an AI's answer or typed text)
def parse_ops(text):
    text = (text or "").strip()
    cands = [m.group(1) for m in re.finditer(r"```(?:jeeg|json|JSON)?[ \t]*\n(.*?)```", text, re.S)] + [text]
    a, b = text.find("["), text.rfind("]")
    if a >= 0 < b: cands.append(text[a:b + 1])
    a, b = text.find("{"), text.rfind("}")
    if a >= 0 < b: cands.append(text[a:b + 1])
    for c in cands:
        try: d = json.loads(c)
        except ValueError: continue
        if isinstance(d, dict): d = d.get("ops") if isinstance(d.get("ops"), list) else [d]
        if isinstance(d, list) and d and all(isinstance(x, dict) and "op" in x for x in d): return d
    fail("I could not find edit instructions. They should be a JSON list like:\n"
         '[{"op":"append","note":"Ideas","text":"buy milk"}]   (ops: new, append, prepend, insert_under, replace, remove_text, trash)')


def plan_ops(v, ops):
    """Check every instruction first. Returns (descriptions, changes) where changes = {path: new text or TRASH}. Nothing is written."""
    if len(ops) > MAX_OPS: fail(f"Too many changes at once ({len(ops)}); the limit is {MAX_OPS}.")
    state, desc = {}, []
    def cur(p):
        if p not in state: state[p] = p.read_text(encoding="utf-8") if p.exists() else None
        return state[p]
    for i, o in enumerate(ops, 1):
        op = str(o.get("op", "")).lower().replace("-", "_")
        where = f"change {i} ({op})"
        for k in ("text", "find", "with"):
            if k in o and not isinstance(o[k], str): fail(f"{where}: '{k}' must be text.")
            if k in o and len(o[k]) > MAX_TEXT: fail(f"{where}: '{k}' is too long (limit {MAX_TEXT} characters).")
        if op == "new":
            t = new_target(v, o.get("note", ""))
            if cur(t) is not None: fail(f"{where}: '{t.relative_to(v)}' already exists. Use append instead.")
            if not o.get("text", "").strip(): fail(f"{where}: no text.")
            state[t] = o["text"].rstrip("\n") + "\n"; desc.append(f"Make {t.relative_to(v)}")
            continue
        p = find_note(v, o.get("note", "")).resolve()
        if cur(p) is None or cur(p) is TRASH: fail(f"{where}: that note is no longer there.")
        s = cur(p)
        if op == "append":
            if not o.get("text", "").strip(): fail(f"{where}: no text.")
            state[p] = s.rstrip("\n") + "\n\n" + o["text"].strip("\n") + "\n"; desc.append(f"Add to the end of {p.relative_to(v)}")
        elif op == "prepend":
            if not o.get("text", "").strip(): fail(f"{where}: no text.")
            m = re.match(r"---\n.*?\n---\n", s, re.S)                      # keep front matter first
            head = m.group(0) if m else ""
            state[p] = head + o["text"].strip("\n") + "\n\n" + s[len(head):]; desc.append(f"Add to the start of {p.relative_to(v)}")
        elif op in ("replace", "remove_text"):
            f = o.get("find", "")
            if not f: fail(f"{where}: 'find' is empty.")
            n = s.count(f)
            if n == 0: fail(f"{where}: the text to change was not found in {p.relative_to(v)}: {f[:60]!r}")
            if n > 1 and not o.get("all"): fail(f"{where}: that text appears {n} times in {p.relative_to(v)}; give more of it, or add \"all\": true.")
            state[p] = s.replace(f, o.get("with", "") if op == "replace" else "") ; desc.append(("Change" if op == "replace" else "Remove text in") + f" {p.relative_to(v)}")
        elif op == "insert_under":
            h = str(o.get("heading", "")).strip().lstrip("#").strip()
            if not h or not o.get("text", "").strip(): fail(f"{where}: needs a heading and text.")
            lines = s.split("\n")
            idx = [i for i, l in enumerate(lines) if re.match(r"#{1,6}\s+" + re.escape(h) + r"\s*$", l, re.I)]
            if len(idx) != 1: fail(f"{where}: " + (f"no heading '{h}' in {p.relative_to(v)}" if not idx else f"the heading '{h}' appears {len(idx)} times in {p.relative_to(v)}"))
            lvl = len(re.match(r"#+", lines[idx[0]]).group(0))
            end = next((i for i in range(idx[0] + 1, len(lines)) if re.match(r"#{1,%d}\s" % lvl, lines[i])), len(lines))
            while end > idx[0] + 1 and not lines[end - 1].strip(): end -= 1
            lines[end:end] = [""] + o["text"].strip("\n").split("\n")
            state[p] = "\n".join(lines); desc.append(f"Add under '{h}' in {p.relative_to(v)}")
        elif op == "trash":
            state[p] = TRASH; desc.append(f"Move {p.relative_to(v)} to the vault's .trash folder")
        else:
            fail(f"{where}: unknown change type '{op}'. Use new, append, prepend, insert_under, replace, remove_text or trash.")
    originals = {}
    for p in state:
        originals[p] = p.read_text(encoding="utf-8") if p.exists() else None
    changes = {p: s for p, s in state.items() if s != originals[p]}
    return desc, changes, originals


def preview(v, changes, originals, lines=10):
    out = []
    for p, new in changes.items():
        rel = str(p.relative_to(v))
        if new is TRASH: out.append(f"--- {rel}\n  (moved to .trash)"); continue
        old = originals[p] or ""
        d = [l for l in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0) if not l.startswith(("---", "+++", "@@"))]
        out.append(f"--- {rel}" + ("  (new note)" if originals[p] is None else ""))
        out += ["  " + l[:140] for l in d[:lines]] + ([f"  ... and {len(d) - lines} more lines"] if len(d) > lines else [])
    return "\n".join(out)


def apply(v, changes, originals):
    """Write the planned changes. A copy of what was there is saved first, so `vault undo` can put it back."""
    stamp = f"{time.time_ns():020d}"                      # sorts oldest to newest
    b = v / ".jeeg-backup" / stamp
    b.mkdir(parents=True, exist_ok=True)
    man = []
    for p, new in changes.items():
        rel = str(p.relative_to(v)).replace("\\", "/")
        if originals[p] is not None:
            bp = b / "files" / rel; bp.parent.mkdir(parents=True, exist_ok=True); bp.write_text(originals[p], encoding="utf-8")
        man.append({"rel": rel, "existed": originals[p] is not None, "trashed": new is TRASH})
    (b / "manifest.json").write_text(json.dumps(man))
    for p, new in changes.items():
        if new is TRASH:
            t = v / ".trash" / (p.stem + "-" + time.strftime("%H%M%S") + ".md"); t.parent.mkdir(exist_ok=True)
            shutil.move(str(p), str(t)); continue
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + ".jeeg-tmp"); tmp.write_text(new, encoding="utf-8"); os.replace(tmp, p)
    old = sorted((v / ".jeeg-backup").iterdir())
    for d in old[:-KEEP_BACKUPS]: shutil.rmtree(d, ignore_errors=True)
    return stamp


def undo(v):
    root = v / ".jeeg-backup"
    done = sorted(root.iterdir()) if root.is_dir() else []
    if not done: fail("Nothing to undo.")
    b = done[-1]
    man = json.loads((b / "manifest.json").read_text())
    for m in man:
        p = (v / m["rel"]).resolve()
        if v not in p.parents: continue
        if m["existed"]:
            p.parent.mkdir(parents=True, exist_ok=True); p.write_text((b / "files" / m["rel"]).read_text(encoding="utf-8"), encoding="utf-8")
        elif p.exists(): p.unlink()
    shutil.rmtree(b, ignore_errors=True)
    return len(man)
