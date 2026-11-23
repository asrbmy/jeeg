# keywords: identify file, what type of file, real file type, check file type, file signature, magic bytes, is this file really a pdf
# desc: Tell what a file really is from its first bytes, not its name, and warn if the name is misleading (identify file report.pdf)
# category: security
# usage: identify file <file>
# rawargs: full
# patterns: ^\s*(?:identify\s+file|real\s+file\s+type|file\s+signature|what\s+type\s+of\s+file)\b
# priority: 3
import re
from pathlib import Path
from _lib import args_text, fail
from _files import path_arg
t = re.sub(r"^\s*(?:identify\s+file|real\s+file\s+type|file\s+signature|what\s+type\s+of\s+file(?:\s+is)?)\s*", "", args_text(), flags=re.I)
p = path_arg(t)
if p.is_dir(): fail("Give a file, not a folder.")
with open(p, "rb") as f: h = f.read(4096)
SIG = [(b"%PDF-", "PDF document", {".pdf"}), (b"\x89PNG\r\n\x1a\n", "PNG image", {".png"}), (b"\xff\xd8\xff", "JPEG image", {".jpg", ".jpeg"}),
       (b"GIF8", "GIF image", {".gif"}), (b"PK\x03\x04", "ZIP container (zip, docx, xlsx, pptx, jar, apk...)", {".zip", ".docx", ".xlsx", ".pptx", ".jar", ".apk", ".odt", ".epub", ".whl"}),
       (b"\x1f\x8b", "gzip data", {".gz", ".tgz"}), (b"Rar!", "RAR archive", {".rar"}), (b"7z\xbc\xaf\x27\x1c", "7-Zip archive", {".7z"}),
       (b"MZ", "Windows program (exe/dll)", {".exe", ".dll", ".sys", ".scr"}), (b"\x7fELF", "Linux program (ELF)", {"", ".so", ".bin", ".elf"}),
       (b"\xcf\xfa\xed\xfe", "macOS program (Mach-O)", {"", ".dylib"}), (b"\xca\xfe\xba\xbe", "Java class or macOS universal program", {".class", ""}),
       (b"SQLite format 3\0", "SQLite database", {".db", ".sqlite", ".sqlite3"}), (b"\xd0\xcf\x11\xe0", "Old Microsoft Office file", {".doc", ".xls", ".ppt", ".msi"}),
       (b"RIFF", "RIFF media (wav, avi, webp)", {".wav", ".avi", ".webp"}), (b"ID3", "MP3 audio", {".mp3"}), (b"OggS", "Ogg media", {".ogg", ".oga", ".ogv"}),
       (b"#!", "Script (starts with #!)", {"", ".sh", ".py", ".pl", ".rb"}), (b"<?xml", "XML text", {".xml", ".svg", ".html", ".xhtml"})]
kind, exts = None, set()
for sig, name, e in SIG:
    if h.startswith(sig): kind, exts = name, e; break
if kind is None and len(h) > 8 and h[4:8] == b"ftyp": kind, exts = "MP4/MOV media", {".mp4", ".mov", ".m4a", ".m4v", ".heic"}
if kind is None:
    try: h.decode("utf-8"); kind, exts = "Plain text", None
    except UnicodeDecodeError: kind, exts = "Unknown binary data", None
ext = p.suffix.lower()
print(f"{p.name}: {kind}  ({p.stat().st_size:,} bytes)")
if exts is not None and ext not in exts:
    risky = kind.startswith(("Windows program", "Linux program", "macOS program", "Script"))
    print(("WARNING: " if risky else "Note: ") + f"the name ends in '{ext or '(nothing)'}' but the contents are different." + (" A program pretending to be another file type is a common trick; do not open it unless you trust where it came from." if risky else ""))
