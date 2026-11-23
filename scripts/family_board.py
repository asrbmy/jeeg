# keywords: board, family board, shared list, shared to do, shared chores, team board, board add, board done
# desc: A shared to-do board for a family or small team. Items sync to the paired computers you share the 'board' channel with (board add buy milk, board list, board done 2, channel share board with kitchen-pc)
# category: lists
# usage: board add <text> | board list | board done <number> | board undo <number>
# rawargs: full
# network: yes
# patterns: ^\s*board\b
# priority: 3
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import args_text, fail, data_dir
import jeeg_chan, jeeg_link

base = data_dir()
CH = "board"
t = re.sub(r"^\s*board\s*", "", args_text(), flags=re.I).strip()
cmd, _, rest = t.partition(" ")
cmd, rest = cmd.lower() or "list", rest.strip()
me = jeeg_link.Store(base).identity()["name"]


def state():
    """-> ordered list of [msg_id, text, done]. Messages: 'TODO <text>', 'DONE <id>', 'UNDO <id>'."""
    items, order = {}, []
    for m in jeeg_chan.read(base, CH, jeeg_chan.MAX_PULL):
        tx = str(m.get("text", ""))
        if tx.startswith("TODO "):
            items[m["id"]] = [tx[5:], False, m.get("from", "?")]
            order.append(m["id"])
        elif tx.startswith(("DONE ", "UNDO ")):
            k = tx[5:].strip()
            if k in items:
                items[k][1] = tx.startswith("DONE ")
    return [(i, *items[i]) for i in order]


def post(text):
    m = jeeg_chan.post(base, CH, text, me)
    if jeeg_chan.shared_with(base, CH):
        for name, err in jeeg_link.broadcast(base, CH, dict(m, **{"as": ""})):
            if err:
                print(f"  {name}: not delivered ({err}); they can catch up with  channel pull board from {me}")
    return m


try:
    if cmd == "add":
        if not rest:
            fail("Usage: board add <text>")
        post("TODO " + rest[:300])
        print("Added. " + ("" if jeeg_chan.shared_with(base, CH) else "(Only on this computer. To share:  channel share board with <computer>, on both computers.)"))
    elif cmd in {"list", "show"}:
        rows = state()
        if not rows:
            print("The board is empty. Add something:  board add buy milk")
        for n, (i, tx, done, who) in enumerate(rows, 1):
            if not done:
                print(f"  {n:>2}. [ ] {tx}   ({who})")
        d = [r for r in rows if r[2]]
        if d:
            print(f"  {len(d)} done: " + ", ".join(f"{n}" for n, r in enumerate(rows, 1) if r[2]))
    elif cmd in {"done", "undo"}:
        rows = state()
        if not rest.isdigit() or not 1 <= int(rest) <= len(rows):
            fail(f"Usage: board {cmd} <number from  board list>")
        post(("DONE " if cmd == "done" else "UNDO ") + rows[int(rest) - 1][0])
        print("Marked done." if cmd == "done" else "Marked not done.")
    else:
        fail("Use:  board add | list | done | undo")
except jeeg_chan.ChanError as ex:
    fail(str(ex))
