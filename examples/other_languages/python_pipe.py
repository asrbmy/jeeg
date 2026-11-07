"""Use JeeG from ANY program without a network port: start `jeeg --stdio` and talk in JSON lines.
This example is Python, but the same idea works in Go, Java, C#, Ruby, PHP, ... (anything that can start a process)."""
import json, subprocess

p = subprocess.Popen(["jeeg", "--stdio"],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

def ask(**req):
    p.stdin.write(json.dumps(req) + "\n")
    p.stdin.flush()
    return json.loads(p.stdout.readline())

print(ask(id=1, query="gst 2500 18")["result"]["output"])
print(ask(id=2, op="find", query="open youtube", limit=1)["result"])
p.stdin.close()
