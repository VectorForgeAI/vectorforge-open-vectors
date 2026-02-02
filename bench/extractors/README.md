# CBS Extractors

Reference implementations of Context Basis Set (CBS) extractors for fidelity measurement.

## What is a CBS Extractor?

A CBS extractor computes context similarity between a reference (raw/ground truth) and a Vector record. The similarity score indicates how well the Vector record preserves the context present in the original data.

## Extractor Interface

Each extractor module provides:

```python
def extract(data: dict) -> Optional[dict]:
    """Extract context from data (reference or vector record)."""
    ...

def similarity(ref_context: dict, vec_context: dict) -> float:
    """Compute similarity score in [0, 1]."""
    ...

def similarity_q15(ref_context: dict, vec_context: dict) -> int:
    """Compute similarity as Q15 fixed-point [0, 32768]."""
    ...
```

## Available Extractors

### wavelet_fingerprint_v1 (RFVector)

Computes similarity between wavelet fingerprint matrices.

- **Input**: 3x3 fixed-point integer matrices with scale
- **Metric**: Normalized Frobenius similarity
- **Output**: 1.0 = identical matrices, 0.0 = maximally different

```python
from wavelet_fingerprint_v1 import extract, similarity

ref_ctx = extract({"wavelet_matrix": [[1,2,3],[4,5,6],[7,8,9]], "scale": 1000000})
vec_ctx = extract(vector_record)
score = similarity(ref_ctx, vec_ctx)
```

### flow_stats_v1 (PulseVector)

Computes similarity between flow statistics (bytes, packets).

- **Input**: Flow statistics with bytes_in/out, packets_in/out
- **Metric**: 1 - average relative error (L1)
- **Output**: 1.0 = identical stats, 0.0 = all stats differ by 100%+

```python
from flow_stats_v1 import extract, similarity

ref_ctx = extract({"stats": {"bytes_in": 1000, "bytes_out": 500, ...}})
vec_ctx = extract(vector_record)
score = similarity(ref_ctx, vec_ctx)
```

## CLI Usage

Each extractor can be run from the command line:

```bash
# Compute wavelet fingerprint similarity
python wavelet_fingerprint_v1.py datasets/rf_starter/reference.jsonl datasets/rf_starter/vector.jsonl

# Compute flow stats similarity
python flow_stats_v1.py datasets/pulse_starter/reference.jsonl datasets/pulse_starter/vector.jsonl
```

## Adding New Extractors

To add a new CBS extractor:

1. Create `<name>_v1.py` in this directory
2. Implement `extract()`, `similarity()`, `similarity_q15()`
3. Add CLI support for testing
4. Document in this README
5. Reference in the appropriate vector documentation

Extractors must be:
- **Deterministic**: Same inputs always produce same outputs
- **Versioned**: Name includes version (e.g., `_v1`)
- **Documented**: Clear description of metric and interpretation
