# Deadlock Diagnosis

## Runtime Signal

Go's runtime prints `fatal error: all goroutines are asleep - deadlock!` and dumps all goroutine stacks. Read the stack to find which goroutine is blocked and on which channel or mutex.

## Common Causes (from chapter 11)

| Cause | Symptom | Fix |
|-------|---------|-----|
| Inconsistent lock order | Two goroutines each holding one lock and waiting for the other | Sort resources by stable key before locking |
| Receive on empty, never-closed channel | Goroutine blocked on `<-ch` forever | Ensure sender closes channel or sends a sentinel |
| `wg.Add` inside goroutine | `wg.Wait()` returns before goroutines start | Call `Add` before `go` statement |
| `cond.Wait()` never woken | Goroutine sleeps forever | Ensure producer calls `Signal`/`Broadcast` while holding the lock |
| Self-deadlock | Goroutine locks mutex it already holds | Use `sync.RWMutex` or restructure code to avoid re-entry |

## Lock-Order Discipline

When two goroutines must hold two mutexes simultaneously, **always acquire them in the same global order**:

```go
// Derive lock order from a stable identifier (e.g., account ID string)
sort.Slice(accounts, func(i, j int) bool {
    return accounts[i].id < accounts[j].id
})
accounts[0].mu.Lock()
accounts[1].mu.Lock()
defer accounts[1].mu.Unlock()
defer accounts[0].mu.Unlock()
```

## Detection Tools

```bash
# Runtime deadlock detection (automatic for simple cases)
go run ./...

# Race detector (catches data races that may mask deadlocks)
go test -race ./...

# Goroutine stack dump (attach to running process)
kill -SIGQUIT <pid>
# or via HTTP pprof:
curl http://localhost:6060/debug/pprof/goroutine?debug=2
```

## Arbitrator Pattern

When lock ordering cannot be enforced statically, introduce an arbitrator goroutine that serializes access:

```go
type Request struct {
    from, to *Account
    amount   int
    done     chan struct{}
}

func arbiter(requests <-chan Request) {
    for r := range requests {
        r.from.balance -= r.amount
        r.to.balance += r.amount
        close(r.done)
    }
}
```

All mutation goes through the arbiter channel, eliminating the need for direct mutex locking across goroutines.
