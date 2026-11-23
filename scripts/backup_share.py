# keywords: backup share
# desc: Share a backup zip of your JeeG data to a paired computer over the encrypted link (backup share kitchen-pc). It arrives in their Downloads/JeeG received folder. Asks first.
# category: backup
# usage: backup share <computer>
# rawargs: full
# network: yes
# confirm: yes
# patterns: ^\s*backup\s+share\b
# priority: 5
import json, re, sys, tempfile, time, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import args_text, fail, data_dir
from _backup import data_files, mark
import jeeg_link

name = re.sub(r"^\s*backup\s+share\s*", "", args_text(), flags=re.I).strip()
if not name:
    fail("Usage: backup share <computer>     (see:  link peers)")
store = jeeg_link.Store(data_dir())
pid, rec = store.find(name)
if not pid:
    fail(f"No paired computer is called '{name}'. See:  link peers")
files = data_files()
if not files:
    fail("You have no saved data yet (nothing to back up).")
with tempfile.TemporaryDirectory(prefix="jeeg-bk-") as tmp:
    out = Path(tmp) / time.strftime("jeeg_backup_%Y%m%d_%H%M.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps({"jeeg": "backup", "format": 1, "created": time.strftime("%Y-%m-%d %H:%M:%S"), "files": [p.name for p in files]}, indent=1))
        for p in files:
            z.write(p, p.name)
    try:
        chan = jeeg_link.open_session(store, pid, rec)
        try:
            got = jeeg_link.send_file(chan, out)
        finally:
            try:
                chan.send({"t": "bye"})
            except (OSError, jeeg_link.LinkError):
                pass
            chan.sock.close()
    except (jeeg_link.LinkError, OSError) as ex:
        fail(f"Link problem: {getattr(ex, 'strerror', None) or ex}")
mark()
print(f"Sent {len(files)} file(s) to {rec['name']} as {got}. It is in their Downloads/JeeG received folder; they restore it with:  import data <file>")
print("The link encrypts it in transit. The zip itself is not encrypted, so keep it somewhere safe.")
