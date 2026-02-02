# JSON Schemas

This directory contains the normative JSON Schemas for validating VectorForge Open Vectors records.

All schemas use [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/schema).

## Core Schemas

| Schema | Purpose |
|--------|---------|
| `divt.schema.json` | Data Integrity Validation Token (DIVT) structure |
| `vectorforge-vector.schema.json` | Vector Record envelope (common to all vectors) |
| `vectorforge-profile.schema.json` | Fidelity Profile manifest |
| `vectorforge-manifest.schema.json` | Continuity Level 2 window manifest |
| `vectorforge-rawref.schema.json` | Raw artifact reference structure |
| `vectorforge-error.schema.json` | Standard error payload |
| `bench-report.schema.json` | Benchmark report output format |

## Payload Schemas

Vector-specific payload schemas are in the `payloads/` subdirectory:

| Schema | Vector | Status |
|--------|--------|--------|
| `rfvector.payload.schema.json` | RFVector | Pilot-ready |
| `pulsevector.payload.schema.json` | PulseVector | Design-ready |
| `flowvector.payload.schema.json` | FlowVector | Spec-first |
| `exchangevector.payload.schema.json` | ExchangeVector | Spec-first |
| `videovector.payload.schema.json` | VideoVector | Spec-first |

## Usage

### Validating a Vector Record

A Vector record is a JSONL line with two top-level keys:
- `record`: The payload (validate against `vectorforge-vector.schema.json`)
- `divt`: The integrity token (validate against `divt.schema.json`)

Additionally, validate `record.payload` against the appropriate payload schema based on `record.vector`.

### Example (Python with jsonschema)

```python
import json
import jsonschema

# Load schemas
with open("schemas/vectorforge-vector.schema.json") as f:
    vector_schema = json.load(f)
with open("schemas/divt.schema.json") as f:
    divt_schema = json.load(f)
with open("schemas/payloads/rfvector.payload.schema.json") as f:
    rf_payload_schema = json.load(f)

# Parse a record line
line = '{"record": {...}, "divt": {...}}'
data = json.loads(line)

# Validate envelope
jsonschema.validate(data["record"], vector_schema)

# Validate DIVT
jsonschema.validate(data["divt"], divt_schema)

# Validate payload (if RFVector)
if data["record"]["vector"] == "rfvector":
    jsonschema.validate(data["record"]["payload"], rf_payload_schema)
```

## Schema Versioning

Schema `$id` URLs include the version: `https://vectorforge.io/schemas/v0.1.7/...`

Implementations MUST use the schemas shipped with the spec package. Do not fetch schemas from URLs at runtime.

## Strictness

All schemas use `additionalProperties: false` for strict validation. Vendor-specific extensions must use:
- `record.extensions` (namespaced)
- `payload.<vector>.extensions` (namespaced)
