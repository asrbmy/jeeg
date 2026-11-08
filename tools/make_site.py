#!/usr/bin/env python3
"""Rebuild docs/tasks.html (a searchable list of every task) and the terminal screenshots in docs/img/.
    python tools/make_site.py
The page needs no internet: the task list is written into the page itself."""
import html
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = dict(os.environ, JEEG_HOME=tempfile.mkdtemp(prefix="jeeg-site-"))


def jeeg(*a, input=None):
    r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *a], capture_output=True, text=True, env=env, input=input, timeout=120,
                       stdin=None if input is not None else subprocess.DEVNULL)
    return (r.stdout + r.stderr).rstrip("\n")


tasks = json.loads(jeeg("--list-json"))
version = jeeg("--version").split()[-1]
data = json.dumps(sorted(tasks, key=lambda t: (t["category"], t["name"])), separators=(",", ":")).replace("</", "<\\/")
page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JeeG tasks</title>
<style>
:root{--bg:#fbfaf7;--fg:#1c1b19;--mut:#6b6860;--card:#fff;--line:#e4e1d9;--acc:#0b6e5b;--chip:#e8f3ef}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#161715;--fg:#ecebe6;--mut:#9b988f;--card:#1f201d;--line:#34352f;--acc:#5fcfb4;--chip:#223a33}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:860px;margin:0 auto;padding:28px 16px 60px}h1{font-size:28px;margin:0 0 4px}p.s{color:var(--mut);margin:0 0 18px}
input{width:100%;padding:12px 14px;font:inherit;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--fg)}
input:focus-visible,button:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}button.c{border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;padding:4px 11px;font:inherit;font-size:14px;cursor:pointer}
button.c[aria-pressed=true]{background:var(--acc);color:var(--bg);border-color:var(--acc)}
.t{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:8px 0}.t b{font-size:16px}
.t code{display:block;color:var(--acc);font-size:14px;margin-top:2px;word-break:break-word}.t span{color:var(--mut);font-size:13px}
.tag{background:var(--chip);color:var(--acc);border-radius:6px;padding:0 6px;font-size:12px;margin-left:6px}
#n{color:var(--mut);font-size:14px}a{color:var(--acc)}
</style></head><body><main>
<h1>JeeG tasks</h1><p class="s">__COUNT__ tasks, version __VERSION__. Type what you want to do in plain words; this page only helps you find the wording. <a href="index.html">Back to the start</a></p>
<label for="q" class="s">Search tasks</label><input id="q" type="search" placeholder="gst, pdf, weather, flatmates ..." autocomplete="off">
<div class="chips" id="chips" role="group" aria-label="Categories"></div><div id="n" aria-live="polite"></div><div id="list"></div>
<script>
const T=__DATA__;let cat="";const q=document.getElementById("q"),list=document.getElementById("list"),chips=document.getElementById("chips"),n=document.getElementById("n");
const cats=[...new Set(T.map(t=>t.category))];
function chip(label,val){const b=document.createElement("button");b.className="c";b.textContent=label;b.setAttribute("aria-pressed",String(cat===val));b.onclick=()=>{cat=val;draw()};return b}
function esc(s){return s.replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function draw(){chips.replaceChildren(chip("all",""),...cats.map(c=>chip(c,c)));
 const w=q.value.toLowerCase().split(/\\s+/).filter(Boolean);
 const r=T.filter(t=>(!cat||t.category===cat)&&w.every(x=>(t.name+" "+t.description+" "+t.usage+" "+t.category).toLowerCase().includes(x)));
 n.textContent=r.length+" of "+T.length+" tasks";
 list.innerHTML=r.slice(0,300).map(t=>`<div class="t"><b>${esc(t.name.replace(/_/g," "))}</b><span class="tag">${esc(t.category)}</span>${t.online?'<span class="tag">needs internet</span>':''}${t.confirm?'<span class="tag">asks first</span>':''}<br><span>${esc(t.description)}</span>${t.usage?`<code>${esc(t.usage)}</code>`:""}</div>`).join("")}
q.addEventListener("input",draw);draw();
</script></main></body></html>
"""
page = page.replace("__DATA__", data).replace("__COUNT__", str(len(tasks))).replace("__VERSION__", html.escape(version))
(ROOT / "docs" / "tasks.html").write_text(page, encoding="utf-8")
print(f"docs/tasks.html: {len(tasks)} tasks")


def screen(name, title, lines):
    """A small terminal-style picture as SVG (real output, no images or fonts needed)."""
    lh, pad = 20, 16
    h = pad * 2 + 30 + lh * len(lines)
    rows = []
    for i, (kind, text) in enumerate(lines):
        col = {"cmd": "#7ee0c3", "out": "#e6e6e6", "dim": "#8d8d8d"}[kind]
        rows.append(f'<text x="{pad}" y="{pad + 30 + lh * (i + 1) - 6}" fill="{col}" xml:space="preserve">{html.escape(text)}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="{h}" viewBox="0 0 720 {h}" role="img" aria-label="{html.escape(title)}">'
           f'<rect width="720" height="{h}" rx="10" fill="#1b1c1a"/><rect width="720" height="30" rx="10" fill="#2a2b28"/><rect y="20" width="720" height="10" fill="#2a2b28"/>'
           f'<circle cx="18" cy="15" r="5" fill="#ff5f56"/><circle cx="36" cy="15" r="5" fill="#ffbd2e"/><circle cx="54" cy="15" r="5" fill="#27c93f"/>'
           f'<text x="360" y="20" text-anchor="middle" fill="#9a9a96" font-family="system-ui,sans-serif" font-size="12">{html.escape(title)}</text>'
           f'<g font-family="ui-monospace,Menlo,Consolas,monospace" font-size="13.5">{"".join(rows)}</g></svg>')
    (ROOT / "docs" / "img" / f"{name}.svg").write_text(svg, encoding="utf-8")


def real(*a, n=6, input=None):
    return [("out", l[:84]) for l in jeeg(*a, input=input).splitlines() if l.strip() and not l.startswith("ok in")][:n]


screen("terminal", "JeeG in the terminal", [("cmd", "$ jeeg gst 2500 18")] + real("gst", "2500", "18", n=5) +
       [("cmd", "$ jeeg gst 2500 18 then save it to a note")] + real("gst", "2500", "18", "then", "save", "it", "to", "a", "note", n=3))
screen("python", "Use JeeG from Python", [("cmd", ">>> import jeeg"), ("cmd", '>>> r = jeeg.run("sip goal 1 million in 15 years at 8%")'), ("cmd", ">>> print(r.ok, r.task)"),
                                          ("out", "True sip_goal"), ("cmd", ">>> print(r.output)")] + [x for x in real("sip", "goal", "1", "million", "in", "15", "years", "at", "8%", n=6) if not x[1].startswith(">>")][:3] +
       [("cmd", ">>> jeeg.gst_amount(1000, 18).ok"), ("out", "True")])
screen("api", "Local API for other programs", [("cmd", "$ jeeg --serve-api"), ("dim", "JeeG API: http://127.0.0.1:8766/v1/  (this computer only)"), ("dim", "Token: ********"),
                                               ("cmd", '$ curl -H "Authorization: Bearer $TOKEN" -d \'{"query":"gst 2500 18"}\' \\'), ("cmd", "      http://127.0.0.1:8766/v1/run"),
                                               ("out", '{"ok": true, "result": {"exit": 0, "ok": true, "task": "gst_amount", "output": "..."}}')])
screen("mcp", "JeeG as an MCP tool", [("cmd", "$ jeeg --mcp --only money,text"), ("dim", "(your app connects; JeeG answers with tools:)"), ("out", "jeeg_run   - run a task from plain words"),
                                      ("out", "jeeg_find  - which task matches a phrase"), ("out", "jeeg_list  - list the allowed tasks"), ("dim", "Tasks outside money and text are refused.")])
print("docs/img: 4 screenshots")
