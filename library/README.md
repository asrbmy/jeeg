# JeeG plugin library

Small shared tasks. Add one with:

    jeeg plugin search <word>
    jeeg plugin get <name>

Each file's SHA-256 fingerprint is listed in `index.json`; JeeG refuses a file that does not match, then shows you what the plugin says it does and a quick scan before asking you to confirm.

## Contribute a plugin
1. Make it with `jeeg plugin new my_task` and keep it to the standard library, one file, under 200 KB.
2. It must say what it does in its header (`# keywords:` and `# desc:`) and do nothing outside what the description says: no hidden network calls, no files outside the folder the user names.
3. Put it in this folder, run `python tools/make_library_index.py`, and open a pull request.
Maintainers read every plugin before merging. Plugins run with the user's permissions, so a plugin that downloads or runs other code will not be accepted.
