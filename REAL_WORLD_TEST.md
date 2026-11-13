# Testing JeeG on your real computer, with an AI to help

JeeG is built and tested on Linux in a sandbox. It cannot be tested there on a real Windows PC, a real Mac, a real printer, or the real GitHub, Telegram, Discord and Slack. **You can**, and JeeG has a built-in test for exactly that. You can run it yourself, or connect Claude.ai (or any AI that supports MCP) through JeeG and let the AI run it for you and explain what went wrong.

Everything in the test is **harmless**: it only looks, or it shows ("previews") a command without running it. It installs nothing, changes no setting, sends no message, deletes nothing. The list of checks is fixed inside JeeG: an AI can choose which group to run, but it cannot add a check or run anything else through this.

## Option 1: do it yourself (5 minutes)

    real test list              what will be checked (43 checks in 9 groups)
    real test run all           run everything (or one group:  real test run system)
    real test report            a private report you can share

The report has your user name, computer name, IP and MAC addresses, e-mail addresses, home folder and anything that looks like a secret **removed**. Read it before you send it.

## Option 2: let Claude.ai run it for you

1. Connect Claude.ai to your PC through JeeG (full steps in REMOTE_AI.md). In short, on the PC:

       connect ai ask

   `ask` mode shows you every request before it runs. Add the printed link in Claude.ai as a custom connector.
2. Print the instructions for the AI and paste them into Claude.ai:

       real test ai

3. Claude runs the checks one group at a time, fetches the report, asks you about the few things only a person can see (for example "did a notification pop up?"), and writes you a summary: what works, what failed with the exact error, and a likely cause and fix.
4. Copy that summary, and the report, to whoever is fixing JeeG (you can paste them to me in the chat).

Why it is safe to let an AI do this:
- In `read` mode (the default way to try it) the AI can run the real test, and nothing that changes anything.
- The AI never sees your logins. For linked apps the test only says "worked" or "did not", and never shows what is inside your GitHub or Telegram.
- Report and results are redacted before the AI or you see them.
- Linking apps and logging in are terminal-only, so the AI cannot do them.

## Compare two runs, and test after an update

`real test run all` keeps a snapshot of every result with the JeeG version (last 10 runs). After updating JeeG, JeeG tells you ("JeeG was updated 2.19.0 -> 2.20.0 since your last real test"); run the test again and then:

    real test compare

It lists what got worse, what got better, and which checks are new or gone, and says if the version changed in between. Send the "got worse" lines with `real test report` to whoever fixes JeeG.

## What the groups check

| Group | What | Notes |
|---|---|---|
| engine | JeeG's own self-check, calculator, unit conversion | |
| system | disk, memory, processor, battery, Wi-Fi, processes, programs, USB, ports | Parts that differ most between Windows, Mac and Linux. A desktop with no battery or Wi-Fi gives a warning, which is normal. |
| files | folder size, tree, word count, file fingerprint | In a throw-away folder. |
| install | the install, uninstall, update and bundle commands are built and shown | Never run. Shows which package manager JeeG found (winget, choco, brew, apt, dnf, pacman, flatpak). |
| network | network doctor, internet, devices on your Wi-Fi | |
| devices | printers, a desktop notification | The notification needs your eyes. |
| env | saving an environment variable and PATH | Shown only, nothing saved. |
| apps | each app you linked: read works, write shown as a preview | Apps you have not logged in to are skipped, with how to log in. |
| ai | whether this PC has a tunnel program for AI mode (cloudflared, ngrok or ssh) | |

## Reading the result

- **PASS**: it worked.
- **warn**: it did not work but that is often fine (hardware you do not have, or being offline).
- **FAIL**: a real problem. `real test show <id>` gives the command, the output and a hint.
- **MANUAL**: a person must confirm (the AI will ask you).
- **skip**: not logged in or not applicable.

## What no program can check for you

`real test manual` prints this list. It is the part to do by hand, once:

1. Phone approval page: `connect ai ask phone`, open the link on your phone, approve one request.
2. The Claude.ai connection itself (steps above).
3. Telegram: `telegram setup`, then message your bot from your phone.
4. A linked-app **write**, one at a time, to yourself: a Telegram message to your own chat id, a comment on a repository of your own.
5. WhatsApp: the chat opens with your text typed in, and you press Send.
6. Printing a real page.
7. The standalone program (`jeeg.exe`, `jeeg-macos`) from a double-click or a terminal.
8. Installing and uninstalling one small program for real (for example 7zip).
9. Windows: PowerShell and cmd. Mac: the macOS security prompt on first run.

## When something fails

Send the report (and, for a FAIL, the output of `real test show <id>`). Real failures I would expect on a first run, and where to look:

- **install.manager FAIL**: JeeG could not find winget, choco, brew, apt, dnf or pacman. Windows 10/11: install "App Installer" from the Microsoft Store.
- **system.* warn on Windows or Mac**: a few readouts use different commands per system; a warning there is exactly the kind of thing worth reporting.
- **network.wifi warn**: the neighbour table is hidden on some systems.
- **apps.* FAIL**: the login is wrong or expired (`app login <name>`), or the app changed its API. `app read <app> <action>` shows the app's own error.
