# keywords: printer status, my printers, list printers, is the printer on, printer queue, printer online
# desc: List your printers and whether they are ready, and the default one
# category: system
# usage: show printers
# patterns: \bprinters?\s+(?:status|list|queue|online|ready)\b ;; \b(?:list|show|my)\s+printers?\b ;; \bis\s+(?:the\s+|my\s+)?printer\s+(?:on|online|ready|working)\b
# priority: 3
import shutil, sys
from _lib import WIN, fail
from _netdoc import parse_lpstat, parse_powershell_printers, run_text

if WIN:
    ps = shutil.which("powershell") or shutil.which("pwsh")
    if not ps:
        fail("PowerShell was not found, so I cannot list printers.")
    out = run_text([ps, "-NoProfile", "-Command", "Get-Printer | ForEach-Object { '{0}  {1}' -f $_.Name, $_.PrinterStatus }"], timeout=20)
    rows = parse_powershell_printers(out)
    default = None
else:
    if not shutil.which("lpstat"):
        fail("The printing system (CUPS) is not installed here, so I cannot list printers.")
    rows, default = parse_lpstat(run_text(["lpstat", "-p", "-d"]))
if not rows:
    print("No printers found. Add one in your system's printer settings.")
    sys.exit(0)
print(f"{len(rows)} printer(s):")
for n, s in rows:
    print(f"  {n}  -  {s}" + ("   (default)" if n == default else ""))
