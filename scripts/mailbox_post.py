# keywords: mailbox post, post mail from my mailbox
# desc: Send a mail from your saved account (mail send bob@example.com | Subject | Body). It asks first. Needs  mail setup.
# category: email
# usage: mail send <to> | <subject> | <body>
# confirm: yes
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*mail\s+send\b
# priority: 4
import re, smtplib, ssl
from email.message import EmailMessage
from _lib import args_text, fail
from _conn import load_reg, split_host
reg = load_reg("mail")
if not reg:
    fail("No mail account yet. Run:  mail setup you@gmail.com imap.gmail.com smtp.gmail.com")
t = re.sub(r"^\s*mail\s+send\s*", "", args_text(), flags=re.I)
parts = [p.strip() for p in t.split("|", 2)]
if len(parts) < 3 or not parts[0] or not parts[2]:
    fail("Usage: mail send <to> | <subject> | <body>")
to, subject, body = parts
if not re.fullmatch(r"[^@\s,;<>]+@[^@\s,;<>]+\.[A-Za-z]{2,}", to):
    fail("Give one valid address to send to.")
if re.search(r"[\r\n]", subject) or len(subject) > 200 or len(body) > 20000:
    fail("The subject must be one short line and the body under 20,000 characters.")
msg = EmailMessage()
msg["From"], msg["To"], msg["Subject"] = reg["address"], to, subject
msg.set_content(body)
ctx = ssl.create_default_context()
try:
    host, port = split_host(reg["smtp"], 0)
    if host in {"localhost", "127.0.0.1"}:                          # a mail server on this very computer: no TLS needed
        s = smtplib.SMTP(host, port or 25, timeout=20)
    elif port == 465 or not port:
        try:
            s = smtplib.SMTP_SSL(host, port or 465, timeout=20, context=ctx)
        except (OSError, ssl.SSLError):
            if port:
                raise
            s = smtplib.SMTP(host, 587, timeout=20)
            s.starttls(context=ctx)
    else:
        s = smtplib.SMTP(host, port, timeout=20)
        s.starttls(context=ctx)
    with s:
        s.login(reg["address"], reg["password"])
        s.send_message(msg)
except smtplib.SMTPAuthenticationError:
    fail("The mail server refused the login. Gmail and others need an app password.")
except (smtplib.SMTPException, OSError) as ex:
    fail(f"Could not send: {ex}")
print(f"Sent to {to}.")
