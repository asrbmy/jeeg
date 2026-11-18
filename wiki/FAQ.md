# FAQ

**Is it private?** Yes. Everything runs on your computer. Only a listed set of tasks use the internet (`privacy`). Nothing is sent to any AI service unless *you* connect one.

**Is there an AI inside?** No. Matching is by words and scripts. That is deliberate: it is fast, predictable and free.

**Does it work offline?** Yes, except online lookups, which say so.

**Why does it ask me to choose?** Two tasks fit equally and a wrong guess might do the wrong thing.

**Why did it not understand my sentence?** It matches words to scripts. Use the task's words, check `explain`, or add an alias.

**Can I use it by voice?** Not in this version.

**Does it need an account or send telemetry?** No account, no telemetry.

**Can I change what a task does?** Yes, scripts are plain files in `scripts/`. `reindex` after changing a header.

**Can I share tasks?** `share plugin <name>`; only run scripts from people you trust.

**How do I update?** `update` / `update now`. Your data folder is separate and kept.

**Where is my data?** `~/.jeeg`. Copy it to back up or use `export data`.

**What platforms are tested?** Linux thoroughly. Windows and macOS-specific parts were written carefully but not run on real machines; the GitHub workflow runs tests on all three if you host the project.

**Can an AI use my computer through JeeG?** Only if you start `connect ai` (or install the MCP entry), only for the modes you choose, and anything that changes things asks you. An AI can never link apps, add servers or change policy.

**Can an AI browse the web through JeeG?** Only with `connect ai ... allow browser`, with limits ([Real Web Browser](Real-Web-Browser)).

**Does JeeG send WhatsApp messages for me?** No: it opens the chat with your text typed; you press Send.

**What if I turn off a whole area?** `pack off <category>`.

**How do I add a program to JeeG without Python code?** A `.sh`, `.bat`, `.ps1` or `.js` file with the same header works.

**Why is my task not found?** Name it in words, run `reindex`, then `selftest`.

**How many tasks are there?** 548 at version 2.20.0. See the [Task Catalog](Task-Catalog).
