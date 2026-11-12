# keywords: print file, print document, print pdf, print this, send to printer
# desc: Print a file on your default printer (print report.pdf; add "preview" to see the command only)
# category: system
# usage: print <file> [preview]
# confirm: yes
# rawargs: full
# patterns: ^\s*print\s+(?:the\s+|this\s+|my\s+)?(?:file\s+|document\s+|pdf\s+)?\S+\.\w{2,5}\b
# priority: 4
import os, re, shutil, subprocess
from pathlib import Path
from _lib import WIN, args_text, fail, safe_is_file

t = args_text().strip()
preview = bool(re.search(r"\b(preview|dry-run|dryrun)\b", t, re.I))
t = re.sub(r"\b(preview|dry-run|dryrun)\b", "", t, flags=re.I)
t = re.sub(r"^\s*print\s+(?:the\s+|this\s+|my\s+)?(?:file\s+|document\s+|pdf\s+)?", "", t, flags=re.I).strip().strip("\"'")
p = Path(os.path.expanduser(t)) if t else None
if p is None or not safe_is_file(p):
    fail("Say which file, for example:  print report.pdf")
p = p.resolve()
if WIN:
    ps = shutil.which("powershell") or shutil.which("pwsh")
    if not ps:
        fail("PowerShell was not found.")
    cmd = [ps, "-NoProfile", "-Command", "Start-Process -FilePath $args[0] -Verb Print", str(p)]
    shown = f"powershell Start-Process -Verb Print {p}"
else:
    lp = shutil.which("lp")
    if not lp:
        fail("The printing system (CUPS) is not installed here.")
    cmd = [lp, "--", str(p)]
    shown = " ".join(cmd)
print("Command:  " + shown)
if preview:
    print("Preview only: nothing was printed.")
    raise SystemExit(0)
r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=60)
print((r.stdout + r.stderr).strip()[:500] or "Sent to the printer.")
raise SystemExit(0 if r.returncode == 0 else 1)
