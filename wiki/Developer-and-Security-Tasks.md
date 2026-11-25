# Developer and security tasks

Defensive, local-only tasks for software engineers and security-minded people. None of them sends anything over the network, and the ones that look at secrets **never print the secret values**.

| Say | What it does |
|---|---|
| `find todo [folder]` | Lists TODO, FIXME and HACK comments in a project folder. |
| `find secrets [folder]` | Looks for passwords, API keys and private keys left in code before you share it. Values are hidden; you see the file, line and kind. |
| `env diff <file1> <file2>` | Compares two `.env` files: which keys are missing or different. Values are not printed. |
| `log analyze <file>` | Counts by level, the most common errors, the busiest minutes. |
| `semver <a> vs <b>` | Compares versions the way package managers do (`semver 1.2.3 vs 1.10.0`). |
| `identify file <file>` | Tells what a file really is from its first bytes and warns if the name is misleading. |
| `ssh key audit` | Checks your SSH folder for old key types, no passphrase and loose permissions. Reads only; never shows a key. |
| `integrity save <folder>` | Saves fingerprints of a folder. |
| `integrity check <folder>` | Shows which files were added, changed or removed since the save. Also `integrity list` and `integrity forget <folder>`. |

## Examples
```
find secrets myproject
env diff .env.example .env
integrity save ~/site
integrity check ~/site
```

## Good to know
- `find secrets` is a pattern scanner. It finds common shapes (cloud keys, private key blocks, `password = "..."`), not everything. Treat a clean result as "nothing obvious", not as proof.
- `integrity` detects changes since *you* saved the baseline. It does not tell you who changed a file, and an attacker who can change the files can also change the baseline folder, so keep important baselines elsewhere (for example on a USB stick).
- These tasks read only what you point them at. Hidden links (symlinks) are not followed out of the folder.
- Related: [Safety and Privacy](Safety-and-Privacy), [Reference: Developer tools](Reference-Developer-Tools), and the published security notes in `SECURITY.md`.
