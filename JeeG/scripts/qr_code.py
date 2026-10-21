# keywords: qr code, qrcode, make qr, generate qr, create qr code, qr for url, qr image, barcode
# desc: Make a QR code picture from text or a link (qr code https://example.com)
# category: text
# usage: qr code <text or link>
# rawargs: yes
import re, time
from pathlib import Path
from _lib import args_text, fail, need, open_path
t = args_text().strip().strip("\"'")
t = re.sub(r"^(?:for|of|from)\s+", "", t, flags=re.I)
if not t: fail("Usage: qr code <text or link>")
if len(t) > 1000: fail("That is too long for a QR code (limit 1000 characters).")
qrcode = need("qrcode", "qrcode[pil]")
out = Path.cwd() / ("qr_" + time.strftime("%Y%m%d_%H%M%S") + ".png")
img = qrcode.make(t)
img.save(str(out))
print(f"Saved {out}")
try: open_path(out)
except SystemExit: pass
