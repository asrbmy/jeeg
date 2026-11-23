# keywords: agent, ai agent, agent goal, work on a goal, autonomous, do this for me step by step, agent setup, agent last
# desc: Give JeeG a goal and a model you chose (Ollama, LM Studio, or your own Claude/ChatGPT/DeepSeek key) plans the steps; JeeG runs them and asks you before anything risky. agent setup | agent goal <text> | agent last | agent status | agent forget
# category: ai
# usage: agent setup | agent goal <what you want> [read|ask|safe] [steps 8] [for 10 minutes] | agent last | agent status | agent test | agent forget
# rawargs: full
# network: yes
# patterns: ^\s*agent\b
# priority: 9
import os, re, sys
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
    jeeg_agent.save_cfg(state, cfg)
    where = "on this computer" if jeeg_agent.is_local(cfg) else "at " + (jeeg_agent.base_of(cfg).split('/')[2])
    print(f"Saved. The model runs {where}." + ("" if jeeg_agent.is_local(cfg) else " When you use the agent, your goal, remembered facts that match it, and what tasks print are sent there.") + "\nTry:  agent test")
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
        m = jeeg_mind.Mind(state); print(f"Memory: {len(m.memories())} facts.  Skills: {len(m.skills())}.")
elif cmd == "test":
    cfg = jeeg_agent.load_cfg(state)
    try: r = jeeg_agent.ask_model(cfg, [{"role": "system", "content": "Reply with the single word ready."}, {"role": "user", "content": "ping"}], timeout=60)
    except jeeg_agent.AgentError as e: fail(str(e))
    print("The model answered: " + r.strip()[:80])
elif cmd == "last":
    r = jeeg_mind.Mind(state).last_run()
    if not r: fail("No agent runs yet.")
    print(f"Goal: {r['goal']}   ({r.get('mode')}, {r.get('outcome')}, {r.get('seconds', '?')} s)")
    for s in r.get("steps", []):
        if "run" in s: print(f"  {s['n']}. {s['run']}  ->  {'ok' if s.get('ok') else 'refused or failed'}: {s.get('result', '')[:100]}")
        elif "find" in s: print(f"  {s['n']}. looked for tasks: {s['find']}")
        elif "ask" in s: print(f"  {s['n']}. asked you: {s['ask']}")
    print("Answer: " + (r.get("answer") or "(none)"))
elif cmd in ("goal", "do", "run") or (cmd and cmd not in ("setup", "forget", "status", "test", "last")):
    goal = rest if cmd in ("goal", "do", "run") else (cmd + " " + rest).strip()
    mode, steps, minutes = "ask", jeeg_agent.DEFAULT_STEPS, jeeg_agent.DEFAULT_MINUTES
    m = re.search(r"\bsteps\s+(\d{1,2})\b", goal, re.I)
    if m: steps = int(m.group(1)); goal = goal.replace(m.group(0), " ")
    m = re.search(r"\bfor\s+(\d{1,2})\s+minutes?\b", goal, re.I)
    if m: minutes = int(m.group(1)); goal = goal.replace(m.group(0), " ")
    m = re.search(r"\b(safe|read|ask)\s*$", goal.strip(), re.I)
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
        res = jeeg_agent.run_goal(goal, cfg, mode, appr, state, log=lambda l: None, source="agent", say=print, max_steps=steps, minutes=minutes, ask_user=ask_user)
    except jeeg_agent.AgentError as e: fail(str(e))
    except KeyboardInterrupt: fail("Stopped.")
    print("\n" + (res["answer"] or "(no answer)"))
    if res["outcome"] == "error": raise SystemExit(1)
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
else:
    fail("Usage: agent setup | agent goal <what you want> | agent last | agent status | agent test | agent forget")
