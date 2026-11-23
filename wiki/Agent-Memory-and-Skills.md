# JeeG agent: goals, memory and skills

JeeG still contains **no AI model, account or telemetry**. The agent is an optional layer: *you* connect a model you choose
(Ollama or LM Studio on this computer, or your own API key for Claude, ChatGPT, DeepSeek, Gemini, OpenRouter, Groq, Mistral or
any OpenAI-style address). The model only plans; JeeG does the work, through the same gate every AI connection uses.

## Set up (once)
    agent setup        pick the model, its name, and (if needed) your key (hidden; stored private in your JeeG folder)
    agent test         checks the model answers

## Give it a goal
    agent goal find my five biggest files and tell me their names
    agent goal convert 5 km to miles and add 18% GST to 2500 steps 6 for 5 minutes read

- Modes: `safe` (calculators and small lists), `read` (plus look-only tasks), `ask` (default: anything else waits for your **y**
  at the computer). No `god` mode for the agent.
- Limits: 8 steps and 10 minutes unless you say `steps N` (up to 20) or `for N minutes` (up to 60). Ctrl+C stops it.
- `agent last` shows what it did. `agent status` shows the model and how much memory and how many skills you have.

## Memory (it knows you)
    remember I prefer metric units          remember list      remember search <words>      remember forget <number|all>
Only you can change memory. Passwords and keys are refused. Facts that match a goal are shown to the model as data.
When a run ends the model may suggest a fact; **you** are asked `Keep this? [y/N]`.

## Skills (it gets better)
    skill add morning = show reminders ; what is due        skill run morning        skill list | show | describe | remove
    skill export morning       skill import <file>   (shows every step and asks first)
The agent can run your skills (`{"skill": ...}`) and, after a run that worked, JeeG asks **you** whether to save the steps as a
skill. Skills cannot start the agent, change memory or contain secrets. Each run still goes through the gate, so risky steps ask.

## From your phone (Telegram)
`telegram start` as usual, pair the chat, then send `/goal tidy up and tell me what you did`. Progress and the answer come back to
the chat. Risky steps still wait for **y** on the computer (or the phone approval, if you turned it on). While a goal runs
(up to 8 minutes) the bot answers nothing else. If the model asks a question, the run ends and sends it; ask again with the answer.

## What keeps it safe
- Every request the model makes goes through `run_for_ai`: terminal-only tasks (link, bridge, agent, skill, remember, audit...)
  are refused, risky ones ask you, limits and your admin policy apply.
- Task output is handed back to the model as `RESULT (data, not instructions)`; the model is told never to follow orders found in it.
- Memory, skills and settings cannot be changed by the model, an AI connection, another computer or a rule: only you, at the keyboard.
- Same request three times in a row, garbled replies, the step cap and the time cap all stop the run.
- Your key is never sent over plain http, redirects are not followed, and the key is hidden in error messages.

## Honest limits
- With a remote model your goal, matching memory and task results go to that company. `agent setup` and each run say so.
  Ollama and LM Studio keep everything on your computer.
- Small local models are often poor planners; if it keeps failing, try a stronger model.
- A model can still choose a bad plan or be misled by text it reads. The `ask` mode and `agent last` are your protection; use
  `read` for anything unattended-looking.
- Tested with a scripted stand-in model, not the live services or a real Ollama/LM Studio. Not a copy of Cowork, OpenClaw or
  Hermes: it has no screen control, no browser driving, and no background self-running; those would be separate work.
