# keywords: mail inbox, unread mail, unread emails, mail unread
# desc: Show your unread mail (sender, subject, date). Reads only the headers and marks nothing as read. Needs  mail setup.
# category: email
# usage: mail inbox [how many]
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*mail\s+(inbox|unread|new)\b ;; \b(unread|new)\s+(mail|emails?)\b ;; \bcheck\s+(my\s+)?mail\b
# priority: 2
import email, email.header, imaplib, re
from _lib import args_text, fail
from _conn import load_reg, split_host, is_private_host
reg = load_reg("mail")
if not reg:
    fail("No mail account yet. Run:  mail setup you@gmail.com imap.gmail.com smtp.gmail.com")
m = re.search(r"\b(\d{1,2})\b", args_text())
n = max(1, min(30, int(m.group(1)))) if m else 10


def dec(v):
    out = []
    for b, cs in email.header.decode_header(v or ""):
        out.append(b.decode(cs or "utf-8", "replace") if isinstance(b, bytes) else b)
    return " ".join("".join(out).split())[:90]


try:
    host, port = split_host(reg["imap"], 993)
    if host in {"localhost", "127.0.0.1"}:                          # a mail server on this very computer: no TLS needed
        c = imaplib.IMAP4(host, port, timeout=20)
    else:
        c = imaplib.IMAP4_SSL(host, port, timeout=20)
    c.login(reg["address"], reg["password"])
    c.select("INBOX", readonly=True)
    typ, data = c.search(None, "UNSEEN")
    ids = (data[0] or b"").split()
    print(f"{len(ids)} unread message(s)." + (f" Newest {min(n, len(ids))}:" if ids else ""))
    for i in reversed(ids[-n:]):
        typ, msg = c.fetch(i, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
        h = email.message_from_bytes(msg[0][1])
        print(f"  {dec(h['From'])[:40]:<40}  {dec(h['Subject'])}  ({(h['Date'] or '')[:16]})")
    c.logout()
except imaplib.IMAP4.error as ex:
    fail("The mail server refused the login. Gmail and others need an app password. (" + str(ex)[:80] + ")")
except (OSError, TimeoutError) as ex:
    fail(f"Could not reach the mail server: {ex}")
