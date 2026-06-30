---
name: go-concurrent-programming
description: "Applies Go concurrency patterns from the book 'Concurrent Programming with Go' by James Cutajar. Use when implementing or reviewing goroutines, mutexes, condition variables, semaphores, WaitGroups, barriers, channels, select, pipelines (fan-in/fan-out/broadcast), deadlock avoidance, and atomic operations in Go. Includes the quit-channel idiom, lock-ordering discipline, and channel-pipeline composition. Don't use for general Go syntax help, non-concurrent code review, testing infrastructure, or deployment configuration."
---

# Concurrent Programming with Go — Patterns & Best Practices

Based on the book *Concurrent Programming with Go* by James Cutajar. Covers patterns from goroutine basics through atomic operations, organized by the discipline they enforce.

## Core Disciplines

1. **Protect shared state** — every mutable variable accessed from multiple goroutines needs a guard (mutex, channel ownership, or atomic)
2. **Signal state changes** — use `sync.Cond`, channels, or atomics to notify waiting goroutines; never busy-poll
3. **Always provide an exit** — every goroutine must have a termination path (quit channel, channel close, or `context.Context`)
4. **Lock in consistent order** — when locking multiple mutexes, always acquire them in the same deterministic order to prevent deadlock
5. **Owner closes the channel** — only the sending side closes; a receiver closing causes panic on subsequent sends

---

## Step 1 — Identify the Concurrency Problem

Classify before coding:

| Problem | Primitive |
|---------|-----------|
| Unprotected shared variable | `sync.Mutex` / `sync.RWMutex` / `sync/atomic` |
| Goroutine must wait for a condition | `sync.Cond` |
| Limit concurrent access count | Channel-based semaphore |
| Wait for N goroutines to finish | `sync.WaitGroup` |
| Synchronize goroutines at a checkpoint | Barrier (`sync.Cond` + counter) |
| Pass data between goroutines | Unbuffered channel |
| Pipeline of processing stages | Chained goroutines with channels |
| Merge multiple channels | Fan-in (`sync.WaitGroup` + output channel) |
| Replicate one channel to N | Broadcast (goroutine per subscriber) |
| Cancel / stop goroutines | Quit channel (`chan struct{}`) |
| Simple counter / flag | `sync/atomic` typed ops |
| Custom spin lock | `atomic.CompareAndSwapInt32` + `runtime.Gosched()` |
| Fixed-size concurrent workers | Worker pool (shared input channel + N goroutines) |

---

## Step 2 — Apply the Right Pattern

### Race-condition-free shared state

Always use `defer mutex.Unlock()` to guarantee release even on early return:

```go
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}
```

For read-heavy data, prefer `sync.RWMutex`:

```go
func (c *SafeCounter) Value() int {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.count
}
```

### Condition variables — wait for a condition

Always loop on `Wait()` to guard against spurious wakeups.  
Use `Signal()` to wake one waiter; `Broadcast()` to wake all:

```go
cond := sync.NewCond(&sync.Mutex{})

// Writer
cond.L.Lock()
value += 10
cond.Signal()   // or cond.Broadcast()
cond.L.Unlock()

// Reader — always loop, never if
cond.L.Lock()
for value < threshold {
    cond.Wait()
}
// use value
cond.L.Unlock()
```

> **Anti-pattern:** calling `Signal()` before the reader calls `Wait()` loses the notification. Ensure the producer holds the lock when signalling, or use a flag the reader checks in its loop condition.

### Channel-based semaphore

```go
sem := make(chan struct{}, maxConcurrent)

sem <- struct{}{}   // acquire
defer func() { <-sem }()  // release
```

### WaitGroup — wait for goroutines to complete

Call `Add` **before** launching the goroutine; never inside it:

```go
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(v Item) {
        defer wg.Done()
        process(v)
    }(item)
}
wg.Wait()
```

### Barrier — synchronize goroutines at a checkpoint

Read `references/barrier-pattern.md` for the full implementation.

```go
barrier := NewBarrier(nGoroutines)
// each goroutine calls barrier.Wait() — all block until all have arrived
```

### Quit channel — graceful goroutine cancellation

Use a dedicated quit channel. Close it to broadcast stop to all goroutines:

```go
quit := make(chan struct{})
defer close(quit)

go func() {
    for {
        select {
        case data := <-input:
            process(data)
        case <-quit:
            return
        }
    }
}()
```

> Closing the quit channel (rather than sending a value) signals **all** goroutines simultaneously.

### Pipeline pattern

Each stage returns a receive-only channel. The stage goroutine closes it when done:

```go
func stage(quit <-chan struct{}, in <-chan T) <-chan U {
    out := make(chan U)
    go func() {
        defer close(out)
        for v := range in {
            select {
            case out <- transform(v):
            case <-quit:
                return
            }
        }
    }()
    return out
}
```

Compose stages:

```go
quit := make(chan struct{})
defer close(quit)
results := stageC(quit, stageB(quit, stageA(quit)))
```

### Fan-in — merge N channels into one

Read `references/fan-in-pattern.md` for the full generic implementation.

```go
func FanIn[K any](quit <-chan struct{}, channels ...<-chan K) <-chan K {
    out := make(chan K)
    var wg sync.WaitGroup
    wg.Add(len(channels))
    for _, ch := range channels {
        go func(c <-chan K) {
            defer wg.Done()
            for v := range c {
                select {
                case out <- v:
                case <-quit:
                    return
                }
            }
        }(ch)
    }
    go func() { wg.Wait(); close(out) }()
    return out
}
```

### Broadcast — replicate one channel to N subscribers

```go
func Broadcast[K any](quit <-chan struct{}, in <-chan K, n int) []<-chan K {
    outs := make([]chan K, n)
    for i := range outs {
        outs[i] = make(chan K)
    }
    go func() {
        defer func() {
            for _, o := range outs { close(o) }
        }()
        for v := range in {
            for _, o := range outs {
                select {
                case o <- v:
                case <-quit:
                    return
                }
            }
        }
    }()
    result := make([]<-chan K, n)
    for i, o := range outs { result[i] = o }
    return result
}
```

### Worker pool — bounded concurrent processing

N goroutines share a single input channel. The pool limits concurrency without spawning unbounded goroutines:

```go
func StartWorkers(n int, jobs <-chan Job) {
    for i := 0; i < n; i++ {
        go func() {
            for job := range jobs {
                process(job)
            }
        }()
    }
}

// Usage
jobs := make(chan Job)
StartWorkers(10, jobs)

// Feed work — workers pick up jobs as they become free
for _, j := range workItems {
    jobs <- j
}
close(jobs) // signals all workers to exit after draining
```

**With quit channel** (when you need early cancellation):

```go
func StartWorkers(n int, quit <-chan struct{}, jobs <-chan Job) {
    for i := 0; i < n; i++ {
        go func() {
            for {
                select {
                case job, ok := <-jobs:
                    if !ok {
                        return
                    }
                    process(job)
                case <-quit:
                    return
                }
            }
        }()
    }
}
```

**With results collection** (scatter-gather):

```go
func StartWorkers(n int, jobs <-chan Job) <-chan Result {
    results := make(chan Result)
    var wg sync.WaitGroup
    wg.Add(n)
    for i := 0; i < n; i++ {
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- process(job)
            }
        }()
    }
    go func() { wg.Wait(); close(results) }()
    return results
}
```

> **Sizing the pool:** start with `runtime.NumCPU()` for CPU-bound work; for I/O-bound work (HTTP, disk) use a higher number measured by benchmarking.

### Deadlock avoidance — consistent lock ordering

When locking multiple mutexes simultaneously, sort them by a stable key before acquiring:

```go
func Transfer(src, dst *Account, amount int) {
    accounts := []*Account{src, dst}
    sort.Slice(accounts, func(i, j int) bool {
        return accounts[i].id < accounts[j].id
    })
    accounts[0].mu.Lock()
    accounts[1].mu.Lock()
    defer accounts[1].mu.Unlock()
    defer accounts[0].mu.Unlock()
    // perform transfer
}
```

> Never lock in call-site order — callers may reverse the argument order, creating a circular wait.

### Atomic operations

Prefer typed atomics (Go 1.19+) over raw `sync/atomic` functions:

```go
var counter atomic.Int64
counter.Add(1)
val := counter.Load()
```

Use Compare-And-Swap (CAS) for lock-free updates:

```go
for {
    old := atomic.LoadInt32(&state)
    if atomic.CompareAndSwapInt32(&state, old, newVal) {
        break
    }
    runtime.Gosched() // yield to avoid starvation
}
```

---

## Step 3 — Validate Before Committing

Run these checks before marking concurrent code as done:

```bash
# Detect data races
go test -race ./...

# Vet for common issues
go vet ./...

# Static analysis (if golangci-lint available)
golangci-lint run --enable=gocritic,revive ./...
```

**Manual checklist:**

- [ ] Every goroutine has a clear exit path (quit channel or channel close)
- [ ] `wg.Add(n)` is called before the goroutine launch, not inside it
- [ ] `sync.Cond.Wait()` is inside a `for` loop, not an `if`
- [ ] `Broadcast()` used (not `Signal()`) when multiple goroutines wait on the same condition
- [ ] Channels closed only by the sender
- [ ] Multiple mutexes always acquired in the same sorted order
- [ ] No shared pointer sent over a channel (send a copy or use immutable data)
- [ ] Semaphore `release` is deferred immediately after `acquire`
- [ ] Worker pool size is explicit and justified (`NumCPU()` for CPU-bound, benchmarked for I/O-bound)
- [ ] `close(jobs)` is called after all work is submitted so workers exit cleanly

---

## Error Handling

- If `-race` reports a data race, identify the unsynchronized variable and wrap access with a mutex or convert to channel ownership.
- If a deadlock is detected at runtime (`all goroutines are asleep`), read `references/deadlock-diagnosis.md` for diagnostic steps.
- If a condition variable is missed (goroutine never wakes), verify the producer calls `Signal`/`Broadcast` **while holding the lock**, and the consumer loop condition is re-checked after `Wait`.
- If goroutines are leaking, confirm every goroutine has a `case <-quit` branch in its `select` and that `quit` is eventually closed.
