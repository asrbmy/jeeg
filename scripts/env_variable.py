# keywords: environment variable, env variable, permanent variable, persistent variable, add to path, add folder to path, setx
# desc: Save an environment variable for good (set env variable API_URL to https://x.com) or add a folder to PATH (add C:\tools to path). Add "preview" to see what would change. New terminals pick it up.
# category: system
# usage: set env variable NAME to VALUE | remove env variable NAME | add <folder> to path
# confirm: yes
# rawargs: full
# patterns: ^\s*(?:set|save|make)\s+(?:an?\s+|the\s+)?(?:(?:permanent|persistent)\s+)?(?:env(?:ironment)?\s+(?:var|variable)|(?:permanent|persistent)\s+variable)\s+\w+ ;; ^\s*(?:remove|unset|delete)\s+(?:the\s+)?env(?:ironment)?\s+(?:var|variable)\b ;; ^\s*add\s+.+\s+to\s+(?:my\s+|the\s+|user\s+)?path\b
# priority: 5
import os, re, shlex
from pathlib import Path
from _lib import MAC, WIN, args_text, fail

t = args_text().strip()
preview = bool(re.search(r"\b(?:preview|dry-run|dryrun)\b", t, re.I))
t = re.sub(r"\s*\b(?:preview|dry-run|dryrun)\b\s*$", "", t, flags=re.I).strip()
NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,63}$")
MARK = "# jeeg:{kind} {name}"


def profile_file():
    env = os.environ.get("JEEG_PROFILE_FILE")
    if env:
        return Path(env)
    shell = os.path.basename(os.environ.get("SHELL", ""))
    home = Path.home()
    if shell == "zsh" or MAC:
        return home / ".zshrc"
    return home / (".bashrc" if shell == "bash" else ".profile")


def rewrite_block(p, kind, name, line):
    """Replace (or remove, when line is None) the one two-line block JeeG owns for this name. Returns what happened."""
    old = p.read_text(encoding="utf-8") if p.exists() else ""
    mark = MARK.format(kind=kind, name=name)
    lines, out, i, had = old.splitlines(), [], 0, False
    while i < len(lines):
        if lines[i].strip() == mark:
            had = True
            i += 2
            continue
        out.append(lines[i])
        i += 1
    if line is not None:
        out += [mark, line]
    new = "\n".join(out).rstrip("\n") + ("\n" if out else "")
    if new != old:
        if p.exists():
            p.with_name(p.name + ".jeeg-backup").write_text(old, encoding="utf-8")
        p.write_text(new, encoding="utf-8")
    return had


def win_set(name, value):                              # per-user environment, the same place the System dialog edits
    import winreg, ctypes
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE) as k:
        if value is None:
            try:
                winreg.DeleteValue(k, name)
            except FileNotFoundError:
                pass
        else:
            try:
                kind = winreg.QueryValueEx(k, name)[1]
            except FileNotFoundError:
                kind = winreg.REG_EXPAND_SZ if name.upper() == "PATH" else winreg.REG_SZ
            winreg.SetValueEx(k, name, 0, kind, value)
    ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x1A, 0, "Environment", 2, 3000, None)


def win_get(name):
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            return winreg.QueryValueEx(k, name)[0]
    except FileNotFoundError:
        return ""


m = re.match(r"^(?:set|save|make)\s+(?:a\s+|the\s+)?(?:permanent\s+|persistent\s+)?(?:env(?:ironment)?\s+(?:var|variable)|(?:permanent|persistent)\s+variable)\s+(\S+?)\s*(?:=|to|as)\s*(.+)$", t, re.I | re.S)
if m:
    name, value = m.group(1), m.group(2).strip()
    if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    if not NAME.match(name):
        fail("A variable name uses letters, numbers and _ and cannot start with a number.")
    if name.upper() in {"PATH", "PATHEXT", "LD_PRELOAD", "LD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES", "DYLD_LIBRARY_PATH"}:
        fail(f"I will not set {name} like that. For PATH use:  add <folder> to path")
    if not value or len(value) > 2000 or re.search(r"[\x00-\x1f]", value):
        fail("The value is empty, too long, or has a line break.")
    if WIN:
        print(f"Would set {name} for your user (registry, Environment)." if preview else "")
        if not preview:
            win_set(name, value)
            print(f"Saved {name}. Open a new terminal to see it.")
    else:
        p = profile_file()
        line = f"export {name}={shlex.quote(value)}"
        print(f"{'Would add to' if preview else 'Adding to'} {p}:\n  {line}")
        if not preview:
            rewrite_block(p, "env", name, line)
            print(f"Saved {name}. Open a new terminal (or run: source {p}). A backup is next to the file.")
    raise SystemExit(0)
m = re.match(r"^(?:remove|unset|delete)\s+(?:the\s+)?env(?:ironment)?\s+(?:var|variable)\s+(\S+)\s*$", t, re.I)
if m:
    name = m.group(1)
    if not NAME.match(name):
        fail("A variable name uses letters, numbers and _.")
    if WIN:
        if not preview:
            win_set(name, None)
        print(f"{'Would remove' if preview else 'Removed'} {name} from your user environment.")
    else:
        p = profile_file()
        if preview:
            print(f"Would remove the block for {name} from {p} (only one that JeeG added).")
        elif rewrite_block(p, "env", name, None):
            print(f"Removed {name} from {p}.")
        else:
            fail(f"JeeG did not add {name} to {p}, so I left it alone.")
    raise SystemExit(0)
m = re.match(r"^add\s+(.+?)\s+to\s+(?:my\s+|the\s+|user\s+)?path\s*$", t, re.I | re.S)
if m:
    folder = Path(os.path.expanduser(m.group(1).strip().strip("\"'"))).resolve()
    if not folder.is_dir():
        fail(f"{folder} is not a folder that exists.")
    if re.search(r"[\x00-\x1f;:]", str(folder)) and not (WIN and re.fullmatch(r"[A-Za-z]:[\\/].*", str(folder)) and ";" not in str(folder)):
        fail("That folder name has characters that cannot go in PATH.")
    if WIN:
        cur = win_get("Path")
        parts = [x for x in cur.split(";") if x]
        if str(folder).lower() in [x.lower().rstrip("\\") for x in parts]:
            print("Already in your PATH.")
            raise SystemExit(0)
        print(f"{'Would add' if preview else 'Adding'} {folder} to your user PATH.")
        if not preview:
            win_set("Path", ";".join(parts + [str(folder)]))
            print("Done. Open a new terminal to use it.")
    else:
        p = profile_file()
        line = f"export PATH={shlex.quote(str(folder))}:\"$PATH\""
        print(f"{'Would add to' if preview else 'Adding to'} {p}:\n  {line}")
        if not preview:
            rewrite_block(p, "path", re.sub(r"[^A-Za-z0-9_.\-/]", "_", str(folder)), line)
            print(f"Done. Open a new terminal (or run: source {p}).")
    raise SystemExit(0)
fail("Try:  set env variable API_URL to https://example.com   |   remove env variable API_URL   |   add ~/tools to path")
