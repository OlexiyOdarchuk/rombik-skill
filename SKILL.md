---
name: rombik-api
description: Generates ДСТУ (GOST 19.701-90) algorithm flowcharts from source code (Python, C++, C, Java, C#, Pascal, JavaScript, TypeScript, PHP, Go) via the rombik HTTP API. Use it when you need to turn code into a flowchart or Nassi-Shneiderman structogram in docx/visio/drawio/typst/excalidraw/svg/png/jpeg/webp/gif/html/pdf (and an animated GIF).
---

# rombik — code → ДСТУ flowchart

rombik turns source code into a ДСТУ 19.701-90 (ISO 5807) algorithm flowchart over HTTP.
Auth is by API key. 1 export — 1 credit.

Canonical, always-current version of this skill: https://rombik.app/api/v1/skill.md
(`?lang=uk` for Ukrainian). This repository mirrors it in the Agent Skills layout.

## Ways to use it (pick one)

1. **CLI** (recommended for agents with a shell) — the key stays in a config file and never
   enters the model context.
2. **MCP server** (for MCP-capable clients without a shell) — the same binary, tools available natively.
3. **Raw HTTP API** — when neither is possible. See [references/api.md](references/api.md).

## CLI (recommended for agents)
Instead of raw HTTP calls with the key in the prompt — install the `rombik` CLI; it keeps the key in a config file (`~/.config/rombik`), so the key never enters the model context:
```bash
curl -fsSL https://rombik.app/install.sh | sh   # macOS/Linux → ~/.local/bin
# Windows (PowerShell): irm https://rombik.app/install.ps1 | iex
rombik auth                                # log in via browser (or: rombik auth rk_…)
```
Then use commands WITHOUT passing the key as an argument (it is read from the config):
- `rombik render main.py -f pdf -o out.pdf` — file/stdin/`--url` → chart; `--link` — also a temporary public link to the result (valid 1h)
- `rombik batch src/*.py -f pdf -o project.pdf` — many sources at once
- `rombik me` · `rombik products` · `rombik topup` · `rombik gift --email … --qty …`
- `rombik version --json` → `{version,latest,updateAvailable}`; `rombik update` — update the CLI to the latest version
- Engine options — the same flags as the API `options` field: `--locale`, `--for-format`, `--single-end`, `--strip-types`, `--yes/--no`, `--in-word/--out-word`, `--cap-word/--cap-format`, etc. (full list: `rombik render -h`; custom values need Pro).
Commands map 1:1 to the HTTP endpoints below; exit codes follow the error `code`. Download & details: https://rombik.app/developers

## MCP (for clients without a shell)
Two ways in; the tools are the same: `render_flowchart` (code|url → PNG image, or jpeg/webp/gif/gif_anim/svg/html/typst/excalidraw/pdf), `balance`, `products`, `topup_link`, `gift_credits`. API errors with a `code` come back as isError.
- **Remote (no install):** add the URL `https://rombik.app/mcp` (Streamable HTTP) to your MCP client — authorization happens by itself via OAuth discovery and a browser consent page, no keys to type.
- **Local (stdio):** the user installs the CLI once, runs `rombik auth`, and adds to the MCP client config:
```json
{ "mcpServers": { "rombik": { "command": "rombik", "args": ["mcp"] } } }
```

## HTTP API — quick start

Base: `https://rombik.app/api/v1`. Auth header: `X-API-Key: rk_...`
(or `Authorization: Bearer rk_...`). The key is created in the account on the site (shown once).

```bash
curl -X POST https://rombik.app/api/v1/render \
  -H "X-API-Key: rk_YOUR_KEY" -H "Content-Type: application/json" \
  -d '{"code":"def f(a):\n    return a*2","lang":"python","format":"svg"}' -o out.svg
```

- `lang`: python | cpp | c | java | csharp | pascal | javascript | typescript | php | go | rombik (Pro: `code` carries a ready astJSON tree instead of source code; spec in the format section below)
- `format`: docx | visio | drawio | typst | excalidraw | svg | png | jpeg | webp | gif | gif_anim | html | pdf | json | poster (svg by default). jpeg/webp/gif — the same raster as png (webp is lossless); gif_anim — an animated GIF, the chart draws itself block by block; html — a self-contained page "chart + code with line numbers". poster — code on the left, chart on the right, as one shareable image (styling goes in the poster block; works together with mode:"nsd" and options.locale). `docx` — Word with native shapes; `visio` — .vsdx native shapes; `drawio` — editable diagrams.net; `json` — raw Diagram geometry.
- `mode`: empty — flowchart (default); `nsd` — Nassi-Shneiderman structogram in any format

Full endpoint reference (render, batch, balance, top-up, gifting, engine options, error codes,
limits): [references/api.md](references/api.md).

## No supported language, or no code at all?

For languages rombik does not auto-parse (assembler, Rust, pseudocode…) or for a verbal
description of an algorithm, build a compact JSON control-flow tree (**astJSON**) and send it
with `lang:"rombik"` (Pro). The full specification with modeling rules and examples:
[references/astjson.md](references/astjson.md).

## Errors

The API returns `{ error, code }` — branch on the stable `code`, not on text. The two you will
meet first: `no_credits` (402 → call /topup) and `pro_required` (402). The full table:
[references/api.md](references/api.md).

## Machine-readable specification

OpenAPI 3.1: https://rombik.app/api/v1/openapi.json
