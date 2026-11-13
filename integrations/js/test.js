// node integrations/js/test.js  (needs python and this repository; used by tests/test_connect_js.py)
const assert = require("node:assert");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { run, find, tasks, info, Http, JeegError } = require("./index.js");
const root = path.resolve(__dirname, "..", "..");
const py = process.env.PYTHON || "python3";
const opts = { command: py, args: [path.join(root, "jeeg.py")] };
(async () => {
  let n = 0; const ok = (c, m) => { if (!c) { console.log("FAIL:", m); process.exitCode = 1; } else n++; };
  const r = await run("gst 100 18", opts); ok(r.ok && r.task === "gst_amount" && r.output.includes("118"), "run");
  const f = await find("open youtube", 2, opts); ok(f[0].name === "open_youtube", "find");
  ok((await tasks("money", opts)).length > 5, "tasks");
  ok((await info("gst_amount", opts)).category === "money", "info");
  const bad = await run("shutdown in 60 minutes", opts); ok(bad.needs_confirmation === true, "confirmation task is refused");
  await run("x".repeat(3000), opts).then(() => ok(false, "long request"), (e) => ok(e instanceof JeegError, "long request rejected"));
  await run("gst 1 1", { command: "definitely-not-installed-jeeg" }).then(() => ok(false, "missing"), (e) => ok(/not installed/.test(e.message), "missing jeeg explained"));
  try { new Http("t", "http://evil.example:8766"); ok(false, "non-local base"); } catch (e) { ok(e instanceof JeegError, "Http refuses a non-local address"); }
  // the HTTP client against a real --serve-api
  const home = require("node:fs").mkdtempSync(path.join(require("node:os").tmpdir(), "jeeg-js-"));
  const env = { ...process.env, JEEG_HOME: home, JEEG_API_TOKEN: "t".repeat(40) };
  const port = await new Promise((res) => { const s = require("node:net").createServer().listen(0, "127.0.0.1", () => { const p = s.address().port; s.close(() => res(p)); }); });   // a free port, so parallel runs never collide
  const srv = spawn(py, [path.join(root, "jeeg.py"), "--serve-api", String(port)], { env, stdio: "ignore" });
  const base = `http://127.0.0.1:${port}`;
  for (let i = 0; i < 100; i++) {                                    // wait until it answers, however slow the machine is
    try { await new Http("t".repeat(40), base).health(); break; } catch (e) { await new Promise((r) => setTimeout(r, 150)); }
  }
  try {
    const api = new Http("t".repeat(40), base);
    ok((await api.health()).jeeg, "http health");
    ok((await api.run("gst 100 18")).output.includes("118"), "http run");
    ok((await api.find("disk space", 1))[0].name === "disk_space", "http find");
    await new Http("wrong".repeat(10), base).run("gst 1 1").then(() => ok(false, "wrong token"), (e) => ok(e instanceof JeegError, "wrong token refused"));
  } finally { srv.kill(); }
  console.log(`js client: ${n} passed${process.exitCode ? ", some FAILED" : ""}`);
})();
