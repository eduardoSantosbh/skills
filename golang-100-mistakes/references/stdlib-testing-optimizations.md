# Standard Library (#75–81), Testing (#82–90), Optimizations (#91–100)

---

## Standard Library

### #75 — Wrong time duration
- `time.Duration` is in nanoseconds. `time.Sleep(1000)` sleeps 1 microsecond, not 1 second.
- Always use constants: `time.Sleep(1 * time.Second)`, `time.After(500 * time.Millisecond)`.

### #76 — `time.After` and memory leaks
- `time.After(d)` creates a channel and a `time.Timer` that is NOT garbage-collected until it fires.
- In tight loops, use `time.NewTimer(d)` and `defer t.Stop()` instead.

### #77 — JSON handling
- `json.Unmarshal` into an existing struct *merges* rather than replacing; zero the struct first if needed.
- Embedded struct fields are promoted to the parent in JSON; unexported fields are ignored.
- Use `json:",omitempty"` carefully—it omits zero values, including valid `0`, `false`, `""`.
- Custom `MarshalJSON`/`UnmarshalJSON` must call `json.Marshal` on an alias type to avoid infinite recursion.

### #78 — Common SQL mistakes
- Always close `*sql.Rows` with `defer rows.Close()`; forgetting leaks a database connection.
- Use `db.QueryContext` (not `db.Query`) to pass cancellation context.
- Never build SQL strings with `fmt.Sprintf` and user input — use parameterised queries (`?` / `$1`).
- `db.Exec` with `INSERT … ON CONFLICT` is idiomatic; `Query` is for result sets only.

### #79 — Not closing transient resources
- `http.Response.Body` must always be closed even if unread.
- `sql.Rows` must be closed after iteration.
- `os.File` must be closed; defer close and check the error (see #54).
- Unclosed resources cause goroutine leaks, descriptor exhaustion, and connection pool starvation.

### #80 — Missing return after HTTP reply
- After `http.Error(w, …)` or `json.NewEncoder(w).Encode(…)`, the handler continues unless there is an explicit `return`.
- Always `return` immediately after sending an error response.

### #81 — Default HTTP client and server
- `http.DefaultClient` has no timeouts; a slow server can block a goroutine indefinitely.
- `http.ListenAndServe` has no timeouts; slow clients can exhaust file descriptors.
- Configure explicit `ReadTimeout`, `WriteTimeout`, `IdleTimeout` on `http.Server`.
- Set `Timeout` on `http.Client`; use `http.NewRequestWithContext` to pass per-request context.

---

## Testing

### #82 — Not categorising tests
- Use build tags (`//go:build integration`) or `testing.Short()` to separate unit, integration, and E2E tests.
- CI should run short tests on every commit and integration tests on a schedule or before release.

### #83 — Not enabling the race flag
- Run `go test -race ./…` in CI. The race detector has ~10× overhead but catches real bugs.
- Fix every race; never suppress with `//go:build !race`.

### #84 — Not using parallel and shuffle
- `t.Parallel()` inside a test runs it concurrently with other parallel tests; faster and exposes ordering assumptions.
- `go test -shuffle=on` randomises test execution order; catches tests that depend on global state.

### #85 — Not using table-driven tests
- Repeated test cases with different inputs belong in a slice of structs iterated with `t.Run`.
- Each sub-test is individually nameable, runnable, and parallelisable.

### #86 — Sleeping in unit tests
- `time.Sleep` in tests is flaky: too short and CI fails; too long and the suite is slow.
- Use channels, `sync.WaitGroup`, or inject a clock interface for time-dependent code.

### #87 — Time API in tests
- Inject time via an interface (`type Clock interface { Now() time.Time }`) so tests can control it.
- Alternatively, use `github.com/benbjohnson/clock`.

### #88 — Not using `httptest` and `iotest`
- `net/http/httptest.NewRecorder()` tests HTTP handlers without a real server.
- `net/http/httptest.NewServer()` creates a real but ephemeral test server.
- `testing/iotest.ErrReader` and `iotest.OneByteReader` test error paths in `io.Reader` consumers.

### #89 — Inaccurate benchmarks
- Benchmarks must consume the result to prevent the compiler from eliminating the computation: `result = f()` where `result` is a package-level variable.
- Use `b.ResetTimer()` after setup; use `b.StopTimer()`/`b.StartTimer()` around expensive setup inside the loop.
- Run with `go test -bench=. -benchmem -count=5` and use `benchstat` to compare.

### #90 — Not exploring Go testing features
- `t.Cleanup(func())` registers teardown that runs even if the test panics.
- `t.TempDir()` creates a temp dir cleaned up automatically.
- `testdata/` directory is the conventional place for fixture files.
- Fuzz testing (`func FuzzX(f *testing.F)`) discovers edge cases automatically.

---

## Optimizations

### #91 — Not understanding CPU caches
- Accessing memory sequentially (cache-friendly) is orders of magnitude faster than random access.
- Prefer `[]Struct` over `[]*Struct`; prefer arrays of scalars over arrays of pointers.

### #92 — False sharing
- Two goroutines writing to adjacent variables that share a cache line (typically 64 bytes) cause cache invalidation overhead even with no logical sharing.
- Pad hot variables to 64 bytes or use `//go:linkname`/`atomic` with explicit padding structs.

### #93 — Instruction-level parallelism
- Modern CPUs execute multiple instructions per cycle when there are no data dependencies.
- Long dependency chains (e.g., sequential accumulation in one variable) prevent ILP; use multiple accumulators.

### #94 — Data alignment
- Structs with fields in decreasing size order minimise padding.
- `unsafe.Alignof` shows the alignment requirement; `unsafe.Sizeof` shows total size including padding.
- Use `go vet -fieldalignment` (`golang.org/x/tools/go/analysis/passes/fieldalignment`) to detect waste.

### #95 — Stack vs. heap
- Variables that do not *escape* are allocated on the stack (cheap, no GC pressure).
- Variables passed by pointer, stored in interfaces, or returned from functions may escape to the heap.
- `go build -gcflags="-m"` prints escape analysis decisions.

### #96 — Reducing allocations
- Return values instead of pointers when the value is small and not shared.
- Use `sync.Pool` to reuse short-lived objects (e.g., `bytes.Buffer`).
- Pre-allocate slices and maps (see #21, #27).
- Accept `io.Writer` instead of returning `[]byte` to avoid intermediate allocations.

### #97 — Not relying on inlining
- Small functions (< ~80 AST nodes) are inlined by the compiler, eliminating call overhead.
- Avoid unnecessary `defer` in hot paths (pre-Go 1.14 they prevented inlining; later versions are better).
- `//go:noinline` prevents inlining; use sparingly and only for benchmarking.

### #98 — Not using Go diagnostics tooling
- `go tool pprof` for CPU and memory profiling.
- `go tool trace` for goroutine scheduling, GC events, and latency.
- `GODEBUG=gctrace=1` prints GC statistics.
- `go test -cpuprofile=cpu.out -memprofile=mem.out` integrates profiling into tests.

### #99 — Not understanding the GC
- Go uses a concurrent tri-color mark-sweep GC; STW pauses are short but not zero.
- Reducing allocation rate (see #96) reduces GC frequency.
- `GOGC` (default 100) controls heap growth ratio before a collection; lower = more GC, less memory.
- `runtime.SetMemoryLimit` (Go 1.19+) caps total memory usage.

### #100 — Running Go in Docker/Kubernetes (warning)
- By default, `GOMAXPROCS` is set to the number of host CPUs, not the container's CPU quota.
- Use `go.uber.org/automaxprocs` to automatically set `GOMAXPROCS` to the container's allowed CPU quota.
- The GC uses host memory metrics, not the container's memory limit; set `GOMEMLIMIT` accordingly.
