# keywords: share file, send file to phone, send file over wifi, file to phone, share with phone, qr download, transfer file to phone
# desc: Send one file to your phone or another computer on the same Wi-Fi: shows a link and QR code, serves that one file once, then stops
# category: network
# network: yes
# usage: send <file> to my phone
# rawargs: full
# patterns: ^\s*(?:share|send|transfer)\s+(?:the\s+|this\s+|my\s+)?(?:file\s+)?\S.*\s+(?:to|with|over)\s+(?:my\s+)?(?:phone|mobile|wi-?fi|other\s+(?:computer|laptop|pc))\b
# priority: 4
import http.server, os, re, secrets, socket, sys, threading, time
from pathlib import Path
from urllib.parse import quote
from _lib import args_text, fail, safe_is_file
from _netdoc import local_ip

t = args_text().strip().strip("\"'")
t = re.sub(r"^(?:share|send|transfer)\s+(?:the\s+|this\s+|my\s+)?(?:file\s+)?", "", t, flags=re.I)
t = re.sub(r"\s+(?:to|with|over)\s+(?:my\s+)?(?:phone|mobile|wi-?fi|other\s+(?:computer|laptop|pc)).*$", "", t, flags=re.I).strip().strip("\"'")
p = Path(os.path.expanduser(t)) if t else None
if p is None or not safe_is_file(p):
    fail("Say which file, for example:  send report.pdf to my phone")
p = p.resolve()
host = "127.0.0.1" if os.environ.get("JEEG_SHARE_LOCAL") == "1" else (local_ip() or "")      # the test switch only ever narrows to this computer
if not host:
    fail("This computer is not on a network, so there is nothing to share over.")
try:
    secs = max(5, min(int(os.environ.get("JEEG_SHARE_SECONDS", "600")), 3600))
except ValueError:
    secs = 600
token = secrets.token_urlsafe(16)
path = f"/{token}/{quote(p.name)}"
done = threading.Event()


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if not secrets.compare_digest(self.path.encode(), path.encode()):
            self.send_error(404)
            return
        try:
            size = p.stat().st_size
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition", "attachment; filename*=UTF-8''" + quote(p.name))
            self.end_headers()
            with open(p, "rb") as f:
                while True:
                    b = f.read(65536)
                    if not b:
                        break
                    self.wfile.write(b)
            done.set()
        except OSError:
            pass


srv = http.server.ThreadingHTTPServer((host, 0), H)
url = f"http://{host}:{srv.server_address[1]}{path}"
print(f"Sharing {p.name} ({p.stat().st_size:,} bytes). Open this on your phone (same Wi-Fi):\n  {url}")
try:
    import qrcode
    q = qrcode.QRCode(border=1)
    q.add_data(url)
    q.make(fit=True)
    q.print_ascii(invert=True)
except Exception:
    print("(Install the qrcode package for a scannable code:  pip install qrcode)")
print(f"One download, then it stops. It also stops after {secs // 60 or 1} minute(s), or press Ctrl+C.")
sys.stdout.flush()
threading.Thread(target=srv.serve_forever, daemon=True).start()
try:
    done.wait(secs)
except KeyboardInterrupt:
    pass
time.sleep(0.2)
srv.shutdown()
srv.server_close()
print("Downloaded. Sharing stopped." if done.is_set() else "Time is up. Sharing stopped.")
