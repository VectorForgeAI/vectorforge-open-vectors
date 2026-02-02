# Examples

Concrete, copy-pasteable examples of Vector records and Fidelity Profiles.

## Profiles

Fidelity Profile manifests that configure vectorization parameters:

| File | Vector | Target PF | Notes |
|------|--------|-----------|-------|
| `profile-rf.default.95.json` | RFVector | 0.95 | Default RF profile with wavelet fingerprinting |
| `profile-pulse.default.95.json` | PulseVector | 0.95 | Default network flow profile |

## Records

Example Vector records (JSONL format, one record per line):

| File | Record Type | Description |
|------|-------------|-------------|
| `example-rfvector-record.jsonl` | `rf_capture_v1` | Single RFVector capture with wavelet fingerprint |
| `example-manifest-record.jsonl` | `manifest_v1` | Continuity Level 2 manifest committing to a window |
| `examples-vector-record.jsonl` | Various | Additional example records |

## Important Notes

### Placeholder Signatures

Signature fields (`divt.signatures.ecdsa`, `divt.signatures.pqc`) are **placeholders** in these examples. The package does not include private keys.

To validate:
1. **Hash verification**: Use `divt.hash_b64` with the canonicalization reference code
2. **Full verification**: Use a DIVT service to create real signatures

### Hash Verification Example

```python
import json
from reference.python.json_canon_v1 import compute_hash_b64

with open('examples/example-rfvector-record.jsonl') as f:
    data = json.loads(f.readline())

# Compute hash from record
computed = compute_hash_b64(data['record'])

# Compare to stored hash
stored = data['divt']['hash_b64']

print(f"Computed: {computed[:40]}...")
print(f"Stored:   {stored[:40]}...")
print(f"Match: {computed == stored}")
```

## Record Structure Overview

Every Vector record has this structure:

```json
{
  "record": {
    "schema": {"name": "vectorforge.vector", "version": "0.1.7"},
    "vector": "rfvector",           // Which domain
    "record_type": "rf_capture_v1", // Specific record type
    "record_id": "uuid",
    "tenant_id": "string",
    "time": {
      "start_us": 1738368000000000, // Microseconds since epoch
      "end_us": 1738368001000000,
      "observed_us": 1738368001000000
    },
    "source": {...},
    "chain": {"stream_id": "...", "seq": 1},
    "retention": {...},
    "fidelity": {"profile_id": "...", "profile_divt_id": "..."},
    "payload": {...},               // Domain-specific data
    "extensions": {}
  },
  "divt": {
    "divt_id": "uuid",
    "tenant_id": "string",
    "hash_b64": "base64-sha3-512",
    "hash_mode": "json_canon_v1",
    "hash_version": "sha3-512-v1",
    "crypto_mode": "hybrid",
    "signatures": {...},
    "signature_version": "keyset-v1",
    "ledger_status": "pending",
    "revoked": false,
    "created_at": "2025-02-01T12:00:00Z"
  }
}
```

## See Also

- [Getting Started](../docs/getting-started.md) - How to produce your first record
- [Schemas](../schemas/) - JSON schemas for validation
- [Benchmark Datasets](../bench/datasets/) - Larger example datasets for testing
