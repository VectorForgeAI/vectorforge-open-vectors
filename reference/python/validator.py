#!/usr/bin/env python3
"""VectorForge Open Vectors conformance validator.

Validates Vector records against schemas and checks DIVT integrity.

Usage:
    python validator.py --records output.jsonl --level A
    python validator.py --records output.jsonl --manifest manifest.jsonl --level B
    python validator.py --records output.jsonl --manifest manifest.jsonl --profile profile.json --level C
"""

import argparse
import base64
import hashlib
import json
import sys
from pathlib import Path
from typing import Optional

# Safe integer bounds for json_canon_v1
SAFE_INT_MAX = 2**53 - 1
SAFE_INT_MIN = -SAFE_INT_MAX


def canonicalize(obj: dict) -> bytes:
    """Canonicalize a JSON object for hashing (json_canon_v1)."""
    def normalize(o):
        if isinstance(o, float):
            raise ValueError("FLOAT_NOT_ALLOWED: floats are forbidden in json_canon_v1")
        if isinstance(o, bool):
            return o
        if isinstance(o, int):
            if o < SAFE_INT_MIN or o > SAFE_INT_MAX:
                raise ValueError(f"INT_OUT_OF_RANGE: {o} outside safe range")
            return o
        if isinstance(o, str):
            return o
        if o is None:
            return o
        if isinstance(o, dict):
            return {k: normalize(o[k]) for k in sorted(o.keys())}
        if isinstance(o, list):
            return [normalize(x) for x in o]
        raise ValueError(f"UNSUPPORTED_TYPE: {type(o)}")

    normalized = normalize(obj)
    json_str = json.dumps(normalized, separators=(',', ':'), ensure_ascii=False)
    return json_str.encode('utf-8')


def compute_hash_b64(record_obj: dict) -> str:
    """Compute the SHA3-512 hash of a canonicalized record, base64 encoded."""
    canon_bytes = canonicalize(record_obj)
    digest = hashlib.sha3_512(canon_bytes).digest()
    return base64.b64encode(digest).decode('ascii')


def merkle_root(leaf_hashes_b64: list[str]) -> str:
    """Compute Merkle root from base64-encoded leaf hashes."""
    if not leaf_hashes_b64:
        empty_hash = hashlib.sha3_512(b"").digest()
        return base64.b64encode(empty_hash).decode('ascii')

    leaves = [base64.b64decode(h) for h in leaf_hashes_b64]
    level = leaves

    while len(level) > 1:
        next_level = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else level[i]
            combined = hashlib.sha3_512(left + right).digest()
            next_level.append(combined)
        level = next_level

    return base64.b64encode(level[0]).decode('ascii')


def load_schema(schema_path: Path) -> dict:
    """Load a JSON schema file."""
    with open(schema_path) as f:
        return json.load(f)


def validate_record_schema(record: dict, schema: dict, validator_cls) -> list[str]:
    """Validate a record against a schema, return list of errors."""
    errors = []
    validator = validator_cls(schema)
    for error in validator.iter_errors(record):
        errors.append(f"Schema error at {error.json_path}: {error.message}")
    return errors


def validate_level_a(records: list[dict], schemas_dir: Path) -> tuple[int, int, list[str]]:
    """Validate Level A: Record Integrity."""
    try:
        import jsonschema
    except ImportError:
        print("Error: jsonschema package required. Install with: pip install jsonschema")
        sys.exit(1)

    vector_schema = load_schema(schemas_dir / "vectorforge-vector.schema.json")
    divt_schema = load_schema(schemas_dir / "divt.schema.json")

    passed = 0
    failed = 0
    all_errors = []

    for i, data in enumerate(records):
        errors = []

        # Check structure
        if 'record' not in data:
            errors.append("Missing 'record' key")
        if 'divt' not in data:
            errors.append("Missing 'divt' key")

        if errors:
            failed += 1
            all_errors.append(f"Record {i}: {errors}")
            continue

        # Validate record against the record sub-schema (no $refs, safe to extract)
        record_sub_schema = vector_schema["properties"]["record"]
        envelope_errors = validate_record_schema(
            data['record'], record_sub_schema, jsonschema.Draft202012Validator
        )
        errors.extend(envelope_errors)

        # Validate DIVT — inline $defs so internal $refs resolve correctly
        divt_validator_schema = {
            "$ref": "#/$defs/DIVT",
            "$defs": divt_schema["$defs"],
        }
        divt_errors = validate_record_schema(
            data['divt'], divt_validator_schema, jsonschema.Draft202012Validator
        )
        errors.extend(divt_errors)

        # Validate hash
        try:
            expected_hash = compute_hash_b64(data['record'])
            actual_hash = data['divt'].get('hash_b64', '')
            if expected_hash != actual_hash:
                errors.append(f"Hash mismatch: expected {expected_hash[:20]}..., got {actual_hash[:20]}...")
        except ValueError as e:
            errors.append(f"Canonicalization error: {e}")

        if errors:
            failed += 1
            all_errors.append(f"Record {i}: {errors}")
        else:
            passed += 1

    return passed, failed, all_errors


def validate_level_b(records: list[dict], manifest: dict, schemas_dir: Path) -> tuple[bool, list[str]]:
    """Validate Level B: Completeness (assumes Level A passed)."""
    errors = []

    # Validate manifest schema
    try:
        import jsonschema
        manifest_schema = load_schema(schemas_dir / "vectorforge-manifest.schema.json")
        manifest_errors = validate_record_schema(
            manifest['record']['payload'], manifest_schema, jsonschema.Draft202012Validator
        )
        errors.extend(manifest_errors)
    except Exception as e:
        errors.append(f"Manifest schema validation error: {e}")

    if errors:
        return False, errors

    payload = manifest['record']['payload']
    expected_count = payload.get('expected_count', 0)
    stream_id = payload.get('stream_id')

    # Filter records for this stream
    stream_records = [
        r for r in records
        if r['record'].get('chain', {}).get('stream_id') == stream_id
        and r['record'].get('record_type') != 'manifest_v1'
    ]

    # Check count
    if len(stream_records) != expected_count:
        errors.append(f"Count mismatch: expected {expected_count}, got {len(stream_records)}")

    # Verify Merkle root
    commitment = payload.get('commitment', {})
    if commitment.get('algo') == 'merkle_sha3_512_v1':
        # Sort by seq
        sorted_records = sorted(stream_records, key=lambda r: r['record']['chain']['seq'])
        hashes = [r['divt']['hash_b64'] for r in sorted_records]
        computed_root = merkle_root(hashes)
        expected_root = commitment.get('root_b64', '')

        if computed_root != expected_root:
            errors.append(f"Merkle root mismatch")

    return len(errors) == 0, errors


def validate_level_c(records: list[dict], profile: dict, schemas_dir: Path) -> tuple[bool, list[str]]:
    """Validate Level C: Payload + Profile (assumes Level A and B passed)."""
    try:
        import jsonschema
    except ImportError:
        print("Error: jsonschema package required")
        sys.exit(1)

    errors = []

    # Validate profile schema
    profile_schema = load_schema(schemas_dir / "vectorforge-profile.schema.json")
    profile_errors = validate_record_schema(profile, profile_schema, jsonschema.Draft202012Validator)
    if profile_errors:
        errors.extend([f"Profile: {e}" for e in profile_errors])
        return False, errors

    # Validate each record's payload
    for i, data in enumerate(records):
        record = data['record']
        vector_type = record.get('vector', '')
        payload_schema_path = schemas_dir / "payloads" / f"{vector_type}.payload.schema.json"

        if payload_schema_path.exists():
            payload_schema = load_schema(payload_schema_path)
            payload_errors = validate_record_schema(
                record.get('payload', {}), payload_schema, jsonschema.Draft202012Validator
            )
            if payload_errors:
                errors.extend([f"Record {i} payload: {e}" for e in payload_errors])

        # Check profile reference consistency
        fidelity = record.get('fidelity', {})
        if fidelity.get('profile_id') != profile.get('profile_id'):
            errors.append(f"Record {i}: profile_id mismatch")

        if record.get('vector') != profile.get('vector'):
            errors.append(f"Record {i}: vector type mismatch with profile")

    return len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(description="VectorForge conformance validator")
    parser.add_argument("--records", required=True, help="JSONL file with records")
    parser.add_argument("--manifest", help="JSONL file with manifest (for Level B+)")
    parser.add_argument("--profile", help="JSON file with profile (for Level C)")
    parser.add_argument("--level", choices=["A", "B", "C"], default="A",
                        help="Conformance level to validate")
    parser.add_argument("--schemas", default="schemas",
                        help="Path to schemas directory")

    args = parser.parse_args()

    schemas_dir = Path(args.schemas)
    if not schemas_dir.exists():
        # Try relative to script location
        schemas_dir = Path(__file__).parent.parent.parent / "schemas"

    if not schemas_dir.exists():
        print(f"Error: schemas directory not found at {schemas_dir}")
        sys.exit(1)

    # Load records
    records = []
    with open(args.records) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"Loaded {len(records)} records")
    print(f"Validating Level {args.level}...")
    print()

    # Level A
    passed, failed, errors = validate_level_a(records, schemas_dir)
    print(f"Level A (Record Integrity): {passed} passed, {failed} failed")
    if errors:
        for e in errors[:10]:  # Show first 10
            print(f"  - {e}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")

    if failed > 0:
        print("\nLevel A FAILED - fix errors before proceeding")
        sys.exit(1)

    if args.level == "A":
        print("\nLevel A PASSED")
        sys.exit(0)

    # Level B
    if not args.manifest:
        print("\nError: --manifest required for Level B")
        sys.exit(1)

    with open(args.manifest) as f:
        manifest_line = f.readline().strip()
        manifest = json.loads(manifest_line)

    passed_b, errors_b = validate_level_b(records, manifest, schemas_dir)
    print(f"\nLevel B (Completeness): {'PASSED' if passed_b else 'FAILED'}")
    if errors_b:
        for e in errors_b:
            print(f"  - {e}")

    if not passed_b:
        sys.exit(1)

    if args.level == "B":
        print("\nLevel B PASSED")
        sys.exit(0)

    # Level C
    if not args.profile:
        print("\nError: --profile required for Level C")
        sys.exit(1)

    with open(args.profile) as f:
        profile = json.load(f)

    passed_c, errors_c = validate_level_c(records, profile, schemas_dir)
    print(f"\nLevel C (Payload + Profile): {'PASSED' if passed_c else 'FAILED'}")
    if errors_c:
        for e in errors_c[:10]:
            print(f"  - {e}")
        if len(errors_c) > 10:
            print(f"  ... and {len(errors_c) - 10} more errors")

    if passed_c:
        print("\nLevel C PASSED")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
