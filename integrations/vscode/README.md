# JeeG for VS Code (starter)

A small extension that runs JeeG tasks from inside VS Code.

1. Install JeeG: `pip install jeeg` (check with `jeeg --version`).
2. Press `F1` and choose **JeeG: Run a task**, type a phrase such as `gst 2500 18`, and read the answer in the **JeeG** output panel.
3. Select text and choose **JeeG: Run the selected text as a task**, or **Send the selected text to a task** (for example `word count`, `sort lines`, `uppercase`).

It starts the local `jeeg` command without a shell, never uses the network itself, and has no telemetry.

To try it from source: open this folder in VS Code and press `F5`. To make an installable file: `npm i -g @vscode/vsce` then `vsce package`.
