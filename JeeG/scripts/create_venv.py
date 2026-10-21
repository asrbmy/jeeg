# keywords: venv, virtual environment, virtualenv, create venv, python env, new environment
# desc: Create a Python virtual environment (.venv) here
# category: developer
import os, subprocess, sys
from _lib import WIN, fail
if os.path.isdir(".venv"):
    fail(".venv already exists here.")
if subprocess.call([sys.executable, "-m", "venv", ".venv"]):
    fail("Could not create the virtual environment.")
print("Created .venv. Activate with: " + (".venv\\Scripts\\activate" if WIN else "source .venv/bin/activate"))
