# keywords: semver, compare versions, version compare, which version is newer, version greater than, compare semver
# desc: Compare two version numbers the way package managers do (semver 1.2.3 vs 1.10.0)
# category: developer
# usage: semver <version> vs <version>
# rawargs: full
# patterns: ^\s*(?:semver|compare\s+versions?|version\s+compare)\b
# priority: 3
import re
from _lib import args_text, fail
t = re.sub(r"^\s*(?:semver|compare\s+versions?|version\s+compare)\s*", "", args_text(), flags=re.I)
v = re.findall(r"v?\d+(?:\.\d+)*(?:-[0-9A-Za-z.\-]+)?(?:\+[0-9A-Za-z.\-]+)?", t)
if len(v) != 2: fail("Usage: semver 1.2.3 vs 1.10.0")
def key(s):
    s = s.lstrip("vV").split("+")[0]
    core, _, pre = s.partition("-")
    nums = [int(x) for x in core.split(".")]
    nums += [0] * (3 - len(nums)) if len(nums) < 3 else []
    pk = [(0, int(x), "") if x.isdigit() else (1, 0, x) for x in pre.split(".")] if pre else None
    return nums, pk
def cmp(a, b):
    (na, pa), (nb, pb) = key(a), key(b)
    if na != nb: return (na > nb) - (na < nb)
    if pa is None and pb is None: return 0
    if pa is None: return 1
    if pb is None: return -1
    return (pa > pb) - (pa < pb)
r = cmp(v[0], v[1])
print(f"{v[0]} is " + ("newer than" if r > 0 else "older than" if r < 0 else "the same as") + f" {v[1]}")
