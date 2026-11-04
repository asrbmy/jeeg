# keywords: heart rate zones, max heart rate, target heart rate, hr zones, pulse zones
# desc: Heart rate zones for your age (heart rate zones age 30)
# category: health
# usage: heart rate zones age <years>
# rawargs: yes
# patterns: \bheart\s*rate\b ;; \b(hr|pulse)\s+zones?\b
# priority: 2
from _lib import args_text, fail
from _money import numbers
n = numbers(args_text())
if not n or not (5 <= n[0] <= 110):
    fail("Usage: heart rate zones age 30")
mx = 220 - n[0]
print(f"Age {n[0]:g}: estimated maximum heart rate {mx:g} beats a minute")
for name, a, b in (("Easy / warm-up", .5, .6), ("Fat burn", .6, .7), ("Cardio", .7, .8), ("Hard", .8, .9), ("Maximum effort", .9, 1.0)):
    print(f"  {name:<15} {mx * a:>4.0f} - {mx * b:<4.0f}")
print("  A rough estimate (220 minus age). Not medical advice.")
