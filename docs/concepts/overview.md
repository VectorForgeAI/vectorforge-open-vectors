# Overview: The Vector Family

## The Problem

High-volume telemetry (RF signals, network traffic, video feeds, financial transactions) generates massive data streams. Organizations face a choice:

1. **Store everything**: Expensive, slow to query, often impractical
2. **Discard most of it**: Fast and cheap, but you lose context for future analysis
3. **Compress blindly**: Smaller, but you don't know what you lost

VectorForge Open Vectors provides a fourth option: **structured reduction with measurable fidelity**.

## The Solution: Vector Records

A Vector record is a compact, standardized representation of a time-windowed observation. It captures enough context to support most analysis tasks without shipping the full raw data.

```
Raw Telemetry → Vectorizer → Vector Records → Analysis
     ↓
  Raw Store (optional, rolling retention)
```

Key properties:
- **Compact**: Orders of magnitude smaller than raw
- **Structured**: Common envelope, domain-specific payloads
- **Verifiable**: Cryptographically signed (DIVT)
- **Measurable**: Fidelity is quantified, not assumed

## The Vector Family

Five domains, one format pattern:

### RFVector (Radio Frequency)
**Status: Pilot-ready**

Captures RF observations: center frequency, bandwidth, spectral summaries, wavelet fingerprints, detections.

Use when: You have SDR sensors, spectrum analyzers, or SIGINT collectors.

### PulseVector (Network)
**Status: Design-ready**

Captures network activity: flow summaries (5-tuple, bytes, packets), protocol metadata (DNS, TLS, HTTP), security events.

Use when: You have network taps, packet brokers, or flow exporters.

### FlowVector (Content Streams)
**Status: Spec-first**

Captures high-volume content: web scrapes, social feeds, API firehoses. Normalized items with text, metadata, and optional embeddings.

Use when: You ingest web content, social media, or streaming APIs at scale.

### ExchangeVector (Financial)
**Status: Spec-first**

Captures transaction activity: payment events, settlements, ledger changes. Normalized lifecycle with amounts, parties, and instruments.

Use when: You process payments, crypto transactions, or financial audit trails.

### VideoVector (Video)
**Status: Spec-first**

Captures video activity: shot boundaries, keyframes, motion summaries, object tracks.

Use when: You analyze surveillance footage, streaming video, or media archives.

## Package vs. Raw

Every Vector deployment separates two concerns:

**Vector Package** (always transmitted):
- The JSONL records
- Compact, indexed, queryable
- Carries derived features (fingerprints, summaries, metadata)

**Raw Store** (optional, rolling retention):
- Original artifacts (IQ captures, PCAP, video segments)
- Referenced by Vector records via `artifacts[]`
- Retrieved on-demand for "zoom-in" analysis

This enables two operational modes:
1. **Package-only**: Analyze Vector records directly (fast, low bandwidth)
2. **Recoverable**: Pull raw artifacts within retention window for deeper analysis

## Common Record Structure

All Vectors share the same envelope:

```json
{
  "record": {
    "schema": {"name": "vectorforge.vector", "version": "0.1.7"},
    "vector": "rfvector",
    "record_type": "rf_capture_v1",
    "record_id": "uuid",
    "tenant_id": "string",
    "time": {"start_us": int, "end_us": int, "observed_us": int},
    "source": {"source_id": "string", "source_type": "string", "labels": {}},
    "chain": {"stream_id": "string", "seq": int},
    "retention": {"raw_available_until_us": int, "policy_id": "string"},
    "fidelity": {"profile_id": "string", "profile_divt_id": "uuid"},
    "payload": { ... },
    "extensions": {}
  },
  "divt": { ... }
}
```

The `payload` object varies by vector type. See individual vector documentation for details.

## Design Principles

### 1. Deterministic
Records can be canonicalized and hashed reproducibly across platforms. This requires: no floats, sorted keys, safe integer range.

### 2. Verifiable
Every record has a DIVT (Data Integrity Validation Token) that proves authenticity and detects tampering.

### 3. Configurable
Fidelity is not hard-coded. Fidelity Profiles control the trade-off between context preservation and resource usage.

### 4. Multi-resolution
Some phenomena are only visible at certain time scales. Profiles can emit both short-window (detail) and long-window (structure) records.

## What's Next

- [DIVT: Data Integrity](divt.md) - How cryptographic integrity works
- [Fidelity: The Dial](fidelity.md) - How context preservation is measured
- [Continuity: Completeness](continuity.md) - How to prove your stream is complete
- [Canonicalization](canonicalization.md) - How to produce deterministic JSON
