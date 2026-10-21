# keywords: localhost, local site, local host, dev server, open port, 127.0.0.1
# desc: Open http://localhost:<port> in the browser
# category: developer
# usage: open localhost [port]
import re, webbrowser
from _lib import args_text
m = re.search(r"\d{2,5}", args_text())
webbrowser.open(f"http://localhost:{m.group() if m else 3000}")
