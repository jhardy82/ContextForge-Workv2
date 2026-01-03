# Deterministic JSON Serialization Specification

**Status**: Draft
**Version**: 1.0.0
**Authority**: OM-003 (Linear Issue)
**Last Updated**: 2025-11-29
**Related**: [RFC 8785 (JCS)](https://www.rfc-editor.org/rfc/rfc8785) | [RFC 7493 (I-JSON)](https://www.rfc-editor.org/rfc/rfc7493)

---

## Table of Contents

1. [Purpose](#purpose)
2. [Standards Compliance](#standards-compliance)
3. [Key Ordering Rules](#key-ordering-rules)
4. [Number Formatting Rules](#number-formatting-rules)
5. [String Handling Rules](#string-handling-rules)
6. [Whitespace Rules](#whitespace-rules)
7. [Rejection Rules](#rejection-rules)
8. [SHA-256 Hashing Protocol](#sha-256-hashing-protocol)
9. [PowerShell Implementation Notes](#powershell-implementation-notes)
10. [Test Cases](#test-cases)
11. [Evidence Bundle Integration](#evidence-bundle-integration)

---

## Purpose

This specification defines the **canonical JSON serialization** algorithm for ContextForge Output Manager. The primary goals are:

1. **Determinism**: Identical input always produces byte-identical output
2. **Stable Hashing**: SHA-256 hashes are reproducible across sessions, machines, and PowerShell versions
3. **Evidence Integrity**: Evidence bundles can be cryptographically verified for tampering
4. **Interoperability**: Output is compatible with I-JSON consumers (JavaScript, Python, etc.)

> **UCL Compliance**: Evidence bundles without deterministic serialization violate UCL Law 3 (evidence completeness) because hash verification becomes unreliable.

---

## Standards Compliance

### RFC 8785 (JSON Canonicalization Scheme - JCS)

The Output Manager implements **JCS** with the following commitments:

| JCS Requirement | Implementation |
|-----------------|----------------|
| Key ordering | UTF-16 code unit lexicographic sort |
| Number formatting | ECMAScript `JSON.stringify` compatible |
| String escaping | Minimal escaping (control chars only) |
| Whitespace | None (compact output) |
| Unicode | UTF-8 encoding throughout |

### RFC 7493 (I-JSON)

The Output Manager enforces **I-JSON** constraints:

| I-JSON Requirement | Implementation |
|--------------------|----------------|
| Number range | IEEE 754 double precision: ±(2^53 - 1) |
| Unique keys | Enforced; duplicates cause rejection |
| UTF-8 encoding | BOM-less UTF-8 only |
| Non-finite numbers | Rejected (NaN, Infinity, -Infinity) |

---

## Key Ordering Rules

### Algorithm

Object keys MUST be sorted using **UTF-16 code unit lexicographic ordering**:

```
1. Convert each key to UTF-16 representation
2. Compare keys code unit by code unit (unsigned 16-bit values)
3. Shorter keys precede longer keys when prefixes match
4. Sort in ascending order
```

### PowerShell Implementation

```powershell
function Get-CanonicalKeyOrder {
    param([hashtable]$Object)

    # UTF-16 lexicographic sort (JCS-compliant)
    $sortedKeys = $Object.Keys | Sort-Object {
        # PowerShell strings are already UTF-16 internally
        [System.Text.Encoding]::Unicode.GetBytes($_)
    }

    return $sortedKeys
}
```

### Examples

| Input Keys | Canonical Order | Rationale |
|------------|-----------------|-----------|
| `["b", "a", "c"]` | `["a", "b", "c"]` | Standard ASCII sort |
| `["10", "2", "1"]` | `["1", "10", "2"]` | String sort, not numeric |
| `["α", "a", "ä"]` | `["a", "ä", "α"]` | UTF-16 code point order |
| `["", "a"]` | `["", "a"]` | Empty string first |
| `["a", "aa", "aaa"]` | `["a", "aa", "aaa"]` | Prefix ordering |

### Nested Objects

Canonical ordering applies **recursively** to all nested objects:

```json
{
    "inner": {
        "z": 1,
        "a": 2
    },
    "outer": 3
}
```

Canonical output:

```json
{"inner":{"a":2,"z":1},"outer":3}
```

---

## Number Formatting Rules

### Integer Handling

| Condition | Format | Example |
|-----------|--------|---------|
| Standard integer | No decimal point | `42` |
| Negative integer | Leading minus | `-42` |
| Zero | Just `0` | `0` |
| Negative zero | Convert to `0` | `-0` → `0` |

### Floating-Point Handling

| Condition | Format | Example |
|-----------|--------|---------|
| Standard decimal | Minimal representation | `3.14` |
| Trailing zeros | Remove | `3.140` → `3.14` |
| Leading zeros | Remove | `0.5` (not `.5`) |
| Scientific notation | Only when shorter | `1e10` vs `10000000000` |

### Scientific Notation Thresholds (ECMAScript Compatible)

```
- Use scientific notation if exponent >= 21 or <= -7
- Lowercase 'e' for exponent
- No plus sign on positive exponents
- Example: 1e21, 1e-7
```

### Range Validation (I-JSON)

Numbers MUST be within IEEE 754 double precision range:

```
Minimum safe integer: -(2^53 - 1) = -9007199254740991
Maximum safe integer:  (2^53 - 1) =  9007199254740991
```

Numbers outside this range MUST be rejected (see [Rejection Rules](#rejection-rules)).

### PowerShell Implementation

```powershell
function Format-CanonicalNumber {
    param([object]$Value)

    # Reject non-finite values
    if ([double]::IsNaN($Value) -or [double]::IsInfinity($Value)) {
        throw "Non-finite number rejected: $Value"
    }

    # Convert -0 to 0
    if ($Value -eq 0) {
        return "0"
    }

    # Check I-JSON range for integers
    if ($Value -is [int64] -or $Value -is [int32]) {
        if ([Math]::Abs($Value) -gt 9007199254740991) {
            throw "Integer out of I-JSON safe range: $Value"
        }
        return $Value.ToString()
    }

    # Format floating-point with ECMAScript rules
    $formatted = $Value.ToString("G17", [System.Globalization.CultureInfo]::InvariantCulture)

    # Apply scientific notation thresholds
    # (Additional formatting logic here)

    return $formatted
}
```

---

## String Handling Rules

### Escaping Requirements

Only the following characters MUST be escaped:

| Character | Escape Sequence | Unicode |
|-----------|-----------------|---------|
| Quotation mark | `\"` | U+0022 |
| Reverse solidus | `\\` | U+005C |
| Backspace | `\b` | U+0008 |
| Form feed | `\f` | U+000C |
| Line feed | `\n` | U+000A |
| Carriage return | `\r` | U+000D |
| Tab | `\t` | U+0009 |
| Control chars (U+0000-U+001F) | `\uXXXX` | Hex escape |

### Non-Escaped Characters

All other characters, including:
- Unicode characters above U+001F
- Forward solidus `/` (NOT escaped)
- Non-ASCII printable characters

MUST appear as literal UTF-8 bytes.

### PowerShell Implementation Note

PowerShell's `ConvertTo-Json` escapes `/` and non-ASCII characters unnecessarily. The Output Manager MUST post-process to remove superfluous escaping.

---

## Whitespace Rules

### Canonical Output

**No whitespace** between tokens:

```json
{"key1":"value","key2":42,"key3":[1,2,3]}
```

**Not**:

```json
{
    "key1": "value",
    "key2": 42,
    "key3": [1, 2, 3]
}
```

### PowerShell Implementation

```powershell
# Always use -Compress
$json = $object | ConvertTo-Json -Depth 100 -Compress
```

---

## Rejection Rules

The canonical serializer MUST reject (throw an error) for:

### 1. Non-Finite Numbers

```powershell
# Reject NaN
[double]::NaN  # → Error: "Cannot serialize NaN to canonical JSON"

# Reject Infinity
[double]::PositiveInfinity  # → Error
[double]::NegativeInfinity  # → Error
```

### 2. Out-of-Range Integers

```powershell
# Reject numbers outside ±(2^53 - 1)
9007199254740992  # → Error: "Integer exceeds I-JSON safe range"
```

### 3. Duplicate Keys

```powershell
# Reject objects with duplicate keys
@{ "a" = 1; "A" = 2 }  # Allowed (different case)
# Duplicate keys are rare in PowerShell hashtables but must be checked
```

### 4. Circular References

```powershell
$obj = @{ name = "self" }
$obj.self = $obj  # → Error: "Circular reference detected"
```

### 5. Non-Serializable Types

```powershell
# Reject types that cannot be represented in JSON
[ScriptBlock]{ Get-Process }  # → Error: "ScriptBlock cannot be serialized"
[DateTime]::Now  # → Convert to ISO 8601 string first
```

---

## SHA-256 Hashing Protocol

### Encoding Requirements

1. Serialize to canonical JSON (this spec)
2. Encode as UTF-8 **without BOM**
3. Compute SHA-256 hash
4. Output as **lowercase hexadecimal** (64 characters)

### PowerShell Implementation

```powershell
function Get-CanonicalHash {
    param([string]$CanonicalJson)

    # UTF-8 bytes without BOM
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    $bytes = $utf8NoBom.GetBytes($CanonicalJson)

    # SHA-256 hash
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    $hashBytes = $sha256.ComputeHash($bytes)

    # Lowercase hex output
    $hexHash = [System.BitConverter]::ToString($hashBytes).Replace("-", "").ToLower()

    return $hexHash
}
```

### Example

```powershell
$object = [ordered]@{
    task_id = "TASK-001"
    status = "completed"
    priority = 3
}

$canonical = ConvertTo-CanonicalJson $object
# Output: {"priority":3,"status":"completed","task_id":"TASK-001"}

$hash = Get-CanonicalHash $canonical
# Output: 7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b
```

---

## PowerShell Implementation Notes

### Known Issues with ConvertTo-Json

| Issue | Workaround |
|-------|-----------|
| Random key order | Pre-sort keys with `[ordered]@{}` or custom sort |
| Escapes `/` | Post-process: `$json -replace '\\/', '/'` |
| Escapes non-ASCII | Post-process to unescape Unicode literals |
| Limited `-Depth` default | Always specify `-Depth 100` |
| Includes type annotations | Use `-Compress` and strip `$type` if present |

### Recommended Function Signature

```powershell
function ConvertTo-CanonicalJson {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [object]$InputObject,

        [Parameter()]
        [int]$Depth = 100,

        [Parameter()]
        [switch]$IncludeHash
    )

    process {
        # 1. Deep-sort keys recursively
        $sorted = Sort-ObjectKeysRecursive -Object $InputObject

        # 2. Validate numbers and types
        Assert-SerializableContent -Object $sorted

        # 3. Convert with PowerShell
        $json = $sorted | ConvertTo-Json -Depth $Depth -Compress

        # 4. Post-process for JCS compliance
        $canonical = Repair-JsonForJcs -Json $json

        if ($IncludeHash) {
            return [PSCustomObject]@{
                Json = $canonical
                Hash = Get-CanonicalHash -CanonicalJson $canonical
            }
        }

        return $canonical
    }
}
```

---

## Test Cases

### Key Ordering Tests

```powershell
Describe "Key Ordering" {
    It "Sorts keys alphabetically" {
        $input = @{ z = 1; a = 2; m = 3 }
        $result = ConvertTo-CanonicalJson $input
        $result | Should -Be '{"a":2,"m":3,"z":1}'
    }

    It "Handles numeric string keys correctly" {
        $input = @{ "10" = 1; "2" = 2; "1" = 3 }
        $result = ConvertTo-CanonicalJson $input
        $result | Should -Be '{"1":3,"10":1,"2":2}'
    }

    It "Sorts nested objects recursively" {
        $input = @{ outer = @{ z = 1; a = 2 }; first = 0 }
        $result = ConvertTo-CanonicalJson $input
        $result | Should -Be '{"first":0,"outer":{"a":2,"z":1}}'
    }
}
```

### Number Formatting Tests

```powershell
Describe "Number Formatting" {
    It "Formats integers without decimal" {
        $input = @{ value = 42 }
        $result = ConvertTo-CanonicalJson $input
        $result | Should -Be '{"value":42}'
    }

    It "Converts -0 to 0" {
        $input = @{ value = [double]::Parse("-0") }
        $result = ConvertTo-CanonicalJson $input
        $result | Should -Match '"value":0[^.]'
    }

    It "Rejects NaN" {
        $input = @{ value = [double]::NaN }
        { ConvertTo-CanonicalJson $input } | Should -Throw "*NaN*"
    }

    It "Rejects Infinity" {
        $input = @{ value = [double]::PositiveInfinity }
        { ConvertTo-CanonicalJson $input } | Should -Throw "*Infinity*"
    }
}
```

### Hash Stability Tests

```powershell
Describe "Hash Stability" {
    It "Produces identical hash for identical content" {
        $input1 = @{ a = 1; b = 2 }
        $input2 = @{ b = 2; a = 1 }  # Different order

        $result1 = ConvertTo-CanonicalJson $input1 -IncludeHash
        $result2 = ConvertTo-CanonicalJson $input2 -IncludeHash

        $result1.Hash | Should -Be $result2.Hash
    }

    It "Produces different hash for different content" {
        $input1 = @{ value = 1 }
        $input2 = @{ value = 2 }

        $result1 = ConvertTo-CanonicalJson $input1 -IncludeHash
        $result2 = ConvertTo-CanonicalJson $input2 -IncludeHash

        $result1.Hash | Should -Not -Be $result2.Hash
    }

    It "Hash is exactly 64 lowercase hex characters" {
        $result = ConvertTo-CanonicalJson @{ test = "value" } -IncludeHash
        $result.Hash | Should -Match '^[0-9a-f]{64}$'
    }
}
```

---

## Evidence Bundle Integration

### Usage in Evidence Bundles

```powershell
# Generate evidence bundle with canonical hash
$evidence = @{
    timestamp = (Get-Date -Format 'o')
    event = "task_complete"
    task_id = "TASK-001"
    results = @{
        passed = 42
        failed = 0
        skipped = 3
    }
}

$result = ConvertTo-CanonicalJson $evidence -IncludeHash

# Store in evidence bundle
$bundle = @{
    evidence_hash = $result.Hash
    evidence_json = $result.Json
    created_at = (Get-Date -Format 'o')
}
```

### Verification Workflow

```powershell
function Test-EvidenceIntegrity {
    param(
        [string]$StoredHash,
        [string]$EvidenceJson
    )

    # Re-canonicalize and hash
    $computed = Get-CanonicalHash -CanonicalJson $EvidenceJson

    if ($computed -ne $StoredHash) {
        throw "Evidence integrity check failed: hash mismatch"
    }

    return $true
}
```

---

## See Also

- [RFC 8785 - JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785)
- [RFC 7493 - I-JSON](https://www.rfc-editor.org/rfc/rfc7493)
- [ECMAScript JSON.stringify](https://tc39.es/ecma262/#sec-json.stringify)
- [logging.instructions.md](../../.github/instructions/logging.instructions.md) - Evidence bundle requirements
- [03-Context-Ontology-Framework.md](../03-Context-Ontology-Framework.md) - UCL compliance

---

**Document Status**: Draft ✅
**Authoritative**: Yes (OM-003)
**Next Review**: 2025-12-15
**Maintained By**: ContextForge Output Manager Team
