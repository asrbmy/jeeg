# keywords: env check, dotenv, env file, missing env, check env, env example, environment variables file, env keys
# desc: Compare a .env file with .env.example and list missing keys, without showing secrets (env check; env check myapp)
# category: developer
# usage: env check [folder]
# rawargs: full
# private: yes
# patterns: \benv\s+check\b ;; \bcheck\s+(my\s+)?\.?env\b ;; \bmissing\s+env\b ;; \bdotenv\b ;; \.env\s+(file|example)\b
# priority: 3
import re
from pathlib import Path
from _lib import args_text, fail
t = re.sub(r"\b(env|check|dotenv|file|the|missing|keys?|compare)\b", " ", args_text(), flags=re.I).strip().strip("\"'")
folder = Path(t).expanduser() if t else Path.cwd()
if folder.is_file():
    folder = folder.parent
if not folder.is_dir():
    fail(f"Not a folder: {folder}")
def keys(p):
    out = {}
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.replace("export ", "").strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", k):
            out[k] = v.strip().strip("\"'")
    return out
env, ex = folder / ".env", next((folder / n for n in (".env.example", ".env.sample", ".env.template") if (folder / n).exists()), None)
if not env.exists():
    fail(f"No .env file in {folder}" + (f". Create it from {ex.name}." if ex else "."))
if ex is None:
    fail(f"No .env.example in {folder} to compare with.")
a, b = keys(env), keys(ex)
missing = sorted(set(b) - set(a))
extra = sorted(set(a) - set(b))
empty = sorted(k for k in a if k in b and not a[k])
print(f"Comparing {env.name} with {ex.name} in {folder}   (values are never shown)")
print(f"  {len(a)} keys in .env, {len(b)} in the example")
for title, items in (("Missing from .env", missing), ("Empty in .env", empty), ("In .env but not in the example", extra)):
    if items:
        print(f"  {title}: " + ", ".join(items))
if not (missing or empty):
    print("  Everything the example asks for is set.")
gi = folder / ".gitignore"
if not gi.exists() or not re.search(r"^/?\.env\s*$", gi.read_text(errors="replace"), re.M):
    print("  WARNING: .env is not listed in .gitignore, so it could be committed by mistake.")
