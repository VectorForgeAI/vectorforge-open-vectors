# Conformance Levels

Implementations can claim conformance at four levels. Each level builds on the previous.

## Level A: Record Integrity

**What it proves**: Individual records are valid and cryptographically sound.

### Requirements

1. **Envelope validates** against `vectorforge-vector.schema.json`
2. **DIVT validates** against `divt.schema.json`
3. **Hash matches**: Recomputed `hash_b64` from canonicalized `record` equals `divt.hash_b64`

### Test Procedure

```python
import json
import jsonschema
from reference.python.json_canon_v1 import canonicalize, compute_hash_b64

# Load schemas
vector_schema = json.load(open('schemas/vectorforge-vector.schema.json'))
divt_schema = json.load(open('schemas/divt.schema.json'))

# For each record line:
data = json.loads(line)

# 1. Envelope validates
jsonschema.validate(data['record'], vector_schema)

# 2. DIVT validates
jsonschema.validate(data['divt'], divt_schema)

# 3. Hash matches
expected = compute_hash_b64(data['record'])
actual = data['divt']['hash_b64']
assert expected == actual, f"Hash mismatch"
```

### Claim

> "This implementation produces Level A conformant records."

---

## Level B: Completeness

**What it proves**: Record streams are complete and verifiable for time windows.

### Requirements

All Level A requirements, plus:

1. **Continuity Level 2 implemented**: `manifest_v1` records emitted per stream/window
2. **Manifest validates** against `vectorforge-manifest.schema.json`
3. **CC computable**: `expected_count` in manifest, received count matchable
4. **EF computable**: `EF = PF × CC` can be calculated

### Test Procedure

```python
# Collect records for a stream/window
records = [r for r in all_records if matches_window(r)]
manifest = find_manifest(stream_id, window)

# 1. Manifest validates
jsonschema.validate(manifest['record']['payload'], manifest_schema)

# 2. Count matches
assert len(records) == manifest['record']['payload']['expected_count']

# 3. Merkle root matches
from reference.python.manifest_commitment import compute_merkle_root
hashes = [r['divt']['hash_b64'] for r in sorted(records, key=lambda r: r['record']['chain']['seq'])]
expected_root = compute_merkle_root(hashes)
actual_root = manifest['record']['payload']['commitment']['root_b64']
assert expected_root == actual_root
```

### Claim

> "This implementation produces Level B conformant streams with verifiable completeness."

---

## Level C: Payload + Profile

**What it proves**: Payloads are domain-valid and tied to declared fidelity profiles.

### Requirements

All Level A and B requirements, plus:

1. **Payload validates** against the appropriate `<vector>.payload.schema.json`
2. **Profile validates** against `vectorforge-profile.schema.json`
3. **Profile reference valid**: `record.fidelity.profile_id` and `profile_divt_id` exist and are consistent

### Test Procedure

```python
# Load payload schema based on vector type
payload_schema = json.load(open(f'schemas/payloads/{vector}vector.payload.schema.json'))

# 1. Payload validates
jsonschema.validate(data['record']['payload'], payload_schema)

# 2. Profile validates (load profile by profile_id)
profile = load_profile(data['record']['fidelity']['profile_id'])
jsonschema.validate(profile, profile_schema)

# 3. Profile reference consistency
assert profile['vector'] == data['record']['vector']
```

### Claim

> "This implementation produces Level C conformant records with valid payloads and profile bindings."

---

## Level D: Benchmark

**What it proves**: Fidelity can be measured and reported per the benchmark contract.

### Requirements

All Level A, B, and C requirements, plus:

1. **Benchmark harness runs** against implementation output
2. **PF computed** using declared CBS extractors
3. **CC computed** from manifest verification
4. **EF computed** as `PF × CC`
5. **Report validates** against `bench-report.schema.json`

### Test Procedure

```bash
# Run benchmark harness
python bench/run_benchmark.py \
  --profile profiles/rf.default.95.json \
  --reference datasets/rf_starter/reference.jsonl \
  --vectors datasets/rf_starter/vector.jsonl \
  --manifest datasets/rf_starter/manifest.jsonl \
  --output report.json

# Validate report
python -c "
import json, jsonschema
report = json.load(open('report.json'))
schema = json.load(open('schemas/bench-report.schema.json'))
jsonschema.validate(report, schema)
print('Report valid')
"
```

### Claim

> "This implementation achieves Level D conformance with PF={pf}, CC={cc}, EF={ef} on {dataset}."

---

## Summary Table

| Level | What You Prove | Key Artifacts |
|-------|---------------|---------------|
| A | Records are valid | Envelope + DIVT + hash match |
| B | Streams are complete | Manifests + Merkle verification |
| C | Payloads are correct | Payload schemas + profile binding |
| D | Fidelity is measured | Benchmark report with PF/CC/EF |

## Incremental Adoption

Start with Level A. It's the foundation and catches most integration bugs.

Add Level B when you need to prove completeness (most production deployments).

Add Level C when you need strict payload validation and profile auditing.

Add Level D when you need to benchmark and compare fidelity across implementations.

## Conformance Badges

Once verified, implementations may claim:

```
VectorForge Open Vectors Conformance: Level {A|B|C|D}
Spec Version: 0.1.7
Vector Types: {rfvector, pulsevector, ...}
```
