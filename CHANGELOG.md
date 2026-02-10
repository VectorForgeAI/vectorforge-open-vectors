# Changelog

All notable changes to the VectorForge Open Vectors specification will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.7] - 2025-02-01

### Added

- Initial public release of the Open Vectors specification
- Core schemas: vector envelope, profile, manifest, rawref, error
- Payload schemas: RFVector, PulseVector, FlowVector, ExchangeVector, VideoVector
- DIVT schema and semantics documentation
- Reference implementations for JSON canonicalization (Python, Go)
- Reference implementations for manifest commitment (Python, Go)
- Conformance test vectors for canonicalization and Merkle commitments
- Benchmark harness with starter datasets (RF, Pulse)
- Fidelity framework with PF/CC/EF metrics

### Notes

- RFVector is pilot-ready with comprehensive documentation
- PulseVector is design-ready with baseline schema
- FlowVector, ExchangeVector, VideoVector are spec-first targets (skeletal schemas)

## [0.2.0] - 2026-02-10

### Added

- **RFVector payload v0.2.0**: `spectral_measurements` block (peak/mean/noise/SNR/flatness/variance/PAPR, all fixed-point integers), `location` block (lat/lon microdegrees, alt mm, accuracy, bearing, AoA), `classification` block, `entity_id`, `correlation` block, `hardware` metadata
- **PulseVector payload v0.2.0**: `timing` block (first_seen_us, last_seen_us, duration_us), typed `fingerprints[]` array (JA3, JA3S, JA4, HASSH, flow_behavior, dns_pattern, cert_fingerprint), `classification` block, `entity_id`, `correlation` block, `session_id`, `severity` on net_event_v1; fully typed `tls`, `dns`, `http` detail blocks replacing untyped objects
- **VideoVector payload v0.2.0**: fully typed `stream` block (codec, resolution, fps_x1000, bitrate, device, camera_intrinsics), typed `keyframes[]` with perceptual/difference hashes, color histograms, dominant colors; typed `motion` block (optical flow magnitudes, scene changes, centroid); `quality` metrics (blur, noise, PTS gaps, GOP regularity); typed `tracks[]` and `events[]`; `thumbnail_tile` block
- Record envelope schema bumped to v0.2.0 ($id URL updated)

### Changed

- All floating-point values in payload schemas converted to fixed-point integers for DIVT compatibility (json_canon_v1 mode forbids floats)
- PulseVector `flow_slice_v1` now requires `timing` block (replaces implicit time from envelope)
- PulseVector `stats` block extended with retransmits, rst_count, fin_count, syn_count
- VideoVector `stream` block now has required typed fields (codec, width, height, fps_x1000) instead of untyped object
- All confidence/percentage fields use integer _pct suffix (0-100 range)

### Notes

- RFVector, PulseVector, and VideoVector are implementation-ready with comprehensive typed schemas
- FlowVector and ExchangeVector remain skeletal (deferred)

## [Unreleased]

### Planned

- FlowVector payload schema v0.2.0
- ExchangeVector payload schema v0.2.0
- Additional CBS extractors for benchmark coverage
- Extended test vector suites
