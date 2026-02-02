#!/usr/bin/env python3
"""Reference CBS extractor: flow_stats_v1

Computes similarity between flow statistics from PulseVector records.

Metric: Relative Error L1
- Extract bytes/packets stats from reference and vector
- Compute relative error for each stat: |ref - vec| / max(ref, 1)
- Average across all stats
- Convert to similarity: 1 - avg_error

Usage:
    from flow_stats_v1 import extract, similarity

    ref_context = extract(reference_data)
    vec_context = extract(vector_record)
    score = similarity(ref_context, vec_context)
"""

from typing import Optional


def extract(data: dict) -> Optional[dict]:
    """Extract flow statistics context from data.

    Args:
        data: Either a reference record or a Vector record

    Returns:
        Context dict with 'stats' containing bytes_in/out, packets_in/out
    """
    # Handle reference format (from benchmark reference.jsonl)
    if 'stats' in data and 'flow_id' in data:
        return {
            'flow_id': data.get('flow_id'),
            'stats': data['stats']
        }

    # Handle Vector record format
    if 'record' in data:
        payload = data['record'].get('payload', {})
        pulse = payload.get('pulse', {})

        if pulse.get('kind') == 'flow_slice_v1':
            return {
                'flow_id': pulse.get('flow_id'),
                'stats': pulse.get('stats', {})
            }

    # Handle direct payload format
    if 'pulse' in data:
        pulse = data['pulse']
        if pulse.get('kind') == 'flow_slice_v1':
            return {
                'flow_id': pulse.get('flow_id'),
                'stats': pulse.get('stats', {})
            }

    return None


def relative_error(ref_val: int, vec_val: int) -> float:
    """Compute relative error between two values."""
    if ref_val == 0:
        return 0.0 if vec_val == 0 else 1.0
    return abs(ref_val - vec_val) / ref_val


def similarity(ref_context: dict, vec_context: dict) -> float:
    """Compute similarity between two flow statistics contexts.

    Args:
        ref_context: Context extracted from reference
        vec_context: Context extracted from vector record

    Returns:
        Similarity score in [0, 1] where 1 is identical
    """
    if ref_context is None or vec_context is None:
        return 0.0

    ref_stats = ref_context.get('stats', {})
    vec_stats = vec_context.get('stats', {})

    if not ref_stats or not vec_stats:
        return 0.0

    # Compute relative error for each stat
    errors = []

    stat_keys = ['bytes_in', 'bytes_out', 'packets_in', 'packets_out']
    for key in stat_keys:
        ref_val = ref_stats.get(key, 0)
        vec_val = vec_stats.get(key, 0)
        errors.append(relative_error(ref_val, vec_val))

    if not errors:
        return 1.0

    # Average error
    avg_error = sum(errors) / len(errors)

    # Convert to similarity (clamped to [0, 1])
    similarity_score = max(0.0, 1.0 - avg_error)
    return similarity_score


def similarity_q15(ref_context: dict, vec_context: dict) -> int:
    """Compute similarity as Q15 fixed-point integer.

    Returns:
        Similarity score in [0, 32768] where 32768 is identical
    """
    score = similarity(ref_context, vec_context)
    return int(score * 32768)


# CLI for testing
if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 3:
        print("Usage: flow_stats_v1.py <reference.jsonl> <vector.jsonl>")
        print()
        print("Computes average flow statistics similarity between reference and vector records.")
        sys.exit(1)

    ref_file = sys.argv[1]
    vec_file = sys.argv[2]

    # Load records
    with open(ref_file) as f:
        refs = [json.loads(line) for line in f if line.strip()]

    with open(vec_file) as f:
        vecs = [json.loads(line) for line in f if line.strip()]

    # Match by sequence number and compute similarities
    ref_by_seq = {r.get('seq', i): r for i, r in enumerate(refs)}

    total_sim = 0.0
    count = 0

    for vec in vecs:
        if 'record' not in vec:
            continue
        seq = vec['record'].get('chain', {}).get('seq')
        if seq is None or seq not in ref_by_seq:
            continue

        ref = ref_by_seq[seq]
        ref_ctx = extract(ref)
        vec_ctx = extract(vec)

        if ref_ctx and vec_ctx:
            sim = similarity(ref_ctx, vec_ctx)
            total_sim += sim
            count += 1
            print(f"seq={seq}: similarity={sim:.4f}")

    if count > 0:
        avg = total_sim / count
        print(f"\nAverage similarity: {avg:.4f} (Q15: {int(avg * 32768)})")
    else:
        print("No matching records found")
