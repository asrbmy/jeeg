# keywords: list routines, show routines, my routines, routines, what routines, macros
# desc: List your routines and their steps
# category: routines
from _routine import load
for k, steps in sorted(load().items()):
    print(f"{k}:")
    for s in steps:
        print("   ", s)
