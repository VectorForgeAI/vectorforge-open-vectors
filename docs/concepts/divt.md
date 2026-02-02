# DIVT: Data Integrity Validation Tokens

## What is a DIVT?

A DIVT (Data Integrity Validation Token) is a cryptographic receipt that proves:
1. **Authenticity**: The record was produced by a trusted source
2. **Integrity**: The record has not been modified since signing
3. **Non-repudiation**: The producer cannot deny creating the record

Every Vector record includes a DIVT alongside the record payload.

## Structure

```json
{
  "divt": {
    "divt_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "tenant_id": "your-tenant",
    "hash_b64": "Wm9yZy4uLg==",
    "hash_mode": "json_canon_v1",
    "hash_version": "sha3-512-v1",
    "crypto_mode": "hybrid",
    "signatures": {
      "key_ver": "v1",
      "ecdsa": "MEUCIQDx...",
      "pqc": "MIIBoj..."
    },
    "signature_version": "keyset-production-v2",
    "ledger_status": "anchored",
    "ledger_tx_id": "abc123",
    "revoked": false,
    "created_at": "2025-02-01T12:00:00Z"
  }
}
```

## Key Fields

### Identification
- **divt_id**: Unique identifier for this DIVT (UUID)
- **tenant_id**: Which tenant this DIVT belongs to

### Hash
- **hash_b64**: Base64-encoded hash of the `record` object
- **hash_mode**: How the content was prepared for hashing
- **hash_version**: Hash algorithm used (must be `sha3-512-v1`)

### Signatures
- **crypto_mode**: Signature scheme (`fips`, `pqc`, or `hybrid`)
- **signatures**: The actual signature(s)
- **signature_version**: Which keyset was used to sign

### Lifecycle
- **ledger_status**: Anchoring state (`pending`, `anchored`, `retry`, `failed`)
- **ledger_tx_id**: Transaction ID if anchored
- **revoked**: Whether this DIVT has been invalidated
- **created_at**: When the DIVT was created (ISO 8601)

## Hash Modes

Three hash modes exist for different content types:

| Mode | Use For | Canonicalization |
|------|---------|------------------|
| `json_canon_v1` | Vector records | Yes (sorted keys, no floats) |
| `binary_v1` | Raw artifacts (IQ, PCAP, video) | None (raw bytes) |
| `text_v1` | Plain text content | Line ending normalization |

Vector records MUST use `json_canon_v1`.

## Crypto Modes

Three cryptographic modes support different deployment requirements:

| Mode | Algorithms | Use When |
|------|------------|----------|
| `fips` | ECDSA P-521 only | FIPS 140-2/3 compliance required |
| `pqc` | ML-DSA-65 only | Post-quantum only environments |
| `hybrid` | ECDSA P-521 + ML-DSA-65 | Default; provides both classical and PQ security |

Verifiers MUST support all three modes. Producers SHOULD emit `hybrid` by default.

## Computing the Hash

For `json_canon_v1`, the process is:

1. Take the `record` object (not the full JSONL line, just `record`)
2. Canonicalize:
   - Sort all object keys lexicographically
   - Use compact separators (no whitespace)
   - Ensure no floating-point numbers
   - Ensure all integers are within safe range (±2^53-1)
3. Encode as UTF-8 bytes
4. Compute SHA3-512
5. Base64-encode the 64-byte digest

See [Canonicalization](canonicalization.md) for detailed rules.

## Verifying a DIVT

To verify a record's integrity:

1. Extract the `record` object from the JSONL line
2. Canonicalize it using `json_canon_v1` rules
3. Compute SHA3-512 and base64-encode
4. Compare to `divt.hash_b64` - must match exactly
5. Verify the signature(s) against the hash using the keyset identified by `signature_version`

If any step fails, the record MUST be rejected.

## Ledger Anchoring

DIVTs can optionally be anchored to an immutable ledger for stronger auditability:

| Status | Meaning |
|--------|---------|
| `pending` | Signed but not yet anchored |
| `anchored` | Written to ledger (check `ledger_tx_id`) |
| `retry` | Anchoring failed, will retry |
| `failed` | Permanent failure after max retries |

Anchoring is RECOMMENDED but not REQUIRED for conformance. Records with `ledger_status: "pending"` are still valid if signatures verify.

## Revocation

DIVTs can be revoked if a record needs to be invalidated (e.g., data retraction, policy change). Check `revoked: true` before trusting a record.

## What DIVTs Don't Do

DIVTs prove integrity and authenticity. They do NOT:
- Encrypt the record (records are plaintext)
- Guarantee delivery (that's transport's job)
- Prove completeness (that's Continuity's job - see [continuity.md](continuity.md))

## Implementation Notes

- DIVT signing should happen synchronously at ingest time
- Ledger anchoring can happen asynchronously
- The `metadata` field in DIVT service APIs is NOT hashed - don't put audit-critical data there
- Records exceeding 1MB must use hash-only registration (pass `hash_b64`, not full content)
