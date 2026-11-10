# winget (Windows Package Manager)

winget needs a manifest submitted as a pull request to https://github.com/microsoft/winget-pkgs (only you can do this; it needs your GitHub login).

1. Make a release so `jeeg-windows-x64.exe` and its `.sha256` file exist.
2. Run `python tools/fill_packaging.py 2.15.0` (needs internet; it reads the `.sha256` file from the release, updates `packaging/scoop/jeeg.json`, and writes finished winget files into `packaging/winget/out/`).
3. Copy the three files from `packaging/winget/out/` to `manifests/a/asrbmy/JeeG/2.15.0/` in your fork of winget-pkgs, run `winget validate`, and open the pull request.
4. After it is merged people can run `winget install asrbmy.JeeG`.

Signing: unsigned programs show a SmartScreen/Gatekeeper warning. Free signing for open-source projects is available from the SignPath Foundation (Windows); Mac needs an Apple Developer account. Neither can be set up from inside this repository.
