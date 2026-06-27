---
name: golang-100-mistakes
description: "Reviews Go code against the 100 common mistakes catalogued in the book '100 Go Mistakes and How to Avoid Them'. Use when auditing Go code for variable shadowing, slice/map pitfalls, concurrency bugs, error handling anti-patterns, testing gaps, or performance regressions. Covers all ten categories: code organization, data types, control structures, strings, functions and methods, error management, concurrency foundations and practice, standard library, testing, and optimizations. Don't use for general Go syntax help, new feature implementation, non-Go code review, or architecture decisions unrelated to Go idioms."
---

# golang-100-mistakes

Reviews Go code or a file path against the 100 common Go mistakes from the book *100 Go Mistakes and How to Avoid Them* by Teiva Harsanyi.

---

## Step 1: Establish Scope

1. Determine the target: a file path, a code snippet, or an entire package directory.
2. If a `go.mod` is present in the working directory, run the version check helper (read-only):
   ```
   bash <skill-dir>/scripts/check-go-version.sh go.mod
   ```
   where `<skill-dir>` is the absolute path to the `golang-100-mistakes` skill directory.
   Apply any version-sensitive notes printed to stdout.
3. Identify which of the ten categories are likely relevant based on the code's domain:
   - **Code/Project Organization** → always relevant
   - **Data Types** → any use of slices, maps, numbers, or time
   - **Control Structures** → loops, `defer`, `switch`/`select`
   - **Strings** → any string or `[]byte` manipulation
   - **Functions & Methods** → struct methods, constructors, error returns
   - **Error Management** → any function returning `error`
   - **Concurrency** → goroutines, channels, mutexes, `context.Context`
   - **Standard Library** → HTTP, SQL, JSON, file I/O, timers
   - **Testing** → `*_test.go` files
   - **Optimizations** → hot paths, memory-sensitive or high-throughput code

---

## Step 2: Load Relevant Reference Sections

Load only the reference files matching the identified categories.

| Categories | File |
|---|---|
| Code & Project Organization (#1–16) | `<skill-dir>/references/code-organization.md` |
| Data Types (#17–29) | `<skill-dir>/references/data-types.md` |
| Control Structures (#30–35) | `<skill-dir>/references/control-structures.md` |
| Strings (#36–41), Functions (#42–47), Error Mgmt (#48–54) | `<skill-dir>/references/strings-functions-errors.md` |
| Concurrency Foundations (#55–60) + Practice (#61–74) | `<skill-dir>/references/concurrency.md` |
| Standard Library (#75–81), Testing (#82–90), Optimizations (#91–100) | `<skill-dir>/references/stdlib-testing-optimizations.md` |

Read each relevant file now and keep the patterns in working context.

---

## Step 3: Audit the Code

Scan the code systematically against each applicable mistake from the loaded references.

For every finding:
- Record the **mistake number and title** (e.g., `#35 — defer inside a loop`)
- Quote or reference the **specific line(s)** triggering the finding
- Classify as: `BUG` (correctness), `PERF` (performance), `STYLE` (idiom/readability), or `WARN` (context-dependent)

Use this scanning order within each category:
1. Data flow (assignments, returns, copies)
2. Resource lifecycle (open/close, goroutine start/stop)
3. Synchronisation (mutexes, channels, atomics)
4. External interactions (HTTP, SQL, JSON, file I/O)

---

## Step 4: Generate the Review Report

Output a structured report in this format:

```
## 100 Go Mistakes Review

### Summary
- Files reviewed: <list>
- Go version: <version from go.mod or "unknown">
- Categories checked: <list>
- Findings: <N> (BUG: X | PERF: Y | STYLE: Z | WARN: W)

### Findings

#### [BUG|PERF|STYLE|WARN] #<number> — <title>
**Location**: `<file>:<line>` (or inline quote)
**Issue**: <one-sentence description of what is wrong>
**Fix**: <concrete corrected code or pattern>

---
```

If no findings exist in a category, state: `No issues found in <Category>`.

---

## Step 5: Prioritise Recommendations

After all findings, output a **Priority Order** section:

1. `BUG` items first (correctness risk)
2. `PERF` items that affect hot paths
3. `WARN` items requiring context from the author
4. `STYLE` items last

For each finding, suggest whether it warrants an immediate fix, a follow-up ticket, or a team convention change.

---

## Error Handling

- If `scripts/check-go-version.sh` exits non-zero, continue the audit without version-gating but note the failure.
- If the target path does not exist, report the error and ask for the correct path.
- If the code is in a language other than Go, stop and state that this skill only applies to Go.
- If the context window is insufficient to load all six reference files plus the code, prioritise loading references for the categories explicitly requested by the user; discard low-relevance files first.
