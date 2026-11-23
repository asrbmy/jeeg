# Apple Shortcuts (macOS) with JeeG

**A shortcut that runs a task you type**
1. Shortcuts > New Shortcut. Add **Ask for Input** (Text) with the prompt "What do you want to do?".
2. Add **Run Shell Script**: Shell `zsh`, Pass Input `as arguments`, script:

       export PATH="$PATH:/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin"
       jeeg "$1"

3. Add **Show Result** (or **Copy to Clipboard**).

**A shortcut that runs a text task on the selection** (Services menu / Quick Actions)
1. New Quick Action receiving **Text** in any application.
2. **Run Shell Script**, Pass Input `to stdin`, script: `jeeg word count` (or `jeeg uppercase`, `jeeg sort lines`).
3. **Copy to Clipboard**.

`Run Shell Script` is a macOS feature; Shortcuts on iPhone and iPad cannot run it, and JeeG's API listens only on the
computer itself, so the iPhone cannot reach it.
