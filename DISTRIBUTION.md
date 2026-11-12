# Publishing JeeG everywhere

Step-by-step guides for every place JeeG can be published. Do them in this order:
each later step is easier once the earlier ones are done.

Replace `X.Y.Z` with the version (for example `2.17.0`). Your GitHub name is `asrbmy`.

| # | Place | Who it reaches | Effort | Cost |
|---|-------|----------------|--------|------|
| 1 | PyPI | everyone with Python (`pip`, `pipx`, `uv`) | 15 min, once | free |
| 2 | GitHub Release | people who download a file | automatic | free |
| 3 | Homebrew tap | Mac and Linux | 15 min | free |
| 4 | Scoop bucket | Windows | 15 min | free |
| 5 | winget | Windows (built in) | 30 min, reviewed | free |
| 6 | Chocolatey | Windows | 30 min, reviewed | free |
| 7 | AUR | Arch Linux | 20 min | free |
| 8 | conda-forge | Anaconda users | 1 hour, reviewed | free |
| 9 | VS Code Marketplace / Open VSX | VS Code users | 30 min | free |
| 10 | Standalone `.exe` (PyInstaller) | people without Python | 1 hour | free |
| 11 | Docker / GHCR | server users | 20 min | free |
| 12 | Docs site (GitHub Pages) | search engines, new users | 5 min | free |

Never put a token or password in a file, in a commit, or in the repo. Put it in GitHub
**Settings > Secrets and variables** or type it only into the tool that asks for it.

---

## 0. Before every release

1. Change `__version__` in `jeeg.py` (for example `2.16.1`).
2. Add a `## 2.8.1` section at the top of `CHANGELOG.md`. The release notes are taken from it.
3. Run the tests: `python jeeg.py selftest` and the files in `tests/`.
4. Push to `main`. The `publish` workflow does the rest (steps 1 and 2 below).

---

## 1. PyPI (pip, pipx, uv)

This one gives you three install commands at once:

```
pip install jeeg
pipx install jeeg
uv tool install jeeg
```

### A. Automatic, with a trusted publisher (no token needed, recommended)

One-time setup:

1. Sign in to https://pypi.org and open the project **jeeg**, then **Manage > Publishing**.
2. Under **Add a new publisher > GitHub**, fill in exactly:
   - Owner: `asrbmy`
   - Repository name: `jeeg`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
3. On GitHub open the repo, **Settings > Environments > New environment**, name it `pypi`.
4. Still in Settings, go to **Secrets and variables > Actions > Variables > New repository variable**:
   name `PUBLISH_PYPI`, value `true`. It must be a *variable*, not a secret.
5. Make sure **Actions** are allowed (Settings > Actions > General > Allow all actions).

After that, every push that raises `__version__` creates the tag, the GitHub release and the PyPI upload.
If it does not run, open the **Actions** tab, click the red or grey run and read the first error.
Common ones:
- `invalid-publisher`: one of the four publisher fields does not match exactly.
- The `pypi` job is grey (skipped): `PUBLISH_PYPI` is missing or not `true`.
- Nothing ran: `.github/workflows/publish.yml` was not pushed (hidden folder), or the version already has a tag.

### B. By hand (works any time)

```
python -m pip install --upgrade build twine
python -m build
twine check dist/*
twine upload dist/*
```

Username: `__token__`. Password: an API token from https://pypi.org/manage/account/token/
(scope it to the `jeeg` project). A version number can only be uploaded once; to fix a mistake,
raise the version.

### C. Practice first on TestPyPI (optional)

```
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple jeeg
```

Create a separate account and token at https://test.pypi.org.

### Check it worked

```
pip install --upgrade jeeg
jeeg --version
```

---

## 2. GitHub Release (downloads)

Automatic: the `publish` workflow creates `vX.Y.Z` with the wheel, the source archive and
`SHA256SUMS.txt`.

By hand: GitHub > **Releases > Draft a new release**, create the tag `vX.Y.Z`, paste the notes
from `CHANGELOG.md`, attach the files from `dist/`, press **Publish release**.

To create the tag from the command line instead:

```
git tag -a vX.Y.Z -m "JeeG X.Y.Z"
git push origin vX.Y.Z
```

---

## 3. Homebrew (Mac and Linux)

A "tap" is just a GitHub repo named `homebrew-jeeg`.

1. On GitHub create a new public repo **`homebrew-jeeg`** (exactly that name).
2. Get the checksum of the release archive:
   ```
   curl -L https://github.com/asrbmy/jeeg/archive/refs/tags/vX.Y.Z.tar.gz | shasum -a 256
   ```
3. Copy `packaging/homebrew/jeeg.rb` from this project into the repo as `Formula/jeeg.rb`.
   Set `url` to the archive above, `sha256` to the checksum, and `version` to `X.Y.Z`.
4. Commit and push.
5. Anyone can now install it:
   ```
   brew install asrbmy/jeeg/jeeg
   ```
6. Test it yourself first: `brew install --build-from-source asrbmy/jeeg/jeeg && brew test jeeg`.

For each new version, change `url` and `sha256` and push.

---

## 4. Scoop (Windows)

A "bucket" is a GitHub repo with JSON files.

1. Create a public repo **`scoop-jeeg`**.
2. Add `bucket/jeeg.json` (replace the hash with the SHA-256 of the `.whl` or `.tar.gz`; get it
   with `certutil -hashfile file SHA256` or from `SHA256SUMS.txt` in the release):
   ```json
   {
     "version": "X.Y.Z",
     "description": "Type a task in plain words and run it. Local, no account, no AI model.",
     "homepage": "https://github.com/asrbmy/jeeg",
     "license": "MIT",
     "depends": "python",
     "url": "https://github.com/asrbmy/jeeg/archive/refs/tags/vX.Y.Z.zip",
     "hash": "PUT-SHA256-HERE",
     "extract_dir": "jeeg-X.Y.Z",
     "bin": "jeeg.bat",
     "checkver": "github",
     "autoupdate": {
       "url": "https://github.com/asrbmy/jeeg/archive/refs/tags/v$version.zip",
       "extract_dir": "jeeg-$version"
     }
   }
   ```
3. Users install it with:
   ```
   scoop bucket add jeeg https://github.com/asrbmy/scoop-jeeg
   scoop install jeeg
   ```
4. The `checkver` and `autoupdate` lines let `scoop` tools bump the version for you.

If you would rather not depend on the Python that Scoop installs, use `pipx` instead (section 1).

---

## 5. winget (Windows)

winget needs an installer or a portable zip. The simplest path is the standalone `.exe` from
section 10, attached to the GitHub release.

1. Install the tool: `winget install wingetcreate`.
2. Create the manifest: `wingetcreate new https://github.com/asrbmy/jeeg/releases/download/vX.Y.Z/jeeg-windows.zip`.
   Answer the questions (Package identifier `asrbmy.JeeG`, type `zip` or `portable`).
3. Submit it: `wingetcreate submit` (needs a GitHub token; it opens a pull request on
   `microsoft/winget-pkgs`).
4. Wait for the automatic checks and a moderator. This can take a few days.
5. Users then run `winget install asrbmy.JeeG`.
6. For later versions: `wingetcreate update asrbmy.JeeG --version X.Y.Z --urls <new-url> --submit`.

---

## 6. Chocolatey (Windows)

1. Make a free account at https://community.chocolatey.org and copy your API key.
2. Install Chocolatey, then create a folder `jeeg-choco` with `jeeg.nuspec` and
   `tools/chocolateyinstall.ps1`. The install script can simply run `python -m pip install jeeg==X.Y.Z`
   and the nuspec lists `python` as a dependency.
3. Build and test: `choco pack` then `choco install jeeg -s .`.
4. Upload: `choco push jeeg.X.Y.Z.nupkg --source https://push.chocolatey.org/ --api-key YOUR-KEY`.
5. Volunteers review the package before it appears.

---

## 7. AUR (Arch Linux)

1. Create an account at https://aur.archlinux.org and add your SSH key.
2. Clone the empty package: `git clone ssh://aur@aur.archlinux.org/python-jeeg.git`.
3. Add a `PKGBUILD`:
   ```
   pkgname=python-jeeg
   pkgver=X.Y.Z
   pkgrel=1
   pkgdesc="Type a task in plain words and run it (local, no account)"
   arch=('any')
   url="https://github.com/asrbmy/jeeg"
   license=('MIT')
   depends=('python')
   makedepends=('python-build' 'python-installer' 'python-setuptools' 'python-wheel')
   source=("https://files.pythonhosted.org/packages/source/j/jeeg/jeeg-$pkgver.tar.gz")
   sha256sums=('PUT-SHA256-HERE')
   build() { cd jeeg-$pkgver && python -m build --wheel --no-isolation; }
   package() { cd jeeg-$pkgver && python -m installer --destdir="$pkgdir" dist/*.whl; }
   ```
4. Generate the metadata and push:
   ```
   makepkg --printsrcinfo > .SRCINFO
   git add PKGBUILD .SRCINFO && git commit -m "jeeg X.Y.Z" && git push
   ```
5. Needs the PyPI upload (section 1) first, because it downloads from there.

---

## 8. conda-forge

1. Needs PyPI first.
2. Fork https://github.com/conda-forge/staged-recipes.
3. Make `recipes/jeeg/meta.yaml` (use `grayskull pypi jeeg` to generate it):
   ```
   pip install grayskull
   grayskull pypi jeeg
   ```
4. Open a pull request. Bots check it, then a reviewer approves.
5. After the merge, a "feedstock" repo is created. Later versions are updated by a bot that opens
   pull requests for you to merge.
6. Users run `conda install -c conda-forge jeeg`.

---

## 9. VS Code Marketplace and Open VSX

Extension files are in `integrations/vscode/`.

1. Install the tool: `npm install -g @vscode/vsce`.
2. Create a publisher at https://marketplace.visualstudio.com/manage (needs a Microsoft account
   and an Azure DevOps personal access token with the **Marketplace > Manage** scope).
3. Change `"publisher": "jeeg"` in `package.json` to your publisher id, add a `"repository"` field,
   and an `icon.png` (128 x 128).
4. From the `integrations/vscode` folder:
   ```
   vsce login YOUR-PUBLISHER
   vsce package
   vsce publish
   ```
5. Open VSX (for VSCodium and others): create an account at https://open-vsx.org, link GitHub,
   make a token, then `npx ovsx publish jeeg-vscode-0.1.0.vsix -p YOUR-TOKEN`.
6. Bump `version` in `package.json` each time.

---

## 10. Standalone `.exe` / app (no Python needed)

Already set up. Build by hand on the system you want (a Windows PC for `.exe`, a Mac for the Mac program):

```
pip install pyinstaller
python tools/build_exe.py
```

Result: `dist/jeeg` (or `dist/jeeg.exe`). Test it on a computer without Python.

Automatic: the `build-exe` workflow (`.github/workflows/build-exe.yml`) runs after the `publish` workflow,
builds for Windows, Mac and Linux, smoke-tests each program, and attaches `jeeg-windows-x64.exe`,
`jeeg-macos` and `jeeg-linux-x64` to the release. You can also press **Run workflow** on the Actions tab
and give a tag. The workflow also uploads a `.sha256` file for each program, which `update now` uses to verify the download. Use the `.exe` URL for winget and Scoop (`packaging/scoop/jeeg.json` is ready; fill in the hash).

Unsigned programs make Windows SmartScreen and macOS Gatekeeper show a warning. Say so in the README
(users choose "Run anyway" or right-click > Open). Code signing costs money and is optional.

---

## 11. Docker / GitHub Container Registry

Only useful for the API bridge on a server.

1. A ready Dockerfile is in `packaging/docker/Dockerfile`.
2. Build and push to GitHub's registry:
   ```
   docker build -f packaging/docker/Dockerfile --build-arg JEEG_VERSION=X.Y.Z -t ghcr.io/asrbmy/jeeg:X.Y.Z .
   echo YOUR-GITHUB-TOKEN | docker login ghcr.io -u asrbmy --password-stdin
   docker push ghcr.io/asrbmy/jeeg:X.Y.Z
   ```
   The token needs the `write:packages` scope.
3. In the package settings on GitHub, set visibility to **Public**.
4. The API only listens on `127.0.0.1` by design. Inside a container, publish it with care
   and keep the token (`JEEG_API_TOKEN`) set.

---

## 12. Docs site (GitHub Pages)

1. Repo **Settings > Pages**.
2. Source: **Deploy from a branch**, branch `main`, folder `/docs`.
3. After about a minute it is live at `https://asrbmy.github.io/jeeg/`. The task search page is
   `https://asrbmy.github.io/jeeg/tasks.html`.
4. Rebuild the pages after adding tasks: `python tools/make_site.py`, then commit `docs/`.

---

## After publishing

- Add the install lines to `README.md` (pip, pipx, brew, scoop, winget).
- Announce it: r/Python, r/commandline, Hacker News ("Show HN: ..."), dev.to.
- Add topics to the repo (Settings > About): `cli`, `python`, `offline`, `productivity`.
- Pin the release and check `Security > Private vulnerability reporting` is on (see `SECURITY.md`).
