# keywords: payment reminder, remind to pay, dues reminder, unpaid reminder, polite reminder to pay, overdue reminder, invoice reminder
# desc: Write a polite payment-reminder message and copy it (payment reminder ravi, or: payment reminder Ravi Traders 5000 invoice INV-0012 by 15 nov)
# category: money
# usage: payment reminder <name in your ledger | name amount [invoice X] [by date]>
# rawargs: full
# private: yes
# patterns: \bpayment\s+reminder\b ;; \b(draft|write)\b.*\b(payment|dues|overdue)\s+(reminder|message)\b ;; \bremind\b.*\b(to\s+)?pay\b ;; \binvoice\s+reminder\b
# priority: 2
import re
from _lib import args_text, fail
from _store import load
from _sys import clip_set
t = args_text()
t = re.sub(r"\b(payment|dues|invoice|overdue|polite|unpaid)\s+reminder\b|\b(draft|write|make|send)\b|\bremind\b|\bto pay\b|\bpay\b|\ba\b", " ", t, flags=re.I)
inv = re.search(r"\b(INV-\d+)\b", t, re.I)
if inv:
    t = t.replace(inv.group(1), " ")
due = re.search(r"\b(?:by|before|due)\s+(\d{1,2}\s+[A-Za-z]{3,9}(?:\s+\d{4})?|[A-Za-z]{3,9}\s+\d{1,2}(?:,?\s+\d{4})?|tomorrow|today|friday|monday|tuesday|wednesday|thursday|saturday|sunday)", t, re.I)
if due:
    t = t.replace(due.group(0), " ")
amt = re.search(r"(?:\b(?:rs\.?|inr)|₹)?\s*(\d[\d,]*(?:\.\d+)?)", t, re.I)
amount = None
if amt:
    amount = float(amt.group(1).replace(",", ""))
    t = t.replace(amt.group(0), " ", 1)
name = " ".join(w for w in re.sub(r"[^\w .'-]", " ", t).split() if w.lower() not in {"for", "to", "from", "of", "the", "me", "rs", "inr", "invoice", "bill"})
if not name:
    fail("Say who it is for, for example:  payment reminder ravi   (uses your ledger)   or   payment reminder Ravi Traders 5000 by 15 nov")
if amount is None:
    led = load("ledger.json", {})
    rec = led.get(name.split()[0].lower())
    if not rec or rec.get("balance", 0) <= 0.004:
        fail(f"'{name}' does not owe you anything in your ledger. Add an amount:  payment reminder {name} 5000")
    amount = rec["balance"]
amt_txt = f"Rs {amount:,.2f}".replace(".00", "")
ref = f" for invoice {inv.group(1).upper()}" if inv else ""
when = f" by {due.group(1)}" if due else " at your earliest convenience"
msg = (f"Hi {name.title()},\n\nA gentle reminder that a payment of {amt_txt}{ref} is still pending. "
       f"Could you please arrange it{when}? If you have already paid, please ignore this message and share the payment reference so I can update my records.\n\n"
       "Thank you!")
print(msg)
try:
    clip_set(msg)
    print("\n(Copied to the clipboard. Paste it into WhatsApp or email.)")
except (Exception, SystemExit):
    print("\n(Could not copy it automatically; select the text above and copy it.)")
