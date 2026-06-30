# Fan-In Pattern

Merges N input channels into a single output channel. Each input is drained by a dedicated goroutine; a WaitGroup closes the output after all inputs are exhausted.

## Generic Implementation (from chapter 9)

```go
func FanIn[K any](quit <-chan struct{}, channels ...<-chan K) <-chan K {
    var wg sync.WaitGroup
    wg.Add(len(channels))
    output := make(chan K)

    for _, ch := range channels {
        go func(c <-chan K) {
            defer wg.Done()
            for v := range c {
                select {
                case output <- v:
                case <-quit:
                    return
                }
            }
        }(ch)
    }

    go func() {
        wg.Wait()
        close(output) // safe: only this goroutine closes output
    }()

    return output
}
```

## Usage

```go
quit := make(chan struct{})
defer close(quit)

ch1 := producer1(quit)
ch2 := producer2(quit)
ch3 := producer3(quit)

for result := range FanIn(quit, ch1, ch2, ch3) {
    fmt.Println(result)
}
```

## Key Rules

- Pass each loop variable as a function argument to avoid closure capture bugs.
- The `wg.Wait()` goroutine is the only closer of `output` — receiver-side closing causes panic.
- Always include `case <-quit` in the send select to prevent goroutine leaks on early exit.
- Order of results is non-deterministic (whichever producer is fastest wins).
