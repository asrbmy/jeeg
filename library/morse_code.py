# keywords: morse, morse code, to morse, from morse, sos
# desc: Translate text to Morse code and back (morse hello world; morse .... . .-.. .-.. ---)
# category: fun
# usage: morse <text or dots and dashes>
# rawargs: yes
import sys

M = {"a": ".-", "b": "-...", "c": "-.-.", "d": "-..", "e": ".", "f": "..-.", "g": "--.", "h": "....", "i": "..", "j": ".---", "k": "-.-", "l": ".-..",
     "m": "--", "n": "-.", "o": "---", "p": ".--.", "q": "--.-", "r": ".-.", "s": "...", "t": "-", "u": "..-", "v": "...-", "w": ".--", "x": "-..-",
     "y": "-.--", "z": "--..", "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-", "5": ".....", "6": "-....", "7": "--...",
     "8": "---..", "9": "----.", ".": ".-.-.-", ",": "--..--", "?": "..--..", "!": "-.-.--", "/": "-..-.", "@": ".--.-."}
R = {v: k for k, v in M.items()}
t = " ".join(sys.argv[1:]).strip()
if t.lower().startswith("morse"):
    t = t[5:].strip()
if t.lower().startswith("code"):
    t = t[4:].strip()
if not t or len(t) > 500:
    sys.exit("Usage: morse hello world      or      morse .... . .-.. .-.. ---   (up to 500 characters)")
if set(t) <= set(".-/ _"):
    words = t.replace("_", "-").split("/") if "/" in t else t.split("   ")
    print(" ".join("".join(R.get(c, "?") for c in w.split()) for w in words))
else:
    print("   ".join(" ".join(M.get(c, "?") for c in w) for w in t.lower().split()))
