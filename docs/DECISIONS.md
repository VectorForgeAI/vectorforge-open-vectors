# Architectural Decisions

This document records key decisions made in the VectorForge Open Vectors specification. These decisions are normative for v0.1.x implementations.

## D1: Vector Maturity Levels

**Decision**: Not all Vectors are at the same maturity level.

| Vector | Status | Meaning |
|--------|--------|---------|
| RFVector | Pilot-ready | Production-quality schema, comprehensive documentation, reference extractors |
| PulseVector | Design-ready | Stable schema, implementation in progress |
| FlowVector | Spec-first | Skeletal schema, will tighten as reference producers are built |
| ExchangeVector | Spec-first | Skeletal schema, will tighten as reference producers are built |
| VideoVector | Spec-first | Skeletal schema, will tighten as reference producers are built |

**Rationale**: RF domain has existing parsers and concrete requirements. Other domains are being specified ahead of implementation to enable parallel development.

## D2: Conformance Levels A-D

**Decision**: Define four conformance levels that implementations can claim.

| Level | Name | Requirements |
|-------|------|--------------|
| A | Record Integrity | Envelope validates, DIVT validates, hash_b64 matches canonicalized record |
| B | Completeness | Implements Continuity Level 2 (manifest_v1), computes CC and EF correctly |
| C | Payload + Profile | Payload validates against vector payload schema, profile validates, records reference valid profile |
| D | Benchmark | Runs bench harness, produces PF/CC/EF reports per CONTRACT.md |

**Rationale**: Allows incremental adoption. A producer can start with Level A (valid records) and progress to Level D (full fidelity measurement) as their implementation matures.

## D3: Merkle is the Only Normative Manifest Algorithm

**Decision**: For v0.1.x, `merkle_sha3_512_v1` is the only normative commitment algorithm for Continuity Level 2 manifests.

The schema may reference `rolling_sha3_512_v1` but it is **reserved for future use** and not normative until:
- The algorithm is fully specified
- Test vectors are provided
- Reference implementations exist

**Rationale**: Ship what we can test. Rolling commitments require additional specification work.

## D4: hash_version is "sha3-512-v1"

**Decision**: The `hash_version` field in DIVT objects MUST be the string `"sha3-512-v1"`.

Any examples, generators, or implementations using `"1"` or other values are non-conformant and should be corrected.

**Rationale**: Explicit version strings enable future hash algorithm transitions without ambiguity.

## D5: Apache 2.0 License

**Decision**: The Open Vectors specification, schemas, reference implementations, and tooling are licensed under Apache 2.0.

**Rationale**: Apache 2.0 provides broad permissive use with an explicit patent grant, which is appropriate for standards-adjacent work where patent clarity matters.

## D6: Time Bounds Semantics

**Decision**: Time ranges in records use closed-open semantics: `[start_us, end_us)`.

- `start_us` is inclusive
- `end_us` is exclusive
- For instantaneous events, set `end_us = start_us + 1` (one microsecond window)
- `end_us` MUST be greater than or equal to `start_us`
- `observed_us` is when the system recorded the event, separate from the event window

**Rationale**: Closed-open semantics avoid double-counting at window boundaries and make manifest windowing deterministic.

## D7: No Floats in Canonicalized JSON

**Decision**: JSON records hashed with `json_canon_v1` MUST NOT contain floating-point numbers.

Represent fractional values as:
- Fixed-point integers with explicit scale (e.g., `snr_db_q8`, `weight_q15`)
- Decimal strings for values requiring exact decimal semantics (e.g., currency)
- Integer microseconds for timestamps

**Rationale**: Floating-point representation varies across platforms and languages. Integers ensure deterministic canonicalization and cross-platform hash agreement.

## D8: Extensions for Vendor-Specific Data

**Decision**: Vendor- or deployment-specific data MUST use designated extension points:
- `record.extensions` for record-level extensions
- `payload.<vector>.extensions` for payload-level extensions

Extensions MUST be namespaced by reverse-domain (e.g., `com.vendor.feature`).

**Rationale**: Keeps core schemas stable and interoperable while allowing experimentation.
