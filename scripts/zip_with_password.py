# keywords: zip with password, password protect zip, encrypted zip, lock zip, secure zip, encrypt files, zip and encrypt, password zip
# desc: Make a password-protected AES zip of a file or folder (the password is asked privately, not typed in the command)
# category: files
# usage: zip with password <file|folder>
# rawargs: yes
# private: yes
# patterns: \b(zip|archive)\b.*\bpassword\b ;; \b(password|encrypt)\w*\b.*\bzip\b ;; \bencrypted zip\b
import getpass, os, re, sys
from pathlib import Path
from _lib import args_text, fail, need
from _files import path_arg, unique_path, walk_files
from _files import drop_tokens
t = drop_tokens(args_text(), {"zip", "with", "password", "protect", "protected", "encrypted", "encrypt", "lock", "secure", "and", "a", "the", "file", "folder", "of", "my"})
if not t: fail("Usage: zip with password <file or folder>")
pz = need("pyzipper", "pyzipper")
src = path_arg(t)
if src == Path.home().resolve() or src == Path(src.anchor): fail("Choose a specific file or folder, not your whole home folder or drive.")
if not sys.stdin.isatty(): fail("This needs a keyboard to ask for the password.")
pw = getpass.getpass("Password (not shown): ")
if len(pw) < 6: fail("Use at least 6 characters.")
if getpass.getpass("Repeat password: ") != pw: fail("The passwords did not match.")
out = unique_path(src.with_suffix(".zip") if src.is_file() else src.parent / (src.name + ".zip"))
n = total = 0
with pz.AESZipFile(out, "w", compression=pz.ZIP_DEFLATED, encryption=pz.WZ_AES) as z:
    z.setpassword(pw.encode("utf-8"))
    if src.is_file():
        z.write(src, src.name); n = 1
    else:
        for p, st in walk_files(src, seconds=60, hidden=True):
            total += st.st_size
            if total > 2 * 1024 ** 3: out.unlink(); fail("That is larger than 2 GB; refusing.")
            z.write(p, os.path.relpath(p, src.parent)); n += 1
print(f"Encrypted {n} file(s) with AES-256 -> {out}")
print("Remember the password: it cannot be recovered. Open with 7-Zip, WinRAR or The Unarchiver (the built-in Windows extractor does not support AES).")
