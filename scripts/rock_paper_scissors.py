# keywords: rock paper scissors, rps, play rock paper, paper scissors, stone paper scissors, hand game, play rps
# desc: Play rock paper scissors against the computer
# category: fun
import random
R = random.SystemRandom()
names = {"r": "rock", "p": "paper", "s": "scissors"}
beats = {"r": "s", "p": "r", "s": "p"}
w = l = d = 0
print("Type r, p or s (q to stop).")
while True:
    try: u = input("Your move: ").strip().lower()[:1]
    except (EOFError, KeyboardInterrupt): print(); break
    if u == "q": break
    if u not in names: print("  r = rock, p = paper, s = scissors"); continue
    c = R.choice("rps")
    if u == c: d += 1; res = "draw"
    elif beats[u] == c: w += 1; res = "you win"
    else: l += 1; res = "computer wins"
    print(f"  computer: {names[c]}  ->  {res}   (you {w} - {l} computer, {d} draws)")
print(f"Final: you {w}, computer {l}, draws {d}.")
