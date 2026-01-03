---
applyTo: "**/*.go,**/go.mod,**/go.sum"
description: "Go coding standards and patterns"
---

# Go Quick Reference

## Project Structure

```
project/
├── cmd/app/main.go    # Entry points
├── internal/          # Private packages
├── pkg/               # Public packages
├── go.mod             # Dependencies
└── go.sum             # Checksums
```

## Error Handling

```go
result, err := doSomething()
if err != nil {
    return fmt.Errorf("context: %w", err)
}
```

## Interfaces

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}
```

## Goroutines & Channels

```go
ch := make(chan int)
go func() {
    ch <- 42
}()
result := <-ch
```

## Testing

```go
func TestAdd(t *testing.T) {
    got := Add(2, 2)
    want := 4
    if got != want {
        t.Errorf("got %d, want %d", got, want)
    }
}
```

## Best Practices
- Accept interfaces, return structs
- Keep functions short (<30 lines)
- Use `context.Context` for cancellation
- `go fmt` before commit

## Full Reference
See `.github/instructions/archive/go-full.md`
