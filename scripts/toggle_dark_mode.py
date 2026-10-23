# keywords: dark mode, light mode, dark theme, night mode, theme, appearance, toggle theme, dark, light, mode
# desc: Switch dark/light mode (dark mode on, dark mode off, or toggle)
# category: hardware
# usage: dark mode on|off
# rawargs: yes
import shutil, subprocess
from _lib import WIN, MAC, args_text, fail
from _sys import out
a = args_text().lower().split()
want = "dark" if any(x in a for x in ("on", "dark", "enable")) else "light" if any(x in a for x in ("off", "light", "disable")) else None
if WIN:
    import winreg
    k = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, k, 0, winreg.KEY_READ | winreg.KEY_SET_VALUE) as key:
        is_light = winreg.QueryValueEx(key, "AppsUseLightTheme")[0] == 1
        go_dark = (want == "dark") if want else is_light
        for n in ("AppsUseLightTheme", "SystemUsesLightTheme"):
            winreg.SetValueEx(key, n, 0, winreg.REG_DWORD, 0 if go_dark else 1)
    print("Dark mode ON." if go_dark else "Light mode ON.")
elif MAC:
    expr = {"dark": "true", "light": "false", None: "not dark mode"}[want]
    subprocess.run(["osascript", "-e", f'tell application "System Events" to tell appearance preferences to set dark mode to {expr}'])
    print("Theme set." if want else "Theme toggled.")
elif shutil.which("gsettings"):
    cur = out(["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"])
    go_dark = (want == "dark") if want else "dark" not in cur
    subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", "prefer-dark" if go_dark else "default"])
    print("Dark mode ON." if go_dark else "Light mode ON.")
else:
    fail("Theme switching is not supported on this desktop.")
