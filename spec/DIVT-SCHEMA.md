# DIVT Schema Reference

This document provides the complete schema definition for **Data Integrity Validation Tokens (DIVT)** as implemented in VectorForge DataFoundry.

## Overview

A DIVT is a cryptographically signed token that proves content integrity. It combines:
- **SHA3-512 hashing** of canonicalized content
- **Hybrid digital signatures** (ECDSA P-521 + ML-DSA-65) for quantum-safe transition
- **Immutable ledger anchoring** via ImmuDB for tamper-evidence

## JSON Schema

The full JSON Schema is available at [`divt.schema.json`](./divt.schema.json).

## Core Types

### DIVT

The primary data structure representing a Data Integrity Validation Token.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `divt_id` | string (UUID) | Yes | Unique identifier |
| `tenant_id` | string | Yes | Tenant identifier (single-tenant mode) |
| `hash_b64` | string | Yes | Base64-encoded SHA3-512 hash (64 bytes) |
| `hash_mode` | HashMode | Yes | Canonicalization mode used |
| `hash_version` | string | Yes | Always `"sha3-512-v1"` |
| `crypto_mode` | CryptoMode | No | Signing mode (default: `"hybrid"`) |
| `signatures` | Signatures | Yes | Cryptographic signatures |
| `signature_version` | string | Yes | Key version used for signing |
| `metadata` | object | No | Arbitrary JSON (max 4KB, not hashed) |
| `ledger_status` | LedgerStatus | Yes | ImmuDB anchoring status |
| `ledger_tx_id` | string | No | ImmuDB transaction ID (when anchored) |
| `revoked` | boolean | Yes | Revocation status |
| `revoked_at` | datetime | No | Revocation timestamp |
| `revocation_reason` | string | No | Reason for revocation |
| `created_at` | datetime | Yes | Creation timestamp |

### HashMode

Canonicalization mode for content before hashing.

| Value | Description |
|-------|-------------|
| `text_v1` | Plain text: UTF-8 normalized, BOM stripped, line endings normalized to LF |
| `json_canon_v1` | JSON: sorted keys, no floats, integers within safe range |
| `binary_v1` | Binary: raw bytes, no canonicalization |

### LedgerStatus

ImmuDB anchoring status.

| Value | Description |
|-------|-------------|
| `pending` | Queued for anchoring |
| `anchored` | Written to ImmuDB with transaction ID |
| `retry` | Anchoring failed, will retry with exponential backoff |
| `failed` | Permanent failure after max retries (5 attempts) |

### CryptoMode

Signing algorithm selection.

| Value | Algorithms | Description |
|-------|------------|-------------|
| `fips` | ECDSA P-521 | FIPS 186-5 compliant signing |
| `pqc` | ML-DSA-65 | Post-quantum only (NIST FIPS 204) |
| `hybrid` | ECDSA P-521 + ML-DSA-65 | Both signatures for quantum transition |

### Signatures

Cryptographic signature container.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ecdsa` | string | Conditional | Base64-encoded ECDSA P-521 signature |
| `pqc` | string | Conditional | Base64-encoded ML-DSA-65 signature |
| `key_ver` | string | Yes | Key version identifier (e.g., `"v1"`) |

## Database Schema

SQLite with WAL mode enabled. All writes serialized through a single-writer queue.

### `divts` Table

```sql
CREATE TABLE divts (
    divt_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    hash_b64 TEXT NOT NULL,
    hash_mode TEXT NOT NULL,
    hash_version TEXT NOT NULL DEFAULT 'sha3-512-v1',
    crypto_mode TEXT DEFAULT 'hybrid',
    signatures_json TEXT NOT NULL,
    signature_version TEXT NOT NULL,
    metadata_json TEXT,
    dataset_id TEXT,
    ledger_status TEXT NOT NULL DEFAULT 'pending',
    ledger_tx_id TEXT,
    revoked INTEGER NOT NULL DEFAULT 0,
    revoked_at TEXT,
    revocation_reason TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    last_retry TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indexes
CREATE INDEX idx_divts_ledger_status ON divts(ledger_status);
CREATE INDEX idx_divts_created_at ON divts(created_at);
CREATE INDEX idx_divts_tenant ON divts(tenant_id);
CREATE INDEX idx_divts_dataset_id ON divts(dataset_id) WHERE dataset_id IS NOT NULL;
```

### `keys` Table

Cryptographic signing keys (encrypted at rest).

```sql
CREATE TABLE keys (
    key_id TEXT PRIMARY KEY,
    version TEXT NOT NULL UNIQUE,
    algorithm TEXT NOT NULL,
    public_key BLOB NOT NULL,
    encrypted_private_key BLOB NOT NULL,
    nonce BLOB NOT NULL,
    salt BLOB NOT NULL,
    is_current INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_keys_current ON keys(is_current) WHERE is_current = 1;
CREATE INDEX idx_keys_version ON keys(version);
```

## API Request/Response Types

### RegisterRequest (POST /v1/register)

```json
{
  "content": "base64-encoded-content",  // OR hash_b64, not both
  "hash_b64": "base64-sha3-512-hash",   // OR content, not both
  "hash_mode": "text_v1",               // Required
  "metadata": { "key": "value" }        // Optional, max 4KB
}
```

### VerifyRequest (POST /v1/verify)

```json
{
  "divt_id": "uuid",                    // Required
  "content": "base64-encoded-content",  // OR hash_b64, not both
  "hash_b64": "base64-sha3-512-hash"    // OR content, not both
}
```

### VerifyResult

```json
{
  "verified": true,
  "hash_match": true,
  "ecdsa_valid": true,
  "pqc_valid": true,
  "ledger_status": "anchored",
  "revoked": false,
  "failure_reason": null
}
```

### RevokeRequest (POST /v1/divts/{id}/revoke)

```json
{
  "reason": "Content was retracted"
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_INPUT` | 400 | Malformed request (bad JSON, invalid base64, floats in json_canon_v1, etc.) |
| `UNAUTHORIZED` | 401 | Bad or missing API key |
| `NOT_FOUND` | 404 | DIVT does not exist |
| `HASH_MISMATCH` | 200 | Verification result: content doesn't match stored hash |
| `SIGNATURE_INVALID` | 200 | Verification result: signature verification failed |
| `LEDGER_UNAVAILABLE` | 503 | ImmuDB down and queue full |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## Content Limits

| Limit | Value |
|-------|-------|
| Maximum content size | 1 MB |
| Maximum metadata size | 4 KB |
| SHA3-512 hash length | 64 bytes (88 chars base64) |
| Safe integer range | -(2^53-1) to 2^53-1 |

## Cryptographic Details

### Hashing
- Algorithm: SHA3-512 (FIPS 202)
- Output: 64 bytes (512 bits)
- Version string: `"sha3-512-v1"`

### ECDSA Signing
- Curve: P-521 (secp521r1)
- Standard: FIPS 186-5
- Signature: DER-encoded

### Post-Quantum Signing
- Algorithm: ML-DSA-65 (formerly Dilithium)
- Standard: NIST FIPS 204
- Security level: NIST Level 3

### Key Encryption at Rest
- Algorithm: AES-256-GCM
- Key derivation: PBKDF2-SHA256 with 16-byte salt
- Nonce: 12 bytes

## Source Files

| File | Description |
|------|-------------|
| `pkg/divt/types.go` | Go type definitions (canonical) |
| `pkg/divt/errors.go` | Error codes and types |
| `internal/store/db.go` | Database schema migrations |
| `internal/store/store.go` | Store interfaces |
| `internal/divt/service.go` | DIVT creation service |
| `sdk/typescript/src/types.ts` | TypeScript type definitions |
| `sdk/python/src/divt/types.py` | Python type definitions |
