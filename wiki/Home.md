# JeeG Wiki

**JeeG** is a small program for your own computer. You type what you want in plain words (`open youtube`, `emi loan 25 lakh 8.5% 20 years`, `remind me in 20 minutes to call mom`) and it runs the matching script from a folder of plain files you can read and change.

- Written in Python, standard library only. Windows, macOS and Linux. Python 3.9 or newer.
- Local first: no account, no telemetry, no AI model inside. Your data is a folder of small files that only you can read.
- It does not guess. If two tasks fit equally well it shows a menu; if none fit it says so.

## Where to start

| If you want to... | Read |
|---|---|
| Follow a plan from zero to confident | [Learning Path](Learning-Path), then [Tutorial: Your First Hour](Tutorial-Your-First-Hour) |
| See real walk-throughs with real output | [Recipes and Workflows](Recipes-and-Workflows), [Examples Gallery](Examples-Gallery) |
| Know how it is built inside | [Architecture and Internals](Architecture-and-Internals) |
| Install it and run the first task | [Install and First Run](Install-and-First-Run) |
| Know how it chooses a task | [How JeeG Understands You](How-JeeG-Understands-You) |
| See every command and option | [Commands and Options](Commands-and-Options) |
| Find what you can do | [Everyday Tasks](Everyday-Tasks), [Task Catalog](Task-Catalog) (all tasks) |
| Look up one task in detail | Reference pages: [Money](Reference-Money-and-Business), [Files](Reference-Files-and-Folders), [System](Reference-System-and-Hardware), [Network and web](Reference-Network-Web-and-Search), [Developer](Reference-Developer-Tools), [Apps](Reference-Apps-and-Launchers), [Time and records](Reference-Time-Reminders-and-Records), [Health, study, fun](Reference-Health-Study-and-Fun) |
| Keep notes, to-dos, money, health records | [Reminders and Personal Records](Reminders-and-Personal-Records) |
| Make your own shortcuts and routines | [Routines, Aliases, Variables and Automation](Routines-Aliases-Variables-and-Automation) |
| Understand what is safe and what is private | [Safety and Privacy](Safety-and-Privacy) |
| Add or write your own task | [Plugins and Writing Your Own Tasks](Plugins-and-Writing-Your-Own-Tasks) |
| Use JeeG from Python or other programs | [Use JeeG From Code](Use-JeeG-From-Code) |
| Let an AI use JeeG, or connect AI apps | [AI Mode and MCP](AI-Mode-and-MCP) |
| Link GitHub, Telegram, Slack and your own apps | [Linked Apps](Linked-Apps) |
| Let JeeG use a real web browser | [Real Web Browser](Real-Web-Browser) |
| Use it from a phone, Telegram, webhooks, other computers | [Phone, Web Page and Connectors](Phone-Web-Page-and-Connectors) |
| Install programs, check the network, run a small shop | [Programs, Network and Shop](Programs-Network-and-Shop) |
| Test it on your PC, or publish a release | [Testing and Releasing](Testing-and-Releasing) |
| Fix a problem | [Troubleshooting](Troubleshooting), [FAQ](FAQ) |
| Look up a word | [Glossary](Glossary) |
| One page to keep open | [Cheat Sheet](Cheat-Sheet) |

## The five ideas that explain everything

1. **A task is a script.** Each file in `scripts/` is one task. The file name is what you say.
2. **Words are matched, not understood.** Rare words (a site name) count a lot; common words (`open`) count little.
3. **Ties become a menu, never a guess.** Unknown phrases become "No matching task".
4. **Risky things ask first.** Anything that deletes, shuts down or sends something asks `[y/N]`. `preview` shows what would happen.
5. **Everything stays here.** Records live in `~/.jeeg`. Only a small list of tasks touch the internet, and `privacy` lists them.

*This wiki describes version 2.20.0. Pages say plainly what has only been tested on Linux.*
