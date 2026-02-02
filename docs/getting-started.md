# Getting Started

This guide walks you through understanding and producing your first valid Vector record.

## What You're Building

A **Vector record** is a single JSONL line that contains:
1. A **record** object with your telemetry data in a standardized format
2. A **divt** object that cryptographically attests to the record's integrity

```json
{"record": {...}, "divt": {...}}
```

## Step 1: Understand the Record Envelope

Every Vector record has a common envelope structure regardless of domain (RF, network, video, etc.):

```json
{
  "record": {
    "schema": {"name": "vectorforge.vector", "version": "0.1.7"},
    "vector": "rfvector",
    "record_type": "rf_capture_v1",
    "record_id": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "your-tenant",
    "time": {
      "start_us": 1738368000000000,
      "end_us": 1738368001000000,
      "observed_us": 1738368001000000
    },
    "source": {
      "source_id": "sensor-01",
      "source_type": "rf_sensor",
      "labels": {}
    },
    "chain": {
      "stream_id": "rf/sensor-01/band-2450MHz",
      "seq": 1
    },
    "retention": {
      "raw_available_until_us": 1738972800000000,
      "policy_id": "rolling-7d"
    },
    "fidelity": {
      "profile_id": "rf.default.95",
      "profile_divt_id": "..."
    },
    "payload": {
      "rf": { ... }
    },
    "extensions": {}
  },
  "divt": { ... }
}
```

Key fields:
- **vector**: Which domain (`rfvector`, `pulsevector`, `flowvector`, `exchangevector`, `videovector`)
- **record_type**: Specific record subtype within that domain
- **time**: Microsecond timestamps (integers, not floats)
- **chain**: Stream identity and sequence for ordering
- **payload**: Domain-specific data (varies by vector type)

## Step 2: Add the DIVT

The DIVT (Data Integrity Validation Token) proves your record hasn't been tampered with:

```json
{
  "divt": {
    "divt_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "tenant_id": "your-tenant",
    "hash_b64": "base64-encoded-sha3-512-hash",
    "hash_mode": "json_canon_v1",
    "hash_version": "sha3-512-v1",
    "crypto_mode": "hybrid",
    "signatures": {
      "key_ver": "v1",
      "ecdsa": "base64-signature",
      "pqc": "base64-signature"
    },
    "signature_version": "keyset-v1",
    "ledger_status": "pending",
    "revoked": false,
    "created_at": "2025-02-01T12:00:00Z"
  }
}
```

To compute `hash_b64`:
1. Take the `record` object
2. Canonicalize it (sorted keys, no floats, compact JSON)
3. Compute SHA3-512
4. Base64-encode the result

See [Canonicalization](concepts/canonicalization.md) for exact rules.

## Step 3: Validate Your Output

Use the JSON schemas to validate:

```bash
# Using Python jsonschema
pip install jsonschema

python -c "
import json, jsonschema
with open('schemas/vectorforge-vector.schema.json') as f:
    schema = json.load(f)
with open('your-record.jsonl') as f:
    for line in f:
        data = json.loads(line)
        jsonschema.validate(data['record'], schema)
        print('Valid!')
"
```

Or use the reference validator in `reference/python/`.

## Step 4: Test Canonicalization

Your canonicalization must match the reference implementation exactly. Run against the test vectors:

```bash
cd reference/python
python json_canon_v1.py --test ../test-vectors/json_canon_v1_test_vectors.json
```

## What's Next

- **Understand fidelity**: [Fidelity Concepts](concepts/fidelity.md)
- **Choose the right vector**: [Vector Overview](concepts/overview.md)
- **Achieve conformance**: [Conformance Levels](conformance/levels.md)
- **Run benchmarks**: [Benchmark Contract](../bench/CONTRACT.md)

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| Timestamps | Integer microseconds since Unix epoch |
| Floats | Not allowed in records (use fixed-point or decimal strings) |
| Hash algorithm | SHA3-512 |
| Canonicalization | RFC 8785-inspired, but stricter (no floats, no duplicate keys) |
| Extensions | Must be namespaced (e.g., `com.yourcompany.feature`) |
