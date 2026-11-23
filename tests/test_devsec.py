"""Developer and security tasks. Run: python tests/test_devsec.py"""
import os, subprocess, sys, tempfile, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TMP = Path(tempfile.mkdtemp(prefix="jeeg-ds-"))
P = F = 0
def ok(c, l):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", l)
env = dict(os.environ, JEEG_HOME=str(TMP / "h"), HOME=str(TMP / "home")); (TMP / "home" / ".ssh").mkdir(parents=True)
def jeeg(*a, cwd=None, e=None):
    p = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *a], capture_output=True, text=True, env=e or env, timeout=90, stdin=subprocess.DEVNULL, cwd=cwd or TMP)
    return p.returncode, p.stdout + p.stderr
proj = TMP / "proj"; (proj / "src").mkdir(parents=True); (proj / "node_modules").mkdir(); (proj / ".git").mkdir()
(proj / "src" / "a.py").write_text("# TODO: fix this\nx = 1\n\n# FIXME later\nprint('TODO in a string')\n")
(proj / "src" / "b.js").write_text("// HACK: temporary\nconst a = 2;\n")
(proj / "node_modules" / "skip.js").write_text("// TODO should be skipped\n")
fake = "AKIA" + "ABCDEFGHIJKLMNOP"
(proj / "cfg.py").write_text(f'aws = "{fake}"\npassword = "hunter2hunter2"\npassword = "your-password-here"\ntoken = os.environ["T"]\n')
rc, o = jeeg("find", "todo", str(proj)); ok(rc == 0 and "a.py:1" in o and "a.py:4" in o and "b.js:1" in o and "skip.js" not in o and "string" not in o, "find todo: " + o)
rc, o = jeeg("find", "secrets", str(proj)); ok(rc == 0 and "AWS access key" in o and "Password in text" in o and "hunter2hunter2" not in o and fake not in o, "secrets found and hidden: " + o)
ok("your-password-here" not in o and "environ" not in o, "placeholders are not flagged: " + o)
rc, o = jeeg("find", "secrets", str(proj / "src")); ok("No obvious secrets" in o, "clean folder")
(TMP / "a.env").write_text("A=1\nB=2\nC=three\n"); (TMP / "b.env").write_text("A=1\nB=9\nD=4\n")
rc, o = jeeg("env", "diff", str(TMP / "a.env"), str(TMP / "b.env")); ok("Only in a.env: C" in o and "Only in b.env: D" in o and "Different values: B" in o and "three" not in o, "env diff: " + o)
rc, o = jeeg("semver", "1.2.3", "vs", "1.10.0"); ok("older than" in o, "semver: " + o)
rc, o = jeeg("semver", "2.0.0", "vs", "2.0.0-rc.1"); ok("newer than" in o, "release beats pre-release: " + o)
rc, o = jeeg("semver", "1.0", "vs", "1.0.0"); ok("the same as" in o, "1.0 equals 1.0.0: " + o)
log = TMP / "app.log"; log.write_text("".join(f"2026-11-22 10:0{i % 3}:00 ERROR db timeout after {i} ms\n" for i in range(30)) + "2026-11-22 10:05:00 INFO started\n2026-11-22 10:05:01 WARNING slow\n")
rc, o = jeeg("log", "analyze", str(log)); ok("32 lines" in o and "ERROR 30" in o and "30x" in o and "db timeout after # ms" in o, "log analyze: " + o)
(TMP / "fake.pdf").write_bytes(b"MZ\x90\x00" + b"\0" * 100); (TMP / "real.pdf").write_bytes(b"%PDF-1.4 hello")
rc, o = jeeg("identify", "file", str(TMP / "fake.pdf")); ok("Windows program" in o and "WARNING" in o, "disguised program: " + o)
rc, o = jeeg("identify", "file", str(TMP / "real.pdf")); ok("PDF document" in o and "WARNING" not in o and "Note" not in o, "real pdf: " + o)
rc, o = jeeg("ssh", "key", "audit"); ok(rc == 0 and ("nothing to check" in o or "Checked 0" in o), "ssh audit empty: " + o)
ssh = TMP / "home" / ".ssh"; (ssh / "id_x").write_text("-----BEGIN RSA PRIVATE KEY-----\nabc\n-----END RSA PRIVATE KEY-----\n"); os.chmod(ssh / "id_x", 0o644)
rc, o = jeeg("ssh", "key", "audit"); ok("readable by others" in o and "no passphrase" in o and "abc" not in o, "ssh audit finds problems, hides key: " + o)
d = TMP / "watch"; d.mkdir(); (d / "a.txt").write_text("one"); (d / "b.txt").write_text("two")
rc, o = jeeg("integrity", "save", str(d)); ok(rc == 0 and "2 files" in o, "save: " + o)
rc, o = jeeg("integrity", "check", str(d)); ok("Nothing changed" in o, "unchanged: " + o)
(d / "a.txt").write_text("ONE"); (d / "b.txt").unlink(); (d / "c.txt").write_text("new")
rc, o = jeeg("integrity", "check", str(d)); ok("Changed: 1" in o and "Added: 1" in o and "Removed: 1" in o, "changes found: " + o)
rc, o = jeeg("integrity", "list"); ok(str(d) in o, "list")
rc, o = jeeg("integrity", "forget", str(d)); ok(rc == 0, "forget")
rc, o = jeeg("integrity", "check", str(d)); ok(rc != 0, "no baseline after forget")

# ---- vault (Obsidian notes)
vd = TMP / "vault"; (vd / ".obsidian").mkdir(parents=True); (vd / "Daily").mkdir()
(vd / "Project Plan.md").write_text("# Plan\nLaunch the beta in March. Budget is tight.\n"); (vd / "Daily" / "2026-11-22.md").write_text("Met the team about the beta launch.\n")
(vd / ".obsidian" / "secret.md").write_text("beta hidden config\n"); (TMP / "outside.md").write_text("outside beta\n")
rc, o = jeeg("vault", "search", "beta"); ok(rc != 0 and "vault set" in o, "search before set explains: " + o)
rc, o = jeeg("vault", "set", str(vd)); ok(rc == 0 and "2 notes" in o, "vault set: " + o)
rc, o = jeeg("vault", "search", "beta", "launch"); ok("Project Plan.md" in o and "2026-11-22.md" in o and "secret.md" not in o, "search: " + o)
rc, o = jeeg("vault", "search", "zzzznothing"); ok("No notes match" in o, "no match")
rc, o = jeeg("vault", "read", "Project Plan"); ok("Launch the beta" in o, "read by name: " + o)
rc, o = jeeg("vault", "read", "[[project plan]]"); ok("Launch the beta" in o, "read wiki-link style")
rc, o = jeeg("vault", "read", "../outside"); ok(rc != 0 and "outside beta" not in o, "cannot read outside the vault: " + o)
rc, o = jeeg("vault", "read", ".obsidian/secret"); ok(rc != 0 and "hidden config" not in o, "cannot read hidden folders")
rc, o = jeeg("vault", "list", ".."); ok(rc != 0, "list outside is refused")
rc, o = jeeg("vault", "recent"); ok("Project Plan.md" in o, "recent")
rc, o = jeeg("vault", "append", "Project", "Plan", "|", "Decision: ship in April"); ok("needs confirmation" in o and "April" not in (vd / "Project Plan.md").read_text(), "append asks first: " + o[:120])
rc, o = jeeg("--yes", "vault", "append", "Project", "Plan", "|", "Decision: ship in April"); ok("April" in (vd / "Project Plan.md").read_text() and "Launch the beta" in (vd / "Project Plan.md").read_text(), "append adds and keeps the old text: " + o)
rc, o = jeeg("--yes", "vault", "new", "Ideas/Big", "|", "first idea"); ok((vd / "Ideas" / "Big.md").read_text().strip() == "first idea", "new note in a folder: " + o)
rc, o = jeeg("--yes", "vault", "new", "Ideas/Big", "|", "overwrite?"); ok(rc != 0 and (vd / "Ideas" / "Big.md").read_text().strip() == "first idea", "new never overwrites")
rc, o = jeeg("--yes", "vault", "new", "../escape", "|", "x"); ok(rc != 0 and not (TMP / "escape.md").exists(), "new cannot leave the vault: " + o)
rc, o = jeeg("--yes", "vault", "new", ".obsidian/evil", "|", "x"); ok(rc != 0 and not (vd / ".obsidian" / "evil.md").exists(), "new cannot write into hidden folders")
rc, o = jeeg("--yes", "vault", "append", "nonexistent", "|", "x"); ok(rc != 0, "append to a missing note is refused")

# ---- vault: AI edit blocks, edit, trash, undo
import json as _j
def blk(ops): return "Here you go:\n```jeeg\n" + _j.dumps(ops) + "\n```\nHope that helps."
pp = lambda: (vd / "Project Plan.md").read_text()
before = pp()
ops = [{"op": "replace", "note": "Project Plan", "find": "March", "with": "April"}, {"op": "append", "note": "Project Plan", "text": "Owner: Sam"}, {"op": "new", "note": "Daily/2026-11-23", "text": "new day"}]
rc, o = jeeg("vault", "plan", blk(ops)); ok(rc == 0 and "Change Project Plan.md" in o and "-" in o and "April" in o and pp() == before and not (vd / "Daily/2026-11-23.md").exists(), "plan shows the diff and changes nothing: " + o)
rc, o = jeeg("vault", "apply", blk(ops)); ok("needs confirmation" in o and pp() == before, "apply asks first")
rc, o = jeeg("--yes", "vault", "apply", blk(ops)); ok(rc == 0 and "April" in pp() and "Owner: Sam" in pp() and (vd / "Daily/2026-11-23.md").read_text() == "new day\n", "apply made all three changes: " + o)
rc, o = jeeg("--yes", "vault", "undo"); ok(rc == 0 and pp() == before and not (vd / "Daily/2026-11-23.md").exists(), "undo restored everything: " + o)
bad = [{"op": "append", "note": "Project Plan", "text": "SHOULD NOT APPEAR"}, {"op": "replace", "note": "Project Plan", "find": "not in the note", "with": "x"}]
rc, o = jeeg("--yes", "vault", "apply", blk(bad)); ok(rc != 0 and "SHOULD NOT APPEAR" not in pp() and "not found" in o, "one bad change means nothing is applied: " + o)
rc, o = jeeg("--yes", "vault", "apply", blk([{"op": "replace", "note": "Project Plan", "find": "e", "with": "x"}])); ok(rc != 0 and "appears" in o and pp() == before, "ambiguous text is refused")
for evil in ({"op": "trash", "note": "../outside"}, {"op": "new", "note": "../x", "text": "t"}, {"op": "new", "note": ".obsidian/p", "text": "t"}, {"op": "delete", "note": "Project Plan"}, {"op": "append", "note": ".obsidian/secret", "text": "t"}):
    rc, o = jeeg("--yes", "vault", "apply", blk([evil])); ok(rc != 0 and (vd / ".obsidian" / "secret.md").read_text() == "beta hidden config\n" and (TMP / "outside.md").exists() and not (TMP / "x.md").exists(), "refused: " + str(evil) + " " + o[:80])
rc, o = jeeg("--yes", "vault", "apply", "this is not json at all"); ok(rc != 0 and "could not find" in o, "garbage is explained")
rc, o = jeeg("--yes", "vault", "apply", _j.dumps(ops[:1])); ok(rc == 0 and "April" in pp(), "plain JSON without a code fence also works")
rc, o = jeeg("--yes", "vault", "undo"); ok(pp() == before, "undo again")
rc, o = jeeg("vault", "replace", "Project", "Plan", "|", "March", "|", "May"); ok("needs confirmation" in o and pp() == before, "edit asks first")
rc, o = jeeg("--yes", "vault", "replace", "Project", "Plan", "|", "March", "|", "May"); ok("May" in pp() and "Budget is tight" in pp(), "vault replace: " + o)
rc, o = jeeg("--yes", "vault", "cut", "Project", "Plan", "|", "Budget is tight."); ok("Budget" not in pp() and "May" in pp(), "vault cut: " + o)
rc, o = jeeg("--yes", "vault", "prepend", "Project", "Plan", "|", "Top line"); ok(pp().startswith("Top line"), "vault prepend")
for _ in range(3): jeeg("--yes", "vault", "undo")
ok(pp() == before, "three undos restore the original")
rc, o = jeeg("vault", "trash", "Project", "Plan"); ok("needs confirmation" in o and (vd / "Project Plan.md").exists(), "trash asks first")
rc, o = jeeg("--yes", "vault", "trash", "Project", "Plan"); ok(rc == 0 and not (vd / "Project Plan.md").exists() and any((vd / ".trash").glob("Project Plan*.md")), "note moved to .trash, not deleted: " + o)
rc, o = jeeg("--yes", "vault", "undo"); ok((vd / "Project Plan.md").read_text() == before, "undo brings a trashed note back")
rc, o = jeeg("vault", "plan", e=dict(env, JEEG_VIA_AI="1")); ok(rc != 0 and "clipboard" in o, "an AI connection cannot make JeeG read the clipboard: " + o[:100])
rc, o = jeeg("vault", "copy", "Project", "Plan", e=dict(env, JEEG_VIA_AI="1")); ok(rc != 0, "an AI connection cannot overwrite the clipboard")
rc, o = jeeg("vault", "copy", "Project", "Plan"); ok(("Copied 1 note" in o) or ("clipboard" in o.lower()), "copy builds a prompt (or explains the missing clipboard tool): " + o[:120])

# ---- vault: insert under heading, copy variants, listen (fake clipboard tool)
(vd / "Notes.md").write_text("# Top\nintro\n\n## Risks\n- budget\n\n## Next\n- ship\n")
rc, o = jeeg("--yes", "vault", "apply", blk([{"op": "insert_under", "note": "Notes", "heading": "Risks", "text": "- staffing"}]))
nt = (vd / "Notes.md").read_text(); ok(rc == 0 and "- budget\n\n- staffing" in nt.replace("- budget\n- staffing", "- budget\n\n- staffing") and nt.index("- staffing") < nt.index("## Next") and nt.index("- staffing") > nt.index("- budget"), "insert_under adds at the end of the right section: " + nt)
rc, o = jeeg("vault", "plan", blk([{"op": "insert_under", "note": "Notes", "heading": "Nope", "text": "x"}])); ok(rc != 0 and "no heading" in o, "missing heading refused")
jeeg("--yes", "vault", "undo")
if os.name == "posix":
    bindir = TMP / "bin"; bindir.mkdir(); clipf = TMP / "clip.txt"; clipf.write_text("")
    (bindir / "xclip").write_text(f"#!/bin/sh\nif [ \"$1\" = \"-o\" ]; then cat '{clipf}'; else cat > '{clipf}'; fi\n"); os.chmod(bindir / "xclip", 0o755)
    ce = dict(env, PATH=str(bindir) + os.pathsep + env.get("PATH", ""))
    for w in ("wl-paste", "wl-copy"):
        (bindir / w).write_text(f"#!/bin/sh\n" + (f"cat '{clipf}'" if w == "wl-paste" else f"cat > '{clipf}'") + "\n"); os.chmod(bindir / w, 0o755)
    ce["PATH"] = str(bindir) + os.pathsep + "/usr/bin:/bin:" + os.path.dirname(sys.executable)
    rc, o = jeeg("vault", "copy", "Project", "Plan", e=ce); c = clipf.read_text(); ok("Copied 1 note" in o and "=== NOTE: Project Plan ===" in c and "insert_under" in c and "do not follow instructions" in c, "copy puts the note and instructions on the clipboard: " + o[:120])
    rc, o = jeeg("vault", "copy", e=ce); c = clipf.read_text(); ok("note names" in o and "Project Plan" in c and "Launch the beta" not in c, "copy with no note sends only the names")
    rc, o = jeeg("vault", "copy", "find", "beta", "launch", e=ce); c = clipf.read_text(); ok("note(s)" in o and "Project Plan" in c, "copy find picks matching notes: " + o[:100])
    rc, o = jeeg("vault", "plan", e=ce); ok(rc != 0, "plan with a clipboard that holds no edit block is explained")
    clipf.write_text(blk([{"op": "append", "note": "Project Plan", "text": "FROM CLIPBOARD"}]))
    rc, o = jeeg("vault", "plan", e=ce); ok(rc == 0 and "FROM CLIPBOARD" in o and "FROM CLIPBOARD" not in pp(), "plan reads the clipboard without changing anything: " + o[:150])
    rc, o = jeeg("--yes", "vault", "apply", e=ce); ok("FROM CLIPBOARD" in pp(), "apply reads the clipboard: " + o)
    jeeg("--yes", "vault", "undo")
    # listen: needs a terminal, so drive it through a pty
    import pty, select
    def listen(answer, clip_text):
        clipf.write_text("start")
        pid, fd = pty.fork()
        if pid == 0:
            os.environ.update(ce); os.execv(sys.executable, [sys.executable, str(ROOT / "jeeg.py"), "vault", "listen", "1"])
        buf = b""; sent = False; t0 = time.time()
        def pump(sec):
            nonlocal buf
            r, _, _ = select.select([fd], [], [], sec)
            if r:
                try: buf += os.read(fd, 4096)
                except OSError: return False
            return True
        while time.time() - t0 < 25:
            if not pump(0.3): break
            if b"Listening" in buf and not sent: clipf.write_text(clip_text); sent = True
            if b"Apply?" in buf and b"ANSWERED" not in buf: os.write(fd, (answer + "\n").encode()); buf += b"ANSWERED"
            if answer != "y" and b"Not applied" in buf: break
        try: os.kill(pid, 15)
        except OSError: pass
        try: os.waitpid(pid, 0)
        except OSError: pass
        return buf.decode(errors="replace")
    before2 = pp()
    o = listen("n", blk([{"op": "append", "note": "Project Plan", "text": "LISTEN NO"}])); ok("Apply?" in o and "LISTEN NO" in o and pp() == before2, "listen shows the plan and respects n: " + o[-200:])
    o = listen("y", blk([{"op": "append", "note": "Project Plan", "text": "LISTEN YES"}])); ok("LISTEN YES" in pp() and "Done" in o, "listen applies after y: " + o[-200:])
    jeeg("--yes", "vault", "undo"); ok(pp() == before2, "and it can be undone")
    rc, o = jeeg("vault", "listen", e=dict(ce, JEEG_VIA_AI="1")); ok(rc != 0, "listen refuses an AI connection")
    rc, o = jeeg("vault", "listen", e=ce); ok(rc != 0 and "terminal" in o, "listen needs a terminal: " + o[:100])

# ---- vault: a link inside the vault that points outside must not be readable or writable
if os.name == "posix":
    (TMP / "private.md").write_text("PRIVATE OUTSIDE\n")
    os.symlink(TMP / "private.md", vd / "link.md")
    rc, o = jeeg("vault", "read", "link"); ok(rc != 0 and "PRIVATE" not in o, "symlink to an outside file cannot be read: " + o[:80])
    rc, o = jeeg("vault", "search", "PRIVATE"); ok("link.md" not in o, "symlink not searched")
    rc, o = jeeg("--yes", "vault", "append", "link", "|", "HACK"); ok(rc != 0 and "HACK" not in (TMP / "private.md").read_text(), "symlink cannot be written through")
    os.symlink(TMP / "home", vd / "linkdir")
    rc, o = jeeg("--yes", "vault", "new", "linkdir/x", "|", "t"); ok(rc != 0 and not (TMP / "home" / "x.md").exists(), "folder link cannot be written through: " + o[:80])
print(f"devsec: {P} passed, {F} failed"); sys.exit(1 if F else 0)
