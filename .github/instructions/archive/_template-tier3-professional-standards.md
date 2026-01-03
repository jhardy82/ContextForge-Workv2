---
applyTo: "[File pattern - e.g., '**/*.ps1,**/*.psm1' for PowerShell, '**/*.py' for Python, '**/*.ts,**/*.tsx' for TypeScript]"
description: "[Brief description of domain-specific professional standards - e.g., 'PowerShell cmdlet development guidelines', 'Python code quality standards', 'TypeScript best practices']"
tier: "TIER_3_PROFESSIONAL"
emphasis: "INSTRUCTIONAL_GUIDANCE"
code_examples: "EXTENSIVE_REQUIRED"
industry_standards: "AUTHORITATIVE_REFERENCES"
version: "1.0-template"
---

# [Language/Framework] [Domain] Guidelines

## Overview

[Brief introduction to the domain and why these guidelines matter - 2-3 sentences explaining the purpose and scope of this instruction file]

---

## Naming Conventions

### [Category 1 - e.g., Function/Class Names]

**Guidelines**:
- Use [specific convention - e.g., "PascalCase for function names"]
- [Convention detail - e.g., "Include verb-noun pairs for clarity"]
- [Convention detail - e.g., "Avoid abbreviations unless widely recognized"]
- [Convention detail - e.g., "Use descriptive names that reveal intent"]

**Examples**:
```[language]
# ✅ GOOD - [Why this is good]
[good_example_code]

# ❌ BAD - [Why this is bad]
[bad_example_code]

# ✅ BETTER - [How to improve]
[improved_example_code]
```

**Industry References**:
- [Authoritative source - e.g., "Microsoft PowerShell Approved Verbs: https://docs.microsoft.com/..."]
- [Style guide reference - e.g., "PEP 8 Naming Conventions: https://peps.python.org/pep-0008/#naming-conventions"]

### [Category 2 - e.g., Variable Names]

**Guidelines**:
- Use [specific convention - e.g., "camelCase for variable names"]
- [Convention detail - e.g., "Choose meaningful names over short ones"]
- [Convention detail - e.g., "Avoid magic numbers; use named constants"]
- [Convention detail - e.g., "Boolean variables should ask yes/no questions"]

**Examples**:
```[language]
# ✅ GOOD - [Why this is good]
[good_example_code]

# ❌ BAD - [Why this is bad]
[bad_example_code]
```

**Industry References**:
- [Clean Code reference - e.g., "Clean Code: Meaningful Names chapter"]
- [Language-specific guide - e.g., "Google TypeScript Style Guide"]

---

## [Domain-Specific Section 1 - e.g., Parameter Design, Function Structure, Class Design]

### [Subsection - e.g., Mandatory vs. Optional Parameters]

**Guidelines**:
- [Guideline with rationale - e.g., "Mark required parameters as Mandatory to fail fast"]
- [Guideline with rationale - e.g., "Provide sensible defaults for optional parameters"]
- [Guideline with rationale - e.g., "Use parameter sets to handle mutually exclusive options"]
- [Guideline with rationale - e.g., "Include help messages for all parameters"]

**Examples**:
```[language]
# Example 1: [Descriptive scenario - e.g., "Basic function with mandatory and optional parameters"]
[comprehensive_example_with_comments]

# Example 2: [Advanced scenario - e.g., "Parameter sets for mutually exclusive options"]
[comprehensive_example_with_comments]
```

**Best Practices**:
- [Practice with explanation - e.g., "Validate input early to provide clear error messages"]
- [Practice with explanation - e.g., "Use type constraints to enforce parameter contracts"]
- [Practice with explanation - e.g., "Document parameter purpose in help text"]

**Common Pitfalls**:
- ❌ **Avoid**: [Anti-pattern description - e.g., "Using positional parameters without clear documentation"]
  - **Why**: [Explanation - e.g., "Reduces code readability and increases error risk"]
  - **Instead**: [Correct approach - e.g., "Use named parameters with explicit binding"]

### [Subsection - e.g., Return Values, Type Annotations]

**Guidelines**:
- [Guideline with rationale]
- [Guideline with rationale]
- [Guideline with rationale]

**Examples**:
```[language]
[comprehensive_example_with_comments]
```

**Best Practices**:
- [Practice with explanation]
- [Practice with explanation]

---

## Error Handling

### Exception Management

**Guidelines**:
- Use [language-specific mechanism - e.g., "try-catch blocks for expected errors"]
- [Guideline - e.g., "Throw exceptions for truly exceptional conditions"]
- [Guideline - e.g., "Provide meaningful error messages with context"]
- [Guideline - e.g., "Log errors with sufficient detail for troubleshooting"]

**Examples**:
```[language]
# Example 1: Basic error handling
[basic_error_handling_example]

# Example 2: Custom exception types
[custom_exception_example]

# Example 3: Error propagation
[error_propagation_example]
```

**Best Practices**:
- Catch specific exceptions rather than generic `Exception`
- Include context in error messages (what failed, why, how to fix)
- Use logging for diagnostic information
- Clean up resources in `finally` blocks or using context managers

**Common Pitfalls**:
- ❌ **Avoid**: Swallowing exceptions without logging
  - **Why**: Makes debugging impossible and hides failures
  - **Instead**: Log the exception and re-raise or handle appropriately

### Input Validation

**Guidelines**:
- Validate input at system boundaries
- [Guideline - e.g., "Use type hints/constraints to enforce contracts"]
- [Guideline - e.g., "Fail fast with clear error messages"]

**Examples**:
```[language]
[input_validation_example]
```

---

## Documentation Standards

### [Documentation Type 1 - e.g., Comment-Based Help, Docstrings, JSDoc]

**Guidelines**:
- [Guideline - e.g., "Include synopsis, description, parameters, examples, outputs"]
- [Guideline - e.g., "Use complete sentences and proper grammar"]
- [Guideline - e.g., "Provide realistic examples that users can run"]
- [Guideline - e.g., "Document edge cases and common gotchas"]

**Examples**:
```[language]
[comprehensive_documentation_example]
```

**Required Sections**:
- **Synopsis**: One-line summary of purpose
- **Description**: Detailed explanation of functionality
- **Parameters**: Each parameter with type, purpose, default
- **Examples**: At least one working example
- **Outputs**: What the function returns

**Best Practices**:
- Update documentation when code changes
- Test documentation examples to ensure they work
- Use consistent formatting across the codebase

### [Documentation Type 2 - e.g., Inline Comments]

**Guidelines**:
- Explain **why**, not **what** (code should be self-explanatory for "what")
- [Guideline - e.g., "Comment complex algorithms or business logic"]
- [Guideline - e.g., "Use TODO/FIXME/NOTE tags for future work"]

**Examples**:
```[language]
[inline_comment_example]
```

---

## Testing Standards

### Unit Testing

**Guidelines**:
- [Guideline - e.g., "Write tests for all public functions and methods"]
- [Guideline - e.g., "Follow Arrange-Act-Assert (AAA) pattern"]
- [Guideline - e.g., "Test edge cases, errors, and happy paths"]
- [Guideline - e.g., "Use descriptive test names that document behavior"]

**Examples**:
```[language]
[unit_test_example]
```

**Framework-Specific Patterns**:
- [Framework - e.g., "Pytest"]: [Specific guidance - e.g., "Use fixtures for setup/teardown"]
- [Framework - e.g., "Pester"]: [Specific guidance - e.g., "Organize tests in Describe/Context/It blocks"]
- [Framework - e.g., "Jest"]: [Specific guidance - e.g., "Mock external dependencies with jest.mock()"]

**Best Practices**:
- Aim for ≥80% code coverage (target: 85%)
- Test should run quickly (<100ms per test)
- Tests should be independent and isolated
- Use descriptive assertion messages

### Integration Testing

**Guidelines**:
- Test interactions between components
- [Guideline - e.g., "Use test doubles (mocks/stubs) for external dependencies"]
- [Guideline - e.g., "Validate end-to-end workflows"]

**Examples**:
```[language]
[integration_test_example]
```

---

## Code Quality Tools

### Linters and Formatters

**Required Tools**:
- **[Tool 1 - e.g., "ruff"]**: [Purpose - e.g., "Python linting and formatting"]
  - Configuration: `[config_file - e.g., "pyproject.toml, ruff.toml"]`
  - Usage: `[command - e.g., "ruff check . && ruff format ."]`
  - Standards: [What it enforces - e.g., "PEP 8 compliance, import sorting, unused code detection"]

- **[Tool 2 - e.g., "PSScriptAnalyzer"]**: [Purpose - e.g., "PowerShell static analysis"]
  - Configuration: `[config_file - e.g., ".pssa-settings.psd1"]`
  - Usage: `[command - e.g., "Invoke-ScriptAnalyzer -Path . -Recurse"]`
  - Standards: [What it enforces - e.g., "Best practices, security rules, performance"]

**Examples**:
```[shell]
# [Tool 1] - Automated checks
[linter_command_example]

# [Tool 2] - Fix automatically where possible
[formatter_command_example]
```

**Best Practices**:
- Run linters in CI/CD pipeline (fail on errors)
- Use pre-commit hooks for local validation
- Configure editors to show linter warnings in real-time
- Address warnings incrementally rather than disabling rules

### Type Checking

**Guidelines**:
- [Guideline - e.g., "Use type hints for all function signatures"]
- [Guideline - e.g., "Run type checker in strict mode"]
- [Guideline - e.g., "Document type constraints in docstrings"]

**Tools**:
- **[Type Checker - e.g., "mypy"]**: `[usage - e.g., "mypy src/ --strict"]`
- **[Alternative - e.g., "pyright"]**: `[usage - e.g., "pyright src/"]`

**Examples**:
```[language]
[type_annotation_example]
```

---

## Performance Optimization

### [Performance Category 1 - e.g., Algorithm Efficiency]

**Guidelines**:
- [Guideline - e.g., "Choose appropriate data structures (O(1) vs O(n) lookup)"]
- [Guideline - e.g., "Avoid premature optimization; profile first"]
- [Guideline - e.g., "Cache expensive computations when appropriate"]

**Examples**:
```[language]
# Before: [Inefficient approach]
[slow_code_example]

# After: [Optimized approach]
[optimized_code_example]

# Performance comparison: [Benchmark results]
```

**Best Practices**:
- Use profiling tools to identify bottlenecks
- Optimize hot paths only (80/20 rule)
- Document performance characteristics in comments

### [Performance Category 2 - e.g., Memory Management]

**Guidelines**:
- [Guideline - e.g., "Use generators/iterators for large datasets"]
- [Guideline - e.g., "Release resources explicitly when needed"]

**Examples**:
```[language]
[memory_optimization_example]
```

---

## Security Best Practices

### Input Sanitization

**Guidelines**:
- Validate and sanitize all external inputs
- [Guideline - e.g., "Use parameterized queries for database operations"]
- [Guideline - e.g., "Escape user input in HTML/JavaScript contexts"]
- [Guideline - e.g., "Never trust client-side validation alone"]

**Examples**:
```[language]
[input_sanitization_example]
```

**Common Vulnerabilities**:
- ❌ **SQL Injection**: [How to prevent]
- ❌ **Cross-Site Scripting (XSS)**: [How to prevent]
- ❌ **Path Traversal**: [How to prevent]

### Secret Management

**Guidelines**:
- Never commit secrets to version control
- Use environment variables or secure vaults
- [Guideline - e.g., "Rotate credentials regularly"]

**Examples**:
```[language]
[secret_management_example]
```

---

## Common Patterns and Idioms

### [Pattern 1 - e.g., Factory Pattern, Pipeline Pattern, Builder Pattern]

**When to Use**:
- [Scenario description - e.g., "When you need to create objects without specifying exact class"]
- [Scenario description]

**Implementation**:
```[language]
[pattern_implementation_example]
```

**Advantages**:
- [Benefit - e.g., "Encapsulates object creation logic"]
- [Benefit]

**Disadvantages**:
- [Limitation - e.g., "Adds complexity for simple cases"]
- [Limitation]

### [Pattern 2]

**When to Use**:
- [Scenario description]

**Implementation**:
```[language]
[pattern_implementation_example]
```

---

## Code Review Checklist

Before submitting code for review, ensure:

- [ ] **Functionality**: Code works as intended and handles edge cases
- [ ] **Naming**: Variables, functions, classes have clear, descriptive names
- [ ] **Documentation**: All public APIs have complete documentation
- [ ] **Testing**: Unit tests cover new functionality (≥80% coverage)
- [ ] **Error Handling**: Exceptions are caught and handled appropriately
- [ ] **Linting**: Code passes all linter checks without warnings
- [ ] **Type Safety**: Type annotations present and type checker passes
- [ ] **Performance**: No obvious performance issues or bottlenecks
- [ ] **Security**: Input validation, no hardcoded secrets, secure APIs used
- [ ] **Style**: Code follows project conventions and industry standards

---

## Additional Resources

### Official Documentation
- **[Language/Framework Official Docs]**: [URL - e.g., "https://docs.python.org/"]
- **[Style Guide]**: [URL - e.g., "https://peps.python.org/pep-0008/"]
- **[Best Practices]**: [URL - e.g., "https://docs.microsoft.com/powershell/"]

### Community Resources
- **[Community Guide 1]**: [Description and URL]
- **[Community Guide 2]**: [Description and URL]

### Tools and Extensions
- **[Tool 1]**: [Description and installation instructions]
- **[Tool 2]**: [Description and installation instructions]

### Related Requirements
- **[Related Instruction File 1]**: [Brief description]
- **[Related Instruction File 2]**: [Brief description]

---

**Document Maintenance**: Update when:
- New language/framework versions introduce breaking changes
- Industry best practices evolve
- Tool recommendations change
- New security vulnerabilities discovered

**Last Updated**: [YYYY-MM-DD]
**Document Version**: [X.Y.Z]
**Standards Compliance**: ✅ Follows [industry standard - e.g., "Microsoft PowerShell Best Practices", "PEP 8", "Google TypeScript Style Guide"]
