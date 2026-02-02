# Python Reference Implementations

Python 3.9+ reference implementations for VectorForge Open Vectors.

## Requirements

```bash
pip install jsonschema  # For validator only
```

## Files

| File | Description |
|------|-------------|
| `json_canon_v1.py` | JSON canonicalization |
| `manifest_commitment.py` | Merkle root computation |
| `validator.py` | Conformance validator |

## JSON Canonicalization

```python
from json_canon_v1 import canonicalize, compute_hash_b64

record = {"b": 2, "a": 1}

# Get canonical bytes
canon_bytes = canonicalize(record)
# b'{"a":1,"b":2}'

# Compute hash
hash_b64 = compute_hash_b64(record)
# 'base64-encoded-sha3-512...'
```

### Testing

```bash
python json_canon_v1.py --test ../../test-vectors/json_canon_v1_test_vectors.json
```

## Manifest Commitment

```python
from manifest_commitment import merkle_root

# Base64-encoded SHA3-512 hashes of records
hashes = [
    "aX8thWFyy4MJ...",
    "hEbEbuA3k7pu...",
    "v+TX9zdxFtwV..."
]

root = merkle_root(hashes)
# 'base64-encoded-merkle-root...'
```

### Testing

```bash
python manifest_commitment.py --test ../../test-vectors/manifest_commitment_test_vectors.json
```

## Validator

Validate records against conformance levels:

```bash
# Level A: Record Integrity
python validator.py --records output.jsonl --level A

# Level B: Completeness
python validator.py --records output.jsonl --manifest manifest.jsonl --level B

# Level C: Payload + Profile
python validator.py --records output.jsonl --manifest manifest.jsonl --profile profile.json --level C
```

### Output

```
Loaded 20 records
Validating Level A...

Level A (Record Integrity): 20 passed, 0 failed

Level A PASSED
```
