# VectorForge Bench Harness Contract (v0.1.7)

This directory defines a minimal, reproducible contract for benchmarking PF/CC/EF for Vector streams.

## 1) Concepts

- PF (Package Fidelity): context similarity between Vector Records and a reference context derived from the Raw Artifact (or a synthetic ground truth).
- CC (Completeness Confidence): the fraction of expected records received for a window.
- EF (End-to-end Fidelity): EF = PF * CC, reported only when CC is defined.

## 2) Dataset layout

A dataset lives under:

`bench/datasets/<dataset_name>/`

Required files:
- `profile.json`  
  Fidelity Profile manifest used for the dataset (must match `vectorforge-profile.schema.json`).
- `reference.jsonl`  
  Reference context items for scoring PF (dataset-specific but deterministic).
- `vector.jsonl`  
  Vector Records (JSONL). Each line is `{ "record": ..., "divt": ... }` and must validate against `vectorforge-vector.schema.json`.
- `manifest.jsonl`  
  One or more `manifest_v1` Vector Records establishing expected_count for CC.

## 3) Windows

Benchmarks score by window. The starter datasets use a single window covering all records, but the contract supports multiple windows.

## 4) Output report

The benchmark runner outputs a JSON report that can be validated against `bench-report.schema.json`:

- `run_id`
- `generated_at`
- `profile_id`
- `windows[]`: per-window PF/CC/EF breakdown

## 5) Starter datasets

This package includes:
- `rf_starter`: RFVector example using wavelet fingerprints
- `pulse_starter`: PulseVector example using flow statistics
