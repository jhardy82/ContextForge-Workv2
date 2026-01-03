# UniversalLogger Centralized Implementation Prompt

## **Core Mission**

You WILL implement a centralized UniversalLogger system that consolidates 6 distributed logging patterns into a unified Loguru-backend registry while maintaining 100% backward
compatibility with existing APIs, environment variables, and output formats.

## **Implementation Requirements**

### **CRITICAL: Backward Compatibility Guarantees**

You MUST preserve these existing interfaces without any breaking changes:

#### **Import Patterns (Must Continue Working)**
```python
# These imports MUST continue working identically
from src.unified_logger import ulog                              # 47 locations
from python.terminal.enhanced_console import success, error     # 23 locations
from python.logging.structured_logger import get_logger         # 12 locations
from python.ulog.unified import get_logger, configure           # 8 locations
from tests.conftest import logger                                # pytest integration
from loguru import logger                                        # 15+ test files
```

#### **Environment Variables (Must Continue Working)**
```bash
# All existing environment variables MUST be preserved
UNIFIED_LOG_LEVEL=DEBUG
UNIFIED_LOG_PATH=logs/unified.log.jsonl
UNIFIED_LOG_MAX_MB=50
UNIFIED_LOG_REDACT=secret,password
UNIFIED_LOG_DUAL_WRITE=1
UNIFIED_LOG_RICH=1
UNIFIED_LOG_RICH_MIRROR=1
UNIFIED_LOG_RICH_STDERR=1
PYTEST_LOG_LEVEL=INFO
```

#### **API Signatures (Must Remain Identical)**
```python
# ulog() function signature preserved exactly
ulog(action: str, target: str = None, result: str = "success", severity: str = "INFO", **fields)

# Enhanced console functions preserved exactly
success(message: str, **details)
error(message: str, **details)
warning(message: str, **details)
info(message: str, **details)

# Structured logger API preserved exactly
get_logger(name: str).info/warn/error()
```

#### **Output Formats (Must Match Byte-for-Byte)**
- **JSONL Structure:** Existing `ulog()` JSONL format with required fields
- **Console Formatting:** Rich-based colored terminal output with icons
- **Test Artifacts:** Specific file naming and rotation patterns
- **Session Logs:** Enhanced console session logging format

### **Architecture Implementation Requirements**

#### **1. Phase 1: Parallel Implementation (MANDATORY FIRST STEP)**

You WILL implement the centralized system alongside existing implementations using feature flags:

##### **1.1 Core Infrastructure Creation**
```bash
# Create new module structure exactly as specified
mkdir -p src/unified_logger_v3/{providers,handlers,config,utils}
touch src/unified_logger_v3/__init__.py
touch src/unified_logger_v3/registry.py
```

##### **1.2 Central UniversalLogger Class**
You MUST implement this exact class structure:

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

##### **1.3 LoggingProvider Base Class**
You MUST implement this abstract base class:

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

##### **1.4 Core Provider Implementations (MANDATORY)**

You MUST implement these exact providers:

###### **StructuredLoggerProvider**
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

    def get_api_facade(self):
        return StructuredLoggerAPI(self.backend)

class StructuredLoggerAPI:
    """Backward-compatible ulog API."""

    def __call__(self, action: str, target: str = None, result: str = "success",
                 severity: str = "INFO", **fields):
        """Main ulog function signature preserved exactly."""
        self.backend.log(severity, action, target=target, result=result, **fields)
```

###### **EnhancedConsoleProvider**
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
    """Backward-compatible enhanced console API."""

    def success(self, message: str, **details):
        self.backend.info(f"✅ {message}", **details)

    def error(self, message: str, **details):
        self.backend.error(f"❌ {message}", **details)

    def warning(self, message: str, **details):
        self.backend.warning(f"⚠️ {message}", **details)

    def info(self, message: str, **details):
        self.backend.info(f"ℹ️ {message}", **details)
```

###### **TestLoggerProvider**
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

###### **DBCliLoggerProvider**
```python
class DBCliLoggerProvider(LoggingProvider):
    """Hybrid console + structured logging for CLI applications."""

    def setup_handlers(self):
        # Combine Enhanced Console + Structured Logger
        # Implementation details based on dbcli.py patterns
```

##### **1.5 Compatibility Facades (CRITICAL)**

You MUST implement these exact compatibility layers to preserve existing imports:

```python
# src/unified_logger.py - Add compatibility layer
_CENTRALIZED_ENABLED = os.getenv("UNIFIED_LOG_CENTRALIZED", "0") == "1"

def ulog(*args, **kwargs):
    if _CENTRALIZED_ENABLED:
        from src.unified_logger_v3 import get_universal_logger
        provider = get_universal_logger().get_provider("structured_logger")
        return provider.get_api_facade()(*args, **kwargs)
    else:
        return _original_ulog(*args, **kwargs)  # Current implementation

# python/terminal/enhanced_console.py - Add compatibility layer
def success(message: str, **details):
    if _CENTRALIZED_ENABLED:
        from src.unified_logger_v3 import get_universal_logger
        provider = get_universal_logger().get_provider("enhanced_console")
        return provider.get_api_facade().success(message, **details)
    else:
        return _original_success(message, **details)  # Current implementation
```

##### **1.6 Feature Flag System**

You MUST implement this environment variable control system:

```python
# Environment variables for gradual rollout
UNIFIED_LOG_CENTRALIZED=0              # Enable centralized system
UNIFIED_LOG_CENTRALIZED_PROVIDER=auto  # Force specific provider
UNIFIED_LOG_CENTRALIZED_DEBUG=0        # Debug migration process
UNIFIED_LOG_MIGRATION_MODE=parallel    # parallel|centralized|legacy
```

##### **1.7 Configuration System**

You MUST implement dual configuration support:

###### **Environment Variable Mapping**
```python
# Legacy environment variables MUST map to new system
UNIFIED_LOG_PATH -> providers.structured_logger.jsonl_path
UNIFIED_LOG_RICH -> providers.enhanced_console.enabled
PYTEST_LOG_LEVEL -> providers.test_logger.level
UNIFIED_LOG_LEVEL -> global.level
UNIFIED_LOG_MAX_MB -> providers.structured_logger.rotation
```

###### **YAML Configuration Support**
```yaml
universal_logger:
  backend: loguru
  auto_detect_provider: true

  providers:
    enhanced_console:
      enabled: true
      session_logging: true
      session_file: "logs/console_session.jsonl"

    structured_logger:
      enabled: true
      jsonl_path: "logs/unified.log.jsonl"
      rotation: "50 MB"
      retention: 5

    test_logger:
      enabled: true
      artifacts_dir: "build/artifacts/tests"
```

### **File Structure Requirements**

You MUST create this exact file structure:

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
│   │   ├── console_handler.py      # Console-based handlers
│   │   └── jsonl_handler.py        # JSONL-specific handlers
│   ├── config/
│   │   ├── __init__.py
│   │   ├── loader.py               # Configuration loading logic
│   │   ├── env_mapper.py           # Environment variable mapping
│   │   └── validator.py            # Configuration validation
│   └── utils/
│       ├── __init__.py
│       ├── context_detector.py     # Provider auto-detection
│       ├── format_converters.py    # Output format utilities
│       └── migration_helpers.py    # Migration support tools
```

### **Testing Requirements**

#### **Validation Criteria (MANDATORY)**

You MUST ensure ALL of these pass before considering Phase 1 complete:

- [ ] **All existing tests pass** with `UNIFIED_LOG_CENTRALIZED=1`
- [ ] **Performance within 5%** of current implementation
- [ ] **Output formats identical** (byte-for-byte JSONL matching)
- [ ] **Environment variables work unchanged**
- [ ] **Import compatibility preserved**

#### **Test Implementation Requirements**

You MUST create tests for:

1. **Backward Compatibility Tests**
   - All existing import patterns continue working
   - All environment variables produce identical behavior
   - All API signatures work identically
   - Output format byte-for-byte comparison

2. **Provider Tests**
   - Each provider registers correctly
   - Provider-specific configuration works
   - Handler setup produces expected outputs
   - API facades work identically to original implementations

3. **Integration Tests**
   - Feature flag switching works correctly
   - Auto-detection selects correct providers
   - Configuration loading from both env vars and YAML
   - Multi-provider scenarios work correctly

4. **Performance Tests**
   - Logging latency within 5% of current system
   - Memory usage comparable or improved
   - Startup time not significantly impacted

### **Implementation Process**

#### **Step 1: Core Infrastructure**
1. Create the exact file structure specified
2. Implement UniversalLogger registry class
3. Implement LoggingProvider base class
4. Set up basic Loguru backend integration

#### **Step 2: Provider Implementation**
1. Implement StructuredLoggerProvider with exact ulog() compatibility
2. Implement EnhancedConsoleProvider with exact console API compatibility
3. Implement TestLoggerProvider with pytest integration
4. Implement DBCliLoggerProvider with hybrid functionality

#### **Step 3: Compatibility Layer**
1. Add feature flag system to existing files
2. Implement compatibility facades for all existing imports
3. Add environment variable mapping logic
4. Test backward compatibility extensively

#### **Step 4: Configuration System**
1. Implement environment variable to configuration mapping
2. Add YAML configuration support
3. Implement provider auto-detection logic
4. Test configuration loading from all sources

#### **Step 5: Validation**
1. Run full test suite with centralized system enabled
2. Performance benchmark against current implementation
3. Output format validation (byte-for-byte comparison)
4. Import compatibility testing across all usage patterns

### **Success Criteria**

The implementation is ONLY complete when:

- ✅ **Zero test failures** with `UNIFIED_LOG_CENTRALIZED=1`
- ✅ **All existing imports work identically**
- ✅ **All environment variables work identically**
- ✅ **JSONL output is byte-for-byte identical**
- ✅ **Console output is visually identical**
- ✅ **Performance within 5% of current system**
- ✅ **Memory usage comparable or better**

### **Critical Implementation Notes**

#### **DO NOT BREAK EXISTING FUNCTIONALITY**
- Every existing import must continue working
- Every existing environment variable must continue working
- Every existing API call must work identically
- Every existing output format must match exactly

#### **USE FEATURE FLAGS FOR SAFETY**
- Default to `UNIFIED_LOG_CENTRALIZED=0` during development
- Only enable centralized system when explicitly requested
- Provide rollback mechanism at all times

#### **MAINTAIN PERFORMANCE**
- Use Loguru's efficient filtering system
- Minimize overhead in compatibility facades
- Optimize provider registration and lookup
- Monitor memory usage during development

#### **PRESERVE OUTPUT FORMATS**
- Match existing JSONL schema exactly
- Preserve Rich console formatting and icons
- Maintain file rotation and naming patterns
- Keep session logging formats identical

### **Migration Path Reference**

After Phase 1 implementation is complete and validated, the system will proceed through:

- **Phase 2:** Default switch with migration tools and deprecation warnings
- **Phase 3:** Legacy code removal and final consolidation

But Phase 1 MUST be 100% complete and validated before any migration activities begin.

### **Architecture Documents Reference**

Refer to these documents for detailed specifications:
- `docs/architecture/unified-logger-centralized-design.md` - Complete architectural design
- `docs/architecture/unified-logger-migration-strategy.md` - Full migration strategy

### **Final Requirements**

You WILL implement this system with:
- **100% backward compatibility** - no breaking changes allowed
- **Feature flag safety** - centralized system off by default
- **Complete test coverage** - all functionality validated
- **Performance parity** - within 5% of current performance
- **Identical output formats** - byte-for-byte compatibility

The centralized UniversalLogger system represents the future of logging in this project, consolidating 6 distributed patterns into a single, maintainable, and extensible system while preserving all existing functionality.
