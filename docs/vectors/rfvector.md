# RFVector

**Status: Pilot-ready**

RFVector captures radio frequency observations: spectrum captures, signal detections, and derived features like wavelet fingerprints.

## Use Cases

- SDR (Software Defined Radio) sensor networks
- Spectrum monitoring and management
- SIGINT collection pipelines
- RF situational awareness systems

## Record Types

| Type | Description |
|------|-------------|
| `rf_capture_v1` | Standard RF observation record |
| `rf_error_v1` | Error during RF processing |
| `manifest_v1` | Continuity Level 2 window manifest |

## Payload Structure

```json
{
  "payload": {
    "rf": {
      "band": {
        "center_hz": 2450000000,
        "span_hz": 20000000
      },
      "sample_rate_hz": 20000000,
      "duration_ms": 1000,
      "fingerprints": [
        {
          "kind": "wavelet_fingerprint_v1",
          "scale": 1000000,
          "matrix": [[1,2,3],[4,5,6],[7,8,9]],
          "params": {
            "window_ms": 20,
            "wavelet": "db4",
            "decomp_level": 3,
            "normalized": true
          }
        }
      ],
      "detections": [],
      "location": {
        "lat_udeg": 37774929,
        "lon_udeg": -122419416
      },
      "hardware": {
        "antenna_model": "omnidirectional",
        "antenna_gain_dbi": 3,
        "receiver": "RTL-SDR",
        "receive_gain_db": 40
      },
      "session_id": "capture-session-001",
      "extensions": {}
    }
  }
}
```

## Key Fields

### Band Information
- **center_hz**: Center frequency in Hz (integer)
- **span_hz**: Bandwidth in Hz (integer)
- **sample_rate_hz**: Sample rate in samples/second (integer)
- **duration_ms**: Capture duration in milliseconds (integer)

### Fingerprints

Derived features for efficient similarity search and classification:

```json
{
  "kind": "wavelet_fingerprint_v1",
  "scale": 1000000,
  "matrix": [[...], [...], [...]],
  "params": {
    "window_ms": 20,
    "wavelet": "db4",
    "decomp_level": 3,
    "normalized": true
  }
}
```

The `matrix` is a fixed-point integer representation. Divide by `scale` to get floating-point values.

### Detections

Signal detections with time/frequency bounds:

```json
{
  "detections": [
    {
      "detection_id": "uuid",
      "time_bounds_us": [1738368000000000, 1738368000500000],
      "freq_bounds_hz": [2440000000, 2460000000],
      "confidence_q15": 28000,
      "classification": "wifi_beacon",
      "embeddings": []
    }
  ]
}
```

### Location

Geographic coordinates as microdegrees (integers):

```json
{
  "location": {
    "lat_udeg": 37774929,
    "lon_udeg": -122419416,
    "alt_mm": 10000,
    "accuracy_mm": 5000
  }
}
```

Convert: `degrees = microdegrees / 1_000_000`

### Raw Artifact Reference

For Level 2+ deployments, reference the raw IQ capture:

```json
{
  "artifacts": [
    {
      "artifact_id": "uuid",
      "kind": "iq",
      "uri": "s3://bucket/path/to/iq.bin",
      "time": {"start_us": 1738368000000000, "end_us": 1738368001000000},
      "content_type": "application/octet-stream",
      "artifact_divt_id": "uuid-of-raw-divt"
    }
  ]
}
```

## Context Basis Set (CBS)

Recommended CBS for RFVector fidelity measurement:

| Extractor | Weight | Metric | Notes |
|-----------|--------|--------|-------|
| `wavelet_fingerprint_v1` | 0.61 | Frobenius similarity | Normalized matrix comparison |
| `detection_parity_v1` | 0.39 | F1 score | Detection bounding box overlap |

Weights expressed as Q15: `[20000, 12768]`

### wavelet_fingerprint_v1

Measures similarity between wavelet matrices:

1. Extract matrices from reference and vector
2. Compute normalized Frobenius distance
3. Convert to similarity: `1 - (distance / max_distance)`

Reference extractor: `bench/extractors/wavelet_fingerprint_v1.py`

### detection_parity_v1

Measures detection agreement:

1. Match detections by time/frequency overlap (IoU threshold)
2. Compute precision, recall, F1
3. F1 is the similarity score

## Fidelity Profile Example

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

## Fidelity Knobs

| Knob | Effect on Fidelity | Effect on Resources |
|------|-------------------|---------------------|
| segment_ms ↓ | Better transient capture | More records/sec |
| overlap_ms ↑ | Less boundary loss | More records/sec |
| wavelet decomp_level ↑ | Richer fingerprint | Larger matrix |
| detection confidence ↓ | More detections | More noise |

## Migration from rfvector-plugin (formerly rf-transformer)

If you have existing `rfvector-plugin` output (formerly `rf-transformer`), see [Migration Guide](../migration/rf-parser-mapping.md) for field-by-field mapping.

## Schema

Full schema: `schemas/payloads/rfvector.payload.schema.json`

## Examples

- Basic capture: `examples/records/rfvector-record.jsonl`
- Profile: `examples/profiles/profile-rf.default.95.json`
