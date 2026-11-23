# Alfred workflow for JeeG (macOS, Alfred Powerpack)

Build it in Alfred in a minute:

1. Alfred Preferences > Workflows > **+** > Blank Workflow, name it JeeG.
2. Add **Inputs > Keyword**: keyword `jg`, argument *Required*, title `JeeG`.
3. Connect it to **Actions > Run Script**: Language `/bin/bash`, *with input as* `argv`, script:

       export PATH="$PATH:/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin"
       jeeg "$1"

4. Connect that to **Outputs > Copy to Clipboard** (and, if you like, **Post Notification** with `{query}` as the text).

Type `jg gst 2500 18` in Alfred. The phrase is passed as one argument, not through a shell string, so quotes and
symbols in it cannot run other commands.

Tasks that ask for confirmation will print that they need one instead of running; run those in a terminal.
