"""Run the test files one by one, each with its own time limit, so a test that hangs is named instead of stalling the whole job.
Usage: python tools/run_tests.py [--limit SECONDS] [test files ...]      (no files = the release list)
Each test runs with a fresh throw-away data folder and no keyboard input. Exit code 1 if any test failed or hung."""
import os, shutil, signal, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELEASE = ["jeeg.py selftest", "tests/test_routing.py", "tests/test_parsers.py", "tests/test_engine.py", "tests/test_cmds.py", "tests/test_v26.py",
           "tests/test_v27.py", "tests/test_api.py", "tests/test_bridge.py", "tests/test_v28.py", "tests/test_v29.py", "tests/test_v210.py",
           "tests/test_phone.py", "tests/test_remote.py", "tests/test_fuzz.py", "tests/test_connect.py", "tests/test_v217.py", "tests/test_v218.py",
           "tests/test_v219.py", "tests/test_v220.py", "tests/test_everyday.py", "tests/test_more.py", "tests/test_prod.py", "tests/test_update.py",
           "tests/test_link.py", "tests/test_iot.py", "tests/test_quality.py", "tests/test_privacy.py", "tests/test_security.py"]


def run_one(spec: str, limit: int) -> tuple:
    home = tempfile.mkdtemp(prefix="jeeg-rt-")
    env = dict(os.environ, JEEG_HOME=home, HOME=home, USERPROFILE=home, PYTHONUNBUFFERED="1")
    out = Path(home) / "out.txt"
    t0 = time.time()
    with open(out, "wb") as fh:
        p = subprocess.Popen([sys.executable] + spec.split(), cwd=str(ROOT), stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.STDOUT, env=env,
                             start_new_session=(os.name != "nt"))
        try:
            rc = p.wait(timeout=limit)
            state = "ok" if rc == 0 else f"FAILED (exit {rc})"
        except subprocess.TimeoutExpired:
            state = f"HUNG (no result after {limit} s)"
            try:
                os.killpg(p.pid, signal.SIGKILL) if os.name != "nt" else p.kill()
            except OSError:
                p.kill()
            p.wait()
    tail = out.read_text(encoding="utf-8", errors="replace").splitlines()[-40:]
    shutil.rmtree(home, ignore_errors=True)
    return state, round(time.time() - t0), tail


def main(argv):
    limit = 600
    if argv[:1] == ["--limit"]:
        limit, argv = int(argv[1]), argv[2:]
    specs = argv or RELEASE
    bad = []
    for spec in specs:
        state, secs, tail = run_one(spec, limit)
        print(f"{'ok  ' if state == 'ok' else 'BAD '} {spec:<28}{secs:>5} s  {state if state != 'ok' else ''}", flush=True)
        if state != "ok":
            bad.append(spec)
            print("      --- last lines of its output ---")
            for ln in tail:
                print("      " + ln[:200])
            print("      --------------------------------", flush=True)
    print(f"\n{len(specs) - len(bad)} of {len(specs)} passed." + (f" Problems: {', '.join(bad)}" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
