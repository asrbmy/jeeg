# keywords: mail setup, mail account, mail login, set up mail, mail forget, mail status, connect my mail
# desc: Save your mail account for mail tasks (mail setup you@gmail.com imap.gmail.com smtp.gmail.com). Uses an app password, asked privately.
# category: email
# usage: mail setup <address> <imap host> <smtp host> | mail status | mail forget
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*mail\s+(setup|status|forget|login)\b
# priority: 4
import re
from _lib import args_text, fail
from _conn import load_reg, save_reg, ask_secret
t = re.sub(r"^\s*mail\s*", "", args_text(), flags=re.I).strip()
parts = t.split()
cmd = parts[0].lower() if parts else "status"
reg = load_reg("mail")
HOST = re.compile(r"(?:[A-Za-z0-9][A-Za-z0-9.\-]+\.[A-Za-z]{2,}|localhost|127\.0\.0\.1)(?::\d{2,5})?")
if cmd == "status":
    print(f"Mail account: {reg['address']} (imap {reg['imap']}, smtp {reg['smtp']}). The password is stored privately." if reg else
          "No mail account saved. Use an app password (not your normal password):  mail setup you@gmail.com imap.gmail.com smtp.gmail.com")
elif cmd in {"setup", "login"}:
    if len(parts) != 4 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}", parts[1]) or not HOST.fullmatch(parts[2]) or not HOST.fullmatch(parts[3]):
        fail("Usage: mail setup <your address> <imap host> <smtp host>   e.g. mail setup you@gmail.com imap.gmail.com smtp.gmail.com")
    pw = ask_secret(f"App password for {parts[1]} (typing is hidden): ")
    if not pw:
        fail("No password given. Nothing was saved.")
    save_reg("mail", {"address": parts[1], "imap": parts[2], "smtp": parts[3], "password": pw})
    print("Saved privately. Try:  mail inbox      or      mail send someone@example.com | Subject | Body")
elif cmd == "forget":
    save_reg("mail", {})
    print("Mail account removed.")
else:
    fail("Use:  mail setup | status | forget")
