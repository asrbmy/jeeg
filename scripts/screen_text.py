# keywords: screen text, read my screen, text on my screen, copy text from screen, screen to text, screenshot to text, grab text from screen
# desc: Take a screenshot, read the text in it and copy it to the clipboard (needs pillow, pytesseract and the Tesseract program)
# category: media
# usage: screen text
# private: yes
# patterns: \b(text|words)\s+(on|from)\s+(my\s+|the\s+)?screen\b ;; \bread\s+(my\s+|the\s+)?screen\b ;; \bscreen\s*(shot)?\s+to\s+(text|clipboard)\b ;; \bcopy\s+text\s+from\s+(my\s+|the\s+)?screen\b
# priority: 2
import os, shutil, subprocess, tempfile
from pathlib import Path
from _lib import fail, need, MAC
from _sys import clip_set
need("PIL", "pillow")
need("pytesseract")
if not shutil.which("tesseract"):
    fail("The Tesseract program is not installed. Windows: github.com/UB-Mannheim/tesseract/wiki  |  Mac: brew install tesseract  |  Linux: sudo apt install tesseract-ocr")
from PIL import Image
import pytesseract
tmp = Path(tempfile.mkdtemp(prefix="jeeg-screen-"))
shot = tmp / "screen.png"
img = None
try:
    from PIL import ImageGrab
    img = ImageGrab.grab(all_screens=True)
except Exception:
    pass
if img is None:
    cmds = [["screencapture", "-x", str(shot)]] if MAC else [["grim", str(shot)], ["gnome-screenshot", "-f", str(shot)], ["scrot", str(shot)], ["import", "-window", "root", str(shot)]]
    for c in cmds:
        if shutil.which(c[0]) and subprocess.run(c, capture_output=True, timeout=20).returncode == 0 and shot.exists():
            img = Image.open(shot)
            break
if img is None:
    shutil.rmtree(tmp, ignore_errors=True)
    fail("Could not take a screenshot on this computer (no screen, or no screenshot tool).")
try:
    text = pytesseract.image_to_string(img)
finally:
    shutil.rmtree(tmp, ignore_errors=True)         # the screenshot is never kept
if not text.strip():
    fail("No text found on the screen.")
print(text.strip()[:1500])
try:
    clip_set(text)
    print(f"\nCopied {len(text.strip()):,} characters to the clipboard. The screenshot was not saved.")
except (Exception, SystemExit):
    print("\nCould not copy to the clipboard; the text is above. The screenshot was not saved.")
