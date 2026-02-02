# Go Reference Implementations

Go 1.21+ reference implementations for VectorForge Open Vectors.

## Files

| File | Description |
|------|-------------|
| `json_canon_v1.go` | JSON canonicalization |
| `manifest_commitment.go` | Merkle root computation |

## Building

```bash
go build -o json_canon_v1 json_canon_v1.go
go build -o manifest_commitment manifest_commitment.go
```

## JSON Canonicalization

The `json_canon_v1.go` implementation provides canonical JSON output.

### CLI Usage

```bash
# Canonicalize JSON from stdin
echo '{"b": 2, "a": 1}' | ./json_canon_v1
# Output: {"a":1,"b":2}

# Compute hash
echo '{"b": 2, "a": 1}' | ./json_canon_v1 --hash
# Output: base64-encoded-sha3-512...
```

### Library Usage

```go
import "your/module/reference/go/jsoncanon"

record := map[string]interface{}{"b": 2, "a": 1}
canonBytes, err := jsoncanon.Canonicalize(record)
hashB64, err := jsoncanon.ComputeHashB64(record)
```

## Manifest Commitment

The `manifest_commitment.go` implementation computes Merkle roots.

### CLI Usage

```bash
# Compute Merkle root from base64 leaf hashes
./manifest_commitment "aX8thWFyy4MJ..." "hEbEbuA3k7pu..."
# Output: base64-encoded-merkle-root...
```

### Library Usage

```go
import "your/module/reference/go/merkle"

leaves := []string{"aX8thWFyy4MJ...", "hEbEbuA3k7pu..."}
root := merkle.ComputeRoot(leaves)
```

## Testing

Run against test vectors:

```bash
# Test canonicalization (manual verification)
cat ../../test-vectors/json_canon_v1_test_vectors.json | \
  jq -r '.cases[] | select(.expected_canon) | .input' | \
  while read input; do
    echo "$input" | ./json_canon_v1
  done

# Test Merkle commitment
./manifest_commitment $(cat ../../test-vectors/manifest_commitment_test_vectors.json | \
  jq -r '.cases[2].leaf_hashes_b64[]')
```

## Notes

- Both implementations use `crypto/sha3` for SHA3-512
- Floats are rejected during canonicalization
- Integer range is checked against ±(2^53-1)
