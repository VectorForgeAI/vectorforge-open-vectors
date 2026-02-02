# RF Parser Event Schemas (Interim, implementation-facing)

This document captures current RF parser outputs so implementers can build ingestion and mapping logic before the full RFVector payload schema tightens further.

Source parsers:
- `rf-transformer` (rf.capture / rf.capture.error)
- `vita49-transformer` (vita49.capture / vita49.capture.error)

## 1) rf.capture (Schema v1.1.0)

### RFCaptureEvent envelope
- `event_id` (string): `evt_rf_{uuid}`
- `event_type` (string): `"rf.capture"`
- `timestamp` (string): ISO 8601 UTC
- `schema_version` (string): `"1.1.0"`
- `source` (EventSource)
- `content` (RFCaptureContent)

### EventSource
- `plugin_id` (string): default `"rf-transformer"`
- `plugin_version` (string): default `"1.1.0"`
- `sensor_id` (string)
- `tenant_id` (string): default `"demo"`

### RFCaptureContent
- `capture_index` (int)
- `center_frequency` (int, Hz)
- `bandwidth` (int, Hz)
- `sampling_rate` (int, samples/sec)
- `duration_ms` (int)
- `allocation` (string, optional)
- `location` (Location, optional): microdegrees
- `hardware` (Hardware, optional)
- `wavelet` (Wavelet): fixed-point fingerprint
- `session_id` (string, optional)
- `emitter_hint` (string, optional)
- `artifact_hash` (string, optional; legacy raw hash)

### Wavelet
- `matrix` (list[list[int]]): 3x3 fixed-point integer matrix
- `scale` (int): default 1_000_000
- `params` (WaveletParams)

### WaveletParams
- `window_ms` (int)
- `wavelet` (string, e.g., `"db4"`)
- `decomp_level` (int)
- `normalized` (bool)

Supporting types:
- Location: `latitude_udeg` (int), `longitude_udeg` (int)
- Hardware: `antenna_model`, `antenna_gain_dbi`, `receiver`, `receive_gain_db`

## 2) Error events

- `rf.capture.error`
- `vita49.capture.error`

`ErrorContent`:
- `capture_key` (string)
- `capture_index` (int)
- `error_type` (string)
- `error_message` (string)
- `source_file` (string)

## 3) Mapping into RFVector (recommended)

When encoding into RFVector:

- `event_id` -> `record.record_id`
- `source.sensor_id` -> `record.source.source_id`
- `timestamp` -> `record.time.observed_us` (microseconds since Unix epoch)
- `content.center_frequency` -> `payload.rf.band.center_hz`
- `content.bandwidth` -> `payload.rf.band.span_hz`
- `content.sampling_rate` -> `payload.rf.sample_rate_hz`
- `content.duration_ms` -> `payload.rf.duration_ms`
- `content.wavelet.*` -> `payload.rf.fingerprints[]` with `kind="wavelet_fingerprint_v1"`

If the parser can address raw IQ artifacts (URI + offsets/sample ranges), prefer emitting `record.artifacts[]` RawRef entries with a raw DIVT (`hash_mode="binary_v1"`) rather than relying on `artifact_hash`.
