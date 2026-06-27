# Data Types — Mistakes #17–29

## #17 — Octal literals
- `0666` is octal (438 decimal). Confusing octal with decimal is a silent bug.
- Prefer `0o666` (Go 1.13+) for clarity; never use bare leading-zero integers except in tests where the literal is documented.

## #18 — Integer overflows
- `int` is architecture-width (32 or 64-bit). Arithmetic on `int32`/`int64` can overflow without panic.
- Use `math.MaxInt32`, `math.MinInt32` checks; for currency/counters prefer `int64` explicitly.

## #19 — Floating-point precision
- `float64` is not decimal. Comparing floats with `==` is almost always wrong.
- Use an epsilon comparison: `math.Abs(a-b) < epsilon`.
- For financial calculations use `big.Rat` or a fixed-point integer type.

## #20 — Slice length vs. capacity
- `len` = number of elements; `cap` = allocated backing array space.
- Accessing beyond `len` panics; accessing beyond `cap` causes a new allocation on append.
- `s[low:high:max]` three-index slice limits capacity shared with the original.

## #21 — Inefficient slice initialisation
- Pre-allocate with `make([]T, 0, n)` when the final size is known to avoid repeated doublings.
- `make([]T, n)` creates n zero-value elements; use only when all elements will be overwritten.

## #22 — nil vs. empty slice
- `var s []T` is nil; `s := []T{}` is non-nil but empty. Both have `len == 0`.
- `json.Marshal` of a nil slice produces `null`; of an empty slice produces `[]`.
- Prefer `nil` slices as the zero value for "no data"; return `nil` from functions that find nothing.

## #23 — Checking slice emptiness
- Use `len(s) == 0`, not `s == nil`. A non-nil empty slice would pass a nil check incorrectly.

## #24 — Copying slices
- `copy(dst, src)` copies `min(len(dst), len(src))` elements; the destination must be pre-allocated.
- `append([]T{}, src...)` is a one-liner but allocates; prefer `copy` for large slices.

## #25 — Unexpected side effects with `append`
- If two slices share a backing array (from reslicing), `append` to one may silently overwrite the other if capacity allows.
- Use three-index slice `s[a:b:b]` to give the sub-slice its own capacity.

## #26 — Slices and memory leaks
- A sub-slice retains a reference to the entire backing array; the GC cannot collect elements outside the sub-slice.
- Copy the relevant elements into a new slice to release the original array.
- Same applies to slice-of-pointers: nil out the pointer beyond the new length before shrinking.

## #27 — Inefficient map initialisation
- `make(map[K]V, hint)` pre-sizes the map's hash table; omitting the hint causes repeated rehashing.
- Provide a size hint whenever the approximate count is known.

## #28 — Maps and memory leaks
- Maps never shrink after deletions; memory is retained even when all keys are deleted.
- For high-churn maps, periodically rebuild the map or use a value type of fixed size.
- Storing large values as pointers allows the GC to collect them individually.

## #29 — Comparing values incorrectly
- Structs containing slices, maps, or functions are not comparable with `==`; use `reflect.DeepEqual` or a custom comparator.
- For `time.Time`, use `t.Equal(u)` not `t == u` (different monotonic readings).
