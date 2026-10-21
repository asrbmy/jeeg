# keywords: flashcards, flash cards, spaced repetition, revise cards, memorize, memory cards, leitner, learn cards, review cards, study cards
# desc: Spaced-repetition flashcards from a 'question | answer' file; cards you miss come back sooner (flashcards, flashcards 5 myfile.txt)
# category: study
# usage: flashcards [count] [file]
# rawargs: yes
# priority: 1
import datetime, hashlib, random, re
from _lib import args_text, data_dir, fail
from _files import path_arg
from _store import load, save
from _files import drop_tokens
toks = args_text().split()
nums = [x for x in toks if re.fullmatch(r"\d{1,3}", x)]
limit = int(nums[0]) if nums else 10
t = drop_tokens(" ".join(x for x in toks if x not in nums), {"flashcards", "flashcard", "cards", "card", "from", "my", "notes", "note", "file", "revise", "review", "study", "practice"})
p = path_arg(t) if t else data_dir() / "quiz.txt"
if not p.exists():
    p.write_text("# one per line:  question | answer\nCapital of India | New Delhi\n2 + 2 | 4\n", encoding="utf-8")
    fail(f"I made a sample file at {p}. Add your own 'question | answer' lines, then run this again.")
cards = []
for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
    if not line.strip() or line.strip().startswith("#"): continue
    q, sep, a = line.partition("|") if "|" in line else line.partition("::")
    if sep and q.strip() and a.strip(): cards.append((q.strip(), a.strip()))
if not cards: fail("No 'question | answer' lines found in " + str(p))
prog = load("flashcards.json", {})
today = datetime.date.today()
GAP = [0, 1, 3, 7, 21]                      # days until a card returns, by box 1..5
def cid(q): return hashlib.sha1(q.lower().encode("utf-8")).hexdigest()[:12]
due = [c for c in cards if datetime.date.fromisoformat(prog.get(cid(c[0]), {}).get("due", today.isoformat())) <= today]
new = sum(1 for c in cards if cid(c[0]) not in prog)
if not due:
    nxt = min(datetime.date.fromisoformat(prog[cid(c[0])]["due"]) for c in cards)
    print(f"Nothing due today. {len(cards)} cards, next review on {nxt:%a %d %b}."); raise SystemExit(0)
random.shuffle(due); due = due[:limit]
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()
print(f"{len(due)} card(s) due ({new} new). Type your answer, press Enter on an empty line to reveal, q to stop.")
right = wrong = 0
for q, a in due:
    try: ans = input(f"\n{q}\n> ").strip()
    except (EOFError, KeyboardInterrupt): print(); break
    if ans.lower() == "q": break
    st = prog.setdefault(cid(q), {"box": 1})
    ok = bool(ans) and norm(ans) == norm(a)
    if not ok and not ans:
        print(f"  Answer: {a}")
        try: ok = input("  Did you know it? [y/N] ").strip().lower() in ("y", "yes")
        except (EOFError, KeyboardInterrupt): break
    elif not ok:
        print(f"  Answer: {a}")
        try: ok = input("  Count it as correct anyway? [y/N] ").strip().lower() in ("y", "yes")
        except (EOFError, KeyboardInterrupt): break
    else: print("  Correct!")
    st["box"] = min(5, st["box"] + 1) if ok else 1
    st["due"] = (today + datetime.timedelta(days=GAP[st["box"] - 1] if ok else 0)).isoformat()
    right += ok; wrong += (not ok)
    save("flashcards.json", prog)
print(f"\nRight {right}, to repeat {wrong}. Cards you got right return after 1, 3, 7 and 21 days.")
