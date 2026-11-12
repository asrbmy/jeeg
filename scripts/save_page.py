# keywords: save page, save web page, offline page, read later offline, download page text, archive page, save article
# desc: Save a web page as readable text for offline reading (save page https://example.com/article). Saved in Documents/JeeG pages.
# category: network
# network: yes
# usage: save page <url>
# rawargs: full
# patterns: ^\s*(?:save|archive|download)\s+(?:this\s+|the\s+)?(?:web\s*)?(?:page|article)\s+(?:for\s+offline\s+)?(?:from\s+)?https?:// ;; \bsave\s+(?:a\s+)?(?:web\s*)?page\s+for\s+offline\b
# priority: 4
import html, re, time
from html.parser import HTMLParser
from _lib import args_text, fail, output_dir
from _conn import check_url
from _net import get


class Text(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "head", "nav", "footer", "form", "iframe"}
    BLOCK = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "section", "article", "blockquote", "pre"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.title, self._t = [], 0, "", False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._t = True
        if tag in self.SKIP:
            self.skip += 1
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag == "title":
            self._t = False
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, d):
        if self._t:
            self.title += d
        elif not self.skip:
            self.out.append(d)


m = re.search(r"https?://\S+", args_text())
if not m:
    fail("Usage: save page https://example.com/article")
url = m.group(0).rstrip(".,;)")
u = check_url(url)
body = get(url, timeout=15)
if body is None:
    fail("Could not download that page (offline, blocked, or too big: the limit is 2 MB).")
p = Text()
p.feed(body)
text = re.sub(r"[ \t]+", " ", "".join(p.out))
text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
if len(text) < 20:
    fail("That page has no readable text (it may need JavaScript).")
title = html.unescape(re.sub(r"\s+", " ", p.title)).strip() or u.hostname
safe = re.sub(r"[^A-Za-z0-9 _-]+", "", title).strip()[:50] or "page"
out = output_dir("JeeG pages") / f"{time.strftime('%Y%m%d')}_{safe}.txt"
out.write_text(f"{title}\n{url}\nSaved {time.strftime('%Y-%m-%d %H:%M')}\n\n{text}\n", encoding="utf-8")
print(f"Saved {len(text):,} characters of text to {out}")
