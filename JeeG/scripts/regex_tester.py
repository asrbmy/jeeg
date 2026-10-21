# keywords: regex test, test regex, regular expression, regex tester, try regex, match pattern, regexp, check regex, find matches regex, pattern test
# desc: Try a regular expression on some text and see the matches (regex test "\d+" on "abc 123 def 45")
# category: developer
# usage: regex test "<pattern>" on "<text>"
# rawargs: full
import re
from _lib import args_text, fail
t = args_text()
q = re.findall(r'"((?:[^"\\]|\\.)*)"|\u201c([^\u201d]*)\u201d', t)
qs = [a or b for a, b in q]
if len(qs) < 2: fail('Usage: regex test "<pattern>" on "<text>" [ignorecase]     e.g. regex test "\\d+" on "abc 123 def 45"')
pat, text = qs[0], qs[1]
if len(text) > 20000 or len(pat) > 500: fail("Pattern or text is too long.")
flags = re.I if re.search(r"\bignore ?case\b|\bcase.insensitive\b", t.lower()) else 0
try: rx = re.compile(pat, flags)
except re.error as e: fail(f"The pattern is not valid: {e}")
import json, subprocess, sys
CHILD = ("import json,re,sys;d=json.load(sys.stdin);rx=re.compile(d['p'],d['f']);"
         "print(json.dumps([[m.start(),m.end(),m.group(0),list(m.groups())] for m in rx.finditer(d['t'])][:200]))")
try:
    r = subprocess.run([sys.executable, "-I", "-c", CHILD], input=json.dumps({"p": pat, "t": text, "f": int(flags)}), capture_output=True, text=True, timeout=3)
except subprocess.TimeoutExpired:
    fail("The pattern took too long (it may backtrack badly, like (a+)+$). Simplify it.")
if r.returncode: fail("The pattern could not be run: " + (r.stderr.strip().splitlines() or ["error"])[-1])
res = {"m": [(a, b, g, tuple(gr)) for a, b, g, gr in json.loads(r.stdout)]}
ms = res["m"]
print(f"{len(ms)} match(es)" + (" (showing 200)" if len(ms) == 200 else "") + f" for /{pat}/")
for s, e, g, groups in ms[:50]:
    print(f"  [{s}:{e}] {g!r}" + (f"   groups: {groups}" if groups else ""))
