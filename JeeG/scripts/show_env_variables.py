# keywords: environment variables, env vars, env variable, show env, printenv, list env, show environment, environment
# desc: List environment variables (secrets hidden); add a word to filter (env variables java)
# category: developer
# usage: env variables [filter]
# rawargs: yes
import os, re
from _lib import args_text
q = re.sub(r"\b(show|list|my|the|all|environment|env|variables?|vars?|for|of)\b", " ", args_text(), flags=re.I).strip().lower()
SECRET = re.compile(r"KEY|TOKEN|SECRET|PASS|PWD|CREDENTIAL|AUTH|COOKIE|SESSION", re.I)
n = 0
for k in sorted(os.environ, key=str.lower):
    if q and q not in k.lower() and q not in os.environ[k].lower(): continue
    v = "********" if SECRET.search(k) else os.environ[k]
    print(f"{k}={v[:150]}"); n += 1
print(f"{n} variable(s)" + ("" if q else "  (names containing KEY/TOKEN/SECRET/PASS are hidden)"))
