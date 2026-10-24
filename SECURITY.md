# Security policy

## Reporting a problem
Please do not open a public issue for a security problem. On GitHub, open the **Security** tab of this repository and choose **Report a vulnerability**. Include what you typed, what happened, and your system (`jeeg --version`).
You should get a reply within a week. Fixes are released as a new version and listed in `CHANGELOG.md`.

## Supported versions
Only the latest release is supported.

## What JeeG protects
- Links: only `http`, `https`, `mailto`, `tel`, `sms` and `whatsapp` links are opened.
- Files: archives cannot write outside the folder they are extracted to; imports and backups are validated; file moves and renames can be undone and never overwrite.
- Data: the data folder is private to you on Mac and Linux; private tasks are not written to history.
- Input: control characters are removed and very long lines are refused.
- Plugins: size limit, built-in names protected, fingerprint check for library plugins, a risk scan and a confirmation before installing.
- Web page (`web`): listens only on `127.0.0.1`, needs a random token, rejects unknown Host and Origin headers, declines tasks that need confirmation.

## What is not protected
- Plugins and extra script folders run with your permissions. Only install ones you trust.
- JeeG does not sandbox the tasks it runs. A task that deletes things asks first (`confirm`), but you are responsible for what you confirm.

## Verifying a release
Releases uploaded to PyPI by the `publish` workflow carry build provenance. Check one with:

    gh attestation verify jeeg-X.Y.Z-py3-none-any.whl --repo asrbmy/jeeg

(download the wheel from the GitHub release first). The workflow also uploads the files and their SHA-256 sums to the release page.
