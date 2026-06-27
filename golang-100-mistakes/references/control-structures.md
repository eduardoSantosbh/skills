# Control Structures — Mistakes #30–35

## #30 — Elements are copied in `range` loops
- `for i, v := range slice` copies each element into `v`; modifying `v` does not modify the original.
- To mutate elements, use `slice[i]` or range over a slice of pointers.

## #31 — Argument evaluation in `range` loops
- The range expression (slice, map, channel, string) is evaluated once before the loop starts.
- For a channel, the channel value is fixed; for a slice, a snapshot of the header (pointer, len, cap) is taken.
- Appending to the slice inside the loop does not extend the iteration range.

## #32 — Pointer elements in `range` loops (warning)
- `for _, v := range pointerSlice` where you take `&v` gives the same address each iteration.
- Store the element itself or use the index: `&pointerSlice[i]`.

## #33 — Map iteration assumptions
- Map iteration order is randomised by design in Go; never assume ordering.
- Inserting into a map during iteration may or may not be visited in that iteration — the spec does not guarantee it.

## #34 — `break` inside `switch`/`select` inside a loop
- `break` inside a `switch` or `select` breaks the `switch`/`select`, not the enclosing `for`.
- Use a labelled break (`break outer`) to exit the loop from inside a `switch`/`select`.

## #35 — `defer` inside a loop
- A deferred call runs when the *function* returns, not when the loop iteration ends.
- Accumulating defers in a long loop (e.g., opening files) holds all resources until the function exits.
- Wrap the loop body in an inner function: `func() { defer f.Close(); … }()`.
