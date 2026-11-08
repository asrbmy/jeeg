# Security policy

## Reporting a problem
Please do not open a public issue for a security problem. Report it privately:

- **GitHub:** https://github.com/asrbmy/jeeg/security/advisories/new  (or the **Security** tab, then **Report a vulnerability**)

Include what you typed, what happened, and your system (`jeeg --version`; `doctor` shows more). Do not include real passwords, tokens or personal files.

### What to expect
| Step | Target time |
|---|---|
| We confirm we received it | within 3 days |
| First assessment (real issue or not, how serious) | within 7 days |
| Fix released for a confirmed high-severity problem | within 30 days |
| Fix released for lower-severity problems | next regular release |
| Public note in `CHANGELOG.md` and the GitHub advisory | when the fix is out, crediting you if you wish |

This is a small project run by volunteers, so these are goals, not guarantees. If you hear nothing in a week, write again on the same advisory.

### Scope
In scope: the `jeeg` code and scripts in this repository, the plugin library and its fingerprints, the local web page, the local API (`--serve-api`, `--stdio`, `--mcp`), and the release workflow. Out of scope: problems that need you to install a plugin or run a script you did not trust, and issues in Python, your operating system or other software.

## Supported versions
Only the latest release is supported.

## What JeeG protects
- Links: only `http`, `https`, `mailto`, `tel`, `sms` and `whatsapp` links are opened.
- Files: archives cannot write outside the folder they are extracted to; imports and backups are validated; file moves and renames can be undone and never overwrite.
- Data: the data folder is private to you on Mac and Linux; private tasks are not written to history.
- Input: control characters are removed and very long lines are refused.
- Plugins: size limit, built-in names protected, fingerprint check for library plugins, a risk scan and a confirmation before installing.
- Web page (`web`): listens only on `127.0.0.1`, needs a random token, rejects unknown Host and Origin headers, declines tasks that need confirmation.
- Local API (`--serve-api`): `127.0.0.1` only, token required, refuses web pages, size/time/parallel limits, optional `--only` / `--except` allow-lists and a content-free `--log`. `--stdio` and `--mcp` use the same rules. Tasks that ask for confirmation never run unless you start with `--allow-confirm`.
- Piped input and `autorun`: piped text is capped at 1 MB and never run as a command; scheduled phrases are quoted for cron and Task Scheduler and cannot be `update`, `plugin` or `setup`.

## What is not protected
- Plugins and extra script folders run with your permissions. Only install ones you trust.
- JeeG does not sandbox the tasks it runs. A task that deletes things asks first (`confirm`), but you are responsible for what you confirm.

## Verifying a release
Releases uploaded to PyPI by the `publish` workflow carry build provenance. Check one with:

    gh attestation verify jeeg-X.Y.Z-py3-none-any.whl --repo asrbmy/jeeg

(download the wheel from the GitHub release first). The workflow also uploads the files and their SHA-256 sums to the release page.
