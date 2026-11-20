"""Share routines, aliases and variables as one file. Not a task."""
import json, re
from pathlib import Path
from _lib import args_text, fail, data_dir, var_all, var_save, output_dir
import _routine


def main(allowed):
    t = re.sub(r"^\s*kit\s*", "", args_text(), flags=re.I).strip()
    sub, _, body = t.partition(" "); sub, body = sub.lower(), body.strip().strip("\"'")
    NAME = re.compile(r"^[a-z][a-z0-9_]{1,40}$")
    def clean(pack):
        """Validate a kit from someone else. Returns (routines, aliases, vars, problems)."""
        if not isinstance(pack, dict) or pack.get("kind") != "kit":
            fail("That is not a JeeG kit file.")
        prob, rt, al, vs = [], {}, {}, {}
        for k, v in list((pack.get("routines") or {}).items())[:30]:
            ok = NAME.match(str(k)) and isinstance(v, list) and 1 <= len(v) <= 30 and all(isinstance(x, str) and 1 <= len(x) <= 200 and not re.search(r"[\x00-\x1f\x7f]", x) for x in v)
            if ok: rt[str(k)] = v
            else: prob.append(f"routine {str(k)[:20]}")
        for k, v in list((pack.get("aliases") or {}).items())[:100]:
            if isinstance(k, str) and isinstance(v, str) and 1 <= len(k) <= 40 and 1 <= len(v) <= 200 and not re.search(r"[\x00-\x1f\x7f]", k + v): al[" ".join(k.lower().split())] = " ".join(v.split())
            else: prob.append(f"alias {str(k)[:20]}")
        for k, v in list((pack.get("vars") or {}).items())[:100]:
            if isinstance(k, str) and re.fullmatch(r"[a-z_][a-z0-9_]{0,30}", k) and isinstance(v, (str, int, float)) and len(str(v)) <= 200: vs[k] = v
            else: prob.append(f"variable {str(k)[:20]}")
        return rt, al, vs, prob
    def load_file(b):
        p = Path(b).expanduser()
        if not p.is_file() or p.stat().st_size > 300_000: fail("Give the path of a kit file (under 300 KB).")
        try: return json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError): fail("That file is not valid JSON.")
    if sub not in allowed:
        fail("Say: kit export <name> | kit show <file> | kit install <file>")
    if sub == "export":
        if not NAME.match(body.lower().replace("-", "_")): fail("Give the kit a short name, like:  kit export mykit")
        cfg = {}
        try: cfg = json.loads((data_dir() / "routines.json").read_text(encoding="utf-8"))
        except (OSError, ValueError): pass
        mine = {k: v for k, v in cfg.items() if k not in _routine.DEFAULTS or v != _routine.DEFAULTS[k]}
        try: al = json.loads((data_dir() / "aliases.json").read_text(encoding="utf-8"))
        except (OSError, ValueError): al = {}
        vs = var_all()
        if not (mine or al or vs): fail("You have no routines, aliases or variables to share yet.")
        p = output_dir("JeeG kits") / (body.lower() + ".jeegkit.json")
        p.write_text(json.dumps({"jeeg": 1, "kind": "kit", "name": body.lower(), "routines": mine, "aliases": al, "vars": vs}, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {p}: {len(mine)} routine(s), {len(al)} alias(es), {len(vs)} variable(s). Check it before you share it: variables may hold private values.")
    elif sub in {"show", "install", "import"}:
        rt, al, vs, prob = clean(load_file(body))
        print(f"Kit contains {len(rt)} routine(s), {len(al)} alias(es), {len(vs)} variable(s)." + (f" Ignored as not valid: {', '.join(prob[:6])}." if prob else ""))
        for k, v in rt.items(): print(f"  routine {k}: " + " | ".join(v)[:110])
        if sub == "show":
            print("Nothing was changed. Install with:  kit install <file>")
            return
        cur = {}
        try: cur = json.loads((data_dir() / "routines.json").read_text(encoding="utf-8"))
        except (OSError, ValueError): pass
        added = [k for k in rt if k not in cur and k not in _routine.DEFAULTS]
        for k in added: cur[k] = rt[k]
        if added: (data_dir() / "routines.json").write_text(json.dumps(cur, indent=2), encoding="utf-8")
        try: a0 = json.loads((data_dir() / "aliases.json").read_text(encoding="utf-8"))
        except (OSError, ValueError): a0 = {}
        na = [k for k in al if k not in a0]
        for k in na: a0[k] = al[k]
        if na: (data_dir() / "aliases.json").write_text(json.dumps(a0, indent=1, ensure_ascii=False), encoding="utf-8")
        v0 = var_all(); nv = [k for k in vs if k not in v0]
        for k in nv: v0[k] = vs[k]
        if nv: var_save(v0)
        print(f"Installed {len(added)} routine(s), {len(na)} alias(es), {len(nv)} variable(s). Anything you already had was kept, not replaced.")
    else:
        fail("Say: kit export <name> | kit show <file> | kit install <file>")

