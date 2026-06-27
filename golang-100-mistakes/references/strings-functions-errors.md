# Strings (#36–41), Functions & Methods (#42–47), Error Management (#48–54)

---

## Strings

### #36 — Not understanding runes
- A `string` is a sequence of bytes; a `rune` is a Unicode code point (up to 4 bytes in UTF-8).
- `len(s)` returns byte count; `utf8.RuneCountInString(s)` returns rune count.
- Do not index a string with `s[i]` when the content may be multi-byte.

### #37 — Inaccurate string iteration
- `for i, r := range s` iterates over runes and advances `i` by the byte width of `r`.
- `for i := 0; i < len(s); i++` iterates over bytes; mixing both idioms causes off-by-one bugs.

### #38 — Misusing trim functions
- `strings.Trim(s, cutset)` removes any *characters* in `cutset` from both ends, not the substring.
- To remove a prefix/suffix substring use `strings.TrimPrefix` / `strings.TrimSuffix`.

### #39 — Under-optimised string concatenation
- `+` concatenation in a loop is O(n²) because strings are immutable and each concat allocates.
- Use `strings.Builder` or `bytes.Buffer`; call `WriteString` in the loop, then `String()` once.

### #40 — Useless string conversions
- Converting `[]byte` → `string` → `[]byte` allocates needlessly. Many stdlib functions accept both.
- Prefer `bytes.Contains`, `bytes.HasPrefix`, etc. when working with byte slices.

### #41 — Substring and memory leaks
- `s[a:b]` shares the backing array of `s`; the full original string is retained by the GC.
- To avoid retaining a large string via a small substring: `result = string([]byte(s[a:b]))` or `strings.Clone` (Go 1.20+).

---

## Functions and Methods

### #42 — Wrong receiver type
- Value receiver: appropriate when the method does not mutate state and `T` is small or contains no mutex/lock.
- Pointer receiver: required when mutating state, when `T` is large, or when `T` implements an interface with pointer receivers.
- Be consistent within a type: mixing pointer and value receivers is confusing.

### #43 — Never using named result parameters
- Named results are useful when: (a) the meaning of multiple return values is not obvious, (b) the function uses `defer` to modify the return values.
- Do not use named results just to allow bare `return`; that harms readability.

### #44 — Side effects with named result parameters
- A `defer` that modifies a named return parameter changes the actual returned value.
- Be explicit: either document the deferred modification or avoid named returns when a bare `return` would be confusing.

### #45 — Returning a nil receiver
- A method returning `error` that returns a typed nil (`var e *MyError; return e`) is NOT a nil `error` interface; the caller's `err != nil` check is `true`.
- Always return the untyped `nil` literal: `return nil`.

### #46 — Filename as function input
- Accept `io.Reader` instead of a file path; the caller can pass an `os.File`, a `bytes.Reader`, or a test fixture.
- This makes the function testable without touching the filesystem.

### #47 — `defer` argument/receiver evaluation
- `defer f(x)` captures the *value* of `x` at the point of the defer statement, not at execution time.
- To defer with a value computed at return time, use a closure: `defer func() { f(x) }()`.
- Pointer receivers are shared; value receivers are copied at defer time.

---

## Error Management

### #48 — Panicking unnecessarily
- `panic` is reserved for truly unrecoverable programmer errors (e.g., nil dereference that cannot be prevented by design).
- External failures (I/O, bad input) must return `error`, not panic.

### #49 — When to wrap an error
- Use `fmt.Errorf("…: %w", err)` to wrap when the caller needs to inspect the cause with `errors.Is`/`errors.As`.
- Wrap for *context addition*; do not wrap when the error's type must be hidden from the caller (i.e., abstraction boundary).

### #50 — Comparing error type inaccurately
- Do not use `err.(*MyError) != nil` directly; use `errors.As(err, &target)` which unwraps the chain.

### #51 — Comparing error value inaccurately
- Do not use `err == ErrNotFound` when wrapping is involved; use `errors.Is(err, ErrNotFound)`.

### #52 — Handling an error twice
- Either log an error or return it — not both. Returning after logging causes the error to be logged multiple times up the call stack.

### #53 — Not handling an error
- Every returned error must be consumed: checked, logged, or explicitly ignored with `_ = f()` plus a comment.
- Silently discarding errors (`f()` with no assignment) is a defect.

### #54 — Not handling `defer` errors
- `defer f.Close()` silently discards the error; capture it: `defer func() { if err := f.Close(); err != nil { … } }()`.
- In named-return functions, propagate the close error only when the function would otherwise succeed.
