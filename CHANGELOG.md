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

## [Unreleased]

### Planned

- Additional CBS extractors for benchmark coverage
- Extended test vector suites
- Schema refinements based on implementation feedback
