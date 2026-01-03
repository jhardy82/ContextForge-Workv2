# UniversalLogger Centralized Architecture Design

**Date:** September 18, 2025
**Status:** Design Phase
**Purpose:** Centralize all logging implementations through UniversalLogger with Loguru backend

## Executive Summary

Transform UniversalLogger from a single structured logging interface into a centralized
logging registry that manages multiple specialized logging providers (Enhanced Console,
DBCli, Test Harness, etc.) through a unified Loguru backend. This consolidates the 6
distributed logging patterns found across the project while maintaining backward compatibility.## Current State Analysis

### Distributed Logging Patterns Identified

1. **UnifiedLogger** (`src/unified_logger.py`)
   - **Purpose:** Authoritative JSONL structured logging
   - **Backend:** structlog with dual-write mode
   - **Features:** Rotation, redaction, OTEL integration, environment controls
   - **API:** `ulog(action, target, result, severity, **fields)`

2. **Enhanced Console** (`python/terminal/enhanced_console.py`)
   - **Purpose:** Rich-formatted terminal output with session logging
   - **Backend:** Rich Console + custom session logs
   - **Features:** Success/error/warning/info functions, session tracking
   - **API:** `success(msg)`, `error(msg)`, `warning(msg)`, `info(msg)`

3. **DBCli Hybrid** (`dbcli.py`)
   - **Purpose:** CLI-specific logging with dual output
   - **Backend:** Enhanced Console + UnifiedLogger
   - **Features:** Environment-driven Rich configuration, session logs
   - **API:** Combination of both above patterns

4. **Test Logging** (`tests/conftest.py`)
   - **Purpose:** Test execution logging with pytest integration
   - **Backend:** Loguru with multiple sinks
   - **Features:** Console + file + JSONL output, rotation, pytest capture
   - **API:** Standard loguru logger methods

5. **Legacy Structured Logger** (`python/logging/structured_logger.py`)
   - **Purpose:** Backward compatibility shim
   - **Backend:** Delegates to ulog()
   - **Features:** Deprecated, scheduled for removal
   - **API:** `get_logger(name).info/warn/error()`

6. **Tools Logging** (`tools/duckdb_queries.py`)
   - **Purpose:** Utility script logging with fallbacks
   - **Backend:** Mixed with graceful degradation
   - **Features:** Optional unified logging, fallback to print
   - **API:** Conditional imports with fallback

## Target Architecture

### Core Concept: Registry Pattern with Loguru Backend

```text
┌─────────────────────────────────────────────────────────────┐
│                    UniversalLogger                          │
│                 (Central Registry)                          │
├─────────────────────────────────────────────────────────────┤
│  Provider Registration System                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐│
│  │ EnhancedConsole │  │    DBCliLogger  │  │ TestLogger   ││
│  │    Provider     │  │     Provider    │  │   Provider   ││
│  └─────────────────┘  └─────────────────┘  └──────────────┘│
├─────────────────────────────────────────────────────────────┤
│                  Loguru Backend                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │File Handler │ │Console      │ │JSONL Handler│ │Network ││
│  │(rotation)   │ │Handler      │ │(structured) │ │Handler ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Component Design

#### 1. Central UniversalLogger Class

```python
class UniversalLogger:
    """Central registry for all logging providers with Loguru backend."""

    def __init__(self):
        self._providers: Dict[str, LoggingProvider] = {}
        self._loguru_backend = logger  # Global loguru instance
        self._configured = False

    def register_provider(self, name: str, provider_class: Type[LoggingProvider],
                         config: Dict[str, Any]) -> LoggingProvider:
        """Register a new logging provider with specific configuration."""

    def get_provider(self, name: str) -> LoggingProvider:
        """Get a registered provider by name."""

    def configure_global(self, config: Dict[str, Any]) -> None:
        """Configure global logging settings and initialize all providers."""

    def auto_detect_provider(self) -> str:
        """Auto-detect appropriate provider based on execution context."""
```

#### 2. LoggingProvider Base Class

```python
class LoggingProvider(ABC):
    """Base class for all logging providers."""

    def __init__(self, name: str, loguru_backend, config: Dict[str, Any]):
        self.name = name
        self.backend = loguru_backend.bind(provider=name)
        self.config = config
        self.handlers: List[LoggingHandler] = []

    @abstractmethod
    def setup_handlers(self) -> None:
        """Set up provider-specific handlers."""

    @abstractmethod
    def get_api_facade(self) -> Any:
        """Return the provider's public API interface."""
```

#### 3. Specific Provider Implementations

##### Enhanced Console Provider
```python
class EnhancedConsoleProvider(LoggingProvider):
    """Rich-formatted console output provider."""

    def setup_handlers(self):
        # Console handler with Rich formatting
        self.backend.add(
            sys.stderr,
            format="<green>{time}</green> | <level>{level}</level> | {message}",
            filter=lambda r: r["extra"].get("provider") == "enhanced_console",
            colorize=True
        )

        # Session log handler
        if self.config.get("session_logging", True):
            session_file = self.config.get("session_file", "logs/console_session.jsonl")
            self.backend.add(
                session_file,
                serialize=True,
                filter=lambda r: r["extra"].get("provider") == "enhanced_console"
            )

    def get_api_facade(self):
        return EnhancedConsoleAPI(self.backend)

class EnhancedConsoleAPI:
    """Backward-compatible API facade."""

    def __init__(self, backend):
        self.backend = backend

    def success(self, message: str, **details):
        self.backend.info(f"✅ {message}", **details)

    def error(self, message: str, **details):
        self.backend.error(f"❌ {message}", **details)

    def warning(self, message: str, **details):
        self.backend.warning(f"⚠️ {message}", **details)

    def info(self, message: str, **details):
        self.backend.info(f"ℹ️ {message}", **details)
```

##### Structured Logger Provider
```python
class StructuredLoggerProvider(LoggingProvider):
    """JSONL structured logging provider (replacement for current ulog)."""

    def setup_handlers(self):
        # JSONL file handler with rotation
        jsonl_file = self.config.get("jsonl_path", "logs/unified.log.jsonl")
        self.backend.add(
            jsonl_file,
            serialize=True,
            rotation=self.config.get("rotation", "50 MB"),
            retention=self.config.get("retention", 5),
            filter=lambda r: r["extra"].get("provider") == "structured_logger",
            format=self._custom_jsonl_format
        )

        # Optional dual-write to structlog for migration period
        if self.config.get("dual_write", False):
            self._setup_structlog_bridge()

    def get_api_facade(self):
        return StructuredLoggerAPI(self.backend)

class StructuredLoggerAPI:
    """Backward-compatible ulog API."""

    def __call__(self, action: str, target: str = None, result: str = "success",
                 severity: str = "INFO", **fields):
        """Main ulog function signature preserved."""
        self.backend.log(severity, action,
                        target=target, result=result, **fields)
```

##### Test Logger Provider
```python
class TestLoggerProvider(LoggingProvider):
    """Test execution logging with pytest integration."""

    def setup_handlers(self):
        # Console handler for test output
        self.backend.add(
            sys.stderr,
            level="DEBUG",
            format="<green>{time}</green> | <level>{level}</level> | {message}",
            filter=lambda r: r["extra"].get("provider") == "test_logger"
        )

        # Test artifacts file
        test_file = self.config.get("test_log", "build/artifacts/tests/test_run.log")
        self.backend.add(
            test_file,
            level="DEBUG",
            rotation="5 MB",
            filter=lambda r: r["extra"].get("provider") == "test_logger"
        )

        # JSONL for machine consumption
        jsonl_file = self.config.get("jsonl_file", "build/artifacts/tests/test_run.jsonl")
        self.backend.add(
            jsonl_file,
            serialize=True,
            filter=lambda r: r["extra"].get("provider") == "test_logger"
        )
```

#### 4. Configuration System

##### Environment Variables (Backward Compatible)
```
# Global settings
UNIFIED_LOG_BACKEND=loguru                    # New: backend selection
UNIFIED_LOG_LEVEL=DEBUG                       # Existing: global level
UNIFIED_LOG_AUTO_PROVIDER=true               # New: auto-detect provider

# Provider-specific settings
UNIFIED_LOG_ENHANCED_CONSOLE_ENABLED=true
UNIFIED_LOG_ENHANCED_CONSOLE_SESSION=true
UNIFIED_LOG_STRUCTURED_JSONL_PATH=logs/unified.log.jsonl
UNIFIED_LOG_STRUCTURED_ROTATION=50MB
UNIFIED_LOG_TEST_ARTIFACTS_DIR=build/artifacts/tests

# Legacy compatibility
UNIFIED_LOG_PATH=logs/unified.log.jsonl      # Maps to structured provider
UNIFIED_LOG_RICH=1                           # Maps to enhanced console
```

##### Configuration File (`logging.yaml`)
```yaml
universal_logger:
  backend: loguru
  auto_detect_provider: true

  providers:
    enhanced_console:
      enabled: true
      session_logging: true
      session_file: "logs/console_session.jsonl"
      handlers:
        - type: console
          format: "<green>{time}</green> | <level>{level}</level> | {message}"
          level: INFO

    structured_logger:
      enabled: true
      jsonl_path: "logs/unified.log.jsonl"
      rotation: "50 MB"
      retention: 5
      dual_write: false  # Disable after migration
      handlers:
        - type: jsonl_file
          path: "logs/unified.log.jsonl"
          serialize: true
          rotation: "50 MB"

    test_logger:
      enabled: true
      artifacts_dir: "build/artifacts/tests"
      handlers:
        - type: console
          level: DEBUG
        - type: file
          path: "build/artifacts/tests/test_run.log"
          rotation: "5 MB"
        - type: jsonl_file
          path: "build/artifacts/tests/test_run.jsonl"
          serialize: true
```

### Migration Strategy

#### Phase 1: Parallel Implementation
1. **Build new centralized system** alongside existing implementations
2. **Add auto-detection** to route calls to appropriate providers
3. **Maintain existing APIs** as facades over new system
4. **Environment flag** to enable new system (`UNIFIED_LOG_CENTRALIZED=1`)

#### Phase 2: Gradual Migration
1. **Update imports** to use central UniversalLogger
2. **Migrate configuration** from multiple env vars to unified config
3. **Deprecation warnings** for direct access to old implementations
4. **Performance testing** with existing benchmark infrastructure

#### Phase 3: Consolidation
1. **Remove old implementations** after migration period
2. **Clean up** deprecated shims and dual-write modes
3. **Update documentation** and examples
4. **Final performance validation**

### Backward Compatibility Guarantees

#### Existing Import Patterns Preserved
```python
# These continue to work unchanged
from src.unified_logger import ulog
from python.terminal.enhanced_console import success, error, warning, info
from python.logging.structured_logger import get_logger

# But now route through centralized system
```

#### API Compatibility
- All existing function signatures preserved
- Environment variables continue to work
- Output formats remain consistent
- Performance characteristics maintained

### Implementation Files

```text
src/
├── unified_logger_v3/
│   ├── __init__.py                 # Public API exports
│   ├── registry.py                 # Central UniversalLogger class
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                 # LoggingProvider base class
│   │   ├── enhanced_console.py     # Enhanced console provider
│   │   ├── structured_logger.py    # JSONL structured provider
│   │   ├── test_logger.py          # Test execution provider
│   │   └── dbcli_logger.py         # DBCli hybrid provider
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── base.py                 # LoggingHandler base class
│   │   ├── file_handler.py         # File-based handlers
│   │   ├── console_handler.py      # Console output handlers
│   │   └── network_handler.py      # Network/remote handlers
│   ├── config/
│   │   ├── __init__.py
│   │   ├── loader.py               # Configuration loading
│   │   └── defaults.yaml           # Default configuration
│   └── utils/
│       ├── __init__.py
│       ├── context_detection.py    # Auto-detect execution context
│       └── migration_helpers.py    # Migration utilities
```### Benefits

1. **Centralization:** Single source of truth for all logging configuration
2. **Consistency:** Unified formatting, filtering, and routing across all components
3. **Flexibility:** Easy to add new providers and handlers without changing core code
4. **Performance:** Loguru's efficient backend with async queuing and optimized routing
5. **Maintainability:** Clear separation of concerns, easier testing and debugging
6. **Extensibility:** Plugin-like architecture for adding new logging destinations
7. **Migration Safety:** Backward compatibility preserves existing functionality

This architecture transforms UniversalLogger into the centralized logging repository you envisioned while maintaining all existing functionality and providing a clear path for future enhancements.
