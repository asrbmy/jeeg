# keywords: lorem ipsum, dummy text, placeholder text, filler text, sample text, fake text, random paragraph, lorem
# desc: Generate placeholder text (lorem ipsum 3 paragraphs, or 50 words)
# category: text
# usage: lorem ipsum [3 paragraphs|50 words]
# rawargs: yes
import random, re
from _lib import args_text
from _text import emit
t = args_text().lower()
m = re.search(r"(\d+)", t)
n = max(1, min(int(m.group(1)), 50 if "word" not in t else 2000)) if m else 2
LOREM = ("lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam "
         "quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit esse cillum "
         "dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum").split()
rnd = random.Random(2026)
def sentence(first=False):
    k = rnd.randint(8, 16); ws = [rnd.choice(LOREM) for _ in range(k)]
    if first: ws[:2] = ["lorem", "ipsum"]
    return " ".join(ws).capitalize() + "."
if "word" in t:
    ws = [LOREM[i % len(LOREM)] for i in range(n)]
    out = " ".join(ws).capitalize() + "."
else:
    out = "\n\n".join(" ".join(sentence(i == 0 and j == 0) for i in range(rnd.randint(3, 5))) for j in range(n))
emit(out)
