#!/usr/bin/env python3
"""Reference CBS extractor: wavelet_fingerprint_v1

Computes similarity between wavelet fingerprint matrices from RFVector records.

Metric: Normalized Frobenius similarity
- Extract 3x3 wavelet matrices from reference and vector
- Compute Frobenius distance: ||A - B||_F
- Normalize by max possible distance
- Convert to similarity: 1 - (distance / max_distance)

Usage:
    from wavelet_fingerprint_v1 import extract, similarity

    ref_context = extract(reference_data)
    vec_context = extract(vector_record)
    score = similarity(ref_context, vec_context)
"""

import math
from typing import Optional


def extract(data: dict) -> Optional[dict]:
    """Extract wavelet fingerprint context from data.

    Args:
        data: Either a reference record or a Vector record

    Returns:
        Context dict with 'matrix' and 'scale', or None if not found
    """
    # Handle reference format (from benchmark reference.jsonl)
    if 'wavelet_matrix' in data:
        return {
            'matrix': data['wavelet_matrix'],
            'scale': data.get('scale', 1000000)
        }

    # Handle Vector record format
    if 'record' in data:
        payload = data['record'].get('payload', {})
        rf = payload.get('rf', {})
        fingerprints = rf.get('fingerprints', [])

        for fp in fingerprints:
            if fp.get('kind') == 'wavelet_fingerprint_v1':
                return {
                    'matrix': fp.get('matrix', []),
                    'scale': fp.get('scale', 1000000)
                }

    # Handle direct payload format
    if 'rf' in data:
        fingerprints = data['rf'].get('fingerprints', [])
        for fp in fingerprints:
            if fp.get('kind') == 'wavelet_fingerprint_v1':
                return {
                    'matrix': fp.get('matrix', []),
                    'scale': fp.get('scale', 1000000)
                }

    return None


def frobenius_norm(matrix: list[list[int]]) -> float:
    """Compute Frobenius norm of a matrix."""
    total = 0
    for row in matrix:
        for val in row:
            total += val * val
    return math.sqrt(total)


def matrix_diff(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    """Compute element-wise difference of two matrices."""
    if len(a) != len(b):
        raise ValueError("Matrix dimensions must match")
    result = []
    for i, row_a in enumerate(a):
        row_b = b[i]
        if len(row_a) != len(row_b):
            raise ValueError("Matrix dimensions must match")
        result.append([row_a[j] - row_b[j] for j in range(len(row_a))])
    return result


def similarity(ref_context: dict, vec_context: dict) -> float:
    """Compute similarity between two wavelet fingerprint contexts.

    Args:
        ref_context: Context extracted from reference
        vec_context: Context extracted from vector record

    Returns:
        Similarity score in [0, 1] where 1 is identical
    """
    if ref_context is None or vec_context is None:
        return 0.0

    ref_matrix = ref_context.get('matrix', [])
    vec_matrix = vec_context.get('matrix', [])
    ref_scale = ref_context.get('scale', 1000000)
    vec_scale = vec_context.get('scale', 1000000)

    # Validate dimensions
    if not ref_matrix or not vec_matrix:
        return 0.0

    if len(ref_matrix) != len(vec_matrix):
        return 0.0

    # Scale matrices to common scale if different
    if ref_scale != vec_scale:
        # Scale vec_matrix to ref_scale
        ratio = ref_scale / vec_scale
        vec_matrix = [
            [int(val * ratio) for val in row]
            for row in vec_matrix
        ]

    # Compute Frobenius distance
    try:
        diff = matrix_diff(ref_matrix, vec_matrix)
        distance = frobenius_norm(diff)
    except ValueError:
        return 0.0

    # Compute max possible distance (both matrices at max magnitude)
    # For a 3x3 matrix with scale 1e6, max single value ~= 1e6
    # Max distance ~= sqrt(9 * (2e6)^2) ~= 6e6
    max_distance = frobenius_norm(ref_matrix) + frobenius_norm(vec_matrix)
    if max_distance == 0:
        return 1.0 if distance == 0 else 0.0

    # Convert to similarity
    similarity_score = max(0.0, 1.0 - (distance / max_distance))
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
        print("Usage: wavelet_fingerprint_v1.py <reference.jsonl> <vector.jsonl>")
        print()
        print("Computes average wavelet fingerprint similarity between reference and vector records.")
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
