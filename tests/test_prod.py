"""Production features: administrator policy, audit log, data migrations. Run: python tests/test_prod.py"""
import csv, json, os, shutil, stat, subprocess, sys, tempfile, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
HOME = tempfile.mkdtemp(prefix="jeeg-prod-"); os.environ["JEEG_HOME"] = HOME; os.environ["HOME"] = HOME; os.environ["USERPROFILE"] = HOME
os.environ.pop("JEEG_POLICY", None)
P = F = 0
def j(q, env=None, yes=False):
    r = subprocess.run([sys.executable, str(ROOT / "jeeg.py")] + (["--yes"] if yes else []) + [q], capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL, env={**os.environ, **(env or {})})
    return r.returncode, r.stdout + r.stderr
def ok(c, l):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", l)
POL = Path(HOME) / "policy.json"
def policy(d, mode=0o644):
    POL.write_text(json.dumps(d)); os.chmod(POL, mode)
    return {"JEEG_POLICY": str(POL)}
# ---- policy
c, o = j("policy"); ok("No administrator policy" in o, "no policy by default")
e = policy({"disable_categories": ["money"], "disable_tasks": ["flip coin"], "ai_max": "read", "ai_browser": False, "note": "Set by IT"})
c, o = j("policy", e); ok("Set by IT" in o and "money" in o and "read" in o, "policy shown: " + o)
c, o = j("gst 100 18", e); ok(c == 1 and "administrator has turned off" in o, "disabled task says why: " + o)
c, o = j("flip coin", e); ok(c == 1 and "administrator" in o, "disabled by name")
c, o = j("25 * 4", e); ok(c == 0 and "100" in o, "other tasks still work")
c, o = j("list", e); ok("gst amount" not in o, "disabled task hidden from list")
c, o = j("gst 100 18"); ok(c == 0 and "118" in o, "without the policy it works")
e = policy({"block_online": True})
import jeeg_policy
os.environ["JEEG_POLICY"] = str(POL)
ents = [{"name": "a", "cat": "x", "net": True, "path": "/p/a.py"}, {"name": "b", "cat": "x", "net": False, "path": "/p/b.py"}, {"name": "c", "cat": "y", "path": "/q/plug/c.py"}]
ok([x["name"] for x in jeeg_policy.apply(ents)] == ["b", "c"], "block_online removes only online tasks")
policy({"block_plugins": True}); ok([x["name"] for x in jeeg_policy.apply(ents, Path("/q/plug"))] == ["a", "b"], "block_plugins removes plugin folder tasks")
policy({"ai_max": "safe"}); ok(jeeg_policy.clamp_ai("god") == "safe" and jeeg_policy.clamp_ai("safe") == "safe", "ai mode clamped")
policy({"ai_max": "ask"}); ok(jeeg_policy.clamp_ai("read") == "read" and jeeg_policy.clamp_ai("god") == "ask", "clamp keeps lower modes")
policy({"ai_max": "banana", "disable_tasks": "notalist", "block_online": "yes"}); pol = jeeg_policy.load()
ok(len(pol.get("_problems", [])) == 3 and "ai_max" not in pol, "bad values reported, not applied: %r" % pol)
POL.write_text("{not json"); ok("could not be read" in jeeg_policy.load()["_problems"][0], "broken file: no crash, no policy")
if os.name != "nt":
    policy({"disable_categories": ["money"]}, 0o666); ok("ignored" in jeeg_policy.load()["_problems"][0] and jeeg_policy.apply(ents) == ents, "world-writable policy is ignored")
# AI path
import jeeg_remote, jeeg_api
policy({"ai_max": "off"})
class Ap:
    dry = False
    def ask(self, *a, **k): return False
txt, bad = jeeg_remote.run_for_ai("gst 100 18", "safe", Ap(), HOME)
ok(bad and "administrator" in txt, "ai off: " + txt)
policy({"ai_browser": False}); txt, bad = jeeg_remote.run_for_ai("browser look", "ask", Ap(), HOME)
ok(bad and "browser" in txt and "administrator" in txt, "ai browser off: " + txt)
policy({"ai_max": "safe"}); txt, bad = jeeg_remote.run_for_ai("gst 100 18", "god", Ap(), HOME); ok(not bad and "118" in txt, "clamped mode still serves safe tasks: " + txt)
os.environ.pop("JEEG_POLICY", None); os.environ.pop("JEEG_VIA_AI", None)
# ---- audit log
c, o = j("audit show"); log = Path(HOME) / "log.jsonl"
c, o = j("gst 100 18", env={"JEEG_VIA_AI": "1"}); c, o = j("25 * 4")
c, o = j("audit ai"); ok("AI" in o and "gst amount" in o and "calculate" not in o, "audit ai: " + o)
c, o = j("audit summary"); ok("asked for by an AI" in o, "audit summary")
c, o = j("audit export"); csvs = list(Path(HOME).rglob("audit-*.csv"))
ok(c == 0 and csvs and "asked_by" in csvs[0].read_text() and "gst 100" not in csvs[0].read_text(), "audit export has no typed text")
rows = list(csv.DictReader(open(csvs[0]))); ok(any(r["asked_by"] == "AI" for r in rows) and any(r["asked_by"] == "you" for r in rows), "audit tells you from AI")
ok("audit" in jeeg_api.TERMINAL_ONLY and "audit" in jeeg_remote.TERMINAL_ONLY, "audit is terminal only")
# ---- migrations
import jeeg_migrate as M
st = Path(tempfile.mkdtemp(prefix="jeeg-mig-"))
ok(M.run(st) == "" and json.loads((st / "data_version.json").read_text())["v"] == M.DATA_VERSION, "fresh folder is stamped")
st2 = Path(tempfile.mkdtemp(prefix="jeeg-mig-")); (st2 / "notes.json").write_text('["old"]')
ok(M.run(st2) == "" and (st2 / "notes.json").read_text() == '["old"]' and not (st2 / "backups").exists(), "old records without a stamp are stamped, untouched")
def up(state):
    d = json.loads((state / "notes.json").read_text()); (state / "notes.json").write_text(json.dumps([{"text": x} for x in d]))
msg = M.run(st2, current=2, migrations={2: up})
ok("upgraded" in msg and json.loads((st2 / "notes.json").read_text()) == [{"text": "old"}], "migration applied: " + msg)
bk = list((st2 / "backups").glob("before-*.zip")); ok(bk and json.loads(zipfile.ZipFile(bk[0]).read("notes.json")) == ["old"], "a copy of the old records was kept")
ok(M.run(st2, current=2, migrations={2: up}) == "", "does not run twice")
st3 = Path(tempfile.mkdtemp(prefix="jeeg-mig-")); (st3 / "notes.json").write_text('["keep"]'); M._stamp(st3, 1)
def boom(state): (state / "notes.json").write_text("garbage"); raise ValueError("x")
msg = M.run(st3, current=2, migrations={2: boom})
ok("put everything back" in msg and (st3 / "notes.json").read_text() == '["keep"]' and M._read(st3) == 1, "failed migration is rolled back: " + msg)
st4 = Path(tempfile.mkdtemp(prefix="jeeg-mig-")); (st4 / "notes.json").write_text("[]"); M._stamp(st4, 9)
msg = M.run(st4); ok("newer JeeG" in msg and M._read(st4) == 9 and (st4 / "notes.json").read_text() == "[]", "newer records are never touched")
c, o = j("gst 100 18"); ok(c == 0 and (Path(HOME) / "data_version.json").exists(), "engine stamps the data folder")
c, o = j("tips"); ok("never been backed up" not in o, "a stamp alone does not trigger the backup nudge")
for d in (st, st2, st3, st4): shutil.rmtree(d, ignore_errors=True)
shutil.rmtree(HOME, ignore_errors=True)
print(f"{P} passed, {F} failed"); sys.exit(1 if F else 0)
