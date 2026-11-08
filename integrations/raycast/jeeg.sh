#!/bin/bash
# Raycast Script Command: run any JeeG task from Raycast. Put this file in your Raycast scripts folder.
# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title JeeG
# @raycast.mode fullOutput
# @raycast.packageName JeeG
# @raycast.argument1 { "type": "text", "placeholder": "task, e.g. gst 2500 18" }
# @raycast.icon 🧰
export PATH="$PATH:/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin"
exec jeeg "$1"
