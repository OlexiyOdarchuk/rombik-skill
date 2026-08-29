# rombik-skill

An [Agent Skill](https://agentskills.io) that teaches AI agents to generate ДСТУ (GOST 19.701-90 /
ISO 5807) algorithm flowcharts and Nassi-Shneiderman structograms from source code via
[rombik](https://rombik.app) — CLI, MCP server, or raw HTTP API.

Input languages: Python, C++, C, Java, C#, Pascal, JavaScript, TypeScript, PHP, Go — plus a
compact astJSON tree for anything else (assembler, Rust, pseudocode, or a verbal description).
Export formats: SVG, PNG, PDF, Word (docx), Visio, draw.io, Typst, Excalidraw.

## Install

Works in any [SKILL.md-compatible agent](https://agentskills.io) — Claude Code, OpenAI Codex,
GitHub Copilot, Cursor, Gemini CLI, VS Code and others:

```bash
npx skills add OlexiyOdarchuk/rombik-skill
```

Or copy this directory into your agent's skills folder manually.

## What's inside

- [`SKILL.md`](SKILL.md) — the skill: when to use rombik and the three ways to call it
  (CLI / MCP / HTTP).
- [`references/api.md`](references/api.md) — full HTTP endpoint reference: render, batch,
  balance, top-up, engine options, error codes, limits.
- [`references/astjson.md`](references/astjson.md) — the astJSON control-flow tree
  specification for unsupported languages and verbal descriptions.

## Canonical source

The always-current version of this skill is served by the API itself:
[`https://rombik.app/api/v1/skill.md`](https://rombik.app/api/v1/skill.md)
(`?lang=uk` for Ukrainian). This repository mirrors it in the standard Agent Skills layout and
stays in sync automatically: every rombik deploy triggers the
[sync workflow](.github/workflows/sync.yml) (`scripts/sync.py`).

Machine-readable API spec: [OpenAPI 3.1](https://rombik.app/api/v1/openapi.json) ·
Developer docs: [rombik.app/developers](https://rombik.app/developers)

## License

The skill text is MIT-licensed (see [LICENSE](LICENSE)). The rombik service itself is a separate
commercial product; API usage is governed by its own terms.
