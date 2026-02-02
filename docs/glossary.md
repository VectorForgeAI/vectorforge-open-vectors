# Glossary

Key terms used in the VectorForge Open Vectors specification.

## A

**Artifact**
A raw data blob (IQ capture, PCAP segment, video file, etc.) referenced by a Vector record but not embedded in it. Artifacts are stored separately with rolling retention.

## C

**Canonicalization**
The process of converting JSON to a deterministic byte representation for hashing. VectorForge uses `json_canon_v1`: sorted keys, compact format, no floats, UTF-8 encoding.

**CBS (Context Basis Set)**
A defined set of extractors and weights used to measure fidelity. Each extractor computes a similarity score between reference data and Vector records.

**CC (Completeness Confidence)**
The ratio of received records to expected records for a time window. `CC = N_received / N_expected`. Undefined if continuity tracking is not enabled.

**Continuity**
The mechanism for proving a Vector stream is complete. Four levels: 0 (integrity only), 1 (gap detection), 2 (window manifests), 3 (tamper-evident chaining).

**Crypto Mode**
The signature scheme used in a DIVT: `fips` (ECDSA P-521), `pqc` (ML-DSA-65), or `hybrid` (both).

## D

**DIVT (Data Integrity Validation Token)**
A cryptographic receipt attached to every Vector record. Contains a hash of the record, signatures, and ledger anchoring status. Proves authenticity and integrity.

## E

**EF (End-to-End Fidelity)**
The combined fidelity metric: `EF = PF × CC`. Captures both context preservation and completeness. Cannot be computed if CC is undefined.

**Envelope**
The common record structure shared by all Vector types. Contains schema info, timestamps, source, chain, retention, fidelity reference, payload, and extensions.

**Extensions**
Namespaced fields for vendor- or deployment-specific data. Must use reverse-domain naming (e.g., `com.vendor.feature`). Located at `record.extensions` or `payload.<vector>.extensions`.

## F

**Fidelity**
Measurable context preservation. How well Vector records retain the information needed to reach the same conclusions as the original raw data.

**Fidelity Profile**
A signed configuration manifest specifying vectorization parameters: window sizes, feature extraction, quantization, target PF, and CBS weights.

**Fixed-Point**
Integer representation of fractional values with an implicit scale. Example: Q15 uses integers 0-32768 to represent 0.0-1.0. Used because floats are forbidden in canonicalized JSON.

## H

**Hash Mode**
How content is prepared for hashing. `json_canon_v1` for Vector records (canonicalized JSON), `binary_v1` for raw artifacts (raw bytes), `text_v1` for plain text.

## J

**JSONL**
JSON Lines format. Each line is a complete, valid JSON object. Vector records are stored and transmitted as JSONL.

## L

**Ledger Anchoring**
Writing a DIVT's hash to an immutable ledger for stronger auditability. Status tracked in `divt.ledger_status`: pending, anchored, retry, failed.

## M

**Manifest**
A `manifest_v1` record that commits to the set of records in a time window. Contains expected count and Merkle root for completeness verification (Continuity Level 2).

**Merkle Root**
A cryptographic commitment to a set of records. Computed by building a binary tree where each node is `SHA3-512(left || right)`. Used in manifests for set completeness verification.

## P

**Payload**
The domain-specific data in a Vector record. Located at `record.payload.<vector>` (e.g., `record.payload.rf` for RFVector).

**PF (Package Fidelity)**
Context fidelity computed using only Vector records, without retrieving raw artifacts. The metric users tune to balance fidelity vs. resources.

**Profile**
See *Fidelity Profile*.

## Q

**Q15**
A fixed-point encoding where integers 0-32768 represent floating-point values 0.0-1.0. Convert: `float = q15_value / 32768`. Used for weights and scores.

## R

**RawRef**
A reference to a raw artifact stored outside the Vector record. Contains artifact ID, URI, time bounds, content type, and the artifact's DIVT ID.

**Record**
The signed content portion of a Vector JSONL line. Contains the envelope and payload. The `record` object is what gets hashed for the DIVT.

**Recoverable Fidelity**
Context fidelity computed with access to raw artifacts (within retention). Approaches 100% while raw data is available.

## S

**Schema**
A JSON Schema document defining the structure of Vector records, payloads, profiles, or other objects. Used for validation.

**Seq (Sequence Number)**
A monotonically increasing integer per stream, used for ordering and gap detection. Located at `record.chain.seq`.

**Stream ID**
An identifier for a logical stream of records from a single source. Located at `record.chain.stream_id`. Example: `rf/sensor-01/band-2450MHz`.

## T

**Tenant ID**
An identifier for the tenant (organization/account) that owns the data. Used for multi-tenant isolation. Located at `record.tenant_id` and `divt.tenant_id`.

**Time Bounds**
The time range covered by a record. Uses closed-open semantics: `[start_us, end_us)`. All timestamps are integer microseconds since Unix epoch.

## V

**Vector**
A domain-specific record format. Five types: RFVector (radio frequency), PulseVector (network), FlowVector (content streams), ExchangeVector (financial), VideoVector (video).

**Vector Package**
The JSONL records that are transmitted, stored, and indexed. Compact compared to raw data. Contrast with *Raw Store*.

**Vectorizer**
A system that transforms raw telemetry into Vector records according to a Fidelity Profile.

## W

**Window**
A time range `[start_us, end_us)` used for segmentation, manifests, and fidelity measurement.
