# keywords: convert encoding, fix encoding, utf-8 convert, garbled text, weird characters, text encoding, change encoding, save as utf8, fix strange characters
# desc: Fix garbled text by saving a file as UTF-8 (convert encoding old.txt)
# category: files
# usage: convert encoding <file>
# rawargs: yes
import re
from _lib import args_text, fail
from _files import path_arg, unique_path
p = path_arg(re.sub(r"^\s*(?:(?:convert|fix|change)\s+)?(?:(?:file|text)\s+)?(?:encoding|to utf-?8)?\s*(?:of|for|file)?\s*", "", args_text(), flags=re.I))
if p.is_dir() or p.stat().st_size > 50 * 1024 * 1024: fail("Give one text file under 50 MB.")
raw = p.read_bytes()
tries = []
if raw.startswith((b"\xff\xfe", b"\xfe\xff")): tries.append("utf-16")
if raw.startswith(b"\xef\xbb\xbf"): tries.append("utf-8-sig")
tries += ["utf-8", "cp1252", "latin-1"]
for enc in tries:
    try: text = raw.decode(enc); break
    except UnicodeDecodeError: continue
out = unique_path(p.with_name(p.stem + "_utf8" + p.suffix))
out.write_bytes(text.encode("utf-8"))
print(f"Read as {enc}; saved as UTF-8 -> {out}")
if enc in ("cp1252", "latin-1"): print("(a guess: if letters still look wrong the file may use another encoding, e.g. a regional one)")
