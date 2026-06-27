# Code and Project Organization — Mistakes #1–16

## #1 — Unintended variable shadowing
- Inner block redeclares a name already in scope (e.g., `err` inside `if err := …`).
- The outer variable never receives the intended value; bugs compile cleanly.
- **Signal**: `if v, err := …; err != nil { … }` followed by use of the outer `v` that was never assigned.

## #2 — Unnecessary nested code
- Each `if/else`, `for`, or `switch` arm that can be inverted into an early-return flattens the tree.
- More than two levels of nesting is a smell. Convert `if !condition { … } else { main logic }` → guard clause.

## #3 — Misusing init functions
- `init` must not depend on package-level state whose initialisation order is undefined.
- Side effects in `init` (network calls, file I/O) make packages hard to test and reuse.
- Multiple `init` functions in one file are allowed but confusing; prefer explicit `Setup()` functions.

## #4 — Overusing getters and setters
- Go is not Java. Plain exported fields are idiomatic when there is no invariant to enforce.
- Add accessors only when the field requires validation, lazy initialisation, or synchronisation.

## #5 — Interface pollution
- Define interfaces at the *consumer* side, not speculatively in the package that owns the concrete type.
- An interface with a single implementation in the same package almost always signals premature abstraction.

## #6 — Interface on the producer side
- Packages should return concrete types; callers define the interface that matches what they need.
- Exception: libraries where the concrete type must stay hidden (e.g., `io.Reader`).

## #7 — Returning interfaces
- Returning an interface from a constructor locks callers into the abstraction and prevents them from accessing additional methods on the concrete type.
- Prefer `return *ConcreteType` and let callers wrap it in an interface if needed.

## #8 — `any` says nothing
- `any` (alias for `interface{}`) loses type safety and forces type assertions at call sites.
- Prefer a concrete type, a union-like sum type pattern, or generics.

## #9 — Being confused about when to use generics
- Generics are appropriate for data structures and algorithms that work identically across types.
- Do not use generics to replace simple interface dispatch when behaviour differs per type.

## #10 — Type embedding problems
- Embedding promotes all methods of the embedded type, which may expose unwanted surface area.
- Never embed a type solely for code reuse when composition via a named field is clearer.
- Embedding `sync.Mutex` leaks `Lock`/`Unlock` to callers; prefer a private field.

## #11 — Not using the functional options pattern
- Constructor functions with many optional parameters should use `Option` funcs, not long signatures or config structs with zero values that are hard to distinguish from defaults.

## #12 — Project misorganisation
- Flat packages for large projects and over-engineered layering for small ones are both mistakes.
- Go stdlib layout: `cmd/`, `internal/`, `pkg/` (optional). Avoid generic names like `util`, `common`, `misc`.

## #13 — Creating utility packages
- Packages named `util`, `helper`, `common` are magnets for unrelated code; they lack cohesion.
- Group by domain responsibility, not by syntactic role.

## #14 — Ignoring package name collisions
- A package imported under its default name that shadows a built-in or standard library name causes silent confusion.
- Alias the import when a collision exists: `import mathrand "math/rand"`.

## #15 — Missing code documentation
- Every exported symbol must have a doc comment starting with the symbol's name.
- `godoc` conventions: use complete sentences, start with the name, no blank line between declaration and comment.

## #16 — Not using linters
- At minimum: `go vet`, `staticcheck`, `errcheck`.
- Linter findings that are intentionally suppressed require an inline `//nolint` comment with a reason.
