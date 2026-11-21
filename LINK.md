# JeeG link: JeeG computers talking to each other

JeeG link lets two or more computers that run JeeG pair once, then send messages and files, and (if you allow it) run tasks on each other. It works on a home network and across the internet. There is no account, no company server, and nothing is sent anywhere you did not choose.

## The short version

On the computer that will **wait** (the "other" computer):

    link name Kitchen PC
    link listen

On your computer:

    link find                      (lists JeeGs on your network)
    link pair 192.168.1.20         (use the address from the list)

Both screens show the same **6-digit number**. If, and only if, the numbers are identical, say yes on both. Then each person chooses what the other computer may do. After that:

    link send kitchen pc dinner is at 7
    link file kitchen pc ~/Documents/plan.pdf
    link run kitchen pc show my reminders
    link ping kitchen pc
    link inbox                     (messages people sent you)
    link peers | link level <name> <level> | link forget <name>

## Levels: what THEY may do on YOUR computer

You choose a level for each paired computer, and can change it at any time (it takes effect at once, even on a connection that is already open).

| Level | What the other computer may do |
|---|---|
| `block` | Nothing. Connections are refused. |
| `chat` | Send messages and files (files go to `Downloads/JeeG received`; programs and scripts are refused). |
| `safe` | Also run tasks that only look (no changes). |
| `read` | Also read your files and records. |
| `ask` | Also ask for changes, and **you approve each one** at your keyboard. |
| `full` | Run any task except the ones listed below. Tasks that change or delete still ask you unless you started `link listen yes`. |

Never allowed remotely, at any level: `link`, `update`, `upgrade`, `autorun`, `kit`, `audit`, `policy`, `gui`, `window`, `desktop`, `plugin`, `allow`, `deny`, `pack`, `connect`, `install`. These can only be used at the computer itself.

Everything another computer runs is written to your audit log (`audit show`) as `computer:<name>`.

## Across the internet

Two ways, both optional:

1. **Direct.** Forward port 8767 on your router to the listening computer (or use a VPN such as WireGuard/Tailscale), then `link pair <public address>:8767` once and later `link ping`.
2. **Relay.** Someone runs `link relay serve` on any machine both can reach (a cheap server, a Raspberry Pi with a forwarded port). The relay only passes encrypted bytes. The waiting computer runs `link listen relay HOST:8768`; it prints a one-time pairing code like `JG-ABCDE-FGHIJ`. The other person runs `link pair relay HOST:8768 JG-ABCDE-FGHIJ`. Afterwards each pair meets in a private room derived from their shared secret.

The relay learns that two connections exist, their IP addresses and how much data moves. It cannot read or change anything, and it cannot pair strangers: pairing still needs both people to compare the 6-digit number.

## How it is protected

- Pairing: a Diffie-Hellman exchange (RFC 3526 2048-bit group, commit-then-reveal) plus a short number both people compare. An attacker in the middle makes the numbers differ.
- Each later connection: a fresh key exchange authenticated with the pairing secret, then every message is encrypted (SHAKE-256 stream) and authenticated (HMAC-SHA256) with strict message order, so tampering, replay and reordering are refused.
- Limits: 5 failed attempts from one address pause that address for 5 minutes; messages up to 2 MB; files up to 100 MB with a SHA-256 check; only one remote task runs at a time.
- Pairing needs a person at a terminal. An AI, a script or the phone page can never pair or change levels.
- An administrator can turn the whole feature off with `"block_link": true` in the policy file (`ADMIN.md`).

## Honest limits

- This protocol is built only from Python's standard library and **has not been reviewed by an independent security expert**. It is designed carefully and tested (`tests/test_link.py`), but treat it as you would any new software. For high-value machines, prefer a VPN plus `chat`/`safe` levels, or SSH.
- `full` means a paired computer can do almost anything JeeG can do on your machine. Give it only to computers and people you trust, and keep `ask` as the default for anything you are unsure about.
- The connection is as private as the pairing was: if the 6-digit numbers were not compared honestly, there is no protection.
- Tested here on Linux, with two programs on one computer and a local relay. Windows and macOS use the same code but were not tried on real separate machines.

## IoT: smart devices and scenes

`iot list` shows everything you saved in one place: smart plugs (`device`), MQTT brokers (`mqtt`), computers over SSH (`computer`), wake-on-LAN targets and paired JeeGs.

Scenes run several steps in order:

    iot scene add night = device off lamp ; mqtt publish home lights/hall off ; pause 5 ; link run kitchen pc lock screen
    iot scene run night

Steps may be `device`, `mqtt`, `serial`, `computer`/`ssh`, `wake`, `pause <seconds>` or `link send|run|ping`. Anything that asks for a yes still asks, so a scene run by an AI cannot silently do risky things. Tested only against a simulated Shelly smart plug.
