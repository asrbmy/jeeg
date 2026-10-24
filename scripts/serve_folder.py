# keywords: serve, http server, local server, web server, host folder, localhost server, preview site
# desc: Serve the current folder at http://localhost:8000
# category: developer
# network: yes
# usage: serve folder [port]
import functools, http.server, re, socketserver, threading, webbrowser
from _lib import args_text, fail
m = re.search(r"\d{2,5}", args_text())
port = int(m.group()) if m else 8000
if not 1024 <= port <= 65535:
    fail("Use a port between 1024 and 65535.")
h = functools.partial(http.server.SimpleHTTPRequestHandler)
socketserver.TCPServer.allow_reuse_address = True
try:
    with socketserver.TCPServer(("127.0.0.1", port), h) as srv:
        print(f"Serving this folder at http://localhost:{port}  (Ctrl+C to stop)")
        threading.Timer(0.5, lambda: webbrowser.open(f"http://localhost:{port}")).start()
        srv.serve_forever()
except OSError as e:
    fail(f"Could not start on port {port}: {e}")
except KeyboardInterrupt:
    print("\nStopped.")
