# Continuity: Proving Stream Completeness

## The Problem

High fidelity per record means nothing if records are missing. A system cannot claim 95% fidelity if it silently dropped 50% of the data.

**Continuity** is the mechanism for proving that a Vector stream is complete for a given time window.

## Completeness Confidence (CC)

For any stream window `[t0, t1]` and `stream_id`:

```
CC = N_received / N_expected
```

Where:
- `N_received` = number of Vector records actually received
- `N_expected` = number of records that should exist

If CC is undefined (no way to know N_expected), you cannot compute End-to-End Fidelity (EF).

## Continuity Levels

Four levels of continuity tracking, with increasing completeness guarantees:

### Level 0: Integrity Only (Baseline)

- Each record has a valid DIVT
- No cross-record validation
- `N_expected` is undefined, so CC is undefined
- EF cannot be computed

**Use when**: Transport already guarantees delivery, or you accept unknown completeness.

### Level 1: Gap Detection

- Records include `stream_id` and `seq` (monotonic sequence number)
- `N_expected = seq_max - seq_min + 1`
- Gaps detected via sequence discontinuities
- Lightweight, no additional records needed

**Use when**: You need basic completeness signals with minimal overhead.

### Level 2: Window Manifests (Recommended)

- Periodic `manifest_v1` records emitted per stream and window
- Manifest includes:
  - Window bounds (`start_us`, `end_us`)
  - Expected record count
  - Merkle root commitment over record hashes
- `N_expected = manifest.expected_count`
- Completeness verified by reconciling against manifest

**Use when**: You need strong completeness guarantees. This is the production minimum.

### Level 3: Tamper-Evident Chaining

- Each record includes `prev_divt_id` linking to the previous record
- Forms a hash chain within the stream
- Verifier validates both DIVTs and chain links
- Detects adversarial deletion or insertion

**Use when**: Threat model includes active attackers manipulating the stream.

## Manifest Records

For Level 2, `manifest_v1` records commit to the set of records in a window:

```json
{
  "record": {
    "schema": {"name": "vectorforge.vector", "version": "0.1.7"},
    "vector": "rfvector",
    "record_type": "manifest_v1",
    "record_id": "uuid",
    "tenant_id": "...",
    "time": {"start_us": 1738368000000000, "end_us": 1738368020000000, "observed_us": ...},
    "source": {...},
    "chain": {"stream_id": "rf/sensor-01/band-2450MHz", "seq": 21},
    "payload": {
      "kind": "manifest_v1",
      "stream_id": "rf/sensor-01/band-2450MHz",
      "window": {"start_us": 1738368000000000, "end_us": 1738368020000000},
      "expected_count": 20,
      "commitment": {
        "algo": "merkle_sha3_512_v1",
        "root_b64": "base64-merkle-root",
        "input": "divt.hash_b64",
        "ordering": "seq_asc"
      }
    }
  },
  "divt": {...}
}
```

## Merkle Commitment

The manifest's `commitment.root_b64` is a Merkle tree root computed from record hashes:

1. Filter records to the window `[t0, t1]` for the `stream_id`
2. Sort by `seq` ascending
3. Extract `divt.hash_b64` from each record, base64-decode to bytes
4. Build Merkle tree: `internal_node = SHA3-512(left || right)`
5. If odd number of nodes at a level, duplicate the last node
6. Root is the final node; base64-encode

Reference implementations and test vectors are provided in `reference/` and `test-vectors/`.

## Verifying Completeness

To verify a window at Level 2:

1. Collect all records for `stream_id` in `[start_us, end_us)`
2. Find the `manifest_v1` record for that window
3. Check `len(records) == manifest.expected_count`
4. Recompute Merkle root from record hashes
5. Compare to `manifest.commitment.root_b64`

If both match, CC = 1.0. If count mismatches, CC = received/expected.

## Profile Declaration

Every Fidelity Profile MUST declare:

```json
{
  "continuity_level": 2,
  ...
}
```

This tells verifiers what completeness guarantees to expect.

## Time Bounds

Time ranges use closed-open semantics: `[start_us, end_us)`

- `start_us` is inclusive
- `end_us` is exclusive
- For instantaneous events: `end_us = start_us + 1`
- Records at exactly `end_us` belong to the next window

This prevents double-counting at window boundaries.

## Production Requirements

**Deployments claiming production-grade completeness MUST implement Level 2 or higher.**

If continuity level is 0 or 1, external reporting must clearly state: "Completeness unproven. EF not computed."

## What's Next

- [Fidelity](fidelity.md) - How EF combines PF and CC
- [Benchmark Contract](../bench/CONTRACT.md) - How manifests are validated in benchmarks
