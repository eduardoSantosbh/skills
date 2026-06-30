# Barrier Pattern

A barrier blocks all goroutines until every participant has arrived at the checkpoint, then releases them all simultaneously.

## Implementation (from chapter 6)

```go
package sync_extras

import "sync"

type Barrier struct {
    size      int
    waitCount int
    cond      *sync.Cond
}

func NewBarrier(size int) *Barrier {
    return &Barrier{
        size: size,
        cond: sync.NewCond(&sync.Mutex{}),
    }
}

func (b *Barrier) Wait() {
    b.cond.L.Lock()
    b.waitCount++
    if b.waitCount == b.size {
        b.waitCount = 0
        b.cond.Broadcast() // release all waiting goroutines
    } else {
        b.cond.Wait() // block until broadcast
    }
    b.cond.L.Unlock()
}
```

## Usage

```go
barrier := NewBarrier(nWorkers)
for i := 0; i < nWorkers; i++ {
    go func(id int) {
        phase1(id)
        barrier.Wait() // all goroutines sync here before phase 2
        phase2(id)
    }(i)
}
```

## Key Rules

- `size` must equal the exact number of goroutines that will call `Wait()`.
- `Broadcast()` is mandatory (not `Signal()`) — all waiters must be released.
- `waitCount` is reset to 0 so the barrier is reusable across multiple phases.
- Never call `Wait()` from more goroutines than `size` — the extras will block forever.
