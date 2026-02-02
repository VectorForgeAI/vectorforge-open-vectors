# Migration Guide: rf-transformer to RFVector

This guide shows how to map existing `rf-transformer` parser output (`RFCaptureEvent`, schema v1.1.0) to the RFVector record format.

## Overview

The rf-transformer emits events like:

```json
{
  "event_id": "evt_rf_550e8400-e29b-41d4-a716-446655440000",
  "event_type": "rf.capture",
  "timestamp": "2025-02-01T12:00:00Z",
  "schema_version": "1.1.0",
  "source": {...},
  "content": {...}
}
```

These need to be transformed into RFVector records:

```json
{
  "record": {
    "schema": {"name": "vectorforge.vector", "version": "0.1.7"},
    "vector": "rfvector",
    "record_type": "rf_capture_v1",
    ...
  },
  "divt": {...}
}
```

## Field Mapping

### Envelope Fields

| rf-transformer Field | RFVector Field | Notes |
|---------------------|----------------|-------|
| `event_id` | `record.record_id` | Strip `evt_rf_` prefix if present, keep UUID |
| `event_type` (`"rf.capture"`) | `record.record_type` (`"rf_capture_v1"`) | Also set `record.vector="rfvector"` |
| `timestamp` (ISO 8601) | `record.time.observed_us` | Convert to microseconds since epoch |
| `schema_version` | `record.extensions.parser.schema_version` | Preserve for debugging |
| `source.sensor_id` | `record.source.source_id` | Primary source identity |
| `source.tenant_id` | `record.tenant_id` | Tenant identity |
| `source.plugin_id` | `record.source.labels.plugin_id` | Metadata |
| `source.plugin_version` | `record.source.labels.plugin_version` | Metadata |

### Content Fields

| rf-transformer Field | RFVector Field | Notes |
|---------------------|----------------|-------|
| `content.capture_index` | `record.payload.rf.capture_index` | Also consider `record.chain.seq` |
| `content.center_frequency` | `record.payload.rf.band.center_hz` | Already integer Hz |
| `content.bandwidth` | `record.payload.rf.band.span_hz` | Already integer Hz |
| `content.sampling_rate` | `record.payload.rf.sample_rate_hz` | Already integer Hz |
| `content.duration_ms` | `record.payload.rf.duration_ms` | Already integer ms |
| `content.allocation` | `record.payload.rf.allocation` | Optional |
| `content.session_id` | `record.payload.rf.session_id` | Cross-record linking |
| `content.emitter_hint` | `record.payload.rf.emitter_hint` | Optional |

### Wavelet Fingerprint

The existing wavelet format is already compatible with canonicalization (integers only):

| rf-transformer Field | RFVector Field |
|---------------------|----------------|
| `content.wavelet.matrix` | `record.payload.rf.fingerprints[0].matrix` |
| `content.wavelet.scale` | `record.payload.rf.fingerprints[0].scale` |
| `content.wavelet.params.window_ms` | `record.payload.rf.fingerprints[0].params.window_ms` |
| `content.wavelet.params.wavelet` | `record.payload.rf.fingerprints[0].params.wavelet` |
| `content.wavelet.params.decomp_level` | `record.payload.rf.fingerprints[0].params.decomp_level` |
| `content.wavelet.params.normalized` | `record.payload.rf.fingerprints[0].params.normalized` |

Set `fingerprints[0].kind = "wavelet_fingerprint_v1"`.

### Location

| rf-transformer Field | RFVector Field | Notes |
|---------------------|----------------|-------|
| `content.location.latitude_udeg` | `record.payload.rf.location.lat_udeg` | Already microdegrees |
| `content.location.longitude_udeg` | `record.payload.rf.location.lon_udeg` | Already microdegrees |

### Hardware

| rf-transformer Field | RFVector Field |
|---------------------|----------------|
| `content.hardware.antenna_model` | `record.payload.rf.hardware.antenna_model` |
| `content.hardware.antenna_gain_dbi` | `record.payload.rf.hardware.antenna_gain_dbi` |
| `content.hardware.receiver` | `record.payload.rf.hardware.receiver` |
| `content.hardware.receive_gain_db` | `record.payload.rf.hardware.receive_gain_db` |

### Artifact Hash / Raw References

| rf-transformer Field | RFVector Approach |
|---------------------|-------------------|
| `content.artifact_hash` | Option 1: Keep at `record.payload.rf.artifact_hash` for continuity |
| | Option 2: Create full `RawRef` in `record.artifacts[]` with `artifact_divt_id` |

Preferred approach (when raw IQ is addressable):

```json
{
  "artifacts": [
    {
      "artifact_id": "uuid",
      "kind": "iq",
      "uri": "s3://bucket/path/to/iq.bin",
      "time": {"start_us": ..., "end_us": ...},
      "content_type": "application/octet-stream",
      "artifact_divt_id": "uuid-of-raw-divt"
    }
  ]
}
```

## Timestamp Conversion

Convert ISO 8601 to microseconds:

```python
from datetime import datetime

iso_timestamp = "2025-02-01T12:00:00Z"
dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
us = int(dt.timestamp() * 1_000_000)
# 1738411200000000
```

## New Required Fields

Fields you need to add (not present in rf-transformer output):

| Field | How to Set |
|-------|------------|
| `record.schema` | `{"name": "vectorforge.vector", "version": "0.1.7"}` |
| `record.time.start_us` | Compute from timestamp or capture metadata |
| `record.time.end_us` | `start_us + (duration_ms * 1000)` |
| `record.chain.stream_id` | Construct from sensor + band (e.g., `rf/sensor-01/band-2450MHz`) |
| `record.chain.seq` | Monotonic sequence per stream (use `capture_index` if contiguous) |
| `record.retention` | Set based on your retention policy |
| `record.fidelity` | Reference your Fidelity Profile |
| `divt` | Compute after constructing `record` |

## Example Transformation

**Input (rf-transformer):**

```json
{
  "event_id": "evt_rf_550e8400-e29b-41d4-a716-446655440000",
  "event_type": "rf.capture",
  "timestamp": "2025-02-01T12:00:00Z",
  "schema_version": "1.1.0",
  "source": {
    "plugin_id": "rf-transformer",
    "plugin_version": "1.1.0",
    "sensor_id": "sensor-01",
    "tenant_id": "demo"
  },
  "content": {
    "capture_index": 1,
    "center_frequency": 2450000000,
    "bandwidth": 20000000,
    "sampling_rate": 20000000,
    "duration_ms": 1000,
    "wavelet": {
      "matrix": [[1,2,3],[4,5,6],[7,8,9]],
      "scale": 1000000,
      "params": {"window_ms": 20, "wavelet": "db4", "decomp_level": 3, "normalized": true}
    }
  }
}
```

**Output (RFVector):**

```json
{
  "record": {
    "schema": {"name": "vectorforge.vector", "version": "0.1.7"},
    "vector": "rfvector",
    "record_type": "rf_capture_v1",
    "record_id": "550e8400-e29b-41d4-a716-446655440000",
    "tenant_id": "demo",
    "time": {
      "start_us": 1738411200000000,
      "end_us": 1738411201000000,
      "observed_us": 1738411200000000
    },
    "source": {
      "source_id": "sensor-01",
      "source_type": "rf_sensor",
      "labels": {
        "plugin_id": "rf-transformer",
        "plugin_version": "1.1.0"
      }
    },
    "chain": {
      "stream_id": "rf/sensor-01/center2450MHz/span20MHz",
      "seq": 1
    },
    "retention": {
      "raw_available_until_us": 1739016000000000,
      "policy_id": "rolling-7d"
    },
    "fidelity": {
      "profile_id": "rf.default.95",
      "profile_divt_id": "profile-divt-uuid"
    },
    "payload": {
      "rf": {
        "band": {"center_hz": 2450000000, "span_hz": 20000000},
        "sample_rate_hz": 20000000,
        "duration_ms": 1000,
        "fingerprints": [
          {
            "kind": "wavelet_fingerprint_v1",
            "scale": 1000000,
            "matrix": [[1,2,3],[4,5,6],[7,8,9]],
            "params": {"window_ms": 20, "wavelet": "db4", "decomp_level": 3, "normalized": true}
          }
        ],
        "extensions": {}
      }
    },
    "extensions": {
      "parser": {"schema_version": "1.1.0"}
    }
  },
  "divt": {
    "divt_id": "generated-uuid",
    "tenant_id": "demo",
    "hash_b64": "computed-sha3-512-base64",
    "hash_mode": "json_canon_v1",
    "hash_version": "sha3-512-v1",
    "crypto_mode": "hybrid",
    "signatures": {"key_ver": "v1", "ecdsa": "...", "pqc": "..."},
    "signature_version": "keyset-v1",
    "ledger_status": "pending",
    "revoked": false,
    "created_at": "2025-02-01T12:00:00Z"
  }
}
```

## Error Events

Map `rf.capture.error` to:

- `record.vector = "rfvector"`
- `record.record_type = "rf_error_v1"`
- `record.payload.error` per `vectorforge-error.schema.json`

## VITA49 Events

VITA49-specific fields map to:

- `record.source.labels` for identity metadata (stream_id, class_id)
- `record.payload.rf.vita49 = {...}` for VITA49-specific data

## See Also

- [RFVector Documentation](../vectors/rfvector.md)
- [rf-parser-events.md](../../spec/rf-parser-events.md) - Full rf-transformer schema
