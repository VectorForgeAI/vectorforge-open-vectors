# PulseVector

**Status: Design-ready**

PulseVector captures network activity: flow summaries, protocol metadata, and security-relevant events.

## Use Cases

- Network traffic analysis
- Flow-based monitoring (NetFlow/IPFIX alternative)
- Security event correlation
- Protocol metadata extraction (DNS, TLS, HTTP)

## Record Types

| Type | Description |
|------|-------------|
| `flow_slice_v1` | Network flow summary for a time slice |
| `net_event_v1` | Discrete network event (alert, state change) |
| `net_error_v1` | Error during network processing |
| `manifest_v1` | Continuity Level 2 window manifest |

## Payload Structure

### flow_slice_v1

```json
{
  "payload": {
    "pulse": {
      "kind": "flow_slice_v1",
      "flow_id": "5tuple:10.0.0.1:5000-10.0.1.1:443-tcp",
      "tuple": {
        "src_ip": "10.0.0.1",
        "src_port": 5000,
        "dst_ip": "10.0.1.1",
        "dst_port": 443,
        "proto": "tcp"
      },
      "stats": {
        "bytes_out": 15000,
        "bytes_in": 120000,
        "packets_out": 100,
        "packets_in": 150
      },
      "tls": {
        "sni": "example.com",
        "ja3": "hash...",
        "ja3s": "hash...",
        "cert_chain_fps": ["sha256:..."]
      },
      "dns": {
        "queries": ["example.com"],
        "answers": [{"name": "example.com", "type": "A", "data": "93.184.216.34"}]
      },
      "http": {
        "method": "GET",
        "uri": "/api/data",
        "status": 200,
        "request_headers": {},
        "response_headers": {}
      },
      "extensions": {}
    }
  }
}
```

### net_event_v1

```json
{
  "payload": {
    "pulse": {
      "kind": "net_event_v1",
      "event_type": "ids_alert",
      "occurred_us": 1738368000500000,
      "attributes": {
        "rule_id": "ET-2024-1234",
        "severity": "high",
        "message": "Suspicious TLS certificate"
      },
      "extensions": {}
    }
  }
}
```

## Key Fields

### Flow Identification

- **flow_id**: Unique flow identifier (typically 5-tuple based)
- **tuple**: The 5-tuple (src_ip, src_port, dst_ip, dst_port, proto)

### Statistics

- **bytes_out/in**: Byte counts for each direction
- **packets_out/in**: Packet counts for each direction

All values are integers.

### Protocol Metadata

Optional objects for protocol-specific data:

- **tls**: TLS handshake metadata (SNI, JA3/JA3S fingerprints, certificate chain)
- **dns**: DNS queries and responses
- **http**: HTTP request/response metadata

### Raw Artifact Reference

For deployments retaining PCAP:

```json
{
  "artifacts": [
    {
      "artifact_id": "uuid",
      "kind": "pcap",
      "uri": "s3://bucket/path/to/segment.pcap",
      "time": {"start_us": 1738368000000000, "end_us": 1738368001000000},
      "content_type": "application/vnd.tcpdump.pcap",
      "artifact_divt_id": "uuid-of-raw-divt"
    }
  ]
}
```

## Context Basis Set (CBS)

Recommended CBS for PulseVector fidelity measurement:

| Extractor | Weight | Metric | Notes |
|-----------|--------|--------|-------|
| `flow_stats_v1` | 0.5 | Relative error L1 | Bytes/packets parity |
| `metadata_parity_v1` | 0.3 | Field match rate | DNS, TLS, HTTP fields |
| `sessionization_v1` | 0.2 | Precision/Recall | Flow grouping accuracy |

### flow_stats_v1

Measures statistical accuracy:

1. Compare bytes/packets between reference and vector
2. Compute relative error: `|ref - vec| / ref`
3. Average across all flows and metrics

Reference extractor: `bench/extractors/flow_stats_v1.py`

## Fidelity Profile Example

```json
{
  "schema": {"name": "vectorforge.profile", "version": "0.1.7"},
  "profile_id": "pulse.default.95",
  "vector": "pulsevector",
  "continuity_level": 2,
  "target_pf_q15": 31129,
  "knobs": {
    "slice_s": 1,
    "sessionization": "5tuple"
  },
  "context_basis": [
    {"name": "flow_stats_v1", "weight_q15": 16384, "metric": "relative_error_l1"},
    {"name": "metadata_parity_v1", "weight_q15": 9830, "metric": "field_match"},
    {"name": "sessionization_v1", "weight_q15": 6554, "metric": "f1"}
  ]
}
```

## Fidelity Knobs

| Knob | Effect on Fidelity | Effect on Resources |
|------|-------------------|---------------------|
| slice_s ↓ | Finer temporal resolution | More records/sec |
| L7 parsing ↑ | Richer metadata | More CPU |
| sampling ↑ | Lower fidelity | Lower bandwidth |

## Schema

Full schema: `schemas/payloads/pulsevector.payload.schema.json`

## Examples

- Flow slice: `examples/records/pulsevector-record.jsonl`
- Profile: `examples/profiles/profile-pulse.default.95.json`
