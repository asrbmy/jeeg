# keywords: base64, encode, encode base64, b64
# desc: Base64-encode text
# category: utility
# usage: encode base64 <text>
import base64
from _lib import args_text, fail
t = args_text()
if not t: fail('Usage: encode base64 <text>')
print(base64.b64encode(t.encode()).decode())
