# keywords: run tests, run the tests, test project, pytest, unit tests, npm test, run unittest, test my code, execute tests, check tests
# desc: Run the tests of the project in this folder (run tests): pytest, unittest, npm, go or cargo is detected
# category: developer
import importlib.util, json, shutil, sys
from pathlib import Path
from _lib import call, fail
c = Path.cwd()
if (c / "package.json").exists():
    try: has = "test" in json.loads((c / "package.json").read_text(encoding="utf-8")).get("scripts", {})
    except ValueError: has = False
    if has and shutil.which("npm"): print("Detected: npm test"); raise SystemExit(call(["npm", "test"]))
if (c / "go.mod").exists() and shutil.which("go"): print("Detected: go test"); raise SystemExit(call(["go", "test", "./..."]))
if (c / "Cargo.toml").exists() and shutil.which("cargo"): print("Detected: cargo test"); raise SystemExit(call(["cargo", "test"]))
pyish = any(c.glob("*.py")) or (c / "tests").is_dir() or (c / "pyproject.toml").exists() or (c / "pytest.ini").exists() or (c / "setup.py").exists()
if pyish:
    if importlib.util.find_spec("pytest"): print("Detected: pytest"); raise SystemExit(call([sys.executable, "-m", "pytest", "-q"]))
    print("Detected: python unittest"); raise SystemExit(call([sys.executable, "-m", "unittest", "discover", "-v"]))
fail("I could not tell how to test this folder (looked for package.json, go.mod, Cargo.toml, Python files).")
