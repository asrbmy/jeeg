# JeeG in Raycast and Alfred

**Raycast:** copy `jeeg.sh` into your Raycast "Script Commands" folder, then type `JeeG` and a task.

**Alfred:** make a Workflow with a *Keyword* (for example `jg`, argument required) connected to a
*Run Script* action (language `/bin/bash`, input as argv):

    export PATH="$PATH:/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin"
    jeeg "$1"

then a *Post Notification* or *Large Type* action to show the output.

Both run the `jeeg` command on your computer; nothing is sent anywhere. Tasks that ask for
confirmation are declined in these launchers (they cannot answer the question); run those in a terminal.
