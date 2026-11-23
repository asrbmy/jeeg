# Bridges, channels and protocols

This page covers three things added in 2.21.0 next to JeeG link (`LINK.md`): AI channels, hand-off, and the bridge. Everything is local. JeeG never contacts an AI service and never stores an AI account.

## How two different AIs talk to each other

Each AI talks to **its own** JeeG the way it already does (AI mode: `connect ai`, or the local API). JeeG then carries the words between computers over the encrypted link:

1. Pair the two JeeG computers (`LINK.md`). Level `chat` is enough for channels and hand-off.
2. On **both** computers, share a channel with the other: `channel share lab with <other computer>`.
3. Either AI posts: `channel post lab as claude: the tests pass` and reads: `channel read lab`, `channel wait lab 30`.
4. `channel pull lab from <computer>` catches up on anything missed while a computer was off. `channel search <word>` looks through all channels and `channel export lab` saves one to a text file.

`as claude:` is only a label so you can see which AI wrote it (`claude@kitchen-pc`).

**Hand-off** is the same idea for jobs. On both sides run `handoff allow <other>`. Then:

    handoff ask kitchen-pc summarise report.pdf       (returns a job id)
    handoff inbox                                     (on kitchen-pc: what is waiting)
    handoff reply <id> three pages about tax          (on kitchen-pc)
    handoff result <id> 60                            (waits up to 60 s for the answer)

Nothing is executed because a message arrived. A channel message or a job is **text for a person or an AI to read**; JeeG prints it with a reminder that it is information, not instructions. An AI that reads channels should treat them like any untrusted web page (another AI could write anything there, including instructions meant to trick it). Use `link run` with a level when you really want another computer to run a task.

Limits: 4000 characters per message (2000 when typed on a command line), 1000 messages per channel, only channels you shared with that exact computer, blocked computers cannot post.

## Bridge: when this happens, do that

    bridge add door when mqtt home door/front if contains open then ha on light.hall ; channel post lab front door opened
    bridge add pad  when udp 4210 then device on lamp
    bridge add hook when webhook 8790 then channel post hooks got {msg}
    bridge list | bridge show <name> | bridge test <name> <message> | bridge remove <name>
    bridge run              (leave the window open; Ctrl+C stops)

Sources: `every <n> seconds|minutes|hours` (a timer, 10 seconds to 7 days; for example `bridge add poll when every 5 minutes then log reading hall-temp 21`), `mqtt <broker> <topic>`, `webhook <port>` (gets a secret address like `/hook/<secret>`), `udp <port>`, `tcp <port>`, `serial <port> [baud]` (needs pyserial), `ws <address>`, `channel <name>`, `chat` (messages from paired computers). Add `if contains <word>` to react only to matching text.

Steps are the same short list scenes use: device, mqtt, serial, computer/ssh, wake, ha, zigbee, modbus, tcp, udp, ws, rest, webhook, channel, handoff, bluetooth, pause, `link send/run/ping`. In a step, `{msg}`, `{topic}` and `{from}` are replaced by what arrived, **only letters, numbers and `. : / @ # + -`** (everything else is removed, so an incoming message cannot add commands). A step that needs a yes (modbus write, rest post) fails with "asks first" instead of running unattended.

Safety rules: terminal only (an AI or another computer cannot create or start rules); a rule fires at most once per 2 seconds and 120 times an hour (this stops loops such as a rule whose action triggers itself); each run appears in `audit show` as `rule:<name>`. A webhook or UDP/TCP source listens on your network, so put it on a network you trust; the webhook needs its secret address.

## New protocol tasks

| Say | What it does |
|---|---|
| `ha add home http://homeassistant.local:8123`, `ha states light`, `ha on light.kitchen`, `ha call light.turn_on light.kitchen {"brightness":120}` | Home Assistant over its REST API (token asked for, kept private) |
| `zigbee devices home`, `zigbee on home hall-lamp`, `zigbee set home hall-lamp brightness 120` | Zigbee devices through zigbee2mqtt on your saved MQTT broker. Z-Wave and others: use `mqtt` with their topics |
| `modbus read 192.168.1.60 holding 0 2`, `modbus write ... coil 5 on` (asks first) | Modbus TCP PLCs and meters (own network only) |
| `tcp send 192.168.1.40:9000 hello`, `udp send ...`, `udp listen 4210 10`, `ws send ws://192.168.1.5:81 hi`, `ws read <address> 10` | Plain sockets and WebSocket |
| `rest add shop https://api.example.com bearer`, `rest get shop /orders`, `rest post shop /items {...}` (asks first) | Any web API with a saved key; redirects are never followed |
| `bluetooth list`, `bluetooth connect headphones` | Paired devices via the system's own tools |

Email, Slack, Discord and chat messages already work through `webhook`, `email to` and `app do`; use them as bridge steps where allowed.

## Playbooks, sensor logging and notifications

- `playbook add morning = show reminders ; what is due` then `playbook run morning`: a saved, reviewed job. A step that needs a yes stops the playbook. An AI or another computer may run a playbook but can never add, change or remove one, and a playbook cannot contain admin, link, update, bridge or delete-style steps.
- Bridge steps `log reading temperature {msg} c` (see `show readings temperature`), `notify <text>` and `playbook run <name>` turn a message into a logged sensor value, a pop-up or a saved job.
- `setup home` looks for Home Assistant, MQTT, Shelly and Tasmota on your network (it saves nothing); `setup check` reports unreachable devices, broken bridge rules and computers with full access.
- `receipt`, `board` and `backup share <computer>` are everyday helpers: receipts with photos and a yearly CSV, a shared to-do board over a channel, and a data backup sent to a paired computer.

## Honest limits

- All of this was tested here only against **simulated** devices and servers on one Linux computer (fake Home Assistant, Modbus, MQTT/zigbee2mqtt, TCP, UDP, WebSocket and REST servers). Real hardware may behave differently.
- **Bluetooth** could not be tested at all (no adapter here); only the argument checks and the "tool missing" message were. Windows and macOS paths use system tools I could not try.
- Real Zigbee/Z-Wave radios need their own gateway software (zigbee2mqtt, Z-Wave JS); JeeG talks to that gateway over MQTT.
- Two AIs only "talk" if each one is connected to its own JeeG and reads and writes the channel; JeeG does not run or call any AI itself.
- The link protocol remains homegrown and unreviewed (see `LINK.md`).
