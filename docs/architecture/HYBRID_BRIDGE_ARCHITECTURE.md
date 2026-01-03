# TypeScript-Python Hybrid Bridge Architecture

## Overview

Bridge TaskMan-v2 TypeScript CLI with Python Rich console implementation for enhanced terminal UI while maintaining TypeScript performance benefits.

## Architecture Options (Ranked by Viability)

### 🥇 **Option 1: JSON Event Streaming (RECOMMENDED)**

**Flow**: `TypeScript CLI → JSON Events → Python Rich Renderer → Terminal`

```typescript
// TypeScript: Emit structured JSON events
interface RichEvent {
  type: 'status' | 'step' | 'warning' | 'error' | 'success' | 'table' | 'panel' | 'progress';
  data: {
    message?: string;
    title?: string;
    style?: string;
    rows?: any[];
    columns?: string[];
    value?: number;
    total?: number;
  };
  timestamp: string;
  correlation_id: string;
}

// TaskMan TypeScript: Emit events
console.log(JSON.stringify({
  type: 'status',
  data: { message: 'Loading projects...', style: 'info' },
  timestamp: new Date().toISOString(),
  correlation_id: 'QSE-20251003-2000-001'
}));
```

```python
# Python: Rich event consumer
import sys
import json
from rich.console import Console
from rich.status import Status
from rich.panel import Panel
from rich.table import Table

console = Console()

def process_rich_event(event: dict):
    """Process TypeScript JSON event and render with Rich"""
    event_type = event['type']
    data = event['data']

    match event_type:
        case 'status':
            with console.status(data['message'], spinner="dots12"):
                pass
        case 'panel':
            console.print(Panel(data['message'], title=data.get('title')))
        case 'table':
            table = Table(title=data.get('title'))
            for col in data['columns']:
                table.add_column(col)
            for row in data['rows']:
                table.add_row(*row)
            console.print(table)
        case 'error':
            console.print(Panel(data['message'], title="🚨 Error", border_style="red"))
        # ... etc

# Main loop: consume JSON events from TypeScript
for line in sys.stdin:
    try:
        event = json.loads(line)
        process_rich_event(event)
    except json.JSONDecodeError:
        console.print(f"[dim red]Invalid JSON: {line}[/dim red]")

```

**Usage**:
```bash
# Direct piping
node taskman.js project:list --json-events | python python/tools/rich_bridge.py

# Or wrapper script
./taskman-rich project:list
```

**Pros**:
- ✅ Zero TypeScript dependency changes
- ✅ Minimal performance overhead (~1-2ms)
- ✅ Full Rich UI capabilities
- ✅ Maintains TypeScript CLI independence
- ✅ Easy to debug (JSON is human-readable)
- ✅ Works with existing MCP infrastructure

**Cons**:
- ⚠️ Requires Python runtime available
- ⚠️ Slight latency for real-time updates

---

### 🥈 **Option 2: Child Process Spawning**

**Flow**: `TypeScript spawns Python → IPC via stdin/stdout → Rich rendering`

```typescript
// TypeScript: Spawn Python Rich renderer
import { spawn } from 'child_process';

class RichBridge {
  private pythonProcess: ChildProcess;

  constructor() {
    this.pythonProcess = spawn('python', [
      'python/tools/rich_bridge.py'
    ]);
  }

  emit(event: RichEvent): void {
    this.pythonProcess.stdin.write(JSON.stringify(event) + '\n');
  }

  close(): void {
    this.pythonProcess.stdin.end();
  }
}

// Usage in TaskMan commands
const rich = new RichBridge();
rich.emit({ type: 'status', data: { message: 'Loading...' } });
rich.close();
```

**Pros**:
- ✅ Seamless integration - TypeScript manages Python lifecycle
- ✅ Rich UI capabilities fully accessible
- ✅ Good for long-running operations

**Cons**:
- ⚠️ More complex error handling
- ⚠️ Python process overhead (~50-100ms startup)
- ⚠️ Need to manage process lifecycle

---

### 🥉 **Option 3: HTTP/WebSocket Bridge**

**Flow**: `TypeScript → HTTP POST → Python FastAPI → Rich SSE stream`

```python
# Python: FastAPI server with Rich rendering
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()
console = Console()

@app.post("/render")
async def render_event(event: dict):
    # Process and render with Rich
    process_rich_event(event)
    return {"status": "rendered"}

@app.get("/stream")
async def event_stream():
    async def generate():
        # Server-Sent Events for real-time updates
        while True:
            yield f"data: {json.dumps(await queue.get())}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

**Pros**:
- ✅ Language-agnostic protocol
- ✅ Supports remote rendering
- ✅ Web UI possible

**Cons**:
- ⚠️ Significant overhead (HTTP server required)
- ⚠️ Overkill for local CLI
- ⚠️ Complex deployment

---

## 🎯 **Recommended Implementation: JSON Stream Bridge**

### Phase 1: Basic Bridge (1-2 hours)

1. **TypeScript: Add JSON event emitter**
```typescript
// TaskMan-v2/cli/lib/utils/rich-bridge.ts
export interface RichEvent {
  type: 'status' | 'step' | 'panel' | 'table' | 'progress' | 'error' | 'warning' | 'success';
  data: Record<string, any>;
  timestamp: string;
  correlation_id: string;
}

export class RichBridge {
  constructor(private enabled: boolean = process.env.RICH_BRIDGE === 'true') {}

  emit(type: string, data: Record<string, any>): void {
    if (!this.enabled) return;

    const event: RichEvent = {
      type,
      data,
      timestamp: new Date().toISOString(),
      correlation_id: process.env.QSE_CORRELATION_ID || 'default'
    };

    console.log(JSON.stringify(event));
  }
}
```

2. **Python: Rich event consumer**
```python
# python/tools/rich_bridge.py
#!/usr/bin/env python3
"""
TypeScript-Python Rich Bridge
Consumes JSON events from TypeScript and renders with Rich console
"""
import sys
import json
from typing import Dict, Any
from rich.console import Console
from rich.status import Status
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

def render_status(data: Dict[str, Any]):
    """Render status with animated spinner"""
    status_text = data.get('message', '')
    console.status(status_text, spinner="dots12")

def render_panel(data: Dict[str, Any]):
    """Render panel with title and styling"""
    message = data.get('message', '')
    title = data.get('title', '')
    style = data.get('style', 'blue')
    console.print(Panel(message, title=title, border_style=style))

def render_table(data: Dict[str, Any]):
    """Render Rich table"""
    table = Table(title=data.get('title', ''))

    for col in data.get('columns', []):
        table.add_column(col.get('name', ''), style=col.get('style', 'cyan'))

    for row in data.get('rows', []):
        table.add_row(*row)

    console.print(table)

def render_error(data: Dict[str, Any]):
    """Render error panel with dramatic styling"""
    console.print(Panel(
        data.get('message', 'Unknown error'),
        title="🚨 Error",
        border_style="red",
        padding=(1, 2)
    ))

def render_success(data: Dict[str, Any]):
    """Render success panel with celebration"""
    console.print(Panel(
        data.get('message', 'Success!'),
        title="🎉 Success",
        border_style="green",
        padding=(1, 2)
    ))

RENDERERS = {
    'status': render_status,
    'panel': render_panel,
    'table': render_table,
    'error': render_error,
    'success': render_success,
}

def process_event(event: Dict[str, Any]):
    """Process single TypeScript event and render"""
    event_type = event.get('type')
    data = event.get('data', {})

    renderer = RENDERERS.get(event_type)
    if renderer:
        renderer(data)
    else:
        console.print(f"[dim yellow]Unknown event type: {event_type}[/dim yellow]")

def main():
    """Main event loop - consume JSON from stdin"""
    console.print("[dim cyan]Rich Bridge: Listening for TypeScript events...[/dim cyan]")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            event = json.loads(line)
            process_event(event)
        except json.JSONDecodeError as e:
            console.print(f"[dim red]Invalid JSON: {line[:50]}... Error: {e}[/dim red]")
        except Exception as e:
            console.print(f"[bold red]Error processing event: {e}[/bold red]")

if __name__ == "__main__":
    main()
```

3. **Wrapper Script**
```bash
#!/usr/bin/env bash
# taskman-rich - TaskMan with Python Rich UI

export RICH_BRIDGE=true
export QSE_CORRELATION_ID="QSE-$(date +%Y%m%d-%H%M)-001"

cd "$(dirname "$0")/TaskMan-v2/cli"
node bin/run.js "$@" | python ../../python/tools/rich_bridge.py
```

### Phase 2: Enhanced Integration (2-4 hours)

- **Progress bars**: TypeScript emits progress events, Python renders multi-phase progress
- **Live tables**: Real-time table updates during long operations
- **Error recovery**: Python handles TypeScript crashes gracefully
- **Performance metrics**: Track bridge overhead

### Phase 3: Production Hardening (4-6 hours)

- **Buffering**: Handle burst events efficiently
- **Error handling**: Comprehensive error recovery
- **Logging**: Structured logging for bridge operations
- **Testing**: E2E tests for TypeScript-Python coordination

---

## Performance Analysis

| Approach | Overhead | Complexity | Rich Capabilities | Deployment |
|----------|----------|------------|------------------|------------|
| JSON Stream | 1-2ms | Low | Full | Simple |
| Child Process | 50-100ms startup | Medium | Full | Medium |
| HTTP Bridge | 10-50ms per request | High | Full | Complex |

**Recommendation**: Start with **JSON Stream Bridge** for 95% of use cases.

---

## Migration Strategy

### Week 1: Proof of Concept
- ✅ Implement basic JSON event emitter in TypeScript
- ✅ Implement basic Rich consumer in Python
- ✅ Test with `project:list` command
- ✅ Validate performance overhead

### Week 2: Full Integration
- ✅ Migrate all TaskMan commands to emit JSON events
- ✅ Implement all Rich renderers (status, panel, table, progress)
- ✅ Add wrapper scripts for seamless UX
- ✅ E2E testing

### Week 3: Production Polish
- ✅ Error handling and recovery
- ✅ Performance optimization
- ✅ Documentation and examples
- ✅ Production deployment

---

## ContextForge Alignment

✅ **Best Tool for Context**: TypeScript for CLI logic, Python for Rich UI rendering
✅ **Workspace First**: Leverages existing Python Rich infrastructure
✅ **Logs First**: JSON events create structured audit trail
✅ **Leave Better**: Reusable pattern for other TypeScript tools
✅ **Iteration Sacred**: Incremental implementation with validation gates

---

## Next Steps

1. **Validate concept**: Quick prototype with `project:list` command
2. **Performance baseline**: Measure overhead with 100+ events
3. **Full implementation**: Migrate all commands to hybrid architecture
4. **Production deployment**: Package as unified TaskMan-Rich CLI

Would you like me to implement the proof of concept now?
