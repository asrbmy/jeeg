# keywords: fetch remote file, save remote file, get file from link
# desc: Download a file from a web address into your Downloads folder (download https://example.com/a.pdf); asks first, refuses programs and scripts
# category: network
# network: yes
# confirm: yes
# usage: download <https address> [preview]
# rawargs: full
# patterns: ^\s*download\s+(?:this\s+|the\s+)?(?:file\s+|link\s+)?https?:// ;; ^\s*download\s+file\b ;; ^\s*download\s+(?:this\s+)?(?:file|link)\s+
# priority: 4
import re, shutil, urllib.error, urllib.parse, urllib.request
from pathlib import Path
from _lib import args_text, fail
from _conn import check_url, is_private_host
from _net import UA
from _files import unique_path
t = args_text()
preview = bool(re.search(r"\b(preview|dry-run|dryrun)\b", t, re.I))
t = re.sub(r"\b(preview|dry-run|dryrun)\b", " ", t, flags=re.I)
t = re.sub(r"^\s*download\s+(?:this\s+|the\s+)?(?:file\s+|link\s+)?(?:from\s+)?", "", t, flags=re.I).strip().strip("\"'")
u = check_url(t, allow_private_http=True)
import os
if os.environ.get("JEEG_VIA_AI") == "1":                 # an AI may not fetch from this computer or your network
    import _cdp
    why = _cdp.check_url(t, True)
    if why:
        fail(why)
BAD = {".exe", ".msi", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".jar", ".scr", ".dll", ".com", ".sh", ".app", ".dmg", ".pkg", ".apk", ".lnk", ".reg", ".hta", ".msix", ".deb", ".rpm", ".appimage", ".py"}
LIMIT = 500 * 1024 * 1024
def name_of(url, cd=""):
    m = re.search(r"filename\*?=(?:UTF-8'')?\"?([^\";]+)", cd or "", re.I)
    n = urllib.parse.unquote(m.group(1)) if m else urllib.parse.unquote(Path(url.path).name)
    n = re.sub(r"[^\w.\- ]", "_", Path(n.replace("\\", "/")).name).strip(" .")[:100]
    return n or "download"
n = name_of(u)
if Path(n).suffix.lower() in BAD:
    fail(f"I will not download '{n}': programs and scripts could harm your computer. Download it yourself if you trust it.")
if preview:
    print(f"Would download {u.scheme}://{u.hostname}{u.path[:60]} into your Downloads folder as {n}. Nothing was changed.")
    raise SystemExit(0)
dest_dir = Path.home() / "Downloads"
dest_dir.mkdir(exist_ok=True)
req = urllib.request.Request(t, headers=UA)
try:
    r = urllib.request.urlopen(req, timeout=20)
except (urllib.error.URLError, OSError, ValueError) as ex:
    fail(f"Could not download it: {getattr(ex, 'reason', ex)}")
with r:
    fin = urllib.parse.urlparse(r.geturl())
    if not fin.hostname or (fin.scheme != "https" and not (fin.scheme == "http" and is_private_host(fin.hostname))):
        fail("The link redirected to a page that is not https, so I stopped.")
    n = name_of(fin, r.headers.get("Content-Disposition", "")) if r.headers.get("Content-Disposition") else name_of(fin)
    if Path(n).suffix.lower() in BAD:
        fail(f"I will not download '{n}': programs and scripts could harm your computer.")
    size = int(r.headers.get("Content-Length") or 0)
    if size > LIMIT:
        fail(f"That file is {size // 1048576} MB; my limit is 500 MB.")
    dest = unique_path(dest_dir / n)
    got = 0
    part = dest.with_suffix(dest.suffix + ".part")
    try:
        with open(part, "wb") as fh:
            while True:
                b = r.read(1 << 16)
                if not b:
                    break
                got += len(b)
                if got > LIMIT:
                    raise OSError("too big")
                fh.write(b)
        part.replace(dest)
    except OSError as ex:
        part.unlink(missing_ok=True)
        fail(f"Download stopped: {ex}")
print(f"Saved {dest} ({got / 1048576:.1f} MB).")
