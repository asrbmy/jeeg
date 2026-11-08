# keywords: fasting, fast start, fast status, fast end, intermittent fasting, fasting timer, break fast, how long have i fasted
# desc: Time a fast (fast start; fast status; fast end)
# category: health
# usage: fast start | fast status | fast end | fast history
# rawargs: full
# private: yes
# patterns: \bfast(ing)?\s+(start|status|end|stop|timer|history)\b ;; \b(start|end|break)\s+(my\s+)?fast\b ;; \bintermittent\s+fasting\b ;; \bhow\s+long\s+(have\s+i|did\s+i)\s+fast
# priority: 3
import re, time
from _lib import args_text, fail
from _store import load, save
low = args_text().lower()
st = load("fast.json", {"start": None, "history": []})
now = time.time()
def fmt(sec):
    h, m = int(sec // 3600), int(sec % 3600 // 60)
    return f"{h}h {m:02d}m"
stages = [(4, "digesting your last meal"), (12, "blood sugar settling, body starting to use stored energy"), (16, "a common intermittent-fasting target (16:8)"),
          (24, "a full day; drink water and rest"), (48, "long fast: only with medical advice")]
if re.search(r"\b(start|begin|begun|started)\b", low):
    if st["start"]:
        fail(f"A fast is already running ({fmt(now - st['start'])} so far). Say: fast end")
    st["start"] = now
    save("fast.json", st)
    print("Fast started. Drink water. Say 'fast status' any time, and 'fast end' when you eat.")
elif re.search(r"\b(end|stop|break|finish|ended|done)\b", low):
    if not st["start"]:
        fail("No fast is running. Say: fast start")
    dur = now - st["start"]
    st["history"] = (st["history"] + [{"start": st["start"], "hours": round(dur / 3600, 2)}])[-100:]
    st["start"] = None
    save("fast.json", st)
    print(f"Fast ended after {fmt(dur)}. Break it gently with something light.")
elif re.search(r"\b(history|past|log|average)\b", low):
    h = st["history"]
    if not h:
        fail("No finished fasts yet.")
    for x in h[-10:]:
        print(f"  {time.strftime('%d %b', time.localtime(x['start']))}  {x['hours']:.1f} hours")
    print(f"Average of {len(h)} fasts: {sum(x['hours'] for x in h) / len(h):.1f} hours")
else:
    if not st["start"]:
        fail("No fast is running. Say: fast start")
    dur = now - st["start"]
    hrs = dur / 3600
    note = next((n for lim, n in stages if hrs < lim), stages[-1][1])
    print(f"Fasting for {fmt(dur)} (since {time.strftime('%a %H:%M', time.localtime(st['start']))}): {note}.")
    nxt = next((lim for lim, _ in stages if hrs < lim), None)
    if nxt:
        print(f"  Next milestone in {fmt((nxt - hrs) * 3600)} ({nxt} hours).")
    print("  General information, not medical advice. Stop if you feel unwell; check with a doctor if you take medicine or have a condition.")
