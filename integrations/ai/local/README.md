# JeeG for Ollama, LM Studio and other local models

`jeeg_chat.py` is a small chat program (Python standard library only) that lets a model running on your own computer use
JeeG for exact work: calculations, conversions, text and dates.

1. Start your model server (Ollama or LM Studio). Use a model that supports tool calling.
2. Run:

       python jeeg_chat.py --ollama --model llama3.1
       python jeeg_chat.py --lmstudio --model <model name>
       python jeeg_chat.py --ollama --model llama3.1 --ask "what is 18% GST on 2500?"

3. Widen or narrow what the model may do with `--only` (kinds of tasks, default `text,money,utility,time`).

How it stays safe: the script starts its own JeeG API on a free local port with a one-time token the model never sees;
only the kinds of task you list are allowed; tasks that ask first are refused; tool replies are marked as data.
Nothing leaves your computer when the model server is local. With a remote model the script prints a notice first.

Not every small model calls tools well; if it ignores them, try a model that lists tool support.

To let the model read your Obsidian notes: run `vault set` once in JeeG, then add `notes` to `--only` (for example `--only text,money,utility,time,notes`). Notes are read-only there; adding text always asks first and is refused in this script.
