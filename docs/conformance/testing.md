# Conformance Testing

This guide explains how to test your implementation for conformance.

## Prerequisites

- Python 3.9+ with `jsonschema` package
- Your implementation's output as JSONL files

```bash
pip install jsonschema
```

## Quick Start

### 1. Validate Canonicalization

First, ensure your JSON canonicalization matches the reference:

```bash
cd reference/python
python json_canon_v1.py --test ../../test-vectors/json_canon_v1_test_vectors.json
```

All test cases must pass. If any fail, fix your canonicalization before proceeding.

### 2. Validate Manifest Commitment

Test your Merkle root computation:

```bash
cd reference/python
python manifest_commitment.py --test ../../test-vectors/manifest_commitment_test_vectors.json
```

### 3. Validate Your Records

Use the reference validator on your output:

```bash
python reference/python/validator.py \
  --records your-output.jsonl \
  --level A
```

For higher levels:

```bash
# Level B (with manifest)
python reference/python/validator.py \
  --records your-output.jsonl \
  --manifest your-manifest.jsonl \
  --level B

# Level C (with profile)
python reference/python/validator.py \
  --records your-output.jsonl \
  --manifest your-manifest.jsonl \
  --profile your-profile.json \
  --level C
```

## Test Vector Files

### json_canon_v1_test_vectors.json

Tests JSON canonicalization:

```json
{
  "cases": [
    {
      "name": "sorted_keys",
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

Your implementation must:
- Produce identical canonical output for valid cases
- Reject invalid cases with appropriate errors

### manifest_commitment_test_vectors.json

Tests Merkle root computation:

```json
{
  "cases": [
    {
      "case": "merkle_zero_leaves",
      "leaf_hashes_b64": [],
      "expected_root_b64": "..."
    },
    {
      "case": "merkle_three_leaves_dup",
      "leaf_hashes_b64": ["...", "...", "..."],
      "expected_root_b64": "..."
    }
  ]
}
```

Your implementation must match the expected root for all cases.

## Running the Benchmark

For Level D conformance:

```bash
# Generate or obtain reference data
# (use starter datasets for initial testing)

# Run benchmark
python bench/run_benchmark.py \
  --profile bench/datasets/rf_starter/profile.json \
  --reference bench/datasets/rf_starter/reference.jsonl \
  --vectors bench/datasets/rf_starter/vector.jsonl \
  --manifest bench/datasets/rf_starter/manifest.jsonl \
  --output report.json

# Check results
cat report.json | python -m json.tool
```

Expected output:

```json
{
  "run_id": "...",
  "generated_at": "2025-02-01T12:00:00Z",
  "profile_id": "rf.default.95",
  "windows": [
    {
      "stream_id": "rf/sensor-01/band-2450MHz",
      "start_us": 1738368000000000,
      "end_us": 1738368020000000,
      "pf": 0.95,
      "cc": 1.0,
      "ef": 0.95
    }
  ]
}
```

## Common Failures

### Hash Mismatch

```
AssertionError: Hash mismatch: expected abc123..., got def456...
```

Causes:
- Floats in your JSON (must be integers)
- Keys not sorted
- Wrong separators (must be compact, no spaces)
- Wrong encoding (must be UTF-8)

Fix: Compare your canonical output byte-by-byte against the reference.

### Schema Validation Error

```
jsonschema.ValidationError: 'required_field' is a required property
```

Causes:
- Missing required fields
- Wrong field types
- Extra fields (schemas use `additionalProperties: false`)

Fix: Check the schema and ensure all required fields are present with correct types.

### Manifest Count Mismatch

```
AssertionError: Expected 20 records, got 19
```

Causes:
- Records dropped during processing
- Wrong window bounds
- Manifest generated before all records

Fix: Ensure all records are written before generating the manifest.

### Merkle Root Mismatch

```
AssertionError: Merkle root mismatch
```

Causes:
- Records not sorted by `seq`
- Using wrong hash input (should be `divt.hash_b64`)
- Different padding behavior for odd leaf counts

Fix: Review the manifest commitment algorithm in the spec and reference implementation.

## Creating Test Datasets

For thorough testing, generate your own test data:

```bash
# RF dataset
python bench/generate_rf_dataset.py

# Pulse dataset
python bench/generate_pulse_dataset.py
```

Then run conformance tests against the generated data.

## Reporting Results

When claiming conformance, include:

1. **Spec version**: e.g., "0.1.7"
2. **Conformance level**: A, B, C, or D
3. **Vector types tested**: e.g., "rfvector, pulsevector"
4. **Test environment**: Language, OS, relevant versions
5. **Test results**: Pass/fail counts, any notes

Example:

```
VectorForge Open Vectors Conformance Report
-------------------------------------------
Spec Version: 0.1.7
Level: C
Vectors: rfvector

Test Results:
- Canonicalization: 15/15 passed
- Manifest commitment: 7/7 passed
- Schema validation: 100/100 records passed
- Profile binding: Valid

Environment: Python 3.11, Ubuntu 22.04
```
