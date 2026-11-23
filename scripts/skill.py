# keywords: skill, skills, jeeg skill, save skill, run skill, skill list, skill add
# desc: Save a list of plain-words steps as a skill and run it any time (skill add morning = show reminders ; what is due). The agent can use your skills. skill add | run | list | show | remove | describe | share
# category: ai
# usage: skill add <name> = <step> ; <step> | skill run <name> [read|ask|safe] | skill list | skill show <name> | skill describe <name> = <text> | skill remove <name> | skill export <name> | skill import <file>
# rawargs: full
# patterns: ^\s*skills?\b
# priority: 9
import json, os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import args_text, data_dir, fail
import jeeg_mind, jeeg_remote
t = re.sub(r"^\s*skills?\s*", "", args_text(), flags=re.I).strip()
cmd, _, rest = t.partition(" ")
cmd, rest = (cmd.lower() or "list"), rest.strip()
state = data_dir(); m = jeeg_mind.Mind(state)
def guard():
    if any(os.environ.get(k) for k in ("JEEG_VIA_AI", "JEEG_VIA_PEER", "JEEG_VIA_BRIDGE")): fail("Only you, at the keyboard, can change skills.")
try:
    if cmd in ("add", "new", "save"):
        guard(); name, sep, body = rest.partition("=")
        if not sep: fail("Usage: skill add <name> = <step> ; <step>")
        m.save_skill(name.strip(), [s for s in body.split(";") if s.strip()], source="you"); print(f"Saved. Run it with:  skill run {name.strip().lower()}")
    elif cmd == "describe":
        guard(); name, sep, text = rest.partition("="); sk = m.skills().get(name.strip().lower())
        if not sep or not sk: fail("Usage: skill describe <name> = <text>   (the skill must exist)")
        m.save_skill(name.strip(), sk["steps"], desc=text.strip(), source=sk.get("source", "you"), replace=True); print("Updated.")
    elif cmd == "list":
        sk = m.skills()
        if not sk: print("No skills yet. Try:  skill add morning = show reminders ; what is due")
        for k, v in sorted(sk.items()): print(f"{k:<16} {len(v['steps'])} steps, used {v.get('uses', 0)}x  {v.get('desc', '')[:60]}")
    elif cmd == "show":
        sk = m.skills().get(rest.lower())
        if not sk: fail("No skill with that name.")
        print(f"{rest.lower()}: {sk.get('desc', '')}\n" + "\n".join(f"  {i}. {s}" for i, s in enumerate(sk["steps"], 1)) + f"\nUsed {sk.get('uses', 0)}x ({sk.get('ok', 0)} ok, {sk.get('failed', 0)} failed); made by {sk.get('source', 'you')}")
    elif cmd in ("remove", "delete", "forget"):
        guard(); m.drop_skill(rest); print("Removed.")
    elif cmd == "export":
        sk = m.skills().get(rest.lower())
        if not sk: fail("No skill with that name.")
        out = Path.cwd() / f"{rest.lower()}.jeeg-skill.json"; out.write_text(json.dumps({"name": rest.lower(), "desc": sk.get("desc", ""), "steps": sk["steps"]}, indent=1), encoding="utf-8"); print(f"Wrote {out}. Share it as you like; whoever imports it sees every step first.")
    elif cmd == "import":
        guard(); p = Path(rest.strip("\"'")).expanduser()
        try: d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError): fail("Could not read that skill file.")
        steps = m.check_steps(d.get("steps", []))
        print("This skill would run these steps:\n" + "\n".join(f"  {i}. {s}" for i, s in enumerate(steps, 1)))
        if not sys.stdin or not sys.stdin.isatty(): fail("Importing asks you to confirm, so run it in a terminal.")
        if input("Save it? [y/N] ").strip().lower() not in ("y", "yes"): fail("Not saved.")
        m.save_skill(str(d.get("name", p.stem)), steps, desc=str(d.get("desc", "")), source="imported"); print("Saved.")
    elif cmd in ("run", "do"):
        mode = "ask"; mm = re.search(r"\b(safe|read|ask)\s*$", rest, re.I)
        if mm: mode = mm.group(1).lower(); rest = rest[: mm.start()].strip()
        sk = m.skills().get(rest.lower())
        if not sk: fail("No skill with that name.  skill list")
        appr = jeeg_remote.Approver(); allok = True
        for i, s in enumerate(sk["steps"], 1):
            print(f"{i}. {s}")
            out, bad = jeeg_remote.run_for_ai(s, mode, appr, state, lambda l: None, "skill", ())
            print("   " + (("FAILED: " if bad else "") + out).replace("\n", "\n   ")[:1500])
            if bad: allok = False; break
        m.note_skill_run(rest.lower(), allok)
        if not allok: raise SystemExit(1)
    else:
        fail("Usage: skill add | run | list | show | describe | remove | export | import")
except jeeg_mind.MindError as e:
    fail(str(e))
