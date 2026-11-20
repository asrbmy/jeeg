# For administrators: limiting JeeG on a computer

JeeG reads one optional **policy file** that only an administrator can write. It can only limit things; it never adds anything. A person using JeeG cannot change it from JeeG.

## Where it lives

| System | File |
|---|---|
| Windows | `%ProgramData%\JeeG\policy.json` |
| macOS | `/Library/Application Support/JeeG/policy.json` |
| Linux | `/etc/jeeg/policy.json` |
| Testing | any path, with the environment variable `JEEG_POLICY` |

On macOS and Linux a policy file that other users can write (or that belongs to someone else) is **ignored** and reported, because it would not be a policy. On Windows, set the folder permissions so only administrators can write to it.

## What it can say

```json
{
  "note": "Set by IT, ask helpdesk to change",
  "disable_categories": ["system", "files"],
  "disable_tasks": ["shred file", "send email"],
  "block_online": true,
  "block_plugins": true,
  "ai_max": "read",
  "ai_browser": false
}
```

- `disable_categories`, `disable_tasks`: those tasks are removed. Asking for one says "Your administrator has turned off ...".
- `block_online`: removes tasks that JeeG itself sends over the internet (the ones marked `# network: yes`, such as download, exchange rates, news). Tasks that only open a page in your own browser are not network tasks.
- `block_plugins`: ignores everything in the plugin folder.
- `ai_max`: the highest AI mode allowed: `off`, `safe`, `read`, `ask` or `god`. A person asking for a higher one gets this one; `off` refuses every AI request.
- `ai_browser`: `false` stops an AI from controlling the browser.

A wrong value is reported (not applied) instead of breaking JeeG. Check what is in force with `policy`.

## What each person can see

- `policy` shows the limits in plain words.
- `audit show`, `audit summary`, `audit ai` and `audit export` list what ran, when, whether it worked, and whether you or an AI asked for it. The log holds task names and results only, never what was typed. Turn logging off with `--no-log`.

## Saved-data upgrades

JeeG stamps your data folder with a data version. When a future release needs your records in a different shape, it saves a zip copy in `backups/`, upgrades once, and rolls back if anything fails. Records written by a newer JeeG are never changed.

## Not covered (be honest with your users)

A person who can edit files as an administrator can remove the policy. JeeG is a program running as the person, so the policy is a guard rail, not a security boundary against a determined local administrator. It has not had an independent security review.
