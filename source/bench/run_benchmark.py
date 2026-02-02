#!/usr/bin/env python3
"""VectorForge benchmark runner (starter)

This is a reference skeleton that computes:
- CC exactly from manifest expected_count
- PF using dataset-specific reference.jsonl
- EF = PF * CC

Usage:
  python run_benchmark.py datasets/rf_starter
  python run_benchmark.py datasets/pulse_starter
"""

import json
import base64
import hashlib
import sys
from pathlib import Path

def load_jsonl(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)

def frobenius_similarity(a, b):
    # similarity in [0,1], 1 means identical
    num = 0.0
    den = 0.0
    for i in range(3):
        for j in range(3):
            da = float(a[i][j])
            db = float(b[i][j])
            num += (da - db) ** 2
            den += da ** 2 + db ** 2
    if den == 0.0:
        return 1.0
    # 1 - normalized distance
    return max(0.0, 1.0 - (num ** 0.5) / ((den ** 0.5) + 1e-9))

def relative_error_score(ref_stats, stats):
    # 1 - average relative error (clamped)
    keys = ["bytes_out","bytes_in","packets_out","packets_in"]
    errs = []
    for k in keys:
        r = float(ref_stats[k])
        s = float(stats[k])
        if r == 0.0:
            errs.append(0.0 if s == 0.0 else 1.0)
        else:
            errs.append(abs(s - r) / r)
    avg = sum(errs) / len(errs)
    return max(0.0, 1.0 - avg)

def compute_cc(manifest, received_count):
    exp = int(manifest["payload"]["expected_count"])
    if exp <= 0:
        return None
    return max(0.0, min(1.0, received_count / exp))

def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    ds = Path(sys.argv[1])
    profile = json.loads((ds / "profile.json").read_text(encoding="utf-8"))
    profile_id = profile["profile_id"]

    # Load reference items keyed by seq
    ref = {}
    for r in load_jsonl(ds / "reference.jsonl"):
        ref[r["seq"]] = r

    # Load vector records (excluding manifest)
    vec_records = [o for o in load_jsonl(ds / "vector.jsonl")]
    received = len(vec_records)

    # Load manifest
    manifest = next(load_jsonl(ds / "manifest.jsonl"))
    cc = compute_cc(manifest, received)

    # Compute PF
    vector_type = vec_records[0]["record"]["vector"] if vec_records else profile["vector"]
    if vector_type == "rfvector":
        sims = []
        for idx, rec in enumerate(vec_records, start=1):
            seq = rec["record"]["chain"]["seq"]
            mat_ref = ref[seq]["wavelet_matrix"]
            mat_vec = rec["record"]["payload"]["rf"]["fingerprints"][0]["matrix"]
            sims.append(frobenius_similarity(mat_ref, mat_vec))
        pf = sum(sims) / len(sims) if sims else 0.0
    elif vector_type == "pulsevector":
        scores = []
        for rec in vec_records:
            seq = rec["record"]["chain"]["seq"]
            flow_id = rec["record"]["payload"]["pulse"]["flow_id"]
            ref_stats = ref[seq]["stats"]
            stats = rec["record"]["payload"]["pulse"]["stats"]
            scores.append(relative_error_score(ref_stats, stats))
        pf = sum(scores) / len(scores) if scores else 0.0
    else:
        pf = 0.0

    ef = (pf * cc) if cc is not None else None

    # Single window covering the dataset
    start_us = vec_records[0]["record"]["time"]["start_us"] if vec_records else 0
    end_us = vec_records[-1]["record"]["time"]["end_us"] if vec_records else 0
    stream_id = vec_records[0]["record"]["chain"]["stream_id"] if vec_records else "unknown"

    report = {
        "run_id": "run-" + hashlib.sha256((profile_id + str(start_us)).encode("utf-8")).hexdigest()[:12],
        "generated_at": __import__("datetime").datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "profile_id": profile_id,
        "windows": [{
            "stream_id": stream_id,
            "start_us": start_us,
            "end_us": end_us,
            "pf": pf,
            "cc": cc,
            "ef": ef,
            "notes": "starter bench run"
        }]
    }

    out = ds / "report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Wrote:", out)

if __name__ == "__main__":
    raise SystemExit(main())
