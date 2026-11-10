"use strict";
/**
 * JeeG client for Node 18+ (no dependencies).
 *   const { run, find, tasks, Http } = require("jeeg-client");
 *   const r = await run("gst 2500 18");           // starts `jeeg --stdio` for you
 *   console.log(r.output);
 * Or talk to a running `jeeg --serve-api`:   const api = new Http(token); await api.run("disk space");
 */
const { spawn } = require("node:child_process");

class JeegError extends Error {}

function once(request, { command = "jeeg", args = [], timeoutMs = 120000 } = {}) {
  return new Promise((resolve, reject) => {
    let child;
    try { child = spawn(command, [...args, "--stdio"], { stdio: ["pipe", "pipe", "ignore"], windowsHide: true }); }
    catch (e) { return reject(new JeegError(`Could not start jeeg: ${e.message}`)); }
    let out = "";
    const timer = setTimeout(() => { child.kill(); reject(new JeegError("jeeg took too long")); }, timeoutMs);
    child.on("error", (e) => { clearTimeout(timer); reject(new JeegError(e.code === "ENOENT" ? "jeeg is not installed or not on PATH (pip install jeeg)" : e.message)); });
    child.stdout.on("data", (d) => { out += d; });
    child.on("close", () => {
      clearTimeout(timer);
      try {
        const line = out.split("\n").find((l) => l.trim().startsWith("{"));
        const msg = JSON.parse(line);
        msg.ok ? resolve(msg.result) : reject(new JeegError(msg.error || "jeeg refused the request"));
      } catch { reject(new JeegError("jeeg gave no valid answer")); }
    });
    child.stdin.end(JSON.stringify(request) + "\n");
  });
}

/** Run a request in plain words. Resolves to {task, output, exit, ok, needs_confirmation, ambiguous, candidates}. */
const run = (query, opts = {}) => once({ op: "run", query: String(query), yes: !!opts.yes, timeout: opts.timeout }, opts);
/** Which tasks match a phrase (nothing is run). */
const find = (query, limit = 5, opts = {}) => once({ op: "find", query: String(query), limit }, opts);
const tasks = (category, opts = {}) => once({ op: "tasks", category }, opts);
const info = (name, opts = {}) => once({ op: "info", name }, opts);

/** Client for `jeeg --serve-api` (default http://127.0.0.1:8766). Get the token with `jeeg --api-token`. */
class Http {
  constructor(token, base = "http://127.0.0.1:8766") {
    const u = new URL(base);
    if (!["127.0.0.1", "localhost", "[::1]"].includes(u.hostname)) throw new JeegError("The JeeG API only runs on this computer.");
    this.token = token; this.base = base.replace(/\/$/, "");
  }
  async _fetch(path, body) {
    const r = await fetch(this.base + path, { method: body ? "POST" : "GET", headers: { Authorization: `Bearer ${this.token}`, ...(body ? { "Content-Type": "application/json" } : {}) }, body: body ? JSON.stringify(body) : undefined });
    let msg; try { msg = await r.json(); } catch { throw new JeegError(`JeeG answered ${r.status}`); }
    if (!msg.ok) throw new JeegError(msg.error || `JeeG answered ${r.status}`);
    return msg.result;
  }
  run(query, opts = {}) { return this._fetch("/v1/run", { query: String(query), yes: !!opts.yes, timeout: opts.timeout }); }
  find(query, limit = 5) { return this._fetch(`/v1/find?q=${encodeURIComponent(query)}&limit=${limit}`); }
  tasks(category) { return this._fetch("/v1/tasks" + (category ? `?category=${encodeURIComponent(category)}` : "")); }
  info(name) { return this._fetch(`/v1/info?name=${encodeURIComponent(name)}`); }
  health() { return this._fetch("/v1/health"); }
}

module.exports = { run, find, tasks, info, Http, JeegError };
