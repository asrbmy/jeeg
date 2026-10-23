# keywords: typing test, typing speed, wpm, test typing, how fast do i type, typing practice, words per minute, typing game
# desc: Test your typing speed and accuracy
# category: fun
import difflib, random, time
S = ["The quick brown fox jumps over the lazy dog near the quiet river bank.",
     "Practice makes progress, so keep your fingers light and your eyes on the screen.",
     "A small script that runs every day can save hours of work over a single year.",
     "Good code is simple to read, easy to test and kind to the next person who opens it.",
     "India is home to many languages, festivals and flavours that change every few hundred kilometres."]
s = random.choice(S)
print("Type this sentence exactly, then press Enter:\n\n  " + s + "\n")
try:
    input("Press Enter to start... ")
    t0 = time.time(); typed = input("> "); dt = max(time.time() - t0, 0.1)
except (EOFError, KeyboardInterrupt):
    print(); raise SystemExit(0)
acc = difflib.SequenceMatcher(None, s, typed).ratio() * 100
correct = sum(a == b for a, b in zip(s, typed))
wpm = (correct / 5) / (dt / 60)
print(f"\nSpeed: {wpm:.0f} WPM   Accuracy: {acc:.0f}%   Time: {dt:.1f}s")
