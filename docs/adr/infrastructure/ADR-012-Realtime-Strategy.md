# ADR-012: Realtime Strategy

**Status**: Proposed  
**Date**: 2025-12-27  
**Deciders**: James (Owner)  
**Technical Story**: Task/Sprint live updates

## Context and Problem Statement

TaskMan-v2 documentation mentions WebSocket support (`ws://localhost:8000/ws`) but no implementation exists. We need to decide on a realtime strategy for:
- Task status updates
- Sprint progress changes
- Multi-user collaboration (future)

## Decision Drivers

* **MVP Scope** - Minimize complexity for initial launch
* **User Experience** - Perceived responsiveness
* **Implementation Effort** - Single developer team
* **Infrastructure Cost** - Connection persistence costs
* **Scaling Complexity** - WebSocket vs stateless

## Considered Options

1. **Polling** - TanStack Query refetch intervals
2. **WebSocket** - FastAPI WebSocket endpoints
3. **Server-Sent Events (SSE)** - One-way push
4. **No Realtime** - Manual refresh only

## Decision Outcome

**Chosen option: Enhanced Polling for MVP**, because TanStack Query already supports this with zero additional infrastructure.

**Planned upgrade: SSE for v2** when multi-user collaboration becomes a priority.

### Positive Consequences

* Zero implementation effort (already using TanStack Query)
* No additional infrastructure
* Works with stateless hosting (Vercel, Railway)
* Predictable server load

### Negative Consequences

* 5-10 second delay for updates
* Wasted requests when no changes
* Not suitable for real-time collaboration

## Implementation

### Current (MVP): TanStack Query Polling
```typescript
// Already implemented - just tune intervals
const { data: tasks } = useQuery({
  queryKey: ['tasks'],
  queryFn: fetchTasks,
  staleTime: 10_000,     // 10 seconds
  refetchInterval: 30_000, // Poll every 30s when window focused
  refetchOnWindowFocus: true,
});
```

### Future (v2): SSE for Live Updates
```python
# backend-api/routers/events.py
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

@router.get("/events")
async def event_stream():
    async def generate():
        while True:
            event = await event_queue.get()
            yield {"event": event.type, "data": event.json()}
    return EventSourceResponse(generate())
```

## Decision Matrix

| Option | Effort | UX | Scale | Cost | Total |
|--------|--------|-----|-------|------|-------|
| Polling | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **4.5** |
| SSE | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **4.0** |
| WebSocket | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | **3.5** |

## Links

* [TanStack Query Polling](https://tanstack.com/query/latest/docs/react/guides/polling)
* [SSE-Starlette](https://github.com/sysid/sse-starlette)
* [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
