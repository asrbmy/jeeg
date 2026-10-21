# keywords: quiz, quiz me, quiz notes, flashcards, test myself, revision quiz, study quiz, practice questions, self test
# desc: Quiz yourself from a notes file of 'question | answer' lines (quiz notes myfile.txt)
# category: fun
# usage: quiz notes [file]
# rawargs: yes
import random, re
from _lib import args_text, data_dir, fail
from _files import path_arg
t = re.sub(r"^\s*(?:me\s+)?(?:from\s+)?(?:my\s+)?(?:notes?\s+)?(?:file\s+)?", "", args_text(), flags=re.I).strip()
p = path_arg(t) if t else data_dir() / "quiz.txt"
if not p.exists():
    p.write_text("# one per line:  question | answer\nCapital of India | New Delhi\n2 + 2 | 4\n", encoding="utf-8")
    fail(f"I made a sample file at {p}. Add your own 'question | answer' lines, then run this again.")
qa = []
for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
    if line.strip().startswith("#") or not line.strip(): continue
    q, sep, a = line.partition("|") if "|" in line else line.partition("::")
    if sep and q.strip() and a.strip(): qa.append((q.strip(), a.strip()))
if not qa: fail("No 'question | answer' lines found in " + str(p))
random.shuffle(qa)
score = 0
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()
print(f"{len(qa)} question(s) from {p.name}. Type the answer; empty line skips, q quits.")
done = 0
for q, a in qa:
    try: ans = input(f"\n{q}\n> ").strip()
    except (EOFError, KeyboardInterrupt): print(); break
    if ans.lower() == "q": break
    done += 1
    if norm(ans) == norm(a) and ans: score += 1; print("  Correct!")
    else: print(f"  Answer: {a}")
print(f"\nScore: {score}/{done}")
