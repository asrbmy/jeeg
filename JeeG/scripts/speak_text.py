# keywords: speak, say, read aloud, tts, text to speech, talk, voice, read out
# desc: Read text aloud (speak hello there)
# category: clipboard
# usage: speak <text>
import os, shutil, subprocess
from _lib import WIN, MAC, args_text, fail
from _sys import ps
t = args_text()
if not t:
    fail("Say what to speak: speak <text>")
t = t[:2000]
if WIN:
    ps("Add-Type -AssemblyName System.Speech;(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak($env:TR_TEXT)", timeout=120, text=t)
elif MAC:
    subprocess.run(["say", t])
else:
    for cmd in (["spd-say", "-w", t], ["espeak-ng", t], ["espeak", t]):
        if shutil.which(cmd[0]):
            subprocess.run(cmd); break
    else:
        fail("Install espeak-ng or speech-dispatcher for speech on Linux.")
