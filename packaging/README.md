# Packaging JeeG

JeeG is pure Python with no dependencies, so the simplest installs are:

| System | Command |
|---|---|
| Any (recommended) | `pipx install jeeg` (keeps it in its own environment) |
| Any | `pip install jeeg` |
| Mac with Homebrew | `brew install asrbmy/jeeg/jeeg` once the tap below exists |
| Windows | `pipx install jeeg` or `pip install jeeg`; there is no winget or Scoop entry, because those need a standalone installer and JeeG is a Python package |

## One-time: make the Homebrew tap
1. Create a GitHub repository named `homebrew-jeeg`.
2. Copy `packaging/homebrew/jeeg.rb` to `Formula/jeeg.rb` in it.
3. Replace `VERSION` and `SHA256` using the comment at the top of the file (do this after each PyPI release).
4. Test: `brew install --build-from-source ./Formula/jeeg.rb && brew test jeeg`.

## Each release
1. Raise `__version__` in `jeeg.py` and add a line to `CHANGELOG.md`.
2. Commit, tag `vX.Y.Z`, and publish a GitHub release. The `publish` workflow uploads to PyPI and attaches signed build provenance.
3. Update the Homebrew formula's version and SHA256.
