# Reference: System, power, hardware and home

Status of your computer, power and screen control, volume and brightness, devices, and household helpers.

59 tasks. Each entry shows the **usage** (`<x>` you fill in, `[x]` optional), what the task does, how it behaves, other words that also find it, and the script file you can read or edit. Say the task name, or the usage with your words filled in. `explain <words>` shows how any phrase is matched; `<task> preview` or `--dry-run` shows what would happen without doing it.

Categories on this page: [system](#system), [power](#power), [hardware](#hardware), [home](#home), [selfcheck](#selfcheck)

## system

### battery status

**What it does:** Show battery level and charging state  
**Also found by:** `battery`, `charge`, `charging`, `power level`, `plugged`, `laptop`  
**Script:** `scripts/battery_status.py`

### check updates

**What it does:** Check which programs and system updates are waiting (does not install)  
**Behaviour:** asks before running; can use the internet.  
**Also found by:** `software updates`, `windows update`, `available updates`, `pending updates`, `upgradable packages`, `outdated software`, `any updates`  
**Script:** `scripts/check_updates.py`

### cpu temperature

**What it does:** Show processor temperature (where the computer allows it)  
**Also found by:** `temperature`, `cpu temp`, `how hot`, `processor temperature`, `laptop heat`, `thermal`, `overheating`, `check temp`  
**Script:** `scripts/cpu_temperature.py`

### cpu usage

**What it does:** Show current CPU load  
**Also found by:** `cpu`, `processor`, `load`, `cpu load`, `busy`  
**Script:** `scripts/cpu_usage.py`

### desktop input

**Usage:** `desktop type <text> | desktop key <combo> | desktop click <x> <y> | add 'preview' to see what would happen`  
**What it does:** Type, press keys or click at a screen position in whatever window is in front (desktop type hello, desktop key ctrl+s, desktop click 500 300). Asks first; you only, never an AI. Windows built in; Linux needs xdotool; macOS needs cliclick for clicks.  
**Behaviour:** asks before running.  
**Also found by:** `desktop type`, `desktop key`, `desktop click`, `press keys on screen`, `type into app`, `click on screen`, `mouse click`, `send keys`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/desktop_input.py`

### disk space

**What it does:** Show free space on your drives  
**Also found by:** `disk`, `storage`, `drive`, `drives`, `space`, `free space`, `hard disk`, `ssd`, `capacity`  
**Script:** `scripts/disk_space.py`

### env variable

**Usage:** `set env variable NAME to VALUE | remove env variable NAME | add <folder> to path`  
**What it does:** Save an environment variable for good (set env variable API_URL to https://x.com) or add a folder to PATH (add C:\tools to path). Add "preview" to see what would change. New terminals pick it up.  
**Behaviour:** asks before running.  
**Also found by:** `environment variable`, `permanent variable`, `persistent variable`, `add to path`, `add folder to path`, `setx`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/env_variable.py`

### find software

**Usage:** `search app [words]`  
**What it does:** Find an app in your package manager (search app video editor), or list the apps I can install by short name (search app)  
**Behaviour:** can use the internet.  
**Also found by:** `search app`, `find app`, `find program`, `search package`, `what can i install`, `installable apps`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/find_software.py`

### gpu info

**What it does:** Show graphics card details  
**Also found by:** `gpu`, `graphics card`, `video card`, `graphics info`, `nvidia`, `display adapter`, `which gpu`  
**Script:** `scripts/gpu_info.py`

### health check

**What it does:** One-screen check of your computer: disk, memory, CPU, battery, uptime, with warnings  
**Also found by:** `system health`, `pc health`, `computer health`, `is my pc ok`, `pc checkup`, `computer checkup`  
**Script:** `scripts/health_check.py`

### install app

**Usage:** `install <app> [and <app> ...] [preview]`  
**What it does:** Install an app or program by name with your system's package manager (install vlc, install chrome and git; add "preview" to see the command only)  
**Behaviour:** asks before running; can use the internet.  
**Also found by:** `install software`, `install program`, `install application`, `setup app`, `download and install`, `install chrome`, `install vlc`, `install vscode`, `install git`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/install_app.py`

### install bundle

**Usage:** `install <dev|office|media|student|privacy> bundle [preview]`  
**What it does:** Install a set of apps in one go (install dev bundle: git, python, vscode, nodejs; also office, media, student, privacy). Add "preview" to see the commands only.  
**Behaviour:** asks before running; can use the internet.  
**Also found by:** `setup dev machine`, `setup new computer`, `new pc setup`, `install essentials`, `install pack`, `dev setup`, `office setup`, `install my tools`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/install_bundle.py`

### installed programs

**Usage:** `installed programs [name]`  
**What it does:** List installed programs, or search them (installed programs chrome)  
**Also found by:** `installed apps`, `list programs`, `what is installed`, `installed software`, `list apps`, `programs installed`  
**Your words:** passed through untouched  
**Script:** `scripts/installed_programs.py`

### is installed

**Usage:** `is <app> installed | version of <app>`  
**What it does:** Check whether a program is installed and which version (is git installed, which version of python, do i have vlc)  
**Also found by:** `is it installed`, `installed or not`, `do i have`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/is_installed.py`

### keep awake

**Usage:** `keep awake [2 hours]`  
**What it does:** Stop the computer sleeping for a while (keep awake 2 hours)  
**Also found by:** `stay awake`, `prevent sleep`, `no sleep`, `caffeinate`, `stop sleeping`, `dont sleep`, `keep screen on`, `stop screen sleeping`  
**Your words:** passed through untouched  
**Script:** `scripts/keep_awake.py`

### kill process

**Usage:** `kill process <name>`  
**What it does:** Close a program by name (e.g. kill process notepad)  
**Behaviour:** asks before running.  
**Also found by:** `kill`, `stop`, `terminate`, `end`, `close`, `force quit`, `end task`, `process`, `program`  
**Script:** `scripts/kill_process.py`

### memory usage

**What it does:** Show RAM usage  
**Also found by:** `ram`, `memory`, `free memory`, `ram usage`  
**Script:** `scripts/memory_usage.py`

### print file

**Usage:** `print <file> [preview]`  
**What it does:** Print a file on your default printer (print report.pdf; add "preview" to see the command only)  
**Behaviour:** asks before running.  
**Also found by:** `print document`, `print pdf`, `print this`, `send to printer`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/print_file.py`

### restart explorer

**What it does:** Restart Windows Explorer when the taskbar or desktop freezes  
**Behaviour:** asks before running.  
**Also found by:** `explorer frozen`, `taskbar frozen`, `restart taskbar`, `fix taskbar`, `explorer not responding`, `restart windows explorer`, `desktop frozen`  
**Script:** `scripts/restart_explorer.py`

### running processes

**What it does:** List the programs using the most memory  
**Also found by:** `processes`, `process list`, `running programs`, `what is running`, `tasks running`, `top`, `memory hogs`  
**Script:** `scripts/running_processes.py`

### screen off

**What it does:** Turn the screen off without sleeping  
**Also found by:** `turn off screen`, `turn off display`, `monitor off`, `display off`, `blank screen`, `switch off monitor`  
**Script:** `scripts/screen_off.py`

### screen resolution

**What it does:** Show your screen resolution  
**Also found by:** `display resolution`, `screen size`, `monitor resolution`, `display size`, `how many pixels`, `resolution`  
**Script:** `scripts/screen_resolution.py`

### setup check

**Usage:** `setup check`  
**What it does:** Check your saved devices, paired computers, bridge rules, ports and optional tools, and say what to fix (setup check). For the basic JeeG self-check use: doctor  
**Behaviour:** can use the internet.  
**Also found by:** `check setup`, `check my setup`, `check devices and link`, `devices and link check`, `are my devices ok`  
**Script:** `scripts/setup_check.py`

### show printers

**Usage:** `show printers`  
**What it does:** List your printers and whether they are ready, and the default one  
**Also found by:** `printer status`, `my printers`, `list printers`, `is the printer on`, `printer queue`, `printer online`  
**Script:** `scripts/show_printers.py`

### show uptime

**What it does:** Show how long the computer has been on  
**Also found by:** `uptime`, `how long on`, `running time`, `boot time`, `since boot`, `last restart`  
**Script:** `scripts/show_uptime.py`

### startup programs

**What it does:** List programs that start with your computer  
**Also found by:** `startup apps`, `autostart`, `what starts at boot`, `boot programs`, `login items`, `programs on startup`, `startup items`  
**Script:** `scripts/startup_programs.py`

### system info

**What it does:** Show OS, CPU, memory, disk and uptime  
**Behaviour:** can use the internet.  
**Also found by:** `system`, `info`, `computer`, `specs`, `pc`, `hardware`, `configuration`, `about`, `details`  
**Script:** `scripts/system_info.py`

### uninstall app

**Usage:** `uninstall <app> [preview]`  
**What it does:** Uninstall an app by name with your system's package manager (uninstall vlc; add "preview" to see the command only)  
**Behaviour:** asks before running.  
**Also found by:** `remove app`, `uninstall software`, `remove program`, `uninstall program`, `delete app`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/uninstall_app.py`

### update apps

**Usage:** `update all apps | update app <name> [preview]`  
**What it does:** Update all your installed apps (update all apps), or one (update app vlc); add "preview" to see the command only  
**Behaviour:** asks before running; can use the internet.  
**Also found by:** `upgrade apps`, `update all apps`, `upgrade all software`, `update software`, `update programs`, `update installed apps`, `outdated apps`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/update_apps.py`

### usb devices

**What it does:** List connected USB devices  
**Also found by:** `usb list`, `connected usb`, `what usb is plugged`, `plugged in devices`, `usb drives`, `connected devices`  
**Script:** `scripts/usb_devices.py`

### window control

**Usage:** `windows list | window focus|minimize|maximize|restore|close <part of title> | window snap <part of title> left|right|full`  
**What it does:** List and control open windows (windows list, window focus chrome, window minimize notepad, window snap chrome left, window close notepad). Windows built in; Linux needs wmctrl or xdotool; macOS uses System Events.  
**Also found by:** `windows list`, `list windows`, `focus window`, `close window`, `minimize window`, `maximize window`, `move window`, `snap window`, `switch to window`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/window_control.py`


## power

### cancel shutdown

**What it does:** Cancel a pending shutdown or restart  
**Also found by:** `abort shutdown`, `stop shutdown`, `cancel restart`, `cancel reboot`, `abort`, `undo shutdown`  
**Script:** `scripts/cancel_shutdown.py`

### lock screen

**What it does:** Lock the computer  
**Also found by:** `lock`, `lock pc`, `lock computer`, `secure`, `lock my`  
**Script:** `scripts/lock_screen.py`

### log out

**What it does:** Sign out of the current user  
**Behaviour:** asks before running.  
**Also found by:** `logout`, `sign out`, `signout`, `log off`, `logoff`  
**Script:** `scripts/log_out.py`

### restart pc

**What it does:** Restart the computer (30 second delay, can be cancelled)  
**Behaviour:** asks before running.  
**Also found by:** `restart`, `reboot`, `reset`, `restart computer`  
**Script:** `scripts/restart_pc.py`

### schedule shutdown

**Usage:** `schedule shutdown <minutes>`  
**What it does:** Shut down after N minutes (schedule shutdown 45 minutes)  
**Behaviour:** asks before running.  
**Also found by:** `shutdown after`, `shutdown in`, `auto shutdown`, `shutdown timer`, `sleep timer`  
**Script:** `scripts/schedule_shutdown.py`

### shutdown pc

**What it does:** Shut the computer down (30 second delay, can be cancelled)  
**Behaviour:** asks before running.  
**Also found by:** `shutdown`, `shut down`, `power off`, `turn off`, `switch off`, `switch off pc`, `off`  
**Script:** `scripts/shutdown_pc.py`

### sleep pc

**What it does:** Put the computer to sleep  
**Behaviour:** asks before running.  
**Also found by:** `sleep`, `suspend`, `standby`, `sleep mode`  
**Script:** `scripts/sleep_pc.py`


## hardware

### android adb

**Usage:** `android devices | android battery | android screenshot | android open <web address>`  
**What it does:** Look at an Android phone over USB or Wi-Fi with adb (android devices, android battery, android screenshot, android open https://example.com)  
**Also found by:** `android`, `adb`, `android phone`, `my android`, `android battery`, `android screenshot`, `phone over usb`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/android_adb.py`

### bluetooth devices

**Usage:** `bluetooth list | bluetooth connect <name> | bluetooth disconnect <name>`  
**What it does:** List paired Bluetooth devices and connect or disconnect one (bluetooth list, bluetooth connect headphones). Uses the system's own tools; Linux needs bluetoothctl, macOS needs blueutil for connect.  
**Also found by:** `bluetooth list`, `bluetooth connect`, `bluetooth disconnect`, `paired bluetooth`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/bluetooth_devices.py`

### mute volume

**What it does:** Mute or unmute the sound  
**Also found by:** `mute`, `unmute`, `silence`, `sound off`, `sound on`, `toggle mute`, `quiet`  
**Script:** `scripts/mute_volume.py`

### next track

**What it does:** Skip to the next song  
**Also found by:** `next`, `next song`, `skip`, `skip song`, `forward track`  
**Script:** `scripts/next_track.py`

### play pause

**What it does:** Play or pause the current media  
**Also found by:** `pause`, `resume`, `pause music`, `resume music`, `pause video`, `stop music`, `toggle playback`, `playpause`  
**Script:** `scripts/play_pause.py`

### previous track

**What it does:** Go back to the previous song  
**Also found by:** `previous`, `previous song`, `back track`, `last song`, `rewind track`  
**Script:** `scripts/previous_track.py`

### serial port

**Usage:** `serial ports | serial send <port> <text> [baud 9600] | serial read <port> [seconds]`  
**What it does:** List serial ports or send a line to a device such as an Arduino (serial ports, serial send COM3 hello). Needs pip install pyserial.  
**Also found by:** `arduino`, `com port`, `usb serial`, `serial ports`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/serial_port.py`

### set brightness

**Usage:** `set brightness <0-100>`  
**What it does:** Set screen brightness (set brightness 60)  
**Also found by:** `brightness`, `dim`, `brighten`, `screen brightness`, `dimmer`, `brighter`, `display brightness`  
**Script:** `scripts/set_brightness.py`

### set volume

**Usage:** `set volume <0-100>`  
**What it does:** Set the volume to a level (set volume 40)  
**Also found by:** `volume to`, `volume level`, `volume percent`, `sound level`  
**Script:** `scripts/set_volume.py`

### show desktop

**What it does:** Minimise everything and show the desktop  
**Also found by:** `minimize all`, `minimise all`, `hide windows`, `clear screen windows`, `desktop`  
**Script:** `scripts/show_desktop.py`

### take screenshot

**What it does:** Save a screenshot to your Pictures folder  
**Also found by:** `screenshot`, `screen`, `capture`, `snap`, `screen shot`, `print screen`, `grab screen`, `screengrab`  
**Script:** `scripts/take_screenshot.py`

### toggle dark mode

**Usage:** `dark mode on|off`  
**What it does:** Switch dark/light mode (dark mode on, dark mode off, or toggle)  
**Also found by:** `dark mode`, `light mode`, `dark theme`, `night mode`, `theme`, `appearance`, `toggle theme`, `dark`, `light`, `mode`  
**Your words:** passed through untouched  
**Script:** `scripts/toggle_dark_mode.py`

### volume down

**Usage:** `volume down [amount]`  
**What it does:** Lower the volume  
**Also found by:** `quieter`, `decrease volume`, `lower volume`, `turn down`, `sound down`, `reduce volume`  
**Script:** `scripts/volume_down.py`

### volume up

**Usage:** `volume up [amount]`  
**What it does:** Raise the volume  
**Also found by:** `louder`, `increase volume`, `raise volume`, `turn up`, `sound up`  
**Script:** `scripts/volume_up.py`


## home

### electricity bill

**Usage:** `electricity bill <units> at <rate> [fixed <amt>]`  
**What it does:** Estimate an electricity bill (electricity bill 250 units at 7)  
**Also found by:** `power bill`, `light bill`, `units to bill`, `bijli bill`, `current bill estimate`  
**Your words:** passed through untouched  
**Script:** `scripts/electricity_bill.py`

### gas cylinder

**Usage:** `cylinder changed [date] | cylinder | cylinder remove`  
**What it does:** Track gas cylinder changes and when the next one is due (cylinder changed; cylinder; cylinder history)  
**Behaviour:** never saved in history.  
**Also found by:** `lpg cylinder`, `cylinder changed`, `cylinder refill`, `cylinder due`, `cooking gas`, `when will gas run out`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/gas_cylinder.py`

### service log

**Usage:** `<item> <qty> [at <price>] | <item> absent [date] | <item> summary [month]`  
**What it does:** Keep a daily log for milk, maid, newspaper and similar (milk 1.5 at 60; maid absent 3 nov; milk summary)  
**Behaviour:** never saved in history.  
**Also found by:** `maid log`, `maid absent`, `daily service`, `newspaper log`, `service summary`, `milkman`, `helper attendance`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/service_log.py`

### subscription tracker

**Usage:** `add subscription <name> <date> | subscriptions | remove subscription <name>`  
**What it does:** Track subscriptions and renewal dates (add subscription netflix 15 dec 2026, subscriptions)  
**Also found by:** `subscription`, `subscriptions`, `add subscription`, `renewal`, `subscription renewal`, `remove subscription`, `my subscriptions`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/subscription_tracker.py`

### vehicle dues

**Usage:** `add vehicle due <what> <date> | vehicle dues | remove vehicle due <what>`  
**What it does:** Track insurance, pollution certificate and service dates (add vehicle due insurance bike 15 dec 2026, vehicle dues)  
**Also found by:** `vehicle due`, `insurance due`, `puc due`, `pollution certificate`, `service due`, `car papers`, `bike insurance`, `vehicle log`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/vehicle_dues.py`

### warranty tracker

**Usage:** `add warranty <item> <date> | warranties | remove warranty <item>`  
**What it does:** Keep warranty end dates and see what expires soon (add warranty laptop 12 mar 2027, warranties, remove warranty laptop)  
**Also found by:** `warranty`, `warranties`, `add warranty`, `warranty expiry`, `warranty ends`, `show warranties`, `guarantee expiry`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/warranty_tracker.py`


## selfcheck

### realtest

**Usage:** `real test list | real test run <group|id|all> | real test show <id> | real test compare | real test report | real test ai | real test manual | real test clear`  
**What it does:** Test JeeG on this real computer, by yourself or with an AI you connected (Claude.ai...). Harmless checks only; makes a private report you can share. real test list | run <group> | report | ai | manual  
**Behaviour:** can use the internet.  
**Also found by:** `real pc test`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/realtest.py`


Back to [Home](Home) | [Task Catalog](Task-Catalog).
