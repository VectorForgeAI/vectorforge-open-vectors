#!/usr/bin/env python3
"""manifest_commitment reference implementation (VectorForge open vectors)

Implements:
- Merkle root computation using SHA3-512
- Duplicate-last padding for odd node counts
- Leaves are raw 64-byte hashes (already SHA3-512) unless specified otherwise

Usage:
  python manifest_commitment.py --test ../manifest_commitment_test_vectors.json
"""

import json
import base64
import hashlib
import sys
from typing import List

def merkle_root_sha3_512(leaves: List[bytes]) -> bytes:
    if not leaves:
        return hashlib.sha3_512(b"").digest()
    level = leaves[:]
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i+1] if i+1 < len(level) else level[i]
            nxt.append(hashlib.sha3_512(left + right).digest())
        level = nxt
    return level[0]

def run_test_vectors(path: str) -> int:
    tv = json.loads(open(path, "r", encoding="utf-8").read())
    ok = True
    for c in tv.get("cases", []):
        leaves = [base64.b64decode(x) for x in c["leaf_hashes_b64"]]
        root = base64.b64encode(merkle_root_sha3_512(leaves)).decode("ascii")
        if root != c["expected_root_b64"]:
            print("[FAIL]", c["case"])
            print(" expected:", c["expected_root_b64"])
            print(" got     :", root)
            ok = False
            break
    print("[OK]" if ok else "[NOT OK]", "manifest commitment test vectors")
    return 0 if ok else 1

def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--test":
        return run_test_vectors(argv[2])
    print(__doc__)
    return 2

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
