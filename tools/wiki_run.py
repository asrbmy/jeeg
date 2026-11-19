"""Run a wiki scenario for real and return what was printed. Used by make_wiki.py."""
import os, re, shlex, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(sc, keep=False):
    home = Path(tempfile.mkdtemp(prefix="wikihome-"))
    try:
        for kind, *a in sc["setup"]:
            if kind == "mkdir":
                (home / a[0]).mkdir(parents=True, exist_ok=True)
            elif kind == "write":
                p = home / a[0]
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(a[1].replace("{HOME}", str(home)), encoding="utf-8")
            elif kind == "sh":
                subprocess.run(a[0], shell=True, cwd=home, check=True, capture_output=True)
        env = {k: v for k, v in os.environ.items() if not k.startswith("JEEG_")}
        env.update(HOME=str(home), USERPROFILE=str(home), JEEG_HOME=str(home / ".jeeg"), TZ="Asia/Kolkata", NO_COLOR="1", GIT_CONFIG_GLOBAL=str(home / ".gitconfig"))
        cwd = home / sc["cwd"] if sc.get("cwd") else home
        out = []
        for step in sc["steps"]:
            st = step.replace("{HOME}", str(home))
            argv = shlex.split(st) if st.startswith("--") else [st]
            try:
                r = subprocess.run([sys.executable, str(ROOT / "jeeg.py")] + argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=90, stdin=subprocess.DEVNULL)
                text, rc = (r.stdout + r.stderr), r.returncode
            except subprocess.TimeoutExpired:
                text, rc = "(timed out)", 124
            text = text.replace(str(home), "~")
            lines = [l.rstrip() for l in text.splitlines() if not re.match(r"^(ok|failed \(exit \d+\)) in [\d.]+s$", l) and not l.startswith("[agent-proxy]")]
            lines = [l for l in lines if l is not None]
            if rc not in (0,) and not any(l.startswith("failed") for l in lines):
                pass
            out.append((step.replace("{HOME}", "~"), lines, rc))
        return out
    finally:
        if not keep:
            shutil.rmtree(home, ignore_errors=True)


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "tools"))
    import wiki_content
    for key in sys.argv[1:]:
        print("=====", key)
        for step, lines, rc in run(wiki_content.SC[key]):
            print("task>", step, f"[rc={rc}]")
            print("\n".join(lines[:30]))
