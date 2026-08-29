# The rombik format specification (astJSON)

The **rombik** format is a compact JSON control-flow tree from which the deterministic rombik engine
draws a flowchart to ДСТУ 19.701-90 (ISO 5807). You describe **only the logic** (sequence of actions,
branches, loops) and the **node text**. The standard framing is added automatically: Start/End ovals
around the function, Yes/No labels on diamonds, the shapes themselves, arrow direction, the figure
numbering. Do **not** write those by hand.

Use the format when: (a) the language isn't auto-parsed (assembler, Rust, pseudocode…), or (b) there
is no code at all — only a verbal description. Paste the resulting tree into the rombik editor with the
«rombik» language selected (a Pro feature), or send it via the API with `lang:"rombik"`.

### 1. Top level

A document is an **array of functions**; each function renders as its own chart:

```json
[ { "name": "name", "main": true, "block": { "kind": "block", "stmts": [ /* nodes */ ] } } ]
```

- `name` — the function name (the chart's heading).
- `main` — `true` for the main function (the rest are helpers).
- `block` — the root block node; its `stmts` is a top-to-bottom sequence of nodes.

### 2. Nodes

General shape: `{ "kind": …, "text"?, "cond"?, "then"?, "else"?, "body"?, "stmts"?, "jump"?, "depth"? }`.
The `then` / `else` / `body` branches are **block nodes** of the form `{ "stmts": [ … ] }`; an empty
branch is `{ "stmts": [] }`.

| kind | ДСТУ shape | Required fields | Purpose |
|------|------------|-----------------|---------|
| `process` | rectangle (Process) | `text` | one elementary action: assignment, computation |
| `io` | parallelogram (Data) | `text` | input/output; start the text with «Input»/«Output» |
| `call` | rectangle with double side bars (Predefined process) | `text` | a **standalone** subprogram call |
| `terminal` | oval (Terminator) | — | an explicit function exit: `return` / `raise` |
| `if` | diamond (Decision) | `cond`, `then`, `else` | branching |
| `for` | hexagon (Preparation) | `cond`, `body` (`else` optional) | counted loop; `cond` is the spec |
| `while` | diamond (pre-condition) | `cond`, `body` (`else` optional) | pre-test loop |
| `dowhile` | diamond (post-condition) | `cond`, `body` | post-test loop (`else` not supported) |
| `infloop` | loop | `body` | infinite loop |
| `break` | — | `depth` | exit a loop (only inside a loop) |
| `continue` | — | `depth` | next iteration (only inside a loop) |
| `connector` | circle (Connector) | — | a line break; `jump:true` — a goto |

**Fields by purpose:**
- `text` — the label inside the shape (`process` / `io` / `call` / `terminal` / `connector`).
- `cond` — the condition for `if` / `while` / `dowhile`; for `for` it is the **counter spec** in the
  format `var := start, end[, step]` (e.g. `i := 1, n`). It goes in `cond`, **not** `text`.
- `depth` (`break` / `continue`) — how many loops up: `0` — the nearest, `1` — one level higher
  (labeled break). Range: `0 … (number of enclosing loops − 1)`.
- `jump` (`connector`) — `true` means a goto.

### 3. Modeling rules (follow exactly)

- **Function parameters → the first `io` node.** If a function has parameters, make the very first node
  in `stmts` an `io` with text `Input <parameters, comma-separated>` (no colon):
  `{"kind":"io","text":"Input a, b"}`. This applies to EVERY function with parameters — even a helper,
  even if there is no explicit input in the code.
- **`call` is only a standalone call statement** (a subprogram invocation on its own line: `sort(a)`).
  A call INSIDE an expression is not a separate node. `total = total + sum(a, n)` → one `process`
  (not `call` + `process`). A call in a condition (`if f(x)`, `while f(x)`) → just the diamond `cond`.
  `return n * fact(n-1)` → one `terminal` (not `call` + `terminal`).
- **`terminal` is only an explicit exit** (`return` / `raise` in the source). An assignment is always a
  `process`, even if it sets the function's result (Pascal `Name := value`). Do not add your own
  `terminal` "at the end" if there is no explicit return — the final End oval is added by the engine.
- **`for/else` and `while/else`** (Python): put the branch that runs on NORMAL loop completion into the
  loop's own `else` field, not as separate nodes after it.
- **One `process` = one elementary action.** Do not merge several assignments into one node, and do not
  split one assignment across several.
- **Do not add Start/End nodes and do not write Yes/No** — the engine does that.

### 4. Shape meanings per ДСТУ 19.701-90 / ISO 5807

Pick the `kind` by the MEANING of the action (the engine draws the shape):
- **Process** (rectangle) → `process`: an operation that changes the value, form or location of data.
- **Data** (parallelogram) → `io`: input or output of data (carrier unspecified).
- **Decision** (diamond) → `if` / `while` / `dowhile`: one entry and several alternative exits; exactly
  one is activated after evaluating the condition. The Yes/No labels are added by the engine — you only
  supply `cond`.
- **Predefined process** (rectangle with double side bars) → `call`: a process defined elsewhere
  (a subprogram, module) — a standalone call.
- **Preparation** (hexagon) → `for`: an initialization affecting a subsequent action (a loop counter).
- **Connector** (circle) → `connector`: a line break continued elsewhere; `jump:true` — a goto.
- **Terminator** (oval) → `terminal` and the Start/End the engine adds: entry from / exit to the
  external environment (return / raise).
- **Flow** (done by the engine): the standard direction is top-to-bottom and left-to-right; lines from a
  Decision are labelled with the result. You do not write direction / arrows / labels.

### 5. Validation contract

The engine validates the tree and returns human-readable errors — fix and retry:
- unknown `kind` (allowed: `process, io, call, terminal, if, for, while, dowhile, infloop, break, continue, connector`);
- `if` / `while` / `dowhile` without `cond`; `for` without a `cond` spec;
- `process` / `io` / `call` without `text`;
- `dowhile` with `else` (not supported — remove it or use `while`);
- `break` / `continue` outside a loop; `depth` out of range;
- an empty document (at least one function is required).

**Limits:** ≤ 100 functions, ≤ 2000 nodes total, block nesting ≤ 100, ≤ 2000 characters in `text`/`cond`.

### 6. Examples

**`if` / `elif` / `else`** (elif = a nested `if` inside `else`):
```json
{ "kind": "if", "cond": "x > 0",
  "then": { "stmts": [ { "kind": "io", "text": "Output: plus" } ] },
  "else": { "stmts": [
    { "kind": "if", "cond": "x < 0",
      "then": { "stmts": [ { "kind": "io", "text": "Output: minus" } ] },
      "else": { "stmts": [ { "kind": "io", "text": "Output: zero" } ] } } ] } }
```

**`for` (range) loop and `while`:**
```json
{ "kind": "for", "cond": "i := 0, n-1",
  "body": { "stmts": [ { "kind": "call", "text": "process(i)" } ] } }

{ "kind": "while", "cond": "b <> 0",
  "body": { "stmts": [ { "kind": "process", "text": "t := b" } ] } }
```

**A description in words → astJSON.** «Read a number n. If it is even, print “even”, otherwise “odd”.»
```json
[
  { "name": "parity", "main": true, "block": { "kind": "block", "stmts": [
    { "kind": "io", "text": "Input n" },
    { "kind": "if", "cond": "n mod 2 = 0",
      "then": { "stmts": [ { "kind": "io", "text": "Output: even" } ] },
      "else": { "stmts": [ { "kind": "io", "text": "Output: odd" } ] } }
  ] } }
]
```

**Full example — find the maximum in an array:**
```json
[
  { "name": "findMax", "main": true, "block": { "kind": "block", "stmts": [
    { "kind": "io", "text": "Input a, n" },
    { "kind": "process", "text": "m := a[0]" },
    { "kind": "for", "cond": "i := 1, n-1", "body": { "stmts": [
      { "kind": "if", "cond": "a[i] > m",
        "then": { "stmts": [ { "kind": "process", "text": "m := a[i]" } ] },
        "else": { "stmts": [] } }
    ] } },
    { "kind": "io", "text": "Output m" },
    { "kind": "terminal", "text": "Return m" }
  ] } }
]
```

### Generating from a description or code

Given a description in words or code in any language, build the tree per this specification and return
**only the final JSON array** in a ` ```json ` block, with no surrounding text. If the description is
ambiguous, implement the simplest reasonable interpretation; do not invent extra branches.

Send the resulting tree via the API with `lang:"rombik"` (a Pro feature), or paste it into the
rombik editor with the «rombik» language selected (also Pro).
