# keywords: cite, citation, bibliography, apa citation, mla citation, reference format, cite book, cite website, make reference
# desc: Format a citation in APA and MLA (cite book Smith, John; Deep Learning; 2020; MIT Press)
# category: study
# usage: cite <book|article|web> <author>; <title>; <year or source>; ...
# rawargs: full
# patterns: \b(apa|mla)\s+(citation|reference)\b ;; ^\s*(make\s+a\s+)?(citation|cite|bibliography)\b ;; \bcite\s+(a\s+)?(book|article|website|web|journal)\b
# priority: 2
import re
from _lib import args_text, fail
t = args_text().strip()
m = re.match(r"^(?:please\s+)?(?:make\s+|write\s+|create\s+)?(?:an?\s+)?(?:apa\s+|mla\s+)?(?:citation|cite|reference|bibliography)\s*(?:for\s+)?(?:an?\s+)?(book|article|journal|web|website|site|page)?\s*[:\-]?\s*(.*)$", t, re.I | re.S)
kind = (m.group(1) or "book").lower() if m else "book"
rest = (m.group(2) if m else t).strip()
f = [x.strip() for x in rest.split(";")]
need_n = {"book": 4, "article": 5, "journal": 5, "web": 4, "website": 4, "site": 4, "page": 4}.get(kind, 4)
if len(f) < 3 or not f[0]:
    fail("Usage: cite book Smith, John; Deep Learning; 2020; MIT Press\n"
         "       cite article Lee, Ann; Sleep and memory; Journal of Rest; 2021; 12(3), 45-60\n"
         "       cite web Roy, Sam; How tides work; Ocean Guide; 2022; https://example.org/tides")
f += [""] * (6 - len(f))
def names(a):
    out = []
    for p in re.split(r"\s+and\s+|&", a):
        p = p.strip()
        if "," in p:
            last, first = [x.strip() for x in p.split(",", 1)]
        else:
            bits = p.split()
            last, first = (bits[-1], " ".join(bits[:-1])) if len(bits) > 1 else (p, "")
        out.append((last, first))
    return out
def apa_name(l, fi):
    ini = " ".join(x[0].upper() + "." for x in re.split(r"[\s.]+", fi) if x)
    return f"{l}, {ini}".strip(", ")
def mla_name(l, fi):
    return f"{l}, {fi}".strip(", ")
ns = names(f[0])
apa_a = ", & ".join([", ".join(apa_name(*n) for n in ns[:-1]), apa_name(*ns[-1])]) if len(ns) > 1 else apa_name(*ns[0])
mla_a = (mla_name(*ns[0]) + (", and " + " ".join(x for x in ns[1][::-1] if x) if len(ns) == 2 else ", et al." if len(ns) > 2 else ""))
if kind == "book":
    title, year, pub = f[1], f[2], f[3]
    apa = f"{apa_a} ({year}). {title}. {pub}.".replace(" .", ".")
    mla = f"{mla_a}. {title}. {pub}, {year}.".replace(", .", ".")
elif kind in ("article", "journal"):
    title, journal, year, vol = f[1], f[2], f[3], f[4]
    apa = f"{apa_a} ({year}). {title}. {journal}, {vol}."
    mla = f"{mla_a}. \"{title}.\" {journal}, {vol}, {year}."
else:
    title, site, year, url = f[1], f[2], f[3], f[4]
    apa = f"{apa_a} ({year}). {title}. {site}. {url}".strip()
    mla = f"{mla_a}. \"{title}.\" {site}, {year}, {url}.".replace(", ,", ",")
print("APA :", re.sub(r"\.\.+", ".", apa))
print("MLA :", re.sub(r"\.\.+", ".", mla))
print("(Italicise the book title or journal name when you paste this into your document.)")
