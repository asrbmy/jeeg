# keywords: env diff, compare env files, compare dotenv, missing env variables, env file differences
# desc: Compare two .env files and show which keys are missing or different, without printing the values (env diff .env.example .env)
# category: developer
# usage: env diff <file1> <file2>
# rawargs: full
# patterns: ^\s*(?:env\s+diff|compare\s+env)\b
# priority: 3
import re, shlex
from _lib import args_text, fail
from _files import path_arg
t = re.sub(r"^\s*(?:env\s+diff|compare\s+env(?:\s+files?)?)\s*", "", args_text(), flags=re.I)
try: parts = shlex.split(t)
except ValueError: parts = t.split()
if len(parts) != 2:
    fail("Usage: env diff <file1> <file2>   for example:  env diff .env.example .env")
def load(p):
    d = {}
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        d[k.replace("export ", "").strip()] = v.strip().strip("\"'")
    return d
pa, pb = path_arg(parts[0]), path_arg(parts[1])
a, b = load(pa), load(pb)
only_a, only_b = sorted(set(a) - set(b)), sorted(set(b) - set(a))
diff = sorted(k for k in set(a) & set(b) if a[k] != b[k])
print(f"{pa.name} has {len(a)} keys, {pb.name} has {len(b)} keys.")
print(f"Only in {pa.name}: " + (", ".join(only_a) or "none"))
print(f"Only in {pb.name}: " + (", ".join(only_b) or "none"))
print("Different values: " + (", ".join(diff) or "none") + "   (values are not shown)")
