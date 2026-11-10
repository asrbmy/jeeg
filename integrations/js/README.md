# jeeg-client (JavaScript / TypeScript)

Use JeeG from Node 18+ with no dependencies. JeeG must be installed (`pip install jeeg`).

```js
const { run, find, Http } = require("./index.js");

const r = await run("gst 2500 18");          // starts `jeeg --stdio` for you
console.log(r.task, r.output);

console.log(await find("open youtube"));      // which tasks match (nothing runs)

// or talk to a running `jeeg --serve-api` (the token comes from `jeeg --api-token`)
const api = new Http(process.env.JEEG_API_TOKEN);
console.log((await api.run("disk space")).output);
```

Tasks that ask for confirmation (shutdown, delete ...) are refused unless JeeG itself was started with `--allow-confirm`.
For other languages use `integrations/openapi/jeeg-openapi.json` with any OpenAPI generator.

Publish (only you can): `cd integrations/js && npm publish` (needs an npm account).
