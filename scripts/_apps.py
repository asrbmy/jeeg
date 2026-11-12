"""App-installer helpers: friendly name -> the right package id for winget / choco / brew / apt / dnf / pacman / flatpak.
Standard library only. Commands are always run as a list (never through a shell). Not a task."""
import os
import re
import shutil
import subprocess
import sys

from _lib import WIN, MAC, fail

# names (| separated); w=winget  c=choco  b=brew (cask: prefix for apps)  l=apt+dnf  p=pacman  a=apt only  f=flatpak
_TABLE = """
chrome|google chrome; w=Google.Chrome; c=googlechrome; b=cask:google-chrome; f=com.google.Chrome
firefox; w=Mozilla.Firefox; c=firefox; b=cask:firefox; l=firefox; p=firefox; f=org.mozilla.firefox
brave|brave browser; w=Brave.Brave; c=brave; b=cask:brave-browser; f=com.brave.Browser
thunderbird; w=Mozilla.Thunderbird; c=thunderbird; b=cask:thunderbird; l=thunderbird; p=thunderbird; f=org.mozilla.Thunderbird
vlc|vlc player|vlc media player; w=VideoLAN.VLC; c=vlc; b=cask:vlc; l=vlc; p=vlc; f=org.videolan.VLC
vscode|vs code|visual studio code|code editor; w=Microsoft.VisualStudioCode; c=vscode; b=cask:visual-studio-code; p=code; f=com.visualstudio.code
git; w=Git.Git; c=git; b=git; l=git; p=git
python|python3; w=Python.Python.3.12; c=python; b=python; a=python3; l=python3; p=python
nodejs|node|node js|npm; w=OpenJS.NodeJS.LTS; c=nodejs-lts; b=node; l=nodejs; p=nodejs
java|jdk|openjdk; w=EclipseAdoptium.Temurin.21.JDK; c=temurin21; b=openjdk; a=default-jdk; l=java-latest-openjdk; p=jdk-openjdk
go|golang; w=GoLang.Go; c=golang; b=go; a=golang; l=golang; p=go
rust|rustup; w=Rustlang.Rustup; c=rustup.install; b=rustup; p=rustup
7zip|7-zip|7 zip; w=7zip.7zip; c=7zip; b=p7zip; a=p7zip-full; l=p7zip; p=p7zip
notepad++|notepad plus plus|notepadplusplus; w=Notepad++.Notepad++; c=notepadplusplus
sublime|sublime text; w=SublimeHQ.SublimeText.4; c=sublimetext4; b=cask:sublime-text
vim; w=vim.vim; c=vim; b=vim; l=vim; p=vim
libreoffice|libre office|office; w=TheDocumentFoundation.LibreOffice; c=libreoffice-fresh; b=cask:libreoffice; l=libreoffice; p=libreoffice-fresh; f=org.libreoffice.LibreOffice
gimp; w=GIMP.GIMP; c=gimp; b=cask:gimp; l=gimp; p=gimp; f=org.gimp.GIMP
inkscape; w=Inkscape.Inkscape; c=inkscape; b=cask:inkscape; l=inkscape; p=inkscape; f=org.inkscape.Inkscape
blender; w=BlenderFoundation.Blender; c=blender; b=cask:blender; l=blender; p=blender; f=org.blender.Blender
obs|obs studio; w=OBSProject.OBSStudio; c=obs-studio; b=cask:obs; l=obs-studio; p=obs-studio; f=com.obsproject.Studio
audacity; w=Audacity.Audacity; c=audacity; b=cask:audacity; l=audacity; p=audacity; f=org.audacityteam.Audacity
handbrake; w=HandBrake.HandBrake; c=handbrake; b=cask:handbrake; l=handbrake; f=fr.handbrake.ghb
kdenlive; w=KDE.Kdenlive; c=kdenlive; b=cask:kdenlive; l=kdenlive; p=kdenlive; f=org.kde.kdenlive
ffmpeg; w=Gyan.FFmpeg; c=ffmpeg; b=ffmpeg; l=ffmpeg; p=ffmpeg
calibre; w=calibre.calibre; c=calibre; b=cask:calibre; l=calibre; p=calibre; f=com.calibre_ebook.calibre
zoom; w=Zoom.Zoom; c=zoom; b=cask:zoom; f=us.zoom.Zoom
slack; w=SlackTechnologies.Slack; c=slack; b=cask:slack; f=com.slack.Slack
discord; w=Discord.Discord; c=discord; b=cask:discord; f=com.discordapp.Discord
telegram; w=Telegram.TelegramDesktop; c=telegram; b=cask:telegram; f=org.telegram.desktop
signal; w=OpenWhisperSystems.Signal; c=signal; b=cask:signal; f=org.signal.Signal
spotify; w=Spotify.Spotify; c=spotify; b=cask:spotify; f=com.spotify.Client
steam; w=Valve.Steam; c=steam; b=cask:steam; f=com.valvesoftware.Steam
postman; w=Postman.Postman; c=postman; b=cask:postman; f=com.getpostman.Postman
docker; w=Docker.DockerDesktop; c=docker-desktop; a=docker.io; p=docker
putty; w=PuTTY.PuTTY; c=putty; a=putty
filezilla; w=TimKosse.FileZilla.Client; c=filezilla; b=cask:filezilla; l=filezilla; p=filezilla; f=org.filezillaproject.Filezilla
qbittorrent; w=qBittorrent.qBittorrent; c=qbittorrent; b=cask:qbittorrent; l=qbittorrent; p=qbittorrent; f=org.qbittorrent.qBittorrent
keepassxc|keepass; w=KeePassXCTeam.KeePassXC; c=keepassxc; b=cask:keepassxc; l=keepassxc; p=keepassxc; f=org.keepassxc.KeePassXC
bitwarden; w=Bitwarden.Bitwarden; c=bitwarden; b=cask:bitwarden; f=com.bitwarden.desktop
anydesk; w=AnyDeskSoftwareGmbH.AnyDesk; c=anydesk; b=cask:anydesk
wireshark; w=WiresharkFoundation.Wireshark; c=wireshark; b=cask:wireshark; l=wireshark; p=wireshark-qt
nmap; w=Insecure.Nmap; c=nmap; b=nmap; l=nmap; p=nmap
htop; b=htop; l=htop; p=htop
sumatra|sumatrapdf|sumatra pdf; w=SumatraPDF.SumatraPDF; c=sumatrapdf
powertoys|power toys; w=Microsoft.PowerToys; c=powertoys
"""

CATALOG = {}      # canonical name -> dict
ALIAS = {}        # any spelling -> canonical name
for _line in _TABLE.strip().splitlines():
    _head, *_rest = [x.strip() for x in _line.split(";")]
    _names = [n.strip() for n in _head.split("|")]
    _e = dict(kv.split("=", 1) for kv in _rest)
    CATALOG[_names[0]] = _e
    for _n in _names:
        ALIAS[_n] = _names[0]

BUNDLES = {
    "dev": ["git", "python", "vscode", "nodejs"],
    "office": ["libreoffice", "firefox", "7zip", "vlc", "thunderbird"],
    "media": ["vlc", "obs", "audacity", "handbrake", "gimp"],
    "student": ["libreoffice", "firefox", "vlc", "7zip", "zoom"],
    "privacy": ["firefox", "keepassxc", "signal", "bitwarden"],
}

FILLER = {"the", "a", "an", "app", "apps", "application", "applications", "software", "program", "programs", "please", "on", "my",
          "computer", "pc", "laptop", "for", "me", "to", "install", "uninstall", "remove", "setup", "set", "up", "get", "download",
          "update", "upgrade", "latest", "new", "newest", "and", "preview", "dry-run", "dryrun", "using", "with", "via", "now", "it"}
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._+\-]{0,63}$")


def split_names(text):
    """'install vlc and the git app, chrome' -> ['vlc', 'git', 'chrome'] (filler words dropped, max 10)."""
    out = []
    for part in re.split(r"\s*(?:,|&|\band\b|\+|;)\s*", text.lower()):
        w = [x for x in part.split() if x not in FILLER]
        if w:
            out.append(" ".join(w))
    return out[:10]


def lookup(name):
    n = " ".join(name.lower().split())
    if n in ALIAS:
        return ALIAS[n], CATALOG[ALIAS[n]]
    n2 = n.replace("-", " ")
    if n2 in ALIAS:
        return ALIAS[n2], CATALOG[ALIAS[n2]]
    return None, None


def os_name():
    return "windows" if WIN else "mac" if MAC else "linux"


def available(osname=None):
    """Package managers found on this computer, best first."""
    o = osname or os_name()
    order = {"windows": ["winget", "choco"], "mac": ["brew"], "linux": ["apt-get", "dnf", "pacman", "flatpak"]}[o]
    return [m for m in order if shutil.which(m)]


def plan(action, name, have=None, osname=None):
    """Work out the command for one app. Returns dict(cmd, sudo, manager, known, key) or dict(error=...). Pure: nothing is run."""
    o = osname or os_name()
    mgrs = list(have) if have is not None else available(o)
    key, entry = lookup(name)
    if not key and not SAFE_NAME.match(name or ""):
        return {"error": f"'{name}' is not a name I can use (letters, numbers, space, . _ + - only)."}
    if not mgrs:
        hint = {"windows": "Install 'App Installer' from the Microsoft Store (it provides winget), or Chocolatey.",
                "mac": "Install Homebrew first: see https://brew.sh",
                "linux": "No supported package manager found (apt, dnf, pacman or flatpak)."}[o]
        return {"error": "No package manager found. " + hint}
    e = entry or {}
    m = mgrs[0]
    if o == "linux":                                       # native first, flatpak when the app has no native package
        native = [x for x in mgrs if x != "flatpak"]
        if native and (key is None or e.get({"apt-get": "a", "dnf": "l", "pacman": "p"}[native[0]]) or (native[0] == "apt-get" and e.get("l"))):
            m = native[0]
        elif "flatpak" in mgrs and e.get("f"):
            m = "flatpak"
        elif native:
            m = native[0]
        else:
            m = "flatpak"
    pid = None
    if m == "winget":
        pid = e.get("w")
    elif m == "choco":
        pid = e.get("c")
    elif m == "brew":
        pid = e.get("b")
    elif m == "apt-get":
        pid = e.get("a") or e.get("l")
    elif m == "dnf":
        pid = e.get("l")
    elif m == "pacman":
        pid = e.get("p")
    elif m == "flatpak":
        pid = e.get("f")
    known = bool(pid)
    if not pid:
        if key and action != "search":
            return {"error": f"I know '{key}' but have no {m} package for it on this computer. Try:  search app {key}"}
        pid = name.strip() if m == "winget" else name.strip().replace(" ", "-")
    cask = m == "brew" and pid.startswith("cask:")
    if cask:
        pid = pid[5:]
    if pid.startswith("-"):
        return {"error": "That name looks like an option, not an app."}
    verb = {"install": {"winget": ["install", "--id", pid, "-e"], "choco": ["install", pid, "-y"], "brew": ["install"] + (["--cask"] if cask else []) + [pid],
                        "apt-get": ["install", "-y", pid], "dnf": ["install", "-y", pid], "pacman": ["-S", "--needed", "--noconfirm", pid],
                        "flatpak": ["install", "-y", "flathub", pid]},
            "uninstall": {"winget": ["uninstall", "--id", pid, "-e"], "choco": ["uninstall", pid, "-y"], "brew": ["uninstall"] + (["--cask"] if cask else []) + [pid],
                          "apt-get": ["remove", "-y", pid], "dnf": ["remove", "-y", pid], "pacman": ["-R", "--noconfirm", pid],
                          "flatpak": ["uninstall", "-y", pid]},
            "upgrade": {"winget": ["upgrade", "--id", pid, "-e"], "choco": ["upgrade", pid, "-y"], "brew": ["upgrade"] + (["--cask"] if cask else []) + [pid],
                        "apt-get": ["install", "--only-upgrade", "-y", pid], "dnf": ["upgrade", "-y", pid], "pacman": ["-S", "--needed", "--noconfirm", pid],
                        "flatpak": ["update", "-y", pid]},
            "search": {"winget": ["search", pid], "choco": ["search", pid], "brew": ["search", pid],
                       "apt-get": ["search", pid], "dnf": ["search", pid], "pacman": ["-Ss", pid], "flatpak": ["search", pid]}}[action]
    exe = {"apt-get": "apt-cache" if action == "search" else "apt-get"}.get(m, m)
    cmd = [exe] + verb[m]
    sudo = o == "linux" and m in {"apt-get", "dnf", "pacman"} and action != "search"
    return {"cmd": cmd, "sudo": sudo, "manager": m, "known": known, "key": key or name}


def with_sudo(cmd):
    """Put sudo in front when not root. Without a terminal it must not wait for a password."""
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return cmd
    s = shutil.which("sudo")
    if not s:
        fail("This needs administrator rights, and 'sudo' is not available. Run JeeG as an administrator.")
    interactive = sys.stdin is not None and sys.stdin.isatty()
    return [s] + ([] if interactive else ["-n"]) + cmd


def execute(p, preview=False):
    """Show the command, run it unless preview. Returns the exit code."""
    cmd = with_sudo(p["cmd"]) if p.get("sudo") else p["cmd"]
    print("Command:  " + " ".join(cmd))
    if preview:
        return 0
    sys.stdout.flush()
    try:
        return subprocess.call(cmd)
    except OSError as ex:
        print(f"Could not start {cmd[0]}: {ex.strerror or ex}")
        return 1


def is_preview(text):
    return any(w in {"preview", "dry-run", "dryrun"} for w in text.lower().split())


def run_action(action, text):
    """Shared body of install / uninstall / update one app. Prints results; returns the exit code."""
    preview = is_preview(text)
    names = split_names(text)
    if not names:
        fail(f"Say which app, for example:  {action} vlc      (see what I know: search app)")
    code = 0
    for n in names:
        p = plan(action, n)
        if "error" in p:
            print(f"{n}: {p['error']}")
            code = 1
            continue
        note = "" if p["known"] else "  (not in my built-in list: using the name as given)"
        print(f"{action.capitalize()} {p['key']} with {p['manager']}{note}")
        rc = execute(p, preview)
        if rc:
            print(f"{n}: the package manager reported an error (code {rc}). If it asked for a password or approval, run this again in a terminal.")
            code = 1
        elif not preview:
            print(f"{n}: done.")
    if preview:
        print("Preview only: nothing was changed.")
    return code
