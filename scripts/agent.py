# keywords: agent, ai agent, agent goal, work on a goal, autonomous, do this for me step by step, agent setup, agent last
# desc: Give JeeG a goal and a model you chose (Ollama, LM Studio, or your own Claude/ChatGPT/DeepSeek key) plans the steps; JeeG runs them and asks you before anything risky. agent setup | goal | plan | last | history | again | audit | template | schedule | limit | status | forget
# category: ai
# usage: agent goal <goal> careful (checks its own answer) | agent stats | agent setup [backup] | agent goal <what you want> [read|ask|safe] [steps 8] [for 10 minutes] [plan first] | agent plan <goal> | agent last | agent history | agent again <n> | agent audit | agent template list|run <name> | agent schedule add|list|run|on|off|remove | agent limit <calls> | agent status | agent test | agent forget
# rawargs: full
# network: yes
# patterns: ^\s*agent\b
# priority: 9
import os, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import args_text, data_dir, fail
import jeeg_agent, jeeg_mind, jeeg_remote
t = re.sub(r"^\s*agent\s*", "", args_text(), flags=re.I).strip()
cmd, _, rest = t.partition(" ")
cmd, rest = cmd.lower(), rest.strip()
state = data_dir()
if os.environ.get("JEEG_VIA_AI") or os.environ.get("JEEG_VIA_PEER") or os.environ.get("JEEG_VIA_BRIDGE") or os.environ.get("JEEG_VIA_PLAYBOOK"):
    fail("The agent can only be started by you at the keyboard, not by an AI, another computer or a rule.")

def ask_line(prompt, secret=False):
    if not sys.stdin or not sys.stdin.isatty():
        line = sys.stdin.readline() if sys.stdin else ""
        return line.strip()
    if secret:
        import getpass
        return getpass.getpass(prompt).strip()
    return input(prompt).strip()

if cmd == "setup":
    backup = rest.lower() == "backup"
    if backup: print("Choose a BACKUP model, used only when the main one fails.")
    keys = list(jeeg_agent.PROVIDERS)
    print("Which model should plan the steps?")
    for i, k in enumerate(keys, 1):
        p = jeeg_agent.PROVIDERS[k]; print(f"  {i}. {p[0]}" + ("" if not p[3] else "   (needs your API key; your goal and task results are sent to that company)"))
    sel = ask_line("Number: ")
    if not sel.isdigit() or not 1 <= int(sel) <= len(keys): fail("Pick one of the numbers.")
    prov = keys[int(sel) - 1]; P = jeeg_agent.PROVIDERS[prov]; cfg = {"provider": prov}
    cfg["model"] = ask_line("Model name exactly as your provider lists it (for Ollama, as shown by 'ollama list'): ")
    if prov == "custom" or not P[1]: cfg["base"] = ask_line("Address ending in /v1 : ")
    if P[3]: cfg["key"] = ask_line("API key (hidden): ", secret=True)
    try: jeeg_agent.check_config(cfg)
    except jeeg_agent.AgentError as e: fail(str(e))
    if backup:
        main = jeeg_agent.load_cfg(state)
        if not main: fail("Set up the main model first:  agent setup")
        main["fallback"] = cfg; cfg = main
    else:
        old = jeeg_agent.load_cfg(state)
        for k in ("fallback", "daily_calls"):
            if k in old: cfg[k] = old[k]
    jeeg_agent.save_cfg(state, cfg)
    where = "on this computer" if jeeg_agent.is_local(cfg) else "at " + (jeeg_agent.base_of(cfg).split('/')[2])
    print(("Backup saved. " if backup else "Saved. ") + f"The model runs {where}." + ("" if jeeg_agent.is_local(cfg) else " When you use the agent, your goal, remembered facts that match it, and what tasks print are sent there.") + "\nTry:  agent test")
elif cmd == "forget":
    p = state / jeeg_agent.CONF
    if p.exists(): p.unlink(); print("Model settings and key deleted.")
    else: print("Nothing saved.")
elif cmd == "status":
    cfg = jeeg_agent.load_cfg(state)
    if not cfg: print("No model set up yet. Run:  agent setup")
    else:
        P = jeeg_agent.PROVIDERS.get(cfg.get("provider"), ("?",))
        print(f"Model: {cfg.get('model')} via {P[0]}  ({'this computer' if jeeg_agent.is_local(cfg) else 'sent to ' + jeeg_agent.base_of(cfg).split('/')[2]})")
        m = jeeg_mind.Mind(state); print(f"Memory: {len(m.memories())} facts.  Skills: {len(m.skills())}.  Facts waiting for your review: {len(m.suggestions())}.")
        u = jeeg_agent.Usage(state).today(); print(f"Today: {u['calls']} of {cfg.get('daily_calls', jeeg_agent.DEFAULT_DAILY_CALLS)} model calls.")
        if cfg.get("fallback"): print(f"Backup model: {cfg['fallback'].get('model')} ({'this computer' if jeeg_agent.is_local(cfg['fallback']) else 'sent to ' + jeeg_agent.base_of(cfg['fallback']).split('/')[2]})")
elif cmd == "test":
    cfg = jeeg_agent.load_cfg(state)
    try: r = jeeg_agent.ask_model(cfg, [{"role": "system", "content": "Reply with the single word ready."}, {"role": "user", "content": "ping"}], timeout=60, state=state)
    except jeeg_agent.AgentError as e: fail(str(e))
    print("The model answered: " + r.strip()[:80])
elif cmd == "stats":
    st_ = jeeg_agent.Stats(state).all()
    if not st_: fail("No agent runs yet.")
    for k, v in st_.items():
        print(f"{k}: {v['runs']} runs, {v['done']} finished, {v['stopped']} stopped, {v['error']} errors; about {v['steps'] / v['runs']:.1f} steps and {v['calls'] / v['runs']:.1f} model calls per run")
        w = jeeg_agent.Stats(state).warning(k)
        if w: print("  Tip: " + w)
elif cmd == "limit":
    cfg = jeeg_agent.load_cfg(state)
    if not cfg: fail("No model is set up yet. Run:  agent setup")
    if not rest.isdigit() or not 1 <= int(rest) <= 5000: fail("Usage: agent limit <model calls per day, 1 to 5000>")
    cfg["daily_calls"] = int(rest); jeeg_agent.save_cfg(state, cfg); print(f"The agent may make {rest} model calls a day.")
elif cmd == "history":
    runs = jeeg_agent.history(state, 15)
    if not runs: fail("No agent runs yet.")
    for i, r in enumerate(runs, 1):
        print(f"{i:>2}. {time.strftime('%m-%d %H:%M', time.localtime(r.get('started', 0)))}  {r.get('outcome', '?'):<8} {len(r.get('steps', []))} steps  {r.get('model_calls', '?')} calls  [{r.get('source')}]  {r['goal'][:60]}")
    print("Run one again with:  agent again <number>")
elif cmd == "again":
    runs = jeeg_agent.history(state, 15)
    if not rest.isdigit() or not 1 <= int(rest) <= len(runs): fail("Usage: agent again <number from  agent history>")
    r = runs[int(rest) - 1]; mode = r.get("mode") if r.get("mode") in ("safe", "read", "ask") else "ask"
    sys.argv = sys.argv[:1]; os.environ["JEEG_AGAIN"] = "1"
    print(f"Again: {r['goal']}   ({mode})"); t = f"goal {r['goal']} {mode}"; cmd, _, rest = t.partition(" ")
elif cmd == "audit":
    n = int(rest) if rest.isdigit() else 5
    runs = jeeg_agent.history(state, min(n, 30))
    if not runs: fail("No agent runs yet.")
    for r in runs:
        print(f"\n{time.strftime('%Y-%m-%d %H:%M', time.localtime(r.get('started', 0)))}  [{r.get('source')}, {r.get('mode')}]  {r['goal'][:70]}")
        for s_ in r.get("steps", []):
            if "run" in s_:
                res = s_.get("result", "")
                verdict = "REFUSED" if re.search(r"can only be used in the terminal|said no|not allowed|refused|needs the person|Too many non-safe|Chaining", res) else ("ok" if s_.get("ok") else "FAILED")
                print(f"   {verdict:<8} {s_['run'][:80]}")
            elif "find" in s_: print(f"   looked    {s_['find'][:80]}")
            elif "ask" in s_: print(f"   asked you {s_['ask'][:80]}")
elif cmd == "plan":
    cfg = jeeg_agent.load_cfg(state)
    if not cfg: fail("No model is set up yet. Run:  agent setup")
    try: plan = jeeg_agent.plan_goal(rest, cfg, state)
    except jeeg_agent.AgentError as e: fail(str(e))
    print("The plan (nothing has run):\n" + "\n".join(f"  {i}. {p['run']}    [{p['label']}]" + (f"   because {p['why']}" if p["why"] else "") for i, p in enumerate(plan, 1)))
    print("Run it with:  agent goal " + rest.strip() + " plan first")
elif cmd == "template":
    sub, _, extra_ = rest.partition(" ")
    if sub.lower() in ("", "list"):
        for k, (d, g) in jeeg_agent.TEMPLATES.items(): print(f"{k:<16} {d}")
        print("Run one:  agent template run <name>")
    elif sub.lower() == "run" and extra_.strip().lower() in jeeg_agent.TEMPLATES:
        g = jeeg_agent.TEMPLATES[extra_.strip().lower()][1]; os.environ["JEEG_TEMPLATE"] = "1"; cmd, rest = "goal", g + " read"
    else: fail("Usage: agent template list | agent template run <name>")
elif cmd == "schedule":
    sub, _, extra_ = rest.partition(" "); sub = sub.lower(); items = jeeg_agent.schedules(state)
    if sub in ("", "list"):
        if not items: print("No scheduled goals. Example:  agent schedule add brief daily at 08:00 read = tell me what is due today")
        for it in items:
            when = (f"every {it['every']} min" if "every" in it else ("weekdays" if it.get("weekdays") else "daily") + f" at {it['at']}")
            print(f"{it['name']:<14} {'on ' if it.get('on', True) else 'off'} {it.get('mode', 'read'):<5} {when:<22} {it['goal'][:50]}" + (f"\n{'':<14} last: {it.get('outcome', '-')}: {it.get('result', '')[:90]}" if it.get("last") else ""))
    elif sub == "add":
        head, sep, goal_ = extra_.partition("=")
        m = re.match(r"\s*([a-z0-9][a-z0-9_\-]{0,23})\s+(.+?)\s*$", head, re.I)
        if not sep or not m or not goal_.strip(): fail("Usage: agent schedule add <name> <when> [safe|read] = <goal>   when: every 6 hours | daily at 08:00 | weekdays at 08:00")
        name, when = m.group(1).lower(), m.group(2); mode = "read"
        mm = re.search(r"\s+(safe|read)\s*$", when, re.I)
        if mm: mode = mm.group(1).lower(); when = when[:mm.start()]
        w = jeeg_agent.parse_when(when)
        if not w: fail("I did not understand the time. Use: every 6 hours (15 minutes to 30 days), daily at 08:00, or weekdays at 08:00")
        if any(i["name"] == name for i in items): fail("A schedule with that name exists. Remove it first.")
        if len(items) >= 20: fail("You can have up to 20 scheduled goals.")
        notify = bool(re.search(r"\bnotify\b", goal_, re.I)) and False
        items.append(dict(w, name=name, goal=goal_.strip()[:600], mode=mode, on=True)); jeeg_agent.save_schedules(state, items)
        print(f"Saved. It will run {'safe tasks' if mode == 'safe' else 'look-only tasks'} only, with no questions asked. Start the runner:  agent schedule run")
    elif sub in ("on", "off", "remove"):
        it = next((i for i in items if i["name"] == extra_.strip().lower()), None)
        if not it: fail("No schedule with that name.")
        if sub == "remove": items.remove(it)
        else: it["on"] = sub == "on"
        jeeg_agent.save_schedules(state, items); print("Done.")
    elif sub == "notify":
        it = next((i for i in items if i["name"] == extra_.strip().lower()), None)
        if not it: fail("No schedule with that name.")
        it["notify"] = not it.get("notify"); jeeg_agent.save_schedules(state, items); print("Results will be sent with  notify me  (set that up first)." if it["notify"] else "Notifications off.")
    elif sub == "run":
        cfg = jeeg_agent.load_cfg(state)
        if not cfg: fail("No model is set up yet. Run:  agent setup")
        if not items: fail("No scheduled goals yet.")
        once = extra_.strip().lower() == "once"
        print(f"Running {len([i for i in items if i.get('on', True)])} scheduled goal(s) in the background of this window. Only safe or look-only tasks run; Ctrl+C stops.")
        try:
            while True:
                jeeg_agent.run_due(state, cfg, say=print)
                if once: break
                time.sleep(30)
        except KeyboardInterrupt: print("\nStopped.")
    else: fail("Usage: agent schedule add | list | run [once] | on | off | notify | remove")
elif cmd == "last":
    r = jeeg_mind.Mind(state).last_run()
    if not r: fail("No agent runs yet.")
    print(f"Goal: {r['goal']}   ({r.get('mode')}, {r.get('outcome')}, {r.get('seconds', '?')} s)")
    for s in r.get("steps", []):
        if "run" in s: print(f"  {s['n']}. {s['run']}  ->  {'ok' if s.get('ok') else 'refused or failed'}: {s.get('result', '')[:100]}")
        elif "find" in s: print(f"  {s['n']}. looked for tasks: {s['find']}")
        elif "ask" in s: print(f"  {s['n']}. asked you: {s['ask']}")
    print("Answer: " + (r.get("answer") or "(none)"))
if cmd in ("goal", "do", "run") or (cmd and cmd not in ("setup", "forget", "status", "test", "last", "limit", "history", "audit", "plan", "template", "schedule", "again", "stats")):
    goal = rest if cmd in ("goal", "do", "run") else (cmd + " " + rest).strip()
    mode, steps, minutes = "ask", jeeg_agent.DEFAULT_STEPS, jeeg_agent.DEFAULT_MINUTES
    m = re.search(r"\bsteps\s+(\d{1,2})\b", goal, re.I)
    if m: steps = int(m.group(1)); goal = goal.replace(m.group(0), " ")
    m = re.search(r"\bfor\s+(\d{1,2})\s+minutes?\b", goal, re.I)
    if m: minutes = int(m.group(1)); goal = goal.replace(m.group(0), " ")
    m = re.search(r"\b(safe|read|ask)\s*$", goal.strip(), re.I)
    if m: mode = m.group(1).lower(); goal = goal.strip()[: m.start()]
    careful = bool(re.search(r"\bcareful(?:ly)?\b\s*$|\bcareful(?:ly)?\s+(?=safe|read|ask|plan)", goal, re.I))
    if careful: goal = re.sub(r"\s*\bcareful(?:ly)?\b", "", goal, count=1, flags=re.I)
    plan_first = bool(re.search(r"\bplan\s+first\b", goal, re.I))
    if plan_first: goal = re.sub(r"\s*\bplan\s+first\b", "", goal, flags=re.I)
    m = re.search(r"\b(safe|read|ask)\s*$", goal.strip(), re.I)                         # "read plan first" and "plan first read" both work
    if m: mode = m.group(1).lower(); goal = goal.strip()[: m.start()]
    cfg = jeeg_agent.load_cfg(state)
    if not cfg: fail("No model is set up yet. Run:  agent setup")
    if not jeeg_agent.is_local(cfg): print(f"(Using {cfg.get('model')} at {jeeg_agent.base_of(cfg).split('/')[2]}: your goal and what tasks print are sent there.)")
    print(f"Goal: {goal.strip()}   [mode: {mode}; up to {steps} steps, {minutes} minutes; Ctrl+C stops]")
    appr = jeeg_remote.Approver()
    def ask_user(q):
        if not sys.stdin or not sys.stdin.isatty(): return ""
        return input(f"\n  The agent asks: {q}\n  Your answer (Enter to stop): ").strip()
    try:
        if plan_first:
            plan = jeeg_agent.plan_goal(goal, cfg, state, steps)
            print("\nThe plan:\n" + "\n".join(f"  {i}. {p['run']}    [{p['label']}]" + (f"   because {p['why']}" if p["why"] else "") for i, p in enumerate(plan, 1)))
            if not sys.stdin or not sys.stdin.isatty(): fail("A plan needs your approval, so run this in a terminal.")
            if input("\nRun exactly this plan? Steps marked 'asks first' will still ask. [y/N] ").strip().lower() not in ("y", "yes"): fail("Not run.")
            res = jeeg_agent.run_plan(plan, goal, cfg, mode, appr, state, log=lambda l: None, source="agent", say=print)
        else:
            res = jeeg_agent.run_goal(goal, cfg, mode, appr, state, log=lambda l: None, source="agent", say=print, max_steps=steps, minutes=minutes, ask_user=ask_user, verify=careful)
    except jeeg_agent.AgentError as e: fail(str(e))
    except KeyboardInterrupt: fail("Stopped.")
    print("\n" + (res["answer"] or "(no answer)"))
    if res["outcome"] == "error": raise SystemExit(1)
    if not (sys.stdin and sys.stdin.isatty()):                                       # nobody to ask: keep suggestions for `remember review`
        n_ = jeeg_agent.park_suggestions(state, res, "agent")
        if n_: print(f"({n_} suggested fact(s) are waiting for you: remember review)")
    if sys.stdin and sys.stdin.isatty() and res["outcome"] == "done":                    # only you, here, decide what is kept
        mind = jeeg_mind.Mind(state)
        for fact in res["remember"]:
            if input(f"\nKeep this in memory?  \"{fact}\"  [y/N] ").strip().lower() in ("y", "yes"):
                try: mind.remember(fact); print("Remembered.")
                except jeeg_mind.MindError as e: print(str(e))
        good = [s["run"] for s in res["steps"] if s.get("ok") and "run" in s and "skill" not in s]
        if len(good) >= 2:
            name = input(f"\nThat took {len(good)} steps that worked. Save them as a skill? Type a name (Enter = no): ").strip().lower()
            if name:
                try: mind.save_skill(name, good, desc=goal[:100], source="agent"); print(f"Saved. Run it any time:  skill run {name}")
                except jeeg_mind.MindError as e: print(str(e))
elif not cmd:
    fail("Usage: agent setup | goal | plan | last | history | again | audit | template | schedule | limit | status | test | forget")
