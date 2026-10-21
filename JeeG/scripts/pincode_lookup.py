# keywords: pincode, pin code, postal code, zip, post office, postcode, area code
# desc: Look up an Indian PIN code (pincode 110001) (needs internet)
# category: info
# usage: pincode <PIN>
# rawargs: yes
import re
from _lib import args_text, fail
from _info import pincode
m = re.search(r"\b\d{6}\b", args_text())
if not m: fail("Usage: pincode <6-digit PIN>   e.g. pincode 110001")
r = pincode(m.group())
if r is None: fail("Could not reach the postal service (offline?). Try again.")
if not r: fail(f"No post office found for {m.group()}.")
print(r)
