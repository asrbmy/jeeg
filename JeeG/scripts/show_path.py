# keywords: show path, path variable, print path, what is in path, path entries, system path, check path, my path
# desc: Show the folders in your PATH, one per line, marking missing ones
# category: developer
import os
seen = set()
for i, d in enumerate(p for p in os.environ.get("PATH", "").split(os.pathsep) if p):
    note = "" if os.path.isdir(d) else "   <- missing"
    note += "   (duplicate)" if d.lower() in seen else ""
    seen.add(d.lower())
    print(f"{i + 1:>3}. {d}{note}")
