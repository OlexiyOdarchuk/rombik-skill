#!/usr/bin/env python3
"""Синхронізація скіла з канонічного джерела — https://rombik.app/api/v1/skill.md.

Тягне повний skill.md і механічно розкладає його в структуру Agent Skills:
  SKILL.md            — короткий вхід (шаблон + живі фрагменти з джерела)
  references/api.md   — повний довідник HTTP API
  references/astjson.md — специфікація astJSON

Будь-який відсутній якір у джерелі — жорстка помилка: краще червоний CI, ніж тихий дрейф.
"""

import sys
import urllib.request
from pathlib import Path

SOURCE = "https://rombik.app/api/v1/skill.md?lang=en"
ROOT = Path(__file__).resolve().parent.parent


def fetch() -> list[str]:
    req = urllib.request.Request(
        SOURCE,
        headers={"User-Agent": "rombik-skill-sync/1.0 (+https://github.com/OlexiyOdarchuk/rombik-skill)"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8").splitlines(keepends=True)


def find(lines: list[str], prefix: str, start: int = 0) -> int:
    for i in range(start, len(lines)):
        if lines[i].startswith(prefix):
            return i
    sys.exit(f"sync: у джерелі не знайдено якір {prefix!r} — структура skill.md змінилася, онови scripts/sync.py")


def first_line(lines: list[str], prefix: str, lo: int, hi: int) -> str:
    for i in range(lo, hi):
        if lines[i].startswith(prefix):
            return lines[i].rstrip("\n")
    sys.exit(f"sync: не знайдено рядок {prefix!r} у діапазоні — онови scripts/sync.py")


def main() -> None:
    src = fetch()

    # --- якорі -----------------------------------------------------------------
    fm_end = find(src, "---", 1)                       # кінець frontmatter
    i_base = find(src, "## Base")
    i_auth = find(src, "## Authorization")
    i_cli = find(src, "## CLI")
    i_mcp = find(src, "## MCP")
    i_endpoints = find(src, "## Endpoints")
    i_astjson = find(src, "## The rombik format specification")
    i_me = find(src, "### GET /me")
    i_options = find(src, "## Engine options")

    frontmatter = "".join(src[: fm_end + 1])
    cli_block = "".join(src[i_cli:i_mcp]).rstrip() + "\n"
    mcp_block = "".join(src[i_mcp:i_endpoints]).rstrip() + "\n"
    lang_bullet = first_line(src, "- `lang`:", i_endpoints, i_astjson)
    format_bullet = first_line(src, "- `format`:", i_endpoints, i_astjson)

    i_example = find(src, "Example (JSON):", i_endpoints)
    ex_open = find(src, "```", i_example)
    ex_close = find(src, "```", ex_open + 1)
    curl_example = "".join(src[ex_open : ex_close + 1]).rstrip() + "\n"

    # --- references/api.md ------------------------------------------------------
    api = (
        "# rombik HTTP API — full endpoint reference\n\n"
        "Auto-generated from https://rombik.app/api/v1/skill.md — do not edit by hand\n"
        "(see scripts/sync.py).\n\n"
        + "".join(src[i_base:i_cli])
        + "".join(src[i_endpoints:i_astjson])
        + "".join(src[i_me:i_options])
        + "".join(src[i_options:])
    )
    api = api.rstrip() + "\n"

    # --- references/astjson.md --------------------------------------------------
    ast = "".join(src[i_astjson:i_me])
    ast = "# " + ast[3:]  # підняти "## ..." до "# ..." у власному файлі
    ast = (
        ast.rstrip()
        + "\n\nSend the resulting tree via the API with `lang:\"rombik\"` (a Pro feature), or paste it into the\nrombik editor with the «rombik» language selected (also Pro).\n"
    )

    # --- SKILL.md ----------------------------------------------------------------
    skill = f"""{frontmatter}
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

{cli_block}
{mcp_block}
## HTTP API — quick start

Base: `https://rombik.app/api/v1`. Auth header: `X-API-Key: rk_...`
(or `Authorization: Bearer rk_...`). The key is created in the account on the site (shown once).

{curl_example}
{lang_bullet}
{format_bullet}
- `mode`: empty — flowchart (default); `nsd` — Nassi-Shneiderman structogram in any format

Full endpoint reference (render, batch, balance, top-up, gifting, engine options, error codes,
limits): [references/api.md](references/api.md).

## No supported language, or no code at all?

For languages rombik does not auto-parse (assembler, Rust, pseudocode…) or for a verbal
description of an algorithm, build a compact JSON control-flow tree (**astJSON**) and send it
with `lang:"rombik"` (Pro). The full specification with modeling rules and examples:
[references/astjson.md](references/astjson.md).

## Errors

The API returns `{{ error, code }}` — branch on the stable `code`, not on text. The two you will
meet first: `no_credits` (402 → call /topup) and `pro_required` (402). The full table:
[references/api.md](references/api.md).

## Machine-readable specification

OpenAPI 3.1: https://rombik.app/api/v1/openapi.json
"""

    (ROOT / "SKILL.md").write_text(skill, encoding="utf-8")
    (ROOT / "references" / "api.md").write_text(api, encoding="utf-8")
    (ROOT / "references" / "astjson.md").write_text(ast, encoding="utf-8")
    print("sync: SKILL.md, references/api.md, references/astjson.md оновлено")


if __name__ == "__main__":
    main()
