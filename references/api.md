# rombik HTTP API — full endpoint reference

Auto-generated from https://rombik.app/api/v1/skill.md — do not edit by hand
(see scripts/sync.py).

## Base
`https://rombik.app/api/v1` — e.g. the /render endpoint is https://rombik.app/api/v1/render

## Authorization
Header (either of the two):
- `X-API-Key: rk_...`
- `Authorization: Bearer rk_...`

Create a key in your account on the site (shown once).

## Sign in with rombik — when you build an app for OTHER people
Do not ask users to paste a key by hand: rombik issues one itself after their consent (OAuth 2.0 + OIDC, any standard library works).
1. `POST /oauth/register` `{ "client_name": "…", "redirect_uris": ["https://…/callback"], "token_endpoint_auth_method": "none" }` → `client_id` (plus `client_secret` unless the method is `none`).
2. Send the user to https://rombik.app/oauth/authorize?response_type=code&client_id=…&redirect_uri=…&scope=openid%20email%20api&state=…&code_challenge=…&code_challenge_method=S256 — they click "Allow" and come back to `redirect_uri` with a `code`.
3. `POST /oauth/token` (form-urlencoded: grant_type=authorization_code, code, redirect_uri, client_id, code_verifier) → `access_token` is the `rk_…` key for every endpoint below; with scope `openid` you also get an `id_token` (RS256; keys at `GET /oauth/jwks`, identity at `GET /oauth/userinfo`).

PKCE S256 is MANDATORY for a client without a secret; `redirect_uri` must be https (http allowed on localhost) and identical in steps 2 and 3; the code lives 10 minutes and works once. Rendering spends credits of the ACCOUNT OWNER who consented; they revoke access in their account (the key disappears → 401).
Discovery metadata: https://rombik.app/.well-known/oauth-authorization-server and https://rombik.app/.well-known/openid-configuration

## Endpoints

### POST /render — code → flowchart (1 export — 1 credit)
JSON body: `{ "code": "...", "lang": "python", "format": "svg" }`
- `lang`: python | cpp | c | java | csharp | pascal | javascript | typescript | php | go | rombik (Pro: `code` carries a ready astJSON tree instead of source code; spec in the format section below)
- `format`: docx | visio | drawio | typst | excalidraw | svg | png | jpeg | webp | gif | gif_anim | html | pdf | json | poster (svg by default). jpeg/webp/gif — the same raster as png (webp is lossless); gif_anim — an animated GIF, the chart draws itself block by block; html — a self-contained page "chart + code with line numbers". poster — code on the left, chart on the right, as one shareable image (styling goes in the poster block; works together with mode:"nsd" and options.locale). `docx` — Word with native shapes; `visio` — .vsdx native shapes; `drawio` — editable diagrams.net; `json` — raw Diagram geometry.
- `mode`: empty — flowchart (default); `nsd` — Nassi-Shneiderman structogram (nested boxes, no arrows) in any format.
- `split` (default true for docx, PDF & Typst document; for svg/png/jpeg/webp/gif/html/excalidraw — with explicit true): split tall charts into parts with А/Б connectors. For docx/pdf/typst these are separate pages (pdf is multi-page); for svg/png/excalidraw — parts on one canvas. `false` — keep continuous (one sheet)
- `url`: instead of `code` — a link to a file (allowlist: raw.githubusercontent.com, gist, gitlab.com, bitbucket.org, codeberg.org; `github.com/.../blob/...` auto→raw). Language is inferred from the extension.
- optional: `fn` (only the function with this name), `scale` (PNG zoom), `fragment` (Typst fragment), `font`, `options` (object — full list in the «Engine options» section below)
- `options` with custom words/caption/for-format require an account with active **Pro** (otherwise 402 `pro_required`). Toggles, `locale`, `font`, `scale`, `figStart` are free.
- `?json=1` → JSON response `{ format, encoding (utf-8|base64), content, creditsLeft }` instead of a file

### POST /render/batch — many sources at once (1 credit per item)
Body: `{ "items": [ {"code":"...","lang":"python"}, {"url":"https://raw.../b.cpp"} ], "format": "pdf" }`
- `items`: 1..100 items, each `{ code|url, lang?, fn?, name? }`.
- Charges 1 credit per export among successful items; balance ≥ the item count at least.
- `format=pdf` (and not `bundle:"zip"`) → a single multi-page PDF (one page per item); other formats → a zip with one file per item.
- `?json=1` → report `{ count, rendered, creditsLeft, items:[{index,name,ok,error}], encoding:base64, content }`; otherwise a file (pdf|zip) + headers `X-Rombik-Rendered`, `X-Rombik-Failed`.

Example (JSON):
```bash
curl -X POST https://rombik.app/api/v1/render \
  -H "X-API-Key: rk_YOUR_KEY" -H "Content-Type: application/json" \
  -d '{"code":"def f(a):\n    return a*2","lang":"python","format":"svg"}' -o out.svg
```
Example (file): `curl -X POST https://rombik.app/api/v1/render -H "X-API-Key: rk_..." -F file=@prog.py -F format=pdf -o out.pdf`

### GET /me — balance
→ `{ email, name, credits, pro, proUntil }`

### POST /topup — payment link (when out of credits)
- `{ "kind": "credits_unit", "qty": 10 }` — per unit
- `{ "kind": "credits", "id": <packId> }` — a pack (id from /products)
- `{ "kind": "pro", "id": <tierId> }` — Pro
→ `{ provider, payUrl, iframe, invoiceId, code, label, amountKop, amountUah }` — a SINGLE shape, branch on `provider`: `plata` (active; payUrl is the plata by mono payment page: card / Apple·Google Pay) or `jar` (fallback; payUrl is a monobank jar prefilled with amount + code, `code` is the manual-transfer comment). Open `payUrl` in a browser, pay; credits arrive in ~a minute (poll GET /me).
- optional `"provider": "paddle"` in the request — pay in USD (international) via Paddle when /products says `paddle:true`. The response differs: a Paddle.js checkout config (`priceId`, `clientToken`, …) with no `payUrl` — meant for the web; from CLI/agents use the default (UAH).

### GET /products — price catalog
→ `{ credits:[{id,qty,uah,usd}], pro:[{id,bonus,days,uah,usd}], unitUah, unitUsd, available, provider, paddle }`
- `available:false` → payment temporarily unavailable; `provider` — the active UAH provider (plata|jar); `paddle:true` — USD payments available (/topup with `"provider":"paddle"`).

### POST /gift — gift credits to a friend by email
- `{ "email": "friend@example.com", "qty": 5 }` — deducts 5 credits from you, adds them to your friend.
- If the recipient has no account yet — it is created by email (credits wait for first sign-in). They get an email and an in-account notification.
→ `{ ok, credits }` (your new balance). Errors: `gift_failed` (400, e.g. not enough credits), `bad_email`, `bad_qty`.

### POST /r — temporary public link to a result (1 hour)
When your client cannot display files (chat, webhook, email) — hand the user a link instead of bytes.
- The body is the FILE itself (bytes from /render), `Content-Type` is its MIME; `?name=schema.pdf` sets the download name.
→ `{ url, expiresIn }`. Images and PDFs open in the browser, everything else downloads. The CLI does the same with `--link`.

## Engine options — the `options` object on /render and /render/batch
Powerful tuning of the chart to the requirements (teacher/standard). Use them freely.
Toggles, `locale`, `font`, `scale`, `figStart` are free; custom text values
(your own words) require active Pro on the account (otherwise 402 `pro_required`).
```
# toggles (true/false, default false):
singleEnd            one shared "End" instead of one per exit
mainOnlyTerminators  Start/End only for main; subprograms → Entry/Exit
callAsProcess        a function call as a "Process", not a "Subprogram"
stripTypes           strip type annotations from blocks
returnAsIO           render return as an output block
# text / numeric:
locale                "uk" | "en" — language of chart inserts
forFormat             "comma" | "range" | "verbose" — counting-for look
yes / no              branch labels (Yes/No · Так/Ні · +/−)
inWord / outWord      input/output words (Input/Output)
startText / endText   main terminators (Start/End)
entryText / exitText  subprogram terminators (Entry/Exit)
returnWord            word before return (Return)
forEachWord           foreach separator (∈)
capWord               caption word (Figure)
capFormat             caption template: {word} {num} — {text}
figStart              which number to start figures from (integer)
```
Example: {"code":"…","lang":"python","options":{"locale":"en","yes":"Yes","no":"No","singleEnd":true,"stripTypes":true}}
In the CLI these are flags: --locale, --for-format, --single-end, --yes/--no, --strip-types … (full list: rombik render -h).

## Errors
Body `{ error, code }`. Branch on `code` (stable), not on text:
- `unauthorized` (401) — bad/missing key
- `no_credits` (402) — out of credits → call /topup
- `pro_required` (402) — custom Pro options without active Pro; the `proFeatures` field lists which
- `unknown_format` / `unknown_lang` / `bad_request` (400)
- `bad_source` (400) — could not fetch `url` (host not allowed, unreachable, too large)
- `render_failed` (500) — code parsed but render/rasterization failed (check syntax, language, fn)
- `rate_limited` (429) — free endpoints only; Retry-After header is present
- `payment_unavailable` (503), `server_error` (500)

## Credits & limits
- 1 export — 1 credit; there is no free tier in the API.
- /render — no limit (bound by credits). /me, /topup, /products, /gift — 60 requests/min per key.

## Machine-readable specification
OpenAPI 3.1: https://rombik.app/api/v1/openapi.json
