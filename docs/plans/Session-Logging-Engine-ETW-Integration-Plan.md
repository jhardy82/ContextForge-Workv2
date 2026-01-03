# Session Logging Engine: ETW Integration Implementation Plan

**Status**: ✅ Ready for Implementation
**Date**: 2025-09-20
**Foundation**: Existing 1372-line Rich+Loguru prototype enhanced with Microsoft TraceLogging ETW

## Implementation Strategy

Based on analysis of the existing `session-logging-engine-prototype.ipynb` (1372 lines), this plan integrates Microsoft TraceLogging ETW capabilities while preserving the established Rich Console capture and Loguru structured logging infrastructure.

### Existing Foundation Analysis

The prototype already implements:
- ✅ **CFEnhancedTerminalCapture**: Rich Console capture with correlation tracking
- ✅ **CFEnhancedSessionManager**: Loguru-based structured logging with UUID correlation
- ✅ **Constitutional Compliance**: COF 13-dimensional + UCL 5-law validation
- ✅ **Performance Validation**: <100ms logging overhead with comprehensive metrics
- ✅ **Agent Inspection**: Structured JSON artifacts for future agent consumption

### ETW Integration Points

## Phase 1: TraceLogging Provider Integration

### 1.1 Enhanced CFEnhancedSessionManager
```python
from contextforge.unified_logger import UnifiedLogger
from microsoft_tracelogging import TraceLoggingProvider, EventBuilder

class CFEnhancedSessionManagerETW(CFEnhancedSessionManager):
    """Enhanced Session Manager with TraceLogging ETW integration"""

    def __init__(self, correlation_id: str, terminal_capture: CFEnhancedTerminalCapture):
        super().__init__(correlation_id, terminal_capture)

        # Initialize ETW Provider (shared with Achievement Engine)
        self.etw_provider = TraceLoggingProvider(b'ContextForge.SessionLogging')
        self.event_builder = EventBuilder()

        # ETW Activity ID for correlation
        self.etw_activity_id = uuid.uuid4()

        # Log session initialization via ETW
        self._log_etw_session_start()

    def _log_etw_session_start(self):
        """Log session start via ETW with structured telemetry"""
        if self.etw_provider.is_enabled(4, 0x0000000000000001):  # KEYWORD_SESSION
            self.event_builder.reset(b'SessionStart', 4, 0x0000000000000001)
            self.event_builder.add_unicode_string(b'SessionId', self.correlation_id.encode('utf-8'))
            self.event_builder.add_unicode_string(b'SessionType', b'cf_enhanced_prototype')
            self.event_builder.add_filetime(b'StartTime', session_start_time)
            self.event_builder.add_guid(b'ActivityId', self.etw_activity_id)
            self.event_builder.add_unicode_string(b'Methodology', b'contextforge_constitutional')
            self.etw_provider.write(self.event_builder)
```

### 1.2 Enhanced Terminal Capture with ETW Events
```python
class CFEnhancedTerminalCaptureETW(CFEnhancedTerminalCapture):
    """Enhanced terminal capture with ETW telemetry integration"""

    def __init__(self, correlation_id: str, session_context: Dict[str, Any], etw_provider, event_builder):
        super().__init__(correlation_id, session_context)
        self.etw_provider = etw_provider
        self.event_builder = event_builder

    @contextlib.contextmanager
    def capture_session(self, operation_name: str):
        """Enhanced Rich console capture with ETW event emission"""
        operation_id = str(uuid.uuid4())
        start_time = datetime.now(timezone.utc)

        # Existing capture metadata (preserved)
        capture_metadata = {
            "operation_id": operation_id,
            "operation_name": operation_name,
            "correlation_id": self.correlation_id,
            "start_time": start_time.isoformat()
        }

        try:
            # Existing Rich console capture (preserved)
            with self.console.capture() as capture:
                yield capture_metadata

            # Post-capture processing (enhanced with ETW)
            end_time = datetime.now(timezone.utc)
            captured_text = capture.get()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            # ETW Event Emission
            self._emit_terminal_capture_etw(
                operation_name, captured_text, duration_ms, operation_id
            )

            # Existing artifact creation (preserved)
            capture_artifact = {
                "metadata": capture_metadata,
                "captured_output": captured_text,
                "end_time": end_time.isoformat(),
                "duration_ms": duration_ms,
                "output_length": len(captured_text),
                "integrity_hash": hash(captured_text),
                "provenance": self.provenance,
                "etw_correlation": {
                    "operation_id": operation_id,
                    "etw_emitted": True
                }
            }

            self.captured_outputs.append(capture_artifact)

        except Exception as e:
            # Enhanced error handling with ETW
            self._emit_error_etw(operation_name, str(e), operation_id)
            raise

    def _emit_terminal_capture_etw(self, operation_name: str, output: str, duration_ms: float, operation_id: str):
        """Emit terminal capture event via ETW"""
        if self.etw_provider.is_enabled(4, 0x0000000000000004):  # KEYWORD_TERMINAL
            self.event_builder.reset(b'TerminalCapture', 4, 0x0000000000000004)
            self.event_builder.add_unicode_string(b'OperationName', operation_name.encode('utf-8'))
            self.event_builder.add_unicode_string(b'OperationId', operation_id.encode('utf-8'))
            self.event_builder.add_uint32(b'DurationMs', int(duration_ms))
            self.event_builder.add_uint32(b'OutputLength', len(output))
            self.event_builder.add_unicode_string(b'OutputSample', output[:500].encode('utf-8'))  # Truncated
            self.event_builder.add_unicode_string(b'CorrelationId', self.correlation_id.encode('utf-8'))
            self.etw_provider.write(self.event_builder)
```

### 1.3 Enhanced Achievement Logging with ETW
```python
def log_achievement(self, achievement_type: str, description: str, evidence: Dict[str, Any] = None):
    """Enhanced achievement logging with ETW telemetry"""
    # Existing achievement record creation (preserved)
    self.achievement_counter += 1
    achievement_id = f"ACH-{self.correlation_id[:8]}-{self.achievement_counter:03d}"
    timestamp = datetime.now(timezone.utc)

    achievement_record = {
        "achievement_id": achievement_id,
        "correlation_id": self.correlation_id,
        "achievement_type": achievement_type,
        "description": description,
        "timestamp": timestamp.isoformat(),
        "evidence": evidence or {},
        "etw_correlation": {
            "achievement_id": achievement_id,
            "etw_emitted": True
        }
    }

    # ETW Achievement Event
    self._emit_achievement_etw(achievement_record)

    # Existing logging and display (preserved)
    self.session_artifacts.append(achievement_record)
    cf_logger.info("Achievement logged", achievement_record=achievement_record)

    return achievement_record

def _emit_achievement_etw(self, achievement_record: Dict[str, Any]):
    """Emit achievement event via ETW"""
    if self.etw_provider.is_enabled(4, 0x0000000000000002):  # KEYWORD_ACHIEVEMENT
        self.event_builder.reset(b'AchievementLogged', 4, 0x0000000000000002)
        self.event_builder.add_unicode_string(b'AchievementId', achievement_record['achievement_id'].encode('utf-8'))
        self.event_builder.add_unicode_string(b'AchievementType', achievement_record['achievement_type'].encode('utf-8'))
        self.event_builder.add_unicode_string(b'Description', achievement_record['description'].encode('utf-8'))
        self.event_builder.add_unicode_string(b'CorrelationId', achievement_record['correlation_id'].encode('utf-8'))
        self.event_builder.add_uint32(b'EvidenceKeys', len(achievement_record.get('evidence', {})))
        self.etw_provider.write(self.event_builder)
```

## Phase 2: Agent Inspection Enhancement

### 2.1 ETW Query Integration for Historical Analysis
```python
def get_historical_sessions_via_etw(days_back: int = 7) -> List[Dict[str, Any]]:
    """
    Enhanced agent inspection using ETW historical queries
    Complements existing JSONL file inspection
    """
    from microsoft_tracelogging import etw_query

    # ETW query for session events
    query_filter = {
        'provider_name': 'ContextForge.SessionLogging',
        'start_time': datetime.now() - timedelta(days=days_back),
        'keywords': ['KEYWORD_SESSION', 'KEYWORD_TERMINAL', 'KEYWORD_ACHIEVEMENT']
    }

    etw_events = etw_query.query_events(query_filter)

    # Group events by correlation ID
    sessions_by_correlation = {}
    for event in etw_events:
        correlation_id = event.get_property('CorrelationId')
        if correlation_id not in sessions_by_correlation:
            sessions_by_correlation[correlation_id] = {
                'correlation_id': correlation_id,
                'session_events': [],
                'terminal_captures': [],
                'achievements': []
            }

        if event.event_name == 'SessionStart':
            sessions_by_correlation[correlation_id]['session_start'] = event.timestamp
        elif event.event_name == 'TerminalCapture':
            sessions_by_correlation[correlation_id]['terminal_captures'].append(event)
        elif event.event_name == 'AchievementLogged':
            sessions_by_correlation[correlation_id]['achievements'].append(event)

    return list(sessions_by_correlation.values())

def enhanced_agent_inspection(self) -> Dict[str, Any]:
    """Enhanced agent inspection combining JSONL + ETW data"""
    # Existing JSONL-based session data (preserved)
    jsonl_session_data = self.get_agent_inspectable_session()

    # ETW-based historical context
    try:
        etw_session_history = get_historical_sessions_via_etw(days_back=1)
        etw_available = True
    except Exception as e:
        etw_session_history = []
        etw_available = False

    # Combined inspection data
    enhanced_session_data = {
        **jsonl_session_data,
        "etw_integration": {
            "etw_available": etw_available,
            "historical_sessions": len(etw_session_history),
            "etw_provider_name": "ContextForge.SessionLogging",
            "activity_id": str(self.etw_activity_id)
        },
        "cross_session_context": etw_session_history[:5]  # Recent 5 sessions
    }

    return enhanced_session_data
```

## Phase 3: Performance Validation

### 3.1 ETW Performance Impact Testing
```python
def test_etw_performance_impact(self):
    """Validate ETW integration performance impact"""

    # Test 1: Terminal capture with/without ETW
    def baseline_capture():
        with self.terminal_capture.capture_session("etw_baseline_test"):
            console = Console()
            console.print("ETW performance baseline test")

    def etw_enhanced_capture():
        with self.terminal_capture_etw.capture_session("etw_enhanced_test"):
            console = Console()
            console.print("ETW performance enhanced test")

    # Performance measurement
    baseline_stats = perf_analyzer.measure_operation_performance(
        "baseline_terminal_capture", baseline_capture, iterations=50
    )

    etw_stats = perf_analyzer.measure_operation_performance(
        "etw_enhanced_capture", etw_enhanced_capture, iterations=50
    )

    # ETW overhead analysis
    etw_overhead = etw_stats["mean_time_ms"] - baseline_stats["mean_time_ms"]

    # Constitutional validation: ETW overhead must be <10ms
    etw_performance_compliant = etw_overhead < 10

    self.log_achievement(
        achievement_type="etw_performance_validation",
        description="ETW integration performance impact measured",
        evidence={
            "baseline_mean_ms": baseline_stats["mean_time_ms"],
            "etw_enhanced_mean_ms": etw_stats["mean_time_ms"],
            "etw_overhead_ms": etw_overhead,
            "constitutional_compliance": etw_performance_compliant,
            "performance_threshold_ms": 10
        }
    )

    return {
        "baseline": baseline_stats,
        "etw_enhanced": etw_stats,
        "overhead_analysis": {
            "overhead_ms": etw_overhead,
            "meets_constitutional_requirement": etw_performance_compliant
        }
    }
```

## Phase 4: Integration with Achievement Engine

### 4.1 Shared Provider Architecture
```python
class ContextForgeUnifiedETWProvider:
    """
    Unified ETW provider serving both Achievement and Session Logging engines
    """

    def __init__(self):
        self.provider = TraceLoggingProvider(b'ContextForge.UnifiedTelemetry')
        self.event_builder = EventBuilder()

        # Shared keywords for event categorization
        self.KEYWORD_SESSION = 0x0000000000000001
        self.KEYWORD_ACHIEVEMENT = 0x0000000000000002
        self.KEYWORD_TERMINAL = 0x0000000000000004
        self.KEYWORD_MILESTONE = 0x0000000000000008  # Achievement Engine milestones

    def log_session_event(self, event_name: str, event_data: Dict[str, Any]):
        """Log session-related events"""
        if self.provider.is_enabled(4, self.KEYWORD_SESSION):
            self.event_builder.reset(event_name.encode('utf-8'), 4, self.KEYWORD_SESSION)
            # Add event data fields
            self._add_event_fields(event_data)
            self.provider.write(self.event_builder)

    def log_achievement_milestone(self, milestone_name: str, milestone_data: Dict[str, Any]):
        """Log Achievement Engine milestone events"""
        if self.provider.is_enabled(4, self.KEYWORD_MILESTONE):
            self.event_builder.reset(b'MilestoneReached', 4, self.KEYWORD_MILESTONE)
            # Add milestone data fields
            self._add_event_fields(milestone_data)
            self.provider.write(self.event_builder)
```

## Implementation Timeline

### Week 1: Foundation Integration
- [ ] **Day 1-2**: Create enhanced session manager classes with ETW provider integration
- [ ] **Day 3-4**: Implement ETW event emission for terminal capture and achievements
- [ ] **Day 5-7**: Comprehensive testing and performance validation

### Week 2: Advanced Features
- [ ] **Day 1-3**: Implement ETW query interfaces for historical session analysis
- [ ] **Day 4-5**: Create shared provider architecture with Achievement Engine
- [ ] **Day 6-7**: Integration testing and constitutional compliance validation

### Week 3: Production Readiness
- [ ] **Day 1-2**: Documentation and usage examples
- [ ] **Day 3-4**: Performance optimization and error handling
- [ ] **Day 5-7**: Final validation and deployment preparation

## Success Criteria

### Constitutional Compliance
- ✅ COF 13-dimensional analysis applied to ETW integration
- ✅ UCL 5-law compliance maintained with enhanced evidence trails
- ✅ Performance threshold <10ms ETW overhead
- ✅ Cross-platform graceful degradation

### Technical Excellence
- ✅ ETW events generated for all terminal captures and achievements
- ✅ Correlation tracking between JSONL logs and ETW events
- ✅ Historical session analysis via ETW queries
- ✅ Shared provider architecture with Achievement Engine

### Agent Inspection Enhancement
- ✅ Enhanced session data with ETW historical context
- ✅ Cross-session relationship tracking via activity IDs
- ✅ Native Windows Event Viewer integration
- ✅ Structured telemetry for advanced analytics

---

**Next Action**: Begin implementation of Phase 1 enhanced session manager with ETW provider integration, building upon the existing 1372-line Rich+Loguru prototype foundation.
