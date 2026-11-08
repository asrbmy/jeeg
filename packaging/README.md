# Packaging JeeG

JeeG is pure Python with no dependencies, so the simplest installs are:

| System | Command |
|---|---|
| Any (recommended) | `pipx install jeeg` (keeps it in its own environment) |
| Any | `pip install jeeg` |
| Mac with Homebrew | `brew install asrbmy/jeeg/jeeg` once the tap below exists |
| Windows | `pipx install jeeg` or `pip install jeeg`; or download `jeeg-windows-x64.exe` from the GitHub release (no Python needed), or use the Scoop file in `packaging/scoop/` |
| No Python at all | the `jeeg-windows-x64.exe`, `jeeg-macos` and `jeeg-linux-x64` files on each GitHub release (built by the `build-exe` workflow, or by hand with `python tools/build_exe.py`) |

## One-time: make the Homebrew tap
1. Create a GitHub repository named `homebrew-jeeg`.
2. Copy `packaging/homebrew/jeeg.rb` to `Formula/jeeg.rb` in it.
3. Replace `VERSION` and `SHA256` using the comment at the top of the file (do this after each PyPI release).
4. Test: `brew install --build-from-source ./Formula/jeeg.rb && brew test jeeg`.

## Each release
1. Raise `__version__` in `jeeg.py` and add a line to `CHANGELOG.md`.
2. Commit, tag `vX.Y.Z`, and publish a GitHub release. The `publish` workflow uploads to PyPI and attaches signed build provenance.
3. Update the Homebrew formula's version and SHA256.

## Standalone program
`python tools/build_exe.py` (needs `pip install pyinstaller`) builds `dist/jeeg`. The `build-exe` workflow does this for Windows, Mac and Linux after each release and attaches the files. Unsigned programs show a SmartScreen/Gatekeeper warning the first time.

## Docker and Scoop
`packaging/docker/Dockerfile` and `packaging/scoop/jeeg.json` are ready to use; see `DISTRIBUTION.md` for the steps.
