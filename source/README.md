# VectorForge Open Vectors Spec Package (v0.1.7)

This package contains the VectorForge open Vector schemas, integrity artifacts, test vectors, reference implementations, and a starter benchmark harness. Use it to implement producers, validators, and ingestion pipelines for RFVector, PulseVector, FlowVector, ExchangeVector, and VideoVector.

## Start here

1. Read **`vectorforge-vectors-spec-v0.1.7.md`** (the spec).
2. Validate records with the JSON Schemas:
   - `vectorforge-vector.schema.json` (Vector Record envelope)
   - `divt.schema.json` (DIVT)
   - `vectorforge-rawref.schema.json` (RawRef)
   - `vectorforge-profile.schema.json` (Fidelity Profiles)
   - `vectorforge-manifest.schema.json` (manifest_v1 payload)
   - `vectorforge-error.schema.json` (standard error payload)
3. Run canonicalization and commitment tests using the reference code:
   - `reference/json_canon_v1.py --test ../json_canon_v1_test_vectors.json`
   - `reference/manifest_commitment.py --test ../manifest_commitment_test_vectors.json`
4. Run the starter benchmark:
   - `python bench/run_benchmark.py bench/datasets/rf_starter`
   - `python bench/run_benchmark.py bench/datasets/pulse_starter`

## What each file is

### Specification
- **`vectorforge-vectors-spec-v0.1.7.md`**  
  The primary spec. Defines the record envelope, vector types, RawRef references, DIVT integration, canonicalization rules, fidelity and completeness (PF/CC/EF), continuity capability levels, and manifest commitments.

### DIVT integrity artifacts
- **`DIVT-SCHEMA.md`**  
  Human-readable reference for DIVTs: fields, limits, hash modes, crypto modes, ledger status semantics, and service API patterns.

- **`divt.schema.json`**  
  The authoritative JSON Schema for DIVTs embedded in every record.

### Validation schemas
- **`vectorforge-vector.schema.json`**  
  Validates the top-level `{record, divt}` structure and strict envelope fields.

- **`vectorforge-profile.schema.json`**  
  Validates Fidelity Profile manifests.

- **`vectorforge-rawref.schema.json`**  
  Validates raw artifact references (IQ, PCAP, video segments, HTML, etc.).

- **`vectorforge-manifest.schema.json`**  
  Validates `manifest_v1` payloads used for Continuity Level 2 completeness confidence.

- **`vectorforge-error.schema.json`**  
  Validates the standard `payload.error` object used by `*_error_v1` record types.

- **Payload schemas (baseline, stricter than v0.1.6)**
  - `rfvector.payload.schema.json`
  - `pulsevector.payload.schema.json`
  - `flowvector.payload.schema.json`
  - `exchangevector.payload.schema.json`
  - `videovector.payload.schema.json`

### Test vectors (conformance)
- **`json_canon_v1_test_vectors.json`**  
  Positive and negative canonicalization cases. Use it to ensure cross-language canonicalizers produce identical canonical JSON and SHA3-512 hashes, and reject forbidden inputs (floats, duplicate keys, out-of-range integers, malformed JSON).

- **`manifest_commitment_test_vectors.json`**  
  Merkle commitment cases for Continuity Level 2 manifests. Covers empty, odd, even, and identical-leaf inputs.

### Reference implementations
- **`reference/json_canon_v1.py`**, **`reference/json_canon_v1.go`**  
  Reference implementations for `json_canon_v1` canonicalization and hashing.

- **`reference/manifest_commitment.py`**, **`reference/manifest_commitment.go`**  
  Reference implementations for Merkle root commitment computation.

### Examples
- **`examples/README.md`**  
  Explains the example files.

- **`examples/profile-*.json`**  
  Example Fidelity Profiles.

- **`examples/example-*.jsonl`** and **`examples-vector-record.jsonl`**  
  Example Vector Record(s) with computed `divt.hash_b64`. Signatures are placeholders in examples because this package does not ship private keys.

### Benchmark harness
- **`bench/CONTRACT.md`**  
  Defines the on-disk layout and output format for benchmark runs.

- **`bench/datasets/*`**  
  Starter RF and Pulse datasets with reference context, vector records, and manifests.

- **`bench/run_benchmark.py`**  
  A starter scoring runner that produces PF/CC/EF reports for the starter datasets.

- **`bench/generate_rf_dataset.py`**, **`bench/generate_pulse_dataset.py`**  
  Regenerates the starter datasets deterministically.

### Interim RF parser mapping
- **`rf-parser-events.md`**  
  Documents current rf.capture outputs and how to map them into RFVector records.
