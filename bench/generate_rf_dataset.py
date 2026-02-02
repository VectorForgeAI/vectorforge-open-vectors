#!/usr/bin/env python3
"""Generate the rf_starter dataset.

This script writes:
- bench/datasets/rf_starter/profile.json
- bench/datasets/rf_starter/reference.jsonl
- bench/datasets/rf_starter/vector.jsonl
- bench/datasets/rf_starter/manifest.jsonl

The dataset is synthetic and is intended to validate:
- json_canon_v1 hashing
- envelope correctness
- Continuity Level 2 manifests (Merkle commitments)
- a starter PF metric based on wavelet fingerprint similarity
"""

import json, base64, hashlib, uuid
from pathlib import Path
from datetime import datetime

SAFE_INT_MAX = 2**53 - 1
SAFE_INT_MIN = -SAFE_INT_MAX

def canonicalize_record_obj(record_obj: dict) -> bytes:
    def norm(o):
        if isinstance(o, float):
            raise ValueError("FLOAT_NOT_ALLOWED")
        if isinstance(o, int):
            if o < SAFE_INT_MIN or o > SAFE_INT_MAX:
                raise ValueError("INT_OUT_OF_RANGE")
            return o
        if isinstance(o, dict):
            return {k: norm(o[k]) for k in sorted(o.keys())}
        if isinstance(o, list):
            return [norm(x) for x in o]
        return o
    s = json.dumps(norm(record_obj), separators=(",", ":"), ensure_ascii=False)
    return s.encode("utf-8")

def make_divt_for_record(record_obj: dict, tenant_id: str) -> dict:
    canon_bytes = canonicalize_record_obj(record_obj)
    hash_b64 = base64.b64encode(hashlib.sha3_512(canon_bytes).digest()).decode("ascii")
    return {
        "divt_id": str(uuid.uuid4()),
        "tenant_id": tenant_id,
        "hash_b64": hash_b64,
        "hash_mode": "json_canon_v1",
        "hash_version": "sha3-512-v1",
        "crypto_mode": "hybrid",
        "signatures": {
            "key_ver": "v1",
            "ecdsa": "BASE64_SIGNATURE_PLACEHOLDER",
            "pqc": "BASE64_SIGNATURE_PLACEHOLDER"
        },
        "signature_version": "keyset-TEST-v1",
        "ledger_status": "pending",
        "revoked": False,
        "created_at": datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
    }

def merkle_root(leaves: list[bytes]) -> bytes:
    if not leaves:
        return hashlib.sha3_512(b"").digest()
    lvl = leaves[:]
    while len(lvl) > 1:
        nxt = []
        for j in range(0, len(lvl), 2):
            left = lvl[j]
            right = lvl[j+1] if j+1 < len(lvl) else lvl[j]
            nxt.append(hashlib.sha3_512(left+right).digest())
        lvl = nxt
    return lvl[0]

def main():
    root = Path(__file__).resolve().parents[1]
    ds = root / "bench" / "datasets" / "rf_starter"
    ds.mkdir(parents=True, exist_ok=True)

    tenant = "demo"
    stream_id = "rf/sensor-01/center2450MHz/span20MHz"
    t0 = 1738368000000000
    dt = 1_000_000

    profile = {
        "schema":{"name":"vectorforge.profile","version":"0.1.7"},
        "profile_id":"rf.default.95",
        "vector":"rfvector",
        "continuity_level": 2,
        "target_pf_q15": int(0.95 * 32768),
        "knobs":{"segment_ms":1000,"overlap_ms":250,"fingerprint":"wavelet_fingerprint_v1"},
        "context_basis":[
            {"name":"wavelet_fingerprint_v1","weight_q15":20000,"metric":"frobenius_q15","notes":"normalized Frobenius similarity"},
            {"name":"detection_parity_v1","weight_q15":12768,"metric":"f1","notes":"event parity when detections present"}
        ]
    }
    (ds/"profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")

    ref_lines = []
    vec_lines = []
    N = 20
    for i in range(N):
        mat = [[i+1, i+2, i+3],[i+4, i+5, i+6],[i+7, i+8, i+9]]
        ref_lines.append(json.dumps({"seq": i+1, "wavelet_matrix": mat, "scale": 1000000}, separators=(",", ":"), ensure_ascii=False))

        record = {
            "schema":{"name":"vectorforge.vector","version":"0.1.7"},
            "vector":"rfvector",
            "record_type":"rf_capture_v1",
            "record_id": str(uuid.uuid4()),
            "tenant_id": tenant,
            "time":{"start_us": t0 + i*dt, "end_us": t0 + (i+1)*dt, "observed_us": t0 + (i+1)*dt},
            "source":{"source_id":"sensor-01","source_type":"rf_sensor","labels":{"plugin_id":"rf-transformer","plugin_version":"1.1.0","time_source":"ntp"}},
            "chain":{"stream_id": stream_id, "seq": i+1},
            "retention":{"raw_available_until_us": t0 + 7*24*3600*1_000_000, "policy_id":"rolling-7d"},
            "fidelity":{"profile_id": profile["profile_id"], "profile_divt_id": str(uuid.uuid4())},
            "payload":{
                "rf":{
                    "band":{"center_hz":2450000000,"span_hz":20000000},
                    "sample_rate_hz":20000000,
                    "duration_ms":1000,
                    "fingerprints":[
                        {"kind":"wavelet_fingerprint_v1","scale":1000000,"matrix":mat,
                         "params":{"window_ms":20,"wavelet":"db4","decomp_level":3,"normalized":True}}
                    ],
                    "extensions": {}
                }
            },
            "extensions": {}
        }
        divt = make_divt_for_record(record, tenant)
        vec_lines.append(json.dumps({"record":record,"divt":divt}, separators=(",", ":"), ensure_ascii=False))

    (ds/"reference.jsonl").write_text("\n".join(ref_lines) + "\n", encoding="utf-8")
    (ds/"vector.jsonl").write_text("\n".join(vec_lines) + "\n", encoding="utf-8")

    leaves = [base64.b64decode(json.loads(line)["divt"]["hash_b64"]) for line in vec_lines]
    manifest_obj = {
        "kind":"manifest_v1",
        "stream_id": stream_id,
        "window":{"start_us": t0, "end_us": t0 + N*dt},
        "expected_count": N,
        "commitment":{
            "algo":"merkle_sha3_512_v1",
            "root_b64": base64.b64encode(merkle_root(leaves)).decode("ascii"),
            "input":"divt.hash_b64",
            "ordering":"seq_asc"
        }
    }
    manifest_record = {
        "schema":{"name":"vectorforge.vector","version":"0.1.7"},
        "vector":"rfvector",
        "record_type":"manifest_v1",
        "record_id": str(uuid.uuid4()),
        "tenant_id": tenant,
        "time":{"start_us": t0, "end_us": t0 + N*dt, "observed_us": t0 + N*dt},
        "source":{"source_id":"bench","source_type":"bench_generator","labels":{}},
        "chain":{"stream_id": stream_id, "seq": N+1},
        "retention":{"raw_available_until_us": t0 + 7*24*3600*1_000_000, "policy_id":"rolling-7d"},
        "fidelity":{"profile_id": profile["profile_id"], "profile_divt_id": str(uuid.uuid4())},
        "payload": manifest_obj,
        "extensions": {}
    }
    manifest_divt = make_divt_for_record(manifest_record, tenant)
    (ds/"manifest.jsonl").write_text(json.dumps({"record":manifest_record,"divt":manifest_divt}, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")

    print("Wrote dataset to", ds)

if __name__ == "__main__":
    main()
