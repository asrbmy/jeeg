"""A small script that builds a text report from several JeeG tasks."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))  # lets this run from a plain download; not needed after pip install
import jeeg

j = jeeg.JeeG(timeout=20)
parts = {"Battery": "battery", "Disk space": "disk space", "Today": "show time"}
for title, phrase in parts.items():
    r = j(phrase)
    print(f"== {title} ==\n{r.output if r.ok else '(not available)'}\n")
