# keywords: decode, decode base64, b64 decode, base64 decode, decrypt base64
# desc: Decode Base64 text
# category: utility
# usage: decode base64 <text>
import base64, binascii
from _lib import args_text, fail
t = args_text().strip()
if not t: fail('Usage: decode base64 <text>')
try:
    print(base64.b64decode(t + '=' * (-len(t) % 4), validate=True).decode('utf-8', 'replace'))
except (binascii.Error, ValueError):
    fail('That is not valid Base64.')
