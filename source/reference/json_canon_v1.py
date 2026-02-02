#!/usr/bin/env python3
"""json_canon_v1 reference implementation (VectorForge open vectors)

Purpose:
- Canonicalize JSON in an RFC 8785-inspired way
- Deviations:
  - No floats (reject)
  - No duplicate keys (reject)
  - Integers must fit in safe range [-(9007199254740991)..9007199254740991]

This file also provides a CLI to run canonicalization test vectors.

Usage:
  python json_canon_v1.py --test ../json_canon_v1_test_vectors.json
"""

import json
import base64
import hashlib
import sys
from typing import Any, Dict, List, Tuple

SAFE_INT_MAX = 9007199254740991
SAFE_INT_MIN = -SAFE_INT_MAX

class CanonError(ValueError):
    pass

def _object_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    obj: Dict[str, Any] = {}
    seen = set()
    for k, v in pairs:
        if k in seen:
            raise CanonError(f"DUPLICATE_KEY:{k}")
        seen.add(k)
        obj[k] = v
    return obj

def parse_json_strict_no_floats(s: str) -> Any:
    def parse_float(_: str) -> Any:
        raise CanonError("FLOAT_NOT_ALLOWED")
    def parse_int(x: str) -> int:
        i = int(x)
        if i < SAFE_INT_MIN or i > SAFE_INT_MAX:
            raise CanonError("INT_OUT_OF_RANGE")
        return i
    def parse_constant(_: str) -> Any:
        # NaN, Infinity, -Infinity
        raise CanonError("FLOAT_NOT_ALLOWED")

    try:
        return json.loads(
            s,
            object_pairs_hook=_object_pairs_hook,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
        )
    except json.JSONDecodeError as e:
        raise CanonError(f"INVALID_JSON:{e}") from e

def _normalize(o: Any) -> Any:
    if isinstance(o, float):
        raise CanonError("FLOAT_NOT_ALLOWED")
    if isinstance(o, int):
        if o < SAFE_INT_MIN or o > SAFE_INT_MAX:
            raise CanonError("INT_OUT_OF_RANGE")
        return o
    if isinstance(o, dict):
        return {k: _normalize(o[k]) for k in sorted(o.keys())}
    if isinstance(o, list):
        return [_normalize(x) for x in o]
    return o

def canonical_json(obj: Any) -> str:
    norm = _normalize(obj)
    return json.dumps(norm, separators=(",", ":"), ensure_ascii=False)

def sha3_512_b64(data: bytes) -> str:
    return base64.b64encode(hashlib.sha3_512(data).digest()).decode("ascii")

def run_test_vectors(path: str) -> int:
    tv = json.loads(open(path, "r", encoding="utf-8").read())
    ok = True

    for c in tv.get("positive", []):
        canon = canonical_json(c["input"])
        if canon != c["canonical_json"]:
            print("[FAIL] canonical mismatch:", c["case"])
            print(" expected:", c["canonical_json"])
            print(" got     :", canon)
            ok = False
            break
        hb64 = sha3_512_b64(canon.encode("utf-8"))
        if hb64 != c["sha3_512_b64"]:
            print("[FAIL] hash mismatch:", c["case"])
            ok = False
            break

    for c in tv.get("negative", []):
        try:
            obj = parse_json_strict_no_floats(c["input_json"])
            _ = canonical_json(obj)
            print("[FAIL] expected rejection but accepted:", c["case"])
            ok = False
            break
        except CanonError as e:
            exp = c["expect_error"]
            if exp == "DUPLICATE_KEY":
                if not str(e).startswith("DUPLICATE_KEY"):
                    print("[FAIL] wrong error:", c["case"], "got", str(e))
                    ok = False
                    break
            elif exp not in str(e):
                print("[FAIL] wrong error:", c["case"], "got", str(e))
                ok = False
                break

    print("[OK]" if ok else "[NOT OK]", "json_canon_v1 test vectors")
    return 0 if ok else 1

def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--test":
        return run_test_vectors(argv[2])
    print(__doc__)
    return 2

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
