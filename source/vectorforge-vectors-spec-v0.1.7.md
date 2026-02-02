# VectorForge Vector Schemas & Fidelity Framework (Draft v0.1.7)

## 1. Purpose and scope

VectorForge defines a family of **open, JSONL-based “Vector” schemas** for capturing high-volume, high-fidelity signals from many domains (RF, networks, streaming content, video, and transactions). Each Vector schema provides:

- A **stable, vendor-friendly output format** for parsers and sensors.
- A **cryptographically verifiable integrity layer** (DIVTs) for every record.
- A **configurable fidelity model** that lets operators trade off fidelity vs. compute, bandwidth, and storage in real time.
- A **benchmark methodology** to quantify “context fidelity” academically and operationally.

This document is intended to be the foundation for an open-source release of the Vector family and associated tooling (schemas, examples, conformance tests, and fidelity benchmarks).

### 1.1 Normative references and included artifacts (normative)

This spec is shipped as a **stand-alone package**. To claim compliance, an implementation MUST use the exact artifacts shipped with the package (schemas, test vectors, and reference code). Do not rely on remote schema URLs at runtime.

**Normative artifacts**
- `vectorforge-vectors-spec-v0.1.7.md` (this document)
- `DIVT-SCHEMA.md` (DIVT semantics and service behavior)
- `divt.schema.json` (DIVT JSON Schema)
- `vectorforge-vector.schema.json` (Vector Record envelope schema)
- `vectorforge-profile.schema.json` (Fidelity Profile schema)
- `vectorforge-rawref.schema.json` (RawRef schema)
- `vectorforge-manifest.schema.json` (manifest_v1 schema for Continuity Level 2)
- `vectorforge-error.schema.json` (standard error payload schema)
- `rf-parser-events.md` (interim RF parser event outputs and mapping guidance)

**Normative test vectors**
- `json_canon_v1_test_vectors.json` (positive + negative canonicalization cases)
- `manifest_commitment_test_vectors.json` (Merkle commitment cases)

**Normative reference implementations**
- `reference/json_canon_v1.py` and `reference/json_canon_v1.go`
- `reference/manifest_commitment.py` and `reference/manifest_commitment.go`

**Benchmark harness contract and starters**
- `bench/CONTRACT.md` (benchmark input/output contract)
- `bench/generate_rf_dataset.py` and `bench/generate_pulse_dataset.py` (starter synthetic dataset generators)
- `bench/run_benchmark.py` (reference scoring skeleton producing PF/CC/EF)

Implementations MUST validate DIVTs against `divt.schema.json` and MUST follow the canonicalization constraints required by `hash_mode="json_canon_v1"`.

---

## 2. The Vector family

Each Vector is a *domain-specific payload* carried inside a common record envelope and integrity model.

### 2.1 RFVector
RFVector is a structured format for radio frequency observations that normalizes complex RF activity into consistent, integrity-protected records. The value to the customer is faster RF situational awareness and more scalable analysis across distributed sensors without losing decision-grade fidelity.

### 2.2 PulseVector
PulseVector is a structured format for network activity that unifies flow summaries, packet-derived metadata, and security-relevant logs into consistent, integrity-protected records. The value to the customer is clearer network visibility and simpler integrations that speed detection, investigation, and performance understanding at enterprise scale.

### 2.3 FlowVector
FlowVector is a structured format for high-volume content and event streams such as web scraping, social feeds, and other firehose-style sources that normalizes items into consistent, integrity-protected records. The value to the customer is rapid insight from massive streams with less engineering overhead to collect, correlate, and operationalize the data.

### 2.4 ExchangeVector
ExchangeVector is a structured format for financial and digital asset transactions that normalizes payment, settlement, and ledger events into consistent, integrity-protected records. The value to the customer is faster fraud and risk analysis, cleaner auditability, and simpler integration across fiat and crypto transaction sources.

### 2.5 VideoVector
VideoVector is a structured format for video activity that distills high-bandwidth footage into consistent, integrity-protected records using time-segmented summaries such as keyframes, motion cues, and tracked objects. The value to the customer is scalable video situational awareness and faster investigations without needing to move or store full video everywhere.

### 2.5.1 Record subtype registry (normative)

`record.record_type` identifies the subtype of a Vector Record. Baseline interoperable values are listed below. Implementations MAY add custom types, but MUST place custom details under `record.extensions` and MUST NOT claim baseline interoperability for custom types unless upstreamed.

- **RFVector**
  - `rf_capture_v1`
  - `rf_error_v1`
  - `manifest_v1` (Continuity Level 2)

- **PulseVector**
  - `flow_slice_v1`
  - `net_event_v1`
  - `net_error_v1`
  - `manifest_v1`

- **FlowVector**
  - `content_item_v1`
  - `content_error_v1`
  - `manifest_v1` (optional)

- **ExchangeVector**
  - `transaction_event_v1`
  - `transaction_error_v1`
  - `manifest_v1` (optional)

- **VideoVector**
  - `video_segment_v1`
  - `video_event_v1`
  - `video_error_v1`
  - `manifest_v1`


### 2.6 What each Vector package typically contains (and what stays in raw)

This section clarifies what “95–100% context fidelity” looks like operationally: the Vector package carries **context-rich derived representations** and **references** raw artifacts that are retained temporarily for “zoom-in” retrieval.

#### RFVector
- **Vector package contents (typical):**
  - capture envelope (center frequency, bandwidth, sampling rate, duration, sensor metadata)
  - wavelet fingerprints and/or spectral summaries (fixed-point)
  - detections (time/frequency bounds) and optional embeddings/classifier outputs
- **Raw references (rolling retention):**
  - full IQ captures (raw binary artifacts with deterministic addressing)
- **Primary fidelity knobs:**
  - window length / overlap
  - spectral resolution (Δf) and temporal resolution (Δt) of summaries
  - wavelet parameters (window_ms, decomp_level, normalization)
  - quantization scale

#### PulseVector
- **Vector package contents (typical):**
  - flow slices (5-tuple or session key, timing and volume stats)
  - protocol fingerprints and metadata (DNS, TLS handshake, HTTP metadata, etc.)
  - security events (IDS/Zeek-like summaries) when enabled
- **Raw references (rolling retention):**
  - PCAP segments (including encrypted payloads if collected)
- **Primary fidelity knobs:**
  - slice duration and sessionization rules
  - which protocol layers are summarized (L3/L4 only vs. L7 metadata)
  - feature inclusion (JA3/JA4, cert hashes, DNS answers, etc.)
  - sampling policy for high-volume flows

#### FlowVector
- **Vector package contents (typical):**
  - normalized item envelope (URI, timestamps, provenance, content type)
  - extracted text + structural features (links, entities, tags)
  - optional embeddings for retrieval and clustering
- **Raw references (rolling retention):**
  - raw HTML/JSON responses, media attachments
- **Primary fidelity knobs:**
  - extraction depth (full DOM vs. readability text)
  - embedding model selection and dimensionality
  - link graph retention vs. pruning
  - dedup thresholds

#### ExchangeVector
- **Vector package contents (typical):**
  - normalized lifecycle events (auth/capture/settle; pending/confirmed/reorg, etc.)
  - amounts/fees as decimal strings, parties, instrument/channel metadata
  - optional derived risk features (velocity, graph features) if enabled
- **Raw references (rolling retention):**
  - original processor payloads, bank files, on-chain receipt blobs as needed
- **Primary fidelity knobs:**
  - lifecycle normalization strictness (how you reconcile divergent sources)
  - rounding/precision rules per asset
  - enrichment depth (KYC fields, merchant metadata, chain analytics)
  - event batching vs. per-event emission

#### VideoVector
- **Vector package contents (typical):**
  - time-segmented summaries (shot boundaries, keyframes, motion summaries)
  - tracks/tracklets and optional event markers
  - optional embeddings for retrieval (“find the forklift”)
- **Raw references (rolling retention):**
  - original video segments (GOP-aligned when possible), optional audio
- **Primary fidelity knobs:**
  - segment length and keyframe cadence
  - motion representation (codec motion vectors vs. optical flow)
  - detector/tracker choice and confidence thresholds
  - track retention density (all tracks vs. filtered classes)
---

## 3. Core design principles

### 3.1 “Vector package” vs. “raw store”
Vectors are designed to preserve **context** without shipping the full raw stream by default.

- **Vector package**: the JSONL record(s) transmitted, stored, indexed, and compressed further (wavelets/tensors/LSM).
- **Raw store**: the original heavyweight artifacts retained on a rolling policy (IQ, PCAP payloads, full frames, raw HTML, etc.), referenced by the Vector package and retrievable when needed.

This enables two operational modes:
1) **Package-only mode**: analysis on the Vector records alone (fast, low bandwidth).
2) **Recoverable mode**: pull raw on demand within retention windows to re-derive deeper detail.

### 3.2 Multi-resolution by construction
Every Vector schema supports **multi-resolution representations** (short-window high detail + long-window summaries) and **cross-record linking** (session IDs, stream IDs, sequence numbers). This is essential because some phenomena are only visible at certain time scales.

### 3.3 Configurable fidelity
Fidelity is not hard-coded into the schema. Fidelity is controlled by **Fidelity Profiles** (config manifests) that are referenced from each record and cryptographically bound to the stream.

### 3.4 Deterministic and verifiable
Vector records are intentionally designed to be:
- deterministic (canonicalizable JSON)
- verifiable (hashable + signed)
- reproducible (benchmarked with fixed reference extractors)

---

## 4. Record model (common envelope)

All Vectors use the same high-level JSONL record structure:

- Each line is a standalone record (append-only).
- Each record includes:
  - **record**: the signed content envelope (schema name/version, source, time bounds, payload).
  - **divt**: a cryptographic Data Integrity Validation Token attesting to the record content hash.

**Note:** Because DIVT JSON canonicalization forbids floats, Vector records should encode real-valued quantities using fixed-point integers or decimal strings (see §6.6).  

### 4.1 Common record fields (normative)

- `record.schema.name`: `"vectorforge.vector"`
- `record.schema.version`: semantic version of the envelope spec.
- `record.vector`: one of `{rfvector, pulsevector, flowvector, exchangevector, videovector}`.
- `record.record_type`: record subtype within a vector (e.g., `segment_v1`, `event_v1`, `flow_slice_v1`).
- `record.record_id`: UUID.
- `record.tenant_id`: tenant identifier.
- `record.time`: `{start_us, end_us, observed_us}` with microsecond integers.
- `record.source`: `{source_id, source_type, labels}`.
- `record.chain`: `{stream_id, seq, prev_divt_id}` for ordering and tamper-evident chaining.
- `record.retention`: describes raw artifact availability window (rolling policy).
- `record.artifacts`: array of raw artifact references (see §5).
- `record.fidelity`: fidelity profile reference + knobs (see §7).
- `record.payload`: vector-specific payload object.
- `record.extensions`: reserved for vendor- or deployment-specific extensions.

---
### 4.2 Extensions and namespacing (normative)

`record.extensions` exists to carry vendor- or deployment-specific data without breaking interoperability.

Rules:
- Extensions MUST be namespaced by reverse-domain ownership, for example `com.example.feature` or `org.vendor.module`.
- Extensions MUST NOT redefine or shadow core field semantics.
- Extensions MUST remain JSON-canonicalizable under `hash_mode="json_canon_v1"` (no floats).
- Verifiers MUST ignore unknown extensions during semantic processing but MUST include `record.extensions` in hashing if present (because it lives inside the hashed `record` object).


## 5. Raw artifact references (“drop from package, keep recoverable”)

### 5.1 RawRef objects (normative)
Raw artifacts are not embedded in the record when they are too large, too sensitive, or simply not needed for routine analytics. Instead, the record includes **RawRef** entries:

- `artifact_id`: UUID
- `kind`: one of `{iq, pcap, video_segment, audio_segment, html, binary_blob, image_keyframe, ...}`
- `uri`: location in object storage or file system
- `time`: `{start_us, end_us}`
- `locator`: optional addressing (byte offsets, sample offsets, frame ranges)
- `content_type`: MIME type
- `artifact_divt_id`: DIVT ID corresponding to the raw artifact’s hash/signature

#### 5.1.1 URI schemes and access (normative)

`RawRef.uri` is a locator, not an access mechanism. This spec permits URIs such as `s3://...`, `file://...`, and `https://...` (signed URLs or gateway endpoints). Credential and authorization mechanisms are deployment-specific and out of scope.

Multi-tenant isolation MUST be enforced by the deployment’s storage and access control systems using `record.tenant_id` as a primary scoping key.

#### 5.1.2 Retention declaration (normative)

`record.retention` MUST be a structured object that enables deterministic decisions at the edge.

Minimum required fields:
- `raw_available_until_us` (int): best-effort timestamp bound when raw is expected to remain retrievable
- `policy_id` (string): identifier for the applicable retention policy

Policies SHOULD be published as DIVT-signed manifests so retention changes are auditable.

### 5.2 Artifact integrity
Raw artifacts should be hashed with `binary_v1` and registered as DIVTs; Vector records should carry a reference (`artifact_divt_id`). This provides verifiable “zoom-in” when raw is retrieved.

---

## 6. DIVTs (Data Integrity Validation Tokens)

DIVTs provide cryptographic provenance and tamper evidence for both:
- **Vector records** (the JSONL records that carry context and references), and
- **Raw artifacts** (IQ, PCAP, video segments, HTML payloads, etc.) retained under a rolling policy.

This Vector specification depends on the DIVT specification and JSON schema.

### 6.0 Normative dependency

Implementations MUST:
- Produce a `divt` object for each Vector record that conforms to the DIVT JSON Schema (`divt.schema.json`).
- Follow DIVT hashing and canonicalization rules described in the DIVT schema reference (`DIVT-SCHEMA.md`).

### 6.1 What is hashed and signed

To avoid self-referential hashing, every JSONL line is structured as:

- `record`: the canonical, hashed payload (everything we want integrity-protected)
- `divt`: the DIVT receipt (hash + signatures + anchoring status)

Normative rules:
- For Vector records, hash and sign the canonicalized `record` object using `hash_mode = "json_canon_v1"`.
- For raw artifacts, hash and sign the raw bytes using `hash_mode = "binary_v1"`.

### 6.2 Hash modes

DIVT supports three hash modes:

- `text_v1`: use for plain UTF-8 text content where line ending normalization matters.
- `json_canon_v1`: use for JSON content that must be canonicalized (sorted keys; no floats; safe integer range).
- `binary_v1`: use for raw bytes (no canonicalization), appropriate for PCAP, IQ, video chunks, and other opaque blobs.

VectorForge guidance:
- Vector records MUST use `json_canon_v1`.
- Raw artifacts SHOULD use `binary_v1` (unless the artifact is naturally canonical JSON and you want canonical JSON hashing).

### 6.3 Canonicalization constraints (MUST)

Because `json_canon_v1` forbids floats and requires integers within a safe range, Vector records MUST:

- Avoid JSON floating point numbers entirely.
- Represent timestamps as integer microseconds since epoch (e.g., `start_us`, `end_us`, `observed_us`).
- Represent geographic coordinates as fixed-point integers (e.g., microdegrees).
- Represent currency amounts as decimal strings (e.g., `"1250.37"`) rather than floats.
- Represent continuous magnitudes (power, SNR, confidence, etc.) as fixed-point integers plus an implied scale.

#### 6.3.1 RFC 8785 alignment and deviations (normative)

`hash_mode="json_canon_v1"` is **RFC 8785-inspired**. Implementations SHOULD reuse RFC 8785 JSON Canonicalization Scheme libraries where possible, with one deliberate deviation:

- **Deviation D1 (no floats):** JSON numbers MUST be integers. Implementations MUST reject any float-like values (including representations that would parse to non-integers). Producers MUST represent fractional quantities using fixed-point integers (with an explicit `scale`) or decimal strings.
- **Deviation D2 (no duplicate keys):** JSON objects MUST NOT contain duplicate keys. Producers MUST reject inputs with duplicate keys. Verifiers MUST treat duplicate keys as invalid.

**Rejection methodology**
- Producers MUST fail closed: do not silently coerce floats.
- Verifiers MUST treat any float presence in the hashed `record` object as a verification failure.

Implementations MUST pass `json_canon_v1_test_vectors.json`.

### 6.4 Content and metadata limits

DIVT APIs and storage enforce limits that affect Vector record design:

- **Maximum content size:** 1 MB (decoded) when registering by content.
- **Maximum metadata size:** 4 KB (and metadata is NOT hashed).
- **Safe integer range:** from `-(2^53 - 1)` to `(2^53 - 1)`.

Implications:
- If a Vector record’s canonical `record` object exceeds the DIVT maximum content size, the system MUST register using `hash_b64` (hash-only registration) rather than embedding content in the DIVT registration call.
- Do not put security- or audit-critical fields only in DIVT `metadata`; it is not part of the hash.

### 6.5 Cryptographic modes and required DIVT fields


DIVTs use:
- `hash_version = "sha3-512-v1"` (SHA3-512 producing 64 bytes)
- `crypto_mode` in `{ "fips", "pqc", "hybrid" }` (default: `"hybrid"`)
- `signatures` containing one or both signatures (ECDSA P-521 and/or ML-DSA-65) plus `key_ver`
- `signature_version` indicating the key version used

Vector record implementations MUST always emit all required fields in the DIVT schema, including:
`divt_id`, `tenant_id`, `hash_b64`, `hash_mode`, `hash_version`, `signatures`, `signature_version`, `ledger_status`, `revoked`, and `created_at`.

**Baseline compliance**
- Producers SHOULD emit `crypto_mode="hybrid"` by default.
- Producers MAY emit `crypto_mode="fips"` where required by policy.
- Producers MAY emit `crypto_mode="pqc"` in PQC-only deployments.

**Verifier interoperability requirements**
- Verifiers MUST support verification for all crypto modes: `fips`, `pqc`, and `hybrid`.
- If a verifier encounters a DIVT with a supported mode and valid signatures, it MUST accept it.
- If a verifier encounters an unsupported mode, it MUST fail verification with a clear error and SHOULD surface an operator warning.

Key rotation MUST be represented via `signature_version`. Verifiers SHOULD maintain a trust store keyed by `(tenant_id, signature_version)`.

### 6.6 Ledger anchoring lifecycle

DIVTs include `ledger_status` indicating anchoring state in the immutable ledger. The defined states are:

- `pending`: queued for anchoring
- `anchored`: written to the ledger (with `ledger_tx_id`)
- `retry`: anchoring failed and will be retried (exponential backoff)
- `failed`: permanent failure after maximum retries

Operational guidance:
- Systems SHOULD create and sign DIVTs synchronously at ingest time (so records are verifiable immediately).
- Systems MAY anchor asynchronously; `pending` indicates “signed but not yet anchored”.
- Operators SHOULD monitor `retry` and `failed` as an integrity SLO/SLA signal.

### 6.7 DIVT service API patterns (informative, recommended)
#### 6.7.1 Multi-tenant isolation requirements (normative)

If the DIVT service is deployed in a multi-tenant mode, it MUST provide:
- per-tenant rate limits for register/verify/revoke endpoints
- key isolation per tenant (distinct signing keys and trust roots per `tenant_id`)
- immutable audit logs for register/verify/revoke operations, including tenant attribution
- authenticated API access; deployments SHOULD use JWTs or mutual TLS with claims bound to `tenant_id`

These requirements are mandatory for compliance because they affect verifiability and tenant safety.


A typical integration exposes:
- `POST /v1/register`: register content or a precomputed `hash_b64` (mutually exclusive), with `hash_mode` and optional metadata.
- `POST /v1/verify`: verify content or `hash_b64` against an existing `divt_id`.
- `POST /v1/divts/{id}/revoke`: revoke a DIVT with a human-readable reason.

These patterns enable:
- high-throughput registration by hash for large objects,
- audit-friendly verification in pipelines and CI,
- revocation for retractions and policy-driven invalidation.

---
## 7. Fidelity: definitions, metrics, and why it’s a “dial”

### 7.1 Key concept: Context Fidelity (CF)
“Fidelity” here is not “bitwise reconstruction.” It is **context preservation**: retaining the information required to reproduce the same conclusions (human or model) that the original stream supports, within a bounded error.

Formally:

- Let `S` be the original source stream.
- Let `T_θ` be a vectorizer parameterized by `θ` (window sizes, overlaps, feature sets, quantization, etc.).
- The vectorizer produces a vector stream `V = T_θ(S)` (JSONL records + raw refs).

Define a **Context Basis Set** (CBS) as a list of extractors `{φ_i}` that map a stream into context representations:
- `C_ref,i = φ_i(S)` (reference context from original)
- `C_vec,i = φ_i(V)` (context implied by vector record stream, optionally permitting raw retrieval depending on the benchmark mode)

Define a distance metric `d_i(C_ref,i, C_vec,i)` and a normalization constant `κ_i` (so metrics are comparable across dimensions). Define similarity:

`s_i = max(0, 1 - d_i / κ_i)`

Then define **Context Fidelity**:

`CF(θ) = (Σ_i w_i * s_i) / (Σ_i w_i)`

where weights `w_i` encode what “matters most” for the customer (e.g., detections may outweigh embeddings).

### 7.2 Two fidelities: Package vs. Recoverable
Because VectorForge retains raw artifacts for a rolling window:

- **Package Fidelity (PF)**: CF computed using only the Vector records (no raw retrieval).
- **Recoverable Fidelity (RF)**: CF computed allowing retrieval of raw artifacts referenced by the record, within retention.

In most deployments:
- PF is the knob customers tune for bandwidth/compute
- RF approaches 100% while raw is retained, subject to retention policy correctness and artifact addressability


### 7.2.1 Fidelity needs cryptographic binding (normative)
Fidelity is only meaningful when a reviewer can prove **which configuration** produced a given Vector stream. For that reason:

- Every Vector record MUST carry a `record.fidelity.profile_id` and `record.fidelity.profile_divt_id`.
- The profile manifest referenced by `profile_divt_id` MUST be registered and signed as a DIVT, so the profile cannot be silently changed after the fact.
- The fidelity fields MUST live inside the hashed `record` object, not inside DIVT `metadata`, because DIVT metadata is not hashed. See `DIVT-SCHEMA.md`.

### 7.2.2 Numeric encoding constraints (normative)
VectorForge uses DIVT `json_canon_v1` hashing for records. That mode forbids floats and requires integers to remain within the safe range. See `divt.schema.json`.

Therefore, all fidelity knobs and score-related values included in hashed JSON MUST be encoded as one of:

- fixed-point integers (recommended), with explicit scale fields (e.g., `snr_db_q8`, `weight_q15`, `scale=1000000`)
- decimal strings for values that require exact human-facing decimal semantics (recommended for money)
- integer microseconds for timestamps


### 7.3 Completeness confidence and continuity capabilities (normative)
**Production minimum**
Deployments claiming production-grade completeness MUST implement Continuity Level 2 (window manifests) or higher for each `stream_id` they report fidelity on.

**Primary published metric**
External reporting MUST publish End-to-end Fidelity (EF). Implementations MUST also publish PF and CC as components. If CC is undefined, EF MUST NOT be computed and the system MUST emit an explicit warning such as “fidelity unproven due to unknown completeness.”


VectorForge treats fidelity as an end-to-end property of a stream. A system cannot claim high fidelity if it cannot demonstrate that it received the complete set of records needed to form a complete picture for the analysis interval.

We define two components:

- **Package Fidelity (PF)**: context similarity between Vector Records and the Raw Artifact without retrieving raw payloads.
- **Completeness Confidence (CC)**: confidence that the Vector Record stream is complete for a given `stream_id` and time window.

#### 7.3.1 Completeness Confidence (CC)

For any stream window `w = [t0, t1]` and `stream_id`, let:

- `N_recv(w)` be the number of Vector Records received in the window for that stream.
- `N_exp(w)` be the number of Vector Records expected for that stream and window under the configured continuity capability.

Then:

- `CC(w) = clamp(N_recv(w) / N_exp(w), 0, 1)` when `N_exp(w)` is defined.
- `CC(w)` is **undefined** when the configured capability cannot define `N_exp(w)` (see Level 0 below).

A deployment MUST NOT report a single scalar “fidelity” score for a window if `CC(w)` is undefined. It MAY report PF with an explicit statement that completeness is unproven.

#### 7.3.2 End-to-end Fidelity (EF)

For any window `w`, define:

- `EF(w) = PF(w) * CC(w)` when `CC(w)` is defined.

This definition enforces the principle that missing records cap fidelity even if each record preserves context perfectly.

#### 7.3.3 Continuity capability levels

VectorForge implementations SHOULD expose continuity as a configurable capability. Higher levels increase completeness confidence but can add overhead. Implementations MUST declare the selected level in the Fidelity Profile.

**Level 0: Integrity (baseline)**  
- Record-level DIVT validation only.  
- The system verifies each record independently.  
- `N_exp(w)` is not defined, so `CC(w)` is undefined.  
- Use this level when transport and collection already guarantee completeness, or when the deployment accepts unknown completeness.

**Level 1: Gap detection**  
- Add `stream_id` and `seq` (monotonic sequence) to every record.  
- Define `N_exp(w)` as `(seq_max(w) - seq_min(w) + 1)` for contiguous streams, with explicit reset semantics.  
- The system detects gaps and reordering through sequence discontinuities.  
- Use this level when you need lightweight completeness signals with minimal coupling.

**Level 2: Set completeness (window manifests)**  
- Emit periodic `manifest_v1` records per `stream_id` and window.  
- Each manifest MUST include window bounds, expected record count, and a set commitment (Merkle root or equivalent) computed from record hashes or DIVT hashes in the window.  
- Define `N_exp(w)` as `manifest.expected_count`.  
- The system verifies completeness even with out-of-order delivery by reconciling against the manifest commitment.  
- Use this level when you need strong completeness with low pipeline coupling.

**Level 3: Tamper-evident continuity (chaining)**  
- Add a continuity link to each record (for example `prev_divt_id` or `prev_hash_b64`) within the same `stream_id`.  
- The verifier validates record DIVTs and validates continuity links across the stream segment.  
- Define `N_exp(w)` as in Level 1 or Level 2, and require continuity validation for the received set.  
- Use this level when the threat model includes adversarial deletion or insertion of records, or when you need audit-grade continuity.

#### 7.3.4 Profile declaration requirements

A Fidelity Profile MUST declare:
- the continuity capability level (0–3)
- the segmentation rules that determine record production rate (window, overlap, multi-resolution)
- the CBS weights used for PF scoring

A benchmark run MUST report PF, CC (or “undefined”), and EF for each evaluated window.


#### 7.3.5 Manifest commitment pseudocode (normative)

For Continuity Level 2, `manifest_v1` commits to the set of records in a window.

Inputs:
- window bounds `[t0, t1]`
- ordered list of member records for the window
- commitment input field (default: `divt.hash_b64`)
- ordering rule (default: `seq_asc`)

Steps:
1. Filter records to the window `[t0, t1]` for a single `stream_id`.
2. Sort records by the ordering rule.
3. Compute leaf bytes for each record:
   - if input is `divt.hash_b64`: leaf = base64_decode(divt.hash_b64)
   - if input is `divt.divt_id`: leaf = UTF-8 bytes of divt_id
   - if input is `record_hash_b64`: leaf = base64_decode(SHA3-512(canonical(record)))
4. Build a Merkle tree where internal nodes are `SHA3-512(left || right)`.
5. If a level has an odd number of nodes, duplicate the last node.
6. The root is the final node at the top level. Encode root as base64.

Implementations MUST match the provided test vectors in `manifest_commitment_test_vectors.json`.

### 7.4 Why window size can increase or decrease fidelity
A fixed window can be “too short” or “too long” relative to the phenomenon:
- Short windows can lose long-horizon structure (periodicity, session continuity, drift).
- Long windows can smear short events unless short-window detail is also retained.

Therefore, fidelity is inherently a function of:
- window length and overlap
- multi-resolution summaries
- linking and state carryover across windows
- feature selection and quantization

### 7.5 Fidelity Profiles (normative)
To make fidelity user-configurable without fragmenting the ecosystem, VectorForge defines **Fidelity Profiles**.

A Fidelity Profile is a signed manifest describing:
- the vector type(s) it applies to
- segmentation and overlap rules
- which features are included (and at which resolutions)
- quantization/compression settings
- the target PF range (e.g., 0.95–0.98) and the CBS weights used in scoring

Each Vector record includes:
- `record.fidelity.profile_id`
- `record.fidelity.profile_divt_id` (pointer to the signed profile manifest)
- optional per-record overrides (e.g., adaptive segmentation triggered by event rate)

### 7.6 Multi-resolution profiles (recommended default)
To avoid the “10s vs 1s” trap, profiles should support multi-resolution:
- emit a short-window record stream (e.g., 250ms–1s) for transient events
- emit a longer-window summary stream (e.g., 10s–60s) for structure and drift
- link them by `stream_id`, `seq`, and time bounds

---

## 8. Resource model: compute, bandwidth, storage (the slider math)

Users need to understand the cost of a chosen Fidelity Profile. We model costs as functions of profile knobs `θ`.

### 8.1 Record rate (segments and overlap)
Let:
- window length `T` (seconds)
- overlap `O` (seconds), with `0 ≤ O < T`
- step size `Δ = T - O`

Then record rate:

`r = 1 / Δ` records per second (per stream)

Multi-resolution profiles sum record rates across resolutions.

### 8.2 Bandwidth model
Let `b_k(θ)` be the average bytes per record for record type `k` under profile `θ`. Then:

`BW(θ) = Σ_k r_k(θ) * b_k(θ)` bytes/second

This is the “vector output bandwidth” slider users care about.

### 8.3 Vector storage model
Let `R_vec` be retention time for vector records (seconds). Then:

`Storage_vec(θ) = BW(θ) * R_vec`

### 8.4 Raw storage model (rolling window)
Let `BW_raw` be raw ingest byte rate (e.g., IQ or video), and `R_raw` be raw retention time:

`Storage_raw = BW_raw * R_raw`

Raw storage is typically much larger than vector storage and is tuned primarily by retention policy rather than fidelity profile.

### 8.5 Compute model (CPU/GPU)
Let `c_k(θ)` be compute cost per record (e.g., milliseconds of CPU or GPU time). Then:

`CPU_ms_per_s(θ) = Σ_k r_k(θ) * c_k(θ)`

In practice, compute models are best built by **calibration**:
- run reference workloads on representative hardware
- measure actual compute and size
- fit simple predictive models (piecewise-linear is usually enough)

### 8.6 Making the “sliders UI” rigorous
A configuration UI should:
1) Present fidelity as PF with a target range (e.g., 0.95–0.98) tied to a defined CBS.
2) Present constraints:
   - max bandwidth
   - max compute (CPU/GPU)
   - max local storage / retention window
3) Offer pre-defined profiles plus an “expert mode” that varies:
   - window lengths and overlaps
   - feature toggles
   - quantization settings
   - multi-resolution enablement
4) Compute predicted costs using the calibrated models and show:
   - PF estimate with confidence bounds
   - bandwidth estimate
   - compute estimate
   - vector and raw storage impact
5) Output a signed Fidelity Profile manifest so “what was configured” is auditable.

This can be framed as an optimization:
Maximize `PF(θ)` subject to:
- `BW(θ) ≤ BW_max`
- `CPU(θ) ≤ CPU_max`
- `Storage_raw ≤ S_raw_max`
- `Storage_vec(θ) ≤ S_vec_max`

---

## 9. Domain-specific fidelity (what is “context” per Vector)

Each Vector defines a recommended Context Basis Set (CBS) for benchmarking PF.

### 9.1 RFVector CBS (example)
- occupancy / spectrogram similarity (e.g., normalized L1 or SSIM on spectrogram tiles)
- event parity (detections: time/frequency bounding boxes; scored by F1/IoU)
- wavelet fingerprint similarity (matrix error norms; correlation)
- emitter classification parity (if classifier output is included)

RFVector commonly excludes full IQ from the package but retains it as a raw artifact reference; PF targets 0.95–0.98 are plausible when the CBS is built from derived features.

### 9.2 PulseVector CBS (example)
- sessionization parity (flow grouping precision/recall)
- metadata parity (DNS answers, TLS handshake fields, HTTP request/response metadata)
- flow statistics parity (bytes/packets, timing features)
- alert parity (optional: Suricata/Zeek-derived events, if included)

### 9.3 FlowVector CBS (example)
- extracted text parity (token overlap or embedding similarity)
- metadata parity (URL, timestamps, author/platform IDs)
- entity extraction parity (F1 for entities)
- deduplication parity (same duplicates flagged)

### 9.4 ExchangeVector CBS (example)
- lifecycle parity (auth/capture/settle state graph equivalence)
- ledger delta parity (net changes match within rounding rules)
- party graph parity (linking of accounts/addresses)
- fraud/risk feature parity (if features are generated)

### 9.5 VideoVector CBS (example)
- shot boundary parity
- keyframe selection parity (retrieval effectiveness)
- tracklet parity (ID switches, track continuity metrics)
- event parity (enter/exit/loiter etc., if event extraction is included)

---

## 10. Benchmarking and reproducibility

### 10.1 Reference-extractor parity (no human labeling required)
To benchmark PF:
1) Choose a reference extractor suite `{φ_i}` and freeze versions.
2) Compute `C_ref` from the original stream.
3) Compute `C_vec` from the vector record stream (without raw retrieval).
4) Score per-metric distances and aggregate into PF.

To benchmark Recoverable Fidelity:
- allow raw retrieval when computing `C_vec`, bounded by retention availability.

### 10.2 Outputs (normative)
A benchmark run should output:
- PF overall score and per-metric breakdown
- resource measurements (actual bandwidth/compute/storage)
- profile ID and profile DIVT ID
- dataset IDs and DIVT IDs for audit

### 10.3 CI regression
The benchmark harness becomes a regression gate:
- schema changes
- parser changes
- quantization/compression changes
- extractor version changes

---

## 11. Open-source release structure (recommended)

### 11.1 Repositories
- `vectorforge-vectors` (spec): envelope schema, per-vector payload schemas, examples
- `vectorforge-divt` (spec + implementation): DIVT schema and reference services
- `vectorforge-parsers` (reference): minimal open-source parsers for each vector (where feasible)
- `vectorforge-bench` (benchmark): reference extractors + scoring + datasets (sanitized or synthetic)

### 11.2 Spec artifacts
- JSON Schemas for:
  - Vector envelope (`vectorforge.vector`)
  - Fidelity Profile (`vectorforge.profile`)
  - RawRef (`vectorforge.rawref`)
  - Each vector payload subtype
- Example JSONL files
- Conformance tests (golden files + verifier)

### 11.3 Versioning and extensibility
- Semantic versioning with strict backward compatibility within a major version.
- Extensions must live under `record.extensions` (namespaced) and never change meaning of core fields.

---

## 12. Security, privacy, and policy (must be explicit in OSS)
Because vectors can carry sensitive operational data, the spec should explicitly support:
- PII flags and redaction markers
- optional field-level encryption (implementation detail, but schema hooks matter)
- retention declarations
- access control expectations (outside schema, but referenced)

The open-source project should provide guidance and reference configurations for safe defaults.

---

## 13. Summary

VectorForge’s Vector family provides:
- stable, open schemas per domain
- cryptographic integrity via DIVTs
- a mathematical definition of context fidelity (PF/RF)
- a practical, calibration-based resource model that enables “fidelity sliders”
- a reproducible benchmark suite suitable for academic and operational validation

This combination allows enterprises to tune fidelity in real time under bandwidth/compute/storage constraints while maintaining verifiability and interoperability.


---

## Appendix A. Mapping existing RF parser events to RFVector records (informative)

This appendix shows how the current `rf-transformer` parser output (`RFCaptureEvent`, schema_version `1.1.0`) can map into the RFVector envelope without breaking existing semantics.

### A.1 RFCaptureEvent envelope → Vector envelope

| RFCaptureEvent field | RFVector location | Notes |
|---|---|---|
| `event_id` | `record.record_id` | Preserve UUID value. |
| `event_type` (`"rf.capture"`) | `record.record_type` (`"rf_capture_v1"`) | Keep `record.vector="rfvector"`. |
| `timestamp` (ISO 8601 UTC) | `record.time.observed_us` (int) | Store microseconds since epoch. Optionally preserve the original ISO string under `record.extensions.timestamp_iso`. |
| `schema_version` | `record.extensions.parser.schema_version` | Keep parser’s internal version separate from the open schema version. |
| `source.plugin_id`, `source.plugin_version` | `record.source.labels.plugin_id`, `record.source.labels.plugin_version` | Non-identity metadata is best in labels. |
| `source.sensor_id` | `record.source.source_id` | Primary source identity. |
| `source.tenant_id` | `record.tenant_id` | Tenant identity. |

### A.2 RFCaptureContent → RFVector payload

| RFCaptureContent field | RFVector payload path | Notes |
|---|---|---|
| `capture_index` | `record.payload.rf.capture_index` | Also useful for ordering alongside `record.chain.seq`. |
| `center_frequency` | `record.payload.rf.band.center_hz` | Use Hz integer. |
| `bandwidth` | `record.payload.rf.band.span_hz` | Use Hz integer. |
| `sampling_rate` | `record.payload.rf.sample_rate_hz` | Hz integer. |
| `duration_ms` | `record.payload.rf.duration_ms` | Explicit duration for the capture. |
| `allocation` | `record.payload.rf.allocation` | Optional. |
| `session_id` | `record.payload.rf.session_id` | Enables cross-record linking. |
| `emitter_hint` | `record.payload.rf.emitter_hint` | Optional. |

### A.3 Wavelet fingerprint
The existing wavelet fingerprint is already well-aligned with JSON canonicalization constraints:

- `wavelet.matrix`: 3×3 integers
- `wavelet.scale`: implied fixed-point scaling (default 1e6)
- `wavelet.params`: window and transform parameters

Map to:

- `record.payload.rf.wavelet.matrix`
- `record.payload.rf.wavelet.scale`
- `record.payload.rf.wavelet.params`

This preserves the “no floats” requirement for canonical hashing.

### A.4 Location and hardware
- Location fields already use microdegrees (`latitude_udeg`, `longitude_udeg`) and should map directly to `record.payload.rf.location.{lat_udeg, lon_udeg}`.
- Hardware metadata maps to `record.payload.rf.hardware`.

### A.5 Artifact hash / raw artifact references
`RFCaptureContent.artifact_hash` can be upgraded to a full RawRef:

- If the parser currently produces only a hash string:
  - store it under `record.payload.rf.artifact_hash` for continuity
  - and/or generate a `RawRef` with `artifact_divt_id` once raw artifact DIVTs are available.
- Once the raw IQ blob is addressable, prefer:
  - `record.artifacts[]` RawRef entries
  - raw artifact DIVTs (`binary_v1`) referenced by `artifact_divt_id`

### A.6 Error events
`rf.capture.error` events can map to:
- `record.vector="rfvector"`
- `record.record_type="error_v1"`
- `record.payload.error = {capture_key, capture_index, error_type, error_message, source_file, ...}`

### A.7 VITA49 transformer events
VITA49-specific fields (e.g., `stream_id`, `packet_count`, `sample_count`, `vrt_class_id`) should map into:
- `record.source.labels` (identity-adjacent metadata), and/or
- `record.payload.rf.vita49 = {...}` as an optional sub-object,
without changing the core RFVector envelope.

## 14. Standard error records (normative)

Parsers and pipelines must represent failures in a consistent, machine-processable way. Error records MUST use:
- `record.record_type` set to the appropriate `*_error_v1` type
- `record.payload.error` conforming to `vectorforge-error.schema.json`

Minimum required error fields:
- `error_type` (string): stable category (for example `PARSE_ERROR`, `VALIDATION_ERROR`, `IO_ERROR`)
- `error_message` (string): human-readable message
- `source_file` or `source_uri` (string): where the failure occurred
- `capture_key` or equivalent correlation id when available
- `retryable` (boolean) when known
