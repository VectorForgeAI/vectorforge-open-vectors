# Fidelity: Measurable Context Preservation

## What is Fidelity?

Fidelity is not "bitwise reconstruction." It is **context preservation**: retaining the information required to reach the same conclusions from Vector records that you would reach from the original raw data.

A system with 95% fidelity means: for 95% of the analysis tasks you care about, the Vector records give you the same answer as the raw data would.

## The Fidelity Equation

Formally:

1. Start with a raw source stream **S**
2. Apply a vectorizer with parameters **θ** to produce Vector records **V**
3. Define a set of "context extractors" **{φ_i}** that measure what matters
4. Compare context from raw vs. context from vectors

For each extractor:
- `C_ref = φ(S)` - context from raw
- `C_vec = φ(V)` - context from vectors
- `similarity = 1 - (distance / normalization)`

**Context Fidelity** is the weighted average of these similarities.

## Three Fidelity Metrics

### Package Fidelity (PF)

Context similarity using **only** the Vector records, without retrieving raw artifacts.

This is what you tune when you need to reduce bandwidth/compute/storage. Higher PF = more context preserved in the compact records.

### Completeness Confidence (CC)

Confidence that your Vector stream is **complete** for a time window.

If records are missing, even perfect PF doesn't help. CC measures: "Did I receive all the records I should have?"

See [Continuity](continuity.md) for how CC is computed.

### End-to-End Fidelity (EF)

The combined metric:

```
EF = PF × CC
```

This is the primary metric for external reporting. It captures both:
- How well each record preserves context (PF)
- Whether you have all the records (CC)

If CC is undefined (no continuity tracking), EF cannot be computed.

## Context Basis Set (CBS)

A CBS defines **what "context" means** for a given domain. It's a list of extractors with weights.

Example CBS for RFVector:
```json
{
  "context_basis": [
    {"name": "wavelet_fingerprint_v1", "weight_q15": 20000, "metric": "frobenius_q15"},
    {"name": "detection_parity_v1", "weight_q15": 12768, "metric": "f1"}
  ]
}
```

Different deployments can define different CBS weights based on what matters to them:
- Surveillance: Detection parity matters most
- Spectrum management: Occupancy accuracy matters most
- R&D: Everything matters equally

## Fidelity Profiles

A **Fidelity Profile** is a configuration manifest that specifies:
- Which vector type it applies to
- Segmentation rules (window length, overlap)
- Which features are extracted
- Quantization/compression settings
- Target PF range
- CBS weights for scoring

Profiles are DIVT-signed, so you can prove which configuration produced a given stream.

Example profile:
```json
{
  "schema": {"name": "vectorforge.profile", "version": "0.1.7"},
  "profile_id": "rf.default.95",
  "vector": "rfvector",
  "continuity_level": 2,
  "target_pf_q15": 31129,
  "knobs": {
    "segment_ms": 1000,
    "overlap_ms": 250,
    "fingerprint": "wavelet_fingerprint_v1"
  },
  "context_basis": [
    {"name": "wavelet_fingerprint_v1", "weight_q15": 20000, "metric": "frobenius_q15"},
    {"name": "detection_parity_v1", "weight_q15": 12768, "metric": "f1"}
  ]
}
```

Every Vector record references its profile via `record.fidelity.profile_id` and `record.fidelity.profile_divt_id`.

## Why Fidelity is a "Dial"

Fidelity trades off against resources:

| Turn Up | You Get | You Pay |
|---------|---------|---------|
| Window overlap | Better transient capture | More records/sec |
| Feature depth | Richer context | Larger records |
| Multi-resolution | Both detail and structure | 2x+ records |
| Lower quantization | More precision | Larger payloads |

The Fidelity Profile lets operators choose their position on this trade-off curve.

## Numeric Encoding

Because Vector records use `json_canon_v1` hashing (no floats allowed), fidelity values use fixed-point encoding:

- **Q15**: Weights and scores as integers 0-32768 (representing 0.0-1.0)
- **target_pf_q15**: Target PF as Q15 integer (e.g., 31129 ≈ 0.95)
- **weight_q15**: CBS weights as Q15 integers

To convert: `float_value = q15_value / 32768`

## Measuring Fidelity

To measure PF for a stream:

1. Collect reference data (raw telemetry)
2. Run the vectorizer to produce Vector records
3. For each CBS extractor:
   - Compute context from reference
   - Compute context from vectors
   - Measure similarity
4. Compute weighted average

The benchmark harness in `bench/` automates this process.

## What's Next

- [Continuity](continuity.md) - How Completeness Confidence (CC) is computed
- [Benchmark Contract](../bench/CONTRACT.md) - How to run fidelity benchmarks
- [Vector-specific CBS](../vectors/) - Domain-specific context extractors
