# keywords: receipt, receipts, add receipt, receipt total, keep receipt, bill receipt, receipt list, receipt report
# desc: Keep receipts for tax time: receipt add 450 groceries "Big Bazaar", receipt attach 3 photo.jpg, receipt list 2026-11, receipt total 2026-11, receipt report 2026
# category: money
# usage: receipt add <amount> <category> <shop...> [date YYYY-MM-DD] | receipt attach <id> <file> | receipt list [YYYY[-MM]] | receipt total [YYYY[-MM]] | receipt report <YYYY> | receipt remove <id>
# rawargs: full
# patterns: ^\s*receipts?\b
# priority: 3
import csv, io, json, re, shutil, sys, time
from pathlib import Path
from _lib import args_text, data_dir, fail
t = re.sub(r"^\s*receipts?\s*", "", args_text(), flags=re.I).strip()
cmd, _, rest = t.partition(" ")
cmd, rest = cmd.lower() or "list", rest.strip()
f = data_dir() / "receipts.json"
folder = data_dir() / "receipt_files"


def load():
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
        return d if isinstance(d, list) else []
    except (OSError, ValueError):
        return []


def save(d):
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
    tmp.replace(f)


def pick(d, period):
    if period and not re.fullmatch(r"\d{4}(-\d{2})?", period):
        fail("Give a year or month like 2026 or 2026-11.")
    return [r for r in d if r["date"].startswith(period)]


d = load()
if cmd == "add":
    m = re.match(r"([\d,]+(?:\.\d{1,2})?)\s+(\S+)\s*(.*)$", rest)
    if not m:
        fail('Usage: receipt add <amount> <category> <shop...> [date YYYY-MM-DD]   e.g.  receipt add 450 groceries Big Bazaar')
    amount = float(m.group(1).replace(",", ""))
    if amount <= 0 or amount > 1e9:
        fail("That amount does not look right.")
    shop = m.group(3)
    dm = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", shop)
    date = dm.group(1) if dm else time.strftime("%Y-%m-%d")
    if dm:
        try:
            time.strptime(date, "%Y-%m-%d")
        except ValueError:
            fail("That date does not exist. Use YYYY-MM-DD.")
        shop = shop.replace(dm.group(1), "").strip()
    rid = max([r["id"] for r in d] + [0]) + 1
    d.append({"id": rid, "date": date, "amount": amount, "category": m.group(2).lower()[:30], "shop": shop.strip('"\'')[:80], "file": ""})
    save(d)
    print(f"Receipt {rid} saved: {amount:,.2f} {m.group(2).lower()} {shop} on {date}. Attach the picture:  receipt attach {rid} <file>")
elif cmd == "attach":
    w = rest.split(None, 1)
    if len(w) < 2 or not w[0].isdigit():
        fail("Usage: receipt attach <id> <file>")
    r = next((x for x in d if x["id"] == int(w[0])), None)
    src = Path(w[1].strip("\"'")).expanduser()
    if not r:
        fail("No receipt with that id.")
    if not src.is_file() or src.stat().st_size > 30 * 1048576:
        fail("Give a picture or PDF file under 30 MB.")
    if src.suffix.lower() not in {".jpg", ".jpeg", ".png", ".pdf", ".webp", ".heic"}:
        fail("Attach a picture or PDF (jpg, png, webp, heic, pdf).")
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / f"receipt{r['id']}{src.suffix.lower()}"
    shutil.copyfile(src, dest)
    r["file"] = dest.name
    save(d)
    print(f"Attached to receipt {r['id']}: {dest}")
elif cmd in {"list", "show"}:
    rows = pick(d, rest.split()[0] if rest else "")
    if not rows:
        print("No receipts. Add one:  receipt add 450 groceries Big Bazaar")
    for r in sorted(rows, key=lambda x: (x["date"], x["id"])):
        print(f"  {r['id']:>3}  {r['date']}  {r['amount']:>10,.2f}  {r['category']:<12}{r['shop']}{'  [file]' if r.get('file') else ''}")
elif cmd == "total":
    rows = pick(d, rest.split()[0] if rest else "")
    by = {}
    for r in rows:
        by[r["category"]] = by.get(r["category"], 0) + r["amount"]
    for k, v in sorted(by.items(), key=lambda x: -x[1]):
        print(f"  {k:<14}{v:>12,.2f}")
    print(f"  {'Total':<14}{sum(by.values()):>12,.2f}   ({len(rows)} receipt(s))" if rows else "No receipts in that period.")
elif cmd == "report":
    if not re.fullmatch(r"\d{4}", rest):
        fail("Usage: receipt report <YYYY>")
    rows = sorted(pick(d, rest), key=lambda x: (x["date"], x["id"]))
    if not rows:
        fail("No receipts that year.")
    out = Path.cwd() / f"receipts_{rest}.csv"
    n = 1
    while out.exists():
        n += 1
        out = Path.cwd() / f"receipts_{rest}_{n}.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "date", "amount", "category", "shop", "file"])
        for r in rows:
            w.writerow([r["id"], r["date"], f"{r['amount']:.2f}", r["category"], r["shop"], r.get("file", "")])
    print(f"Wrote {len(rows)} receipt(s) to {out}")
elif cmd in {"remove", "delete"}:
    if not rest.isdigit() or not any(x["id"] == int(rest) for x in d):
        fail("Usage: receipt remove <id>")
    save([x for x in d if x["id"] != int(rest)])
    print("Removed (an attached file, if any, stays in the receipt_files folder).")
else:
    fail("Use:  receipt add | attach | list | total | report | remove")
