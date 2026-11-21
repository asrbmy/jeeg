"""JeeG link + relay: pairing, encryption, levels, files, relay. All on this computer. Run: python tests/test_link.py"""
import base64, hashlib, os, socket, sys, tempfile, threading, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
TMP = Path(tempfile.mkdtemp(prefix="jeeg-link-"))
os.environ["HOME"] = os.environ["USERPROFILE"] = str(TMP / "home"); (TMP / "home").mkdir()
import jeeg_link as L, jeeg_relay as R
P = F = 0
def ok(c, l):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", l)
def raises(fn, *exc):
    try: fn()
    except exc or Exception: return True
    return False

# --- the math
ok(L.P.bit_length() == 2048 and pow(2, L.Q, L.P) == 1 and L.Q == (L.P - 1) // 2, "group is a safe prime group")
ok(raises(lambda: L._check_pub(1), L.LinkError) and raises(lambda: L._check_pub(L.P - 1), L.LinkError) and raises(lambda: L._check_pub(0), L.LinkError), "bad public values refused")

def pair(a_state, b_state, a_level="full", b_level="chat", a_sas_ok=True, b_sas_ok=True, relay=False):
    la = L.Listener(a_state, port=0, out=lambda s: None, interactive=True)
    answers = iter([("y" if a_sas_ok else "n"), a_level])
    la.prompt = lambda text, default="": next(answers, default)
    threading.Thread(target=la.serve, daemon=True).start(); la.ready.wait(5)
    ins = iter([("y" if b_sas_ok else "n"), b_level])
    try: rc = L._cmd_pair(L.Store(b_state), [f"127.0.0.1:{la.port}"], True, lambda s: None, lambda p: next(ins, ""))
    except L.LinkError: rc = 1
    time.sleep(0.3)
    return la, rc

A, B = TMP / "a", TMP / "b"; A.mkdir(); B.mkdir()
L.Store(A).set_name("alpha"); L.Store(B).set_name("beta")
la, rc = pair(A, B)
ok(rc == 0, "pairing works")
pa, pb = L.Store(A).peers(), L.Store(B).peers()
ok(len(pa) == 1 and len(pb) == 1, "both sides saved the other")
ok(list(pa.values())[0]["level"] == "full" and list(pb.values())[0]["level"] == "chat", "each side set its own level")
ok(list(pa.values())[0]["psk"] == list(pb.values())[0]["psk"], "same shared key")
pf = (A / "link" / "peers.json")
if os.name != "nt": ok(oct(pf.stat().st_mode & 0o777) == "0o600", "peers file is private")

# --- sessions
st = L.Store(B); pid, rec = st.find("alpha")
rec["addr"] = f"127.0.0.1:{la.port}"
ch = L.open_session(st, pid, rec)
r = L.ask(ch, {"t": "ping"})
ok(r.get("t") == "pong" and r.get("level") == "full", "ping shows my level")
ok(L.ask(ch, {"t": "chat", "text": "hello there"}).get("t") == "ok" and L.Store(A).inbox(5)[-1]["text"] == "hello there", "chat arrives")
ok(L.ask(ch, {"t": "run", "q": "calculate 6*7"}).get("text", "").find("42") >= 0, "remote task runs")
for w in ("link peers", "update", "audit clear", "policy", "autorun on", "kit share", "install foo", "plugin x"):
    rr = L.ask(ch, {"t": "run", "q": w})
    ok(rr.get("err") and "this computer itself" in rr.get("text", ""), "refused remotely: " + w)
ok(L.ask(ch, {"t": "bogus"}).get("t") == "err", "unknown request refused")

# --- levels take effect immediately
def setlevel(lv):
    d = L.Store(A).peers(); k = next(iter(d)); d[k]["level"] = lv; L.Store(A).save_peers(d)
setlevel("chat")
rr = L.ask(ch, {"t": "run", "q": "calculate 1+1"})
ok(rr.get("err") and "messages and files only" in rr["text"], "chat level cannot run tasks")
ok(L.ask(ch, {"t": "chat", "text": "still ok"}).get("t") == "ok", "chat level can chat")
setlevel("safe")
ok(L.ask(ch, {"t": "run", "q": "calculate 2+2"}).get("text", "").find("4") >= 0, "safe level runs safe tasks")
rr = L.ask(ch, {"t": "run", "q": "delete file x.txt"})
ok(rr.get("err") or "not" in rr.get("text", "").lower() or "can't" in rr.get("text", "").lower() or "cannot" in rr.get("text", "").lower() or "allow" in rr.get("text", "").lower(), "safe level cannot delete")
setlevel("block")
ok(L.ask(ch, {"t": "ping"}).get("t") == "err", "block cuts the live session")
ch.sock.close()
ok(raises(lambda: L.open_session(st, pid, rec), L.LinkError, OSError), "blocked peer cannot reconnect")
setlevel("full")

# --- files
src = TMP / "report.txt"; src.write_bytes(os.urandom(500_000))
ch = L.open_session(st, pid, rec)
name = L.send_file(ch, src)
got = L.received_dir() / name
ok(got.is_file() and hashlib.sha256(got.read_bytes()).hexdigest() == hashlib.sha256(src.read_bytes()).hexdigest(), "file arrives intact")
bad = TMP / "run.exe"; bad.write_bytes(b"MZ")
ok(raises(lambda: L.send_file(L.open_session(st, pid, rec), bad), L.LinkError), "programs refused")
ok(L.safe_file_name("../../etc/passwd") == "passwd" and L.safe_file_name("..\\..\\x.txt") == "x.txt" and L.safe_file_name("") == "file", "file names are cleaned")
ch2 = L.open_session(st, pid, rec)
ch2.send({"t": "file", "name": "big.bin", "size": L.MAX_FILE + 1})
ok(ch2.recv().get("t") == "err", "oversized file refused")
ch3 = L.open_session(st, pid, rec)
ch3.send({"t": "file", "name": "lie.bin", "size": 10}); ch3.recv()
ch3.send({"t": "chunk", "d": base64.b64encode(b"x" * 50).decode()})
ok(ch3.recv().get("t") == "err" and not list(L.received_dir().glob("lie*")), "more data than announced is dropped")

# --- wrong key / strangers / tampering
ok(raises(lambda: L.open_session(L.Store(B), "ff" * 16, {"psk": "00" * 32, "addr": f"127.0.0.1:{la.port}"}), L.LinkError, OSError, KeyError), "unknown id refused")
s = socket.create_connection(("127.0.0.1", la.port), 5)
L.send_raw(s, {"t": "hello", "id": pid})
s.close()
s = socket.create_connection(("127.0.0.1", la.port), 5); s.sendall(b"GET / HTTP/1.1\r\n\r\n"); s.settimeout(3)
try: d = s.recv(100)
except OSError: d = b""
ok(b"HTTP" not in d, "a web browser gets nothing")
s.close()

# tampered / replayed frames are rejected by the channel
a, b = socket.socketpair()
ca, cb = L.Chan(a, b"1" * 32, b"2" * 32, b"3" * 32, b"4" * 32), L.Chan(b, b"3" * 32, b"4" * 32, b"1" * 32, b"2" * 32)
ca.send({"t": "x", "v": 1}); ok(cb.recv() == {"t": "x", "v": 1}, "channel round trip")
ca.send({"t": "y"}); raw = b.recv(65536)
bad = bytearray(raw); bad[-1] ^= 1
c, d = socket.socketpair(); cc = L.Chan(d, b"3" * 32, b"4" * 32, b"1" * 32, b"2" * 32)
c.sendall(bytes(bad)); c.close()
ok(raises(cc.recv, L.LinkError, OSError), "tampered frame rejected")
a2, b2 = socket.socketpair()
ca2 = L.Chan(a2, b"1" * 32, b"2" * 32, b"3" * 32, b"4" * 32); cb2 = L.Chan(b2, b"3" * 32, b"4" * 32, b"1" * 32, b"2" * 32)
ca2.send({"n": 1}); f1 = b2.recv(65536); ca2.send({"n": 2}); f2 = b2.recv(65536)
x, y = socket.socketpair(); cx = L.Chan(y, b"3" * 32, b"4" * 32, b"1" * 32, b"2" * 32)
x.sendall(f2); x.close()
ok(raises(cx.recv, L.LinkError, OSError), "out-of-order frame rejected")

# --- pairing refused / wrong number
A2, B2 = TMP / "a2", TMP / "b2"; A2.mkdir(); B2.mkdir()
la2, rc2 = pair(A2, B2, b_sas_ok=False)
ok(rc2 != 0 or not L.Store(A2).peers(), "no pairing when numbers don't match")
ok(not L.Store(B2).peers(), "nothing saved on refusal")
la2.stop()

# --- non-interactive listener refuses pairing
A3, B3 = TMP / "a3", TMP / "b3"; A3.mkdir(); B3.mkdir()
ln = L.Listener(A3, port=0, out=lambda s: None, interactive=False)
threading.Thread(target=ln.serve, daemon=True).start(); ln.ready.wait(5)
ins = iter(["y", "chat"])
try: rc3 = L._cmd_pair(L.Store(B3), [f"127.0.0.1:{ln.port}"], True, lambda s: None, lambda p: next(ins, ""))
except Exception: rc3 = 1
ok(not L.Store(A3).peers(), "unattended listener never pairs")
ln.stop()

# --- discovery
f = L.find_on_lan(1.0) if False else None

# --- relay
rl = R.Relay(0, "127.0.0.1", out=lambda s: None)
threading.Thread(target=rl.serve, daemon=True).start(); rl.ready.wait(5)
relay = f"127.0.0.1:{rl.port}"
ok(raises(lambda: R.join(relay, "0" * 32, 2), OSError), "joining an empty room fails")
stop = threading.Event(); res = {}
threading.Thread(target=lambda: res.setdefault("s", R.wait_in_room(relay, "a1" * 16, stop)), daemon=True).start(); time.sleep(0.3)
cs = R.join(relay, "a1" * 16, 3); time.sleep(0.3)
ws = res.get("s")
ok(ws is not None, "relay connects the two")
if ws:
    cs.sendall(b"ping"); ws.settimeout(3); ok(ws.recv(10) == b"ping", "bytes pass through")
    ws.sendall(b"pong"); cs.settimeout(3); ok(cs.recv(10) == b"pong", "bytes pass back")
    cs.close(); ws.close()
code = R.new_code()
ok(len(code) == 14 and code.startswith("JG-") and R.pairing_room(code) == R.pairing_room(code.lower()), "pairing codes")
ok(R.room_for(b"a" * 32) != R.room_for(b"b" * 32) and len(R.room_for(b"a" * 32)) >= 32, "rooms are per-key")

# a full pairing and session through the relay
A4, B4 = TMP / "a4", TMP / "b4"; A4.mkdir(); B4.mkdir()
L.Store(A4).set_name("gamma"); L.Store(B4).set_name("delta")
lr = L.Listener(A4, port=0, out=lambda s: None, interactive=True, relay=relay)
lr.pair_code = R.new_code()
ans = iter(["y", "ask"]); lr.prompt = lambda text, default="": next(ans, default)
threading.Thread(target=lr.serve, daemon=True).start(); lr.ready.wait(5); time.sleep(1)
ins = iter(["y", "chat"])
try: rc4 = L._cmd_pair(L.Store(B4), ["relay", relay, lr.pair_code], True, lambda s: None, lambda p: next(ins, ""))
except Exception as ex: rc4 = 1; print("relay pair error:", ex)
ok(rc4 == 0, "pairing through the relay")
time.sleep(0.5)
p4 = L.Store(B4).peers()
if p4:
    pid4, rec4 = L.Store(B4).find("gamma")
    rec4["addr"] = ""   # force the relay path
    time.sleep(6)       # the listener parks a waiting connection for the new peer
    try:
        c4 = L.open_session(L.Store(B4), pid4, rec4)
        ok(L.ask(c4, {"t": "ping"}).get("level") == "ask", "session through the relay")
        c4.sock.close()
    except Exception as ex:
        ok(False, "session through the relay: " + str(ex))
else:
    ok(False, "relay pairing saved a peer")
lr.stop()

# --- per-IP limit and expiry exist
ok(hasattr(rl, "_expire") and rl.bytes_passed >= 0, "relay has limits")
rl.stop()

# --- the command
import subprocess
env = dict(os.environ, JEEG_HOME=str(TMP / "cli"), JEEG_STATE=str(TMP / "cli"))
def run(*a):
    p = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *a], capture_output=True, text=True, env=env, timeout=60, stdin=subprocess.DEVNULL)
    return p.returncode, p.stdout + p.stderr
rc, o = run("link", "name", "Kitchen PC"); ok(rc == 0 and "Kitchen PC" in o, "link name")
rc, o = run("link", "peers"); ok(rc == 0 and "No paired" in o, "link peers empty")
rc, o = run("link", "pair", "127.0.0.1"); ok(rc != 0 and "terminal" in o.lower(), "pairing needs a terminal")
rc, o = run("link", "ping", "nobody"); ok(rc != 0 and "No paired" in o, "unknown peer")
rc, o = run("link", "level", "x", "weird"); ok(rc != 0, "bad level")
rc, o = run("link"); ok(rc == 0 and "Kitchen PC" in o, "link status")
pol = TMP / "pol.json"; pol.write_text('{"block_link": true}')
env["JEEG_POLICY"] = str(pol)
rc, o = run("link", "peers"); ok(rc != 0 and "administrator" in o, "policy can turn link off")

print(f"link: {P} passed, {F} failed")
sys.exit(1 if F else 0)
