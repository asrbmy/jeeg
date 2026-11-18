# Testing and Releasing

## Check JeeG on your own computer
    real test list          what is checked
    real test run all       harmless checks (or one group: real test run system)
    real test report        private report (names and addresses removed)
    real test compare       what got better or worse since the last run
    real test ai            text to paste into Claude.ai so it runs the test for you

This matters most on Windows and macOS, where several features were written carefully but never run on real machines. See `REAL_WORLD_TEST.md`.

## The automatic checks
    python jeeg.py selftest          every task is described, compiles, is found by its own name
    python tests/test_routing.py     phrases route to the right task
    python tests/test_privacy.py     network use is declared and counted
    python tests/test_security.py  test_engine.py  test_cmds.py  test_api.py  test_bridge.py
    python tests/test_remote.py  test_connect.py  test_v220.py  test_browser.py ...

Run every file in `tests/` on Python 3.9, 3.12 and 3.13 before a release. A few tests that start servers can flake when several suites run at once; rerun alone to confirm.

`tests/phrases.txt` holds `phrase => task | expected arguments`; add a line for every new task.

## Counts that must stay in step
Adding or removing a task changes: the task count in README.md, USER_GUIDE.md and `docs/tasks.html`, and the "N of M tasks" network sentence in PRIVACY.md. Regenerate docs:

    python tools/make_guide_appendix.py
    python tools/make_site.py
    python tools/make_wiki.py

Tasks that touch the network need `# network: yes`; new helpers that use network modules must be allowed in `tests/test_privacy.py`.

## Release
Summary of `DISTRIBUTION.md` (read it for the exact steps):
1. Version in `jeeg.py` and packaging files; CHANGELOG updated; all suites green.
2. Build: `python -m build`, then `twine check dist/*`; try the wheel in a fresh virtual environment (`jeeg selftest`).
3. **PyPI:** use a trusted publisher (GitHub Actions, no token) or upload by hand. **Never put a PyPI token in a file or in GitHub.**
4. GitHub Release with standalone programs (Windows `.exe`, macOS, Linux) built by the workflow; build provenance attestations are included.
5. Package managers: Homebrew, Scoop, winget, Chocolatey, AUR, conda-forge, Docker. Docs site on GitHub Pages.
6. After publishing: `pip install jeeg` in a clean environment and run `jeeg selftest`.

You (the person) do the push and the release; nothing here pushes or publishes by itself.
