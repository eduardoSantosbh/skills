# Concurrency: Foundations (#55–60) and Practice (#61–74)

---

## Foundations

### #55 — Mixing up concurrency and parallelism
- **Concurrency**: structuring a program as independently executing components (design).
- **Parallelism**: executing multiple computations simultaneously on multiple CPUs (execution).
- A concurrent program may or may not run in parallel; goroutines are concurrent by definition.

### #56 — Thinking concurrency is always faster
- Goroutine and channel overhead (scheduling, synchronisation, cache misses) can make a concurrent solution *slower* than a sequential one for small or CPU-bound tasks.
- Profile before parallelising; use `-race` and benchmarks to justify the decision.

### #57 — Channels vs. mutexes
- Use **channels** when transferring ownership of data or coordinating goroutine lifecycle.
- Use **mutexes** when protecting shared state accessed by multiple goroutines concurrently.
- Mixing both without a clear boundary leads to deadlocks and races.

### #58 — Race problems
- **Data race**: two goroutines access the same memory location concurrently and at least one writes, without synchronisation. Undefined behaviour even if it "works."
- **Race condition**: a logic bug where the correctness depends on the relative order of events.
- Always run tests with `go test -race`; the race detector catches data races at runtime.

### #59 — Workload type and concurrency
- **CPU-bound**: parallelism helps; use `GOMAXPROCS` workers.
- **I/O-bound**: concurrency helps even on one CPU; goroutines block on I/O, not the scheduler.
- **Mixed**: profile to determine the bottleneck before choosing strategy.

### #60 — Misunderstanding Go contexts
- `context.Context` propagates cancellation, deadlines, and request-scoped values.
- Pass `ctx` as the first parameter to every function that does I/O or blocks.
- Never store a context in a struct (except request-scoped types like `http.Request`).
- Check `ctx.Err()` or `<-ctx.Done()` inside long loops to respect cancellation.

---

## Practice

### #61 — Propagating an inappropriate context
- Do not pass a request context to background work that should outlive the request.
- Detach with `context.WithoutCancel` (Go 1.21+) or start fresh from `context.Background()`.

### #62 — Starting a goroutine without knowing when to stop it
- Every goroutine must have an explicit termination condition: context cancellation, channel close, or `sync.WaitGroup`.
- Goroutine leaks are memory leaks; use `goleak` in tests.

### #63 — Goroutines and loop variables (warning)
- In Go < 1.22, `for i, v := range …` captures `i` and `v` by reference in closures; by the time the goroutine runs, `i` may have changed.
- Fix: copy the variable before the goroutine: `v := v` or pass as an argument.
- Go 1.22+ changes loop-variable semantics; new code can rely on per-iteration variables.

### #64 — Deterministic behavior with `select` and channels
- When multiple `case` clauses are ready in a `select`, Go chooses one *uniformly at random*.
- Never write code that relies on a specific case being selected when multiple are ready.

### #65 — Not using notification channels
- To signal an event without sending data, use `chan struct{}`.
- Close the channel to broadcast to all receivers; send a value for point-to-point.

### #66 — Not using nil channels
- Receiving from or sending to a `nil` channel blocks forever (select skips the case).
- Use nil channels to *disable* a case in a `select` dynamically.

### #67 — Channel size
- Unbuffered channel (`make(chan T)`): synchronous rendezvous; both sender and receiver must be ready.
- Buffered channel (`make(chan T, n)`): sender blocks only when full; choose `n` based on measured throughput, not guessing.
- Unbounded queues hide back-pressure problems; buffered channels of size 1 are common for rate-limiting.

### #68 — Side effects with string formatting
- `fmt.Sprintf` and `log` calls with an interface argument may call the argument's methods (e.g., `String()`) unexpectedly, causing data races if the method accesses shared mutable state.
- Ensure stringer methods are concurrency-safe.

### #69 — Data races with `append`
- Concurrent `append` calls on the same slice are a data race even if different elements are appended.
- Protect with a mutex, or use separate slices that are merged afterwards.

### #70 — Mutex with slices and maps
- A `sync.Mutex` protecting a slice/map must guard *all* reads and writes, including ranging.
- A `sync.RWMutex` is safe only when readers never modify the data structure.

### #71 — Misusing `sync.WaitGroup`
- Call `wg.Add(n)` *before* launching goroutines, not inside them.
- Calling `Add` inside a goroutine races with `wg.Wait()`.

### #72 — Forgetting `sync.Cond`
- `sync.Cond` is the right primitive when goroutines must wait for a *condition* on shared state, not just for a channel signal.
- `Broadcast` wakes all waiters; `Signal` wakes one. Always call under the lock.

### #73 — Not using `errgroup`
- `golang.org/x/sync/errgroup` manages a group of goroutines, collects the first error, and cancels the context.
- Prefer it over manual `WaitGroup` + error channel patterns.

### #74 — Copying a `sync` type
- `sync.Mutex`, `sync.RWMutex`, `sync.WaitGroup`, `sync.Cond`, `sync.Once` must never be copied after first use.
- Pass by pointer or embed in a struct that is always passed by pointer.
- `go vet` detects copies of lock values.
