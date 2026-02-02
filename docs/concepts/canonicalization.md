# JSON Canonicalization

## Why Canonicalization?

To verify a DIVT, you must recompute the hash of the `record` object and compare it to `divt.hash_b64`. This only works if everyone computes the **same bytes** from the same logical JSON.

JSON allows many representations of the same data:
- `{"a":1,"b":2}` vs `{"b":2,"a":1}` (key order)
- `{"a": 1}` vs `{"a":1}` (whitespace)
- `1.0` vs `1` vs `1.00` (number representation)

Canonicalization eliminates this ambiguity.

## json_canon_v1

VectorForge uses `hash_mode="json_canon_v1"`, which is RFC 8785-inspired with deliberate deviations.

### Rules

1. **Sorted keys**: Object keys are sorted lexicographically (Unicode code point order)
2. **Compact format**: No whitespace between tokens (use `separators=(',', ':')` in Python)
3. **No floats**: Numbers MUST be integers
4. **Safe integer range**: Integers MUST be in range `[-(2^53-1), 2^53-1]`
5. **No duplicate keys**: Objects MUST NOT have duplicate keys
6. **UTF-8 encoding**: Final output is UTF-8 bytes

### RFC 8785 Deviations

| Deviation | RFC 8785 | json_canon_v1 |
|-----------|----------|---------------|
| Floats | Allowed with specific formatting | **Forbidden** |
| Duplicate keys | Not addressed | **Forbidden** |

These deviations are intentional:
- Floats have platform-dependent representation; forbidding them ensures cross-language hash agreement
- Duplicate keys are ambiguous; forbidding them ensures deterministic parsing

## Encoding Values Without Floats

Since floats are forbidden, use these representations:

| Data Type | Encoding | Example |
|-----------|----------|---------|
| Timestamps | Integer microseconds | `1738368000000000` |
| Coordinates | Integer microdegrees | `37774929` (37.774929°) |
| Weights/Scores | Q15 fixed-point (0-32768) | `31129` (≈0.95) |
| Currency | Decimal strings | `"1250.37"` |
| SNR/dB | Fixed-point with scale | `{"snr_db_q8": 2560, "scale": 256}` (10.0 dB) |

Always document the scale or unit in the schema or field name.

## Pseudocode

```python
import json

SAFE_INT_MAX = 2**53 - 1
SAFE_INT_MIN = -SAFE_INT_MAX

def canonicalize(obj):
    def normalize(o):
        if isinstance(o, float):
            raise ValueError("FLOAT_NOT_ALLOWED")
        if isinstance(o, bool):
            return o  # booleans are fine
        if isinstance(o, int):
            if o < SAFE_INT_MIN or o > SAFE_INT_MAX:
                raise ValueError("INT_OUT_OF_RANGE")
            return o
        if isinstance(o, str):
            return o
        if o is None:
            return o
        if isinstance(o, dict):
            # Check for duplicate keys (most parsers dedupe, but be explicit)
            return {k: normalize(o[k]) for k in sorted(o.keys())}
        if isinstance(o, list):
            return [normalize(x) for x in o]
        raise ValueError(f"UNSUPPORTED_TYPE: {type(o)}")

    normalized = normalize(obj)
    json_str = json.dumps(normalized, separators=(',', ':'), ensure_ascii=False)
    return json_str.encode('utf-8')
```

## Computing the Hash

```python
import hashlib
import base64

def compute_hash_b64(record_obj):
    canon_bytes = canonicalize(record_obj)
    digest = hashlib.sha3_512(canon_bytes).digest()
    return base64.b64encode(digest).decode('ascii')
```

## Verification

```python
def verify_divt(record, divt):
    expected_hash = compute_hash_b64(record)
    actual_hash = divt['hash_b64']

    if expected_hash != actual_hash:
        raise ValueError(f"Hash mismatch: expected {expected_hash}, got {actual_hash}")

    # Then verify signatures against the hash...
```

## Test Vectors

The `test-vectors/json_canon_v1_test_vectors.json` file contains test cases:

```json
{
  "cases": [
    {
      "name": "simple_object",
      "input": {"b": 2, "a": 1},
      "expected_canon": "{\"a\":1,\"b\":2}",
      "expected_hash_b64": "..."
    },
    {
      "name": "float_rejected",
      "input": {"value": 1.5},
      "expected_error": "FLOAT_NOT_ALLOWED"
    }
  ]
}
```

Your implementation MUST pass all test cases.

## Common Mistakes

| Mistake | Result |
|---------|--------|
| Using `json.dumps()` defaults | Keys unsorted, extra whitespace |
| Including floats | Cross-platform hash mismatch |
| Using `ensure_ascii=True` | Non-ASCII characters escaped differently |
| Integer overflow | Out-of-range integers cause verification failure |
| Parsing floats from JSON | Some parsers auto-convert `1` to `1.0` |

## Reference Implementations

- Python: `reference/python/json_canon_v1.py`
- Go: `reference/go/json_canon_v1.go`

These are normative. If your implementation disagrees with them, yours is wrong.

## What's Next

- [DIVT](divt.md) - How canonicalized hashes are used in DIVTs
- [Getting Started](../getting-started.md) - Validate your first record
