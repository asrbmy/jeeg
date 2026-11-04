"""Using JeeG inside your own Python program.  Run:  python examples/use_from_python.py"""
import tempfile

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))  # lets this run from a plain download; not needed after pip install
import jeeg

# 1. Say it in words, exactly like at the JeeG prompt.
r = jeeg.run("gst 2500 18")
print(r.output if r.ok else f"failed: {r.output}")

# 2. Or call a task by name with arguments (no word matching, so it is predictable).
print(jeeg.gst_amount(1000, 18).output)

# 3. Ask which task would run, without running it.
for m in jeeg.find("open youtube", limit=2):
    print(m.name, m.score)

# 4. Keep your own data in a separate folder (notes, expenses ...), so it never mixes with ~/.jeeg.
j = jeeg.JeeG(home=tempfile.mkdtemp(prefix="jeeg-demo-"), timeout=30)
j("add expense 250 food lunch")
print(j("show expenses").output)

# 5. Tasks that ask for confirmation return exit code 3 unless you pass yes=True.
r = j("shutdown pc")
print("needs confirmation:", r.needs_confirmation)

# 6. Make failures raise.
try:
    jeeg.run("qzxqzx", check=True)
except jeeg.JeeGError as e:
    print("caught:", e)
