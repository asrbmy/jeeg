// Use JeeG from Node.js through the local API.
//   1) in a terminal:  jeeg --serve-api        (prints a token)
//   2) here:           JEEG_TOKEN=<token> node node_api.js
const token = process.env.JEEG_TOKEN;
const base = "http://127.0.0.1:8766/v1";
const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

async function run(query) {
  const r = await fetch(`${base}/run`, { method: "POST", headers, body: JSON.stringify({ query }) });
  return (await r.json()).result;
}

(async () => {
  const r = await run("gst 2500 18");
  console.log(r.ok ? r.output : `failed: ${r.output}`);
  const f = await fetch(`${base}/find?q=${encodeURIComponent("open youtube")}&limit=2`, { headers });
  console.log((await f.json()).result.map((m) => m.name));
})();
