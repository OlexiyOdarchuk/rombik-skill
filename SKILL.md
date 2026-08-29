---
name: rombik-api
description: Generates ДСТУ (GOST 19.701-90) algorithm flowcharts from source code (Python, C++, C, Java, C#, Pascal, JavaScript, TypeScript, PHP, Go) via the rombik HTTP API. Use it when you need to turn code into a flowchart or Nassi-Shneiderman structogram in docx/visio/drawio/typst/excalidraw/svg/png/pdf.
---

# rombik — code → ДСТУ flowchart

rombik turns source code into a ДСТУ 19.701-90 (ISO 5807) algorithm flowchart over HTTP.
Auth is by API key. 1 export — 1 credit.

Canonical, always-current version of this skill: https://rombik.app/api/v1/skill.md (`?lang=uk` for Ukrainian).

## Ways to use it (pick one)

1. **CLI** (recommended for agents with a shell) — the key stays in a config file and never
   enters the model context.
2. **MCP server** (for MCP-capable clients without a shell) — the same binary, tools available natively.
3. **Raw HTTP API** — when neither is possible. See [references/api.md](references/api.md).

## CLI

```bash
curl -fsSL https://rombik.app/install.sh | sh   # macOS/Linux → ~/.local/bin
# Windows (PowerShell): irm https://rombik.app/install.ps1 | iex
rombik auth                                # log in via browser (or: rombik auth rk_…)
```

Then use commands WITHOUT passing the key as an argument (it is read from `~/.config/rombik`):

- `rombik render main.py -f pdf -o out.pdf` — file/stdin/`--url` → chart
- `rombik batch src/*.py -f pdf -o project.pdf` — many sources at once
- `rombik me` · `rombik products` · `rombik topup` · `rombik gift --email … --qty …`
- `rombik version --json` → `{version,latest,updateAvailable}`; `rombik update` — update the CLI
- Engine options — the same flags as the API `options` field: `--locale`, `--for-format`,
  `--single-end`, `--strip-types`, `--yes/--no`, `--in-word/--out-word`, `--cap-word/--cap-format`,
  etc. (full list: `rombik render -h`; custom text values need Pro).

Commands map 1:1 to the HTTP endpoints; exit codes follow the error `code`.
Download & details: https://rombik.app/developers

## MCP (for clients without a shell)

The user installs the CLI once, runs `rombik auth`, and adds to the MCP client config
(Claude Desktop, Cursor, Cline…):

```json
{ "mcpServers": { "rombik": { "command": "rombik", "args": ["mcp"] } } }
```

Tools: `render_flowchart` (code|url → PNG image, or svg/typst/excalidraw/pdf), `balance`,
`products`, `topup_link`, `gift_credits`. Transport is stdio; API errors with a `code` come back
as isError.

## HTTP API — quick start

Base: `https://rombik.app/api/v1`. Auth header: `X-API-Key: rk_...` (or `Authorization: Bearer rk_...`).
The key is created in the account on the site (shown once).

```bash
curl -X POST https://rombik.app/api/v1/render \
  -H "X-API-Key: rk_YOUR_KEY" -H "Content-Type: application/json" \
  -d '{"code":"def f(a):\n    return a*2","lang":"python","format":"svg"}' -o out.svg
```

- `lang`: python | cpp | c | java | csharp | pascal | javascript | typescript | php | go | rombik
  (Pro: `code` carries a ready astJSON tree instead of source code — see
  [references/astjson.md](references/astjson.md))
- `format`: docx | visio | drawio | typst | excalidraw | svg | png | pdf | json | poster (svg by default)
- `mode`: empty — flowchart (default); `nsd` — Nassi-Shneiderman structogram in any format

Full endpoint reference (render, batch, balance, top-up, gifting, engine options, error codes,
limits): [references/api.md](references/api.md).

## No supported language, or no code at all?

For languages rombik does not auto-parse (assembler, Rust, pseudocode…) or for a verbal
description of an algorithm, build a compact JSON control-flow tree (**astJSON**) and send it with
`lang:"rombik"`. The full specification with modeling rules and examples:
[references/astjson.md](references/astjson.md).

## Errors (branch on `code`, not on text)

`unauthorized` (401) · `no_credits` (402 → call /topup) · `pro_required` (402) ·
`unknown_format` / `unknown_lang` / `bad_request` / `bad_source` (400) · `render_failed` (500) ·
`rate_limited` (429) · `payment_unavailable` (503) · `server_error` (500).
Details: [references/api.md](references/api.md).

## Machine-readable specification

OpenAPI 3.1: https://rombik.app/api/v1/openapi.json
