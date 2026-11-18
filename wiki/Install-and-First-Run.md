# Install and First Run

## Requirements
Python 3.9 or newer. On Windows tick "Add Python to PATH" in the installer. Nothing else is required; a few tasks use optional extras (see below).

## Three ways to install

**1. From pip (simplest)**

    pip install jeeg
    jeeg setup

`setup` is a one-minute wizard: it checks Python, makes sure the `jeeg` command works and shows how to turn on tab completion.

**2. From a folder (zip or git clone)**

    python jeeg.py doctor
    python jeeg.py
    python install.py          # once: creates the "jeeg" command for any folder
    python install.py --name go        # another command name (avoid "tr")
    python install.py --uninstall

If the installer says its folder is not on your PATH, add that folder as it shows and open a new terminal. If you move the folder, run the installer again.

**3. A standalone program (no Python)**
Download `jeeg-windows-x64.exe`, `jeeg-macos` or `jeeg-linux-x64` from a GitHub release. `update now` replaces it after checking its SHA-256.

## First run

    jeeg doctor          # is everything in place?
    jeeg                 # start the prompt
    task> open youtube
    task> weather in mumbai
    task> 25 * 4
    task> exit

One shot without a prompt: `jeeg "open youtube"`. Use quotes when the text has `*`, `?`, `&` or `;`.

The first time you start JeeG in a terminal it offers a one-minute tour once; `learn` shows it again.

## Updating
`update` checks GitHub (only when you ask; nothing of yours is sent) and prints the command. `update now` runs it after asking: `git pull` for a clone, `pip install --upgrade jeeg` for pip, a checked download for the standalone program. Your data folder is separate and kept.

## Optional extras

| For | Install |
|---|---|
| Pictures | `pip install pillow` |
| PDF | `pip install pypdf` |
| QR codes | `pip install "qrcode[pil]"` |
| Process and temperature detail | `pip install psutil` |
| Video and audio | ffmpeg |
| Clipboard on Linux | `wl-clipboard`, `xclip` or `xsel` |
| Media keys / brightness / speech on Linux | `playerctl` / `brightnessctl` / `espeak-ng` |
| Timezone names on Windows | `pip install tzdata` |
| Password zips / YAML | `pip install pyzipper` / `pip install pyyaml` |
| A real web browser tasks | Chrome, Edge, Brave or Chromium |

`doctor` shows which you already have; a task that needs something missing names it.

## Where things go
Your data: `~/.jeeg` (`C:\Users\<you>\.jeeg` on Windows). Set `JEEG_HOME` to move it. See [Safety and Privacy](Safety-and-Privacy).
