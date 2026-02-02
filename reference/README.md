# Reference Implementations

This directory contains normative reference implementations for VectorForge Open Vectors.

## Languages

- [Python](python/) - Python 3.9+ implementations
- [Go](go/) - Go 1.21+ implementations

## What's Included

### JSON Canonicalization (`json_canon_v1`)

Canonicalizes JSON for deterministic hashing:
- Sorts object keys lexicographically
- Uses compact separators (no whitespace)
- Rejects floats and out-of-range integers
- Encodes as UTF-8

### Manifest Commitment (`manifest_commitment`)

Computes Merkle roots for Continuity Level 2 manifests:
- SHA3-512 hash function
- Duplicate-last padding for odd leaf counts
- Base64 encoding

### Validator (Python only)

Validates records for conformance levels A, B, and C:
- Schema validation
- Hash verification
- Manifest verification
- Profile binding checks

## Normative Status

These implementations are **normative**. If your implementation produces different output for the same input, yours is non-conformant.

Test your implementation against the test vectors in `test-vectors/` to verify correctness.

## Usage

See the README in each language directory for usage instructions.
