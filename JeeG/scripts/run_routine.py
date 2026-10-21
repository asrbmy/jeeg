# keywords: routine, run routine, my routine, custom routine, macro, workflow
# desc: Run any routine from your routines file (run routine <name>)
# category: routines
# usage: run routine <name>
# priority: 1
from _lib import args_text, fail
from _routine import run
n = args_text().strip().lower().replace(" ", "_")
if not n:
    fail("Usage: run routine <name>   (see: list routines)")
run(n)
