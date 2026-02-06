# PulseVector Payload Schema v0.2.0

**Status:** Proposed
**Previous Version:** v0.1.7
**Date:** February 5, 2026

---

## Overview

The PulseVector Payload is the core data structure produced by the Net Transformer after ingesting network traffic from PCAP captures, NetFlow exports, DNS logs, Zeek logs, and firewall logs. Each payload captures a single network flow observation or discrete network event — its endpoints, protocol metadata, encrypted session details, fingerprints, classification, and (when established) its identity as a tracked entity correlated across multiple sensor domains.

Every PulseVector payload is sealed with a DIVT (Digital Integrity Verification Token) for cryptographic chain-of-custody before entering DataFoundry.

**Production data flow:**

```
PCAP / NetFlow / Zeek / Firewall → Net Transformer → PulseVector Payload (+ DIVT) → DataFoundry → LSM → GHOST
```

**Supported input formats:**

| Format | Adapter | Record Type |
|--------|---------|-------------|
| Standard PCAP (.pcap, .pcapng) | `PcapAdapter` | `packet` → `flow_slice_v1` |
| Encrypted PCAP (TLS/IPsec) | `PcapAdapter` | `packet` → `flow_slice_v1` (metadata only, no decryption) |
| Zeek/Bro logs (.log) | `ZeekAdapter` | `flow` / `event` → `flow_slice_v1` / `net_event_v1` |
| NetFlow/IPFIX (JSON/CSV) | `NetFlowAdapter` | `flow` → `flow_slice_v1` |
| Firewall logs (syslog) | `FirewallAdapter` | `event` → `net_event_v1` |

---

## Full Schema — Kind: `flow_slice_v1`

> Fields marked with **🆕** are new in v0.2.0 (not present in v0.1.7).
> Fields marked with **📐** existed in v0.1.7 but have been expanded with full sub-field definitions.

```json
{
  "pulse": {
    "schema_version": "0.2.0",                           // 🆕
    "kind": "flow_slice_v1",
    "flow_id": "flow_a1b2c3d4e5f67890",

    "tuple": {
      "src_ip": "192.168.1.100",
      "src_port": 52341,
      "dst_ip": "93.184.216.34",
      "dst_port": 443,
      "proto": 6,
      "ip_version": 4                                    // 🆕
    },

    "timing": {                                          // 🆕 (entire block)
      "first_seen_us": 1738800000000000,
      "last_seen_us": 1738800060000000,
      "duration_us": 60000000
    },

    "stats": {
      "bytes_out": 154320,
      "bytes_in": 2048576,
      "packets_out": 120,
      "packets_in": 1450,
      "retransmits": 3,                                  // 🆕
      "rst_count": 0,                                    // 🆕
      "fin_count": 1,                                    // 🆕
      "syn_count": 1                                     // 🆕
    },

    "tls": {                                             // 📐 was "type": "object"
      "version": "TLSv1.3",
      "sni": "www.example.com",
      "cipher_suite": "TLS_AES_256_GCM_SHA384",
      "cipher_suite_id": 4866,
      "extensions_count": 12,
      "alpn": ["h2", "http/1.1"],
      "cert_chain": [
        {
          "subject_cn": "www.example.com",
          "issuer_cn": "DigiCert SHA2 Extended Validation Server CA",
          "serial": "0a:12:3b:4c:5d:6e:7f:80",
          "not_before": "2025-06-01T00:00:00Z",
          "not_after": "2026-06-01T23:59:59Z",
          "san": ["www.example.com", "example.com"],
          "fingerprint_sha256": "a1b2c3d4e5f6..."
        }
      ],
      "handshake_duration_us": 45000,
      "resumed": false
    },

    "dns": {                                             // 📐 was "type": "object"
      "query_name": "www.example.com",
      "query_type": "A",
      "query_class": "IN",
      "response_code": "NOERROR",
      "answers": [
        {
          "name": "www.example.com",
          "type": "A",
          "ttl": 300,
          "data": "93.184.216.34"
        }
      ],
      "authority_count": 2,
      "additional_count": 1,
      "response_time_us": 12000,
      "is_dnssec": false,
      "is_recursive": true
    },

    "http": {                                            // 📐 was "type": "object"
      "method": "GET",
      "uri": "/api/v1/data",
      "host": "www.example.com",
      "status_code": 200,
      "request_content_length": 0,
      "response_content_length": 24576,
      "content_type": "application/json",
      "user_agent_hash": "sha256:a1b2c3d4",
      "referrer_domain": "google.com",
      "version": "HTTP/2"
    },

    "fingerprints": [                                    // 🆕 (entire array)
      {
        "kind": "ja3_v1",
        "hash": "e7d705a3286e19ea42f587b344ee6865",
        "raw_string": "771,4866-4867-4865-49196-...",
        "params": {
          "tls_version": "0x0303",
          "source": "client_hello"
        }
      },
      {
        "kind": "ja3s_v1",
        "hash": "eb1d94daa7e0344597e756a1fb6e7054",
        "raw_string": "771,4866,0-51-43",
        "params": {
          "source": "server_hello"
        }
      },
      {
        "kind": "ja4_v1",
        "hash": "t13d1516h2_8daaf6152771_b186095e22b6",
        "params": {
          "protocol": "t",
          "version": "13",
          "sni_present": "d",
          "cipher_count": 15,
          "extension_count": 16,
          "alpn_first": "h2"
        }
      },
      {
        "kind": "flow_behavior_v1",
        "scale": 1000000,
        "matrix": [
          [120000, 250000, 80000],
          [300000, 150000, 100000],
          [50000, 180000, 70000]
        ],
        "params": {
          "rows": "packet_size_buckets",
          "cols": "inter_arrival_time_buckets",
          "bucket_boundaries_bytes": [0, 200, 600, 65535],
          "bucket_boundaries_us": [0, 1000, 50000, 9999999],
          "normalized": true
        }
      },
      {
        "kind": "dns_pattern_v1",
        "query_entropy": 3.45,
        "label_count": 3,
        "max_label_length": 15,
        "has_numeric_labels": false,
        "query_length": 22,
        "unique_query_types": 2,
        "params": {
          "window_queries": 100
        }
      },
      {
        "kind": "cert_fingerprint_v1",
        "hash": "a1b2c3d4e5f6...",
        "subject_cn": "www.example.com",
        "issuer_cn": "DigiCert SHA2 Extended Validation Server CA",
        "valid_days_remaining": 116,
        "params": {
          "hash_algorithm": "sha256"
        }
      }
    ],

    "classification": {                                  // 🆕 (entire block)
      "traffic_type": "web_browsing",
      "confidence": 0.92,
      "model": "net-classifier-v1.0"
    },

    "entity_id": "ent_a1b2c3d4",                        // 🆕

    "correlation": {                                     // 🆕 (entire block)
      "source_refs": ["rf:det_1234", "radar:trk_5678"],
      "method": "multi_sensor_fusion",
      "confidence": 0.87,
      "baseline_ref": "baseline_known_server_v2",
      "deviation_flags": ["new_cipher_suite", "unusual_timing"]
    },

    "session_id": "sess_2026-02-05_capture_001",         // 🆕
    "extensions": {}                                     // 🆕
  }
}
```

---

## Full Schema — Kind: `net_event_v1`

> Fields marked with **🆕** are new in v0.2.0 (not present in v0.1.7).

```json
{
  "pulse": {
    "schema_version": "0.2.0",                           // 🆕
    "kind": "net_event_v1",
    "event_type": "firewall_drop",
    "occurred_us": 1738800000000000,
    "severity": "medium",                                // 🆕

    "attributes": {
      "src_ip": "10.0.0.5",
      "dst_ip": "93.184.216.34",
      "dst_port": 443,
      "proto": 6,
      "rule_id": "FW-2024-001",
      "action": "drop",
      "reason": "policy_violation",
      "message": "Outbound connection blocked by policy"
    },

    "fingerprints": [],                                  // 🆕 (entire array)

    "classification": {                                  // 🆕 (entire block)
      "traffic_type": "unknown",
      "confidence": 0.0,
      "model": "none"
    },

    "entity_id": null,                                   // 🆕

    "correlation": {                                     // 🆕 (entire block)
      "source_refs": [],
      "method": null,
      "confidence": 0.0,
      "baseline_ref": null,
      "deviation_flags": []
    },

    "session_id": null,                                  // 🆕
    "extensions": {}                                     // 🆕
  }
}
```

---

## Field Reference — `flow_slice_v1`

### pulse (root)

| Field | Type | Required | New in v0.2.0 | Description |
|-------|------|----------|:---:|-------------|
| `schema_version` | string | Yes | 🆕 | Schema version. Currently `"0.2.0"`. |
| `kind` | const | Yes | | Discriminator. Must be `"flow_slice_v1"`. |
| `flow_id` | string | Yes | | Deterministic identifier: `flow_` + SHA-256 of 5-tuple + start time, truncated to 16 hex chars. |

### pulse.tuple — Who is talking to whom

| Field | Type | Required | New in v0.2.0 | Description |
|-------|------|----------|:---:|-------------|
| `src_ip` | string | Yes | | Source IP address (IPv4 dotted-quad or IPv6). |
| `src_port` | integer | Yes | | Source port number (0–65535). |
| `dst_ip` | string | Yes | | Destination IP address. |
| `dst_port` | integer | Yes | | Destination port number. |
| `proto` | integer | Yes | | IP protocol number: `6` = TCP, `17` = UDP, `1` = ICMP. Changed from string to integer in v0.2.0. |
| `ip_version` | integer | Yes | 🆕 | IP version: `4` or `6`. |

### pulse.timing — When did this flow happen 🆕

> This entire block is new in v0.2.0.

| Field | Type | Required | New in v0.2.0 | Description |
|-------|------|----------|:---:|-------------|
| `first_seen_us` | integer | Yes | 🆕 | Microsecond Unix epoch of the first packet in this flow. |
| `last_seen_us` | integer | Yes | 🆕 | Microsecond Unix epoch of the last packet in this flow. |
| `duration_us` | integer | Yes | 🆕 | Flow duration in microseconds (`last_seen_us - first_seen_us`). |

### pulse.stats — How much data moved

| Field | Type | Required | New in v0.2.0 | Description |
|-------|------|----------|:---:|-------------|
| `bytes_out` | integer | Yes | | Bytes sent from source to destination. |
| `bytes_in` | integer | Yes | | Bytes sent from destination to source. |
| `packets_out` | integer | Yes | | Packets sent from source to destination. |
| `packets_in` | integer | Yes | | Packets sent from destination to source. |
| `retransmits` | integer | No | 🆕 | TCP retransmission count. `0` if not TCP or not detectable. |
| `rst_count` | integer | No | 🆕 | TCP RST flag count. Indicates abnormal connection termination. |
| `fin_count` | integer | No | 🆕 | TCP FIN flag count. Indicates normal connection teardown. |
| `syn_count` | integer | No | 🆕 | TCP SYN flag count. `1` = normal handshake, `>1` = retries or scan. |

### pulse.tls — TLS/SSL session metadata 📐

> This block existed as `"type": "object"` in v0.1.7. All fields below are **fully defined** in v0.2.0.
> Populated from encrypted PCAP handshake parsing (no decryption). Nullable — `null` when flow has no TLS.

| Field | Type | Required | New in v0.2.0 | Description |
|-------|------|----------|:---:|-------------|
| `version` | string | Yes | 📐 | Negotiated TLS version: `"TLSv1.0"`, `"TLSv1.1"`, `"TLSv1.2"`, `"TLSv1.3"`. |
| `sni` | string / null | No | 📐 | Server Name Indication from ClientHello. `null` if not present. |
| `cipher_suite` | string | Yes | 📐 | Human-readable cipher suite name (e.g., `"TLS_AES_256_GCM_SHA384"`). |
| `cipher_suite_id` | integer | Yes | 📐 | IANA cipher suite number (e.g., `4866`). |
| `extensions_count` | integer | No | 📐 | Number of TLS extensions in ClientHello. |
| `alpn` | array of strings | No | 📐 | Application-Layer Protocol Negotiation values (e.g., `["h2", "http/1.1"]`). |
| `cert_chain` | array of objects | No | 📐 | X.509 certificate chain from TLS Certificate message. See sub-table. |
| `handshake_duration_us` | integer | No | 📐 | Time from ClientHello to Finished in microseconds. |
| `resumed` | boolean | No | 📐 | Whether this is a resumed session (session ticket or PSK). |

**pulse.tls.cert_chain[] — Certificate details**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `subject_cn` | string | Yes | Subject Common Name. |
| `issuer_cn` | string | Yes | Issuer Common Name. |
| `serial` | string | Yes | Certificate serial number (colon-separated hex). |
| `not_before` | string (ISO 8601) | Yes | Certificate validity start. |
| `not_after` | string (ISO 8601) | Yes | Certificate validity end. |
| `san` | array of strings | No | Subject Alternative Names. |
| `fingerprint_sha256` | string | Yes | SHA-256 fingerprint of the DER-encoded certificate. |

### pulse.dns — DNS query/response metadata 📐

> This block existed as `"type": "object"` in v0.1.7. All fields below are **fully defined** in v0.2.0.
> Nullable — `null` when flow is not DNS.

| Field | Type | Required | New in v0.2.0 | Description |
|-------|------|----------|:---:|-------------|
| `query_name` | string | Yes | 📐 | Queried domain name (e.g., `"www.example.com"`). |
| `query_type` | string | Yes | 📐 | DNS query type: `"A"`, `"AAAA"`, `"CNAME"`, `"MX"`, `"TXT"`, `"NS"`, `"PTR"`, `"SRV"`, etc. |
| `query_class` | string | Yes | 📐 | DNS query class. Almost always `"IN"` (Internet). |
| `response_code` | string | No | 📐 | DNS response code: `"NOERROR"`, `"NXDOMAIN"`, `"SERVFAIL"`, `"REFUSED"`, etc. `null` for query-only records. |
| `answers` | array of objects | No | 📐 | DNS answer records. See sub-table. |
| `authority_count` | integer | No | 📐 | Number of authority (NS) records in response. |
| `additional_count` | integer | No | 📐 | Number of additional records in response. |
| `response_time_us` | integer | No | 📐 | Time from query to response in microseconds. |
| `is_dnssec` | boolean | No | 📐 | Whether DNSSEC validation was requested/present. |
| `is_recursive` | boolean | No | 📐 | Whether the Recursion Desired (RD) flag was set. |

**pulse.dns.answers[] — DNS answer records**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Answer record name. |
| `type` | string | Yes | Record type (`"A"`, `"AAAA"`, `"CNAME"`, etc.). |
| `ttl` | integer | Yes | Time-to-live in seconds. |
| `data` | string | Yes | Record data (IP address, domain name, text, etc.). |

### pulse.http — HTTP request/response metadata 📐

> This block existed as `"type": "object"` in v0.1.7. All fields below are **fully defined** in v0.2.0.
> Nullable — `null` when flow is not HTTP. Only populated for unencrypted HTTP or from Zeek logs.

| Field | Type | Required | New in v0.2.0 | Description |
|-------|------|----------|:---:|-------------|
| `method` | string | Yes | 📐 | HTTP method: `"GET"`, `"POST"`, `"PUT"`, `"DELETE"`, etc. |
| `uri` | string | Yes | 📐 | Request URI path (e.g., `"/api/v1/data"`). |
| `host` | string | Yes | 📐 | Host header value. |
| `status_code` | integer | No | 📐 | HTTP response status code (e.g., `200`, `404`, `500`). `null` for request-only records. |
| `request_content_length` | integer | No | 📐 | Request body size in bytes. `0` for bodyless requests. |
| `response_content_length` | integer | No | 📐 | Response body size in bytes. |
| `content_type` | string | No | 📐 | Response Content-Type header. |
| `user_agent_hash` | string | No | 📐 | SHA-256 of User-Agent string, truncated to first 8 hex chars. Privacy-preserving; full UA not stored. |
| `referrer_domain` | string / null | No | 📐 | Domain extracted from Referer header. `null` if not present. |
| `version` | string | No | 📐 | HTTP version: `"HTTP/1.0"`, `"HTTP/1.1"`, `"HTTP/2"`, `"HTTP/3"`. |

### pulse.fingerprints[] — Network identity signatures 🆕

> This entire array is new in v0.2.0. Mirrors the `rf.fingerprints[]` pattern from RFVector.

An array of one or more fingerprints that capture the network flow's unique characteristics. Multiple fingerprint types can coexist on the same payload.

**ja3_v1 — TLS client fingerprint**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `kind` | string | Yes | `"ja3_v1"` |
| `hash` | string | Yes | MD5 hash of the JA3 raw string. |
| `raw_string` | string | Yes | Full JA3 string: `TLSVersion,Ciphers,Extensions,EllipticCurves,ECPointFormats`. |
| `params.tls_version` | string | Yes | TLS version hex (e.g., `"0x0303"`). |
| `params.source` | string | Yes | Always `"client_hello"`. |

**ja3s_v1 — TLS server fingerprint**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `kind` | string | Yes | `"ja3s_v1"` |
| `hash` | string | Yes | MD5 hash of the JA3S raw string. |
| `raw_string` | string | Yes | Full JA3S string: `TLSVersion,Cipher,Extensions`. |
| `params.source` | string | Yes | Always `"server_hello"`. |

**ja4_v1 — Next-generation TLS client fingerprint**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `kind` | string | Yes | `"ja4_v1"` |
| `hash` | string | Yes | Full JA4 fingerprint string: `{a}_{b}_{c}`. |
| `params.protocol` | string | Yes | `"t"` for TCP, `"q"` for QUIC. |
| `params.version` | string | Yes | TLS version shorthand (e.g., `"13"` for TLS 1.3). |
| `params.sni_present` | string | Yes | `"d"` if SNI present, `"i"` if absent. |
| `params.cipher_count` | integer | Yes | Number of cipher suites offered. |
| `params.extension_count` | integer | Yes | Number of extensions offered. |
| `params.alpn_first` | string | Yes | First ALPN value (e.g., `"h2"`), or `"00"` if absent. |

**flow_behavior_v1 — Packet size/timing tensor (analog of wavelet_fingerprint_v1)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `kind` | string | Yes | `"flow_behavior_v1"` |
| `scale` | integer | Yes | Scale factor for matrix values (e.g., `1000000`). Divide matrix values by this to get normalized floats. |
| `matrix` | array[3][3] | Yes | 3x3 integer matrix. Rows = packet size buckets, Columns = inter-arrival time buckets. Fixed-point integers for DIVT compatibility. |
| `params.rows` | string | Yes | `"packet_size_buckets"` |
| `params.cols` | string | Yes | `"inter_arrival_time_buckets"` |
| `params.bucket_boundaries_bytes` | array[4] | Yes | Byte size bucket boundaries: `[0, 200, 600, 65535]`. |
| `params.bucket_boundaries_us` | array[4] | Yes | Inter-arrival time bucket boundaries: `[0, 1000, 50000, 9999999]`. |
| `params.normalized` | boolean | Yes | Whether values are normalized to sum to `scale`. |

The `flow_behavior_v1` tensor is the network traffic analog of RFVector's `wavelet_fingerprint_v1`. Both compress high-dimensional data into a fixed 3x3 matrix suitable for rapid comparison and DIVT sealing.

**dns_pattern_v1 — DNS query structure fingerprint**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `kind` | string | Yes | `"dns_pattern_v1"` |
| `query_entropy` | float | Yes | Shannon entropy of the query name characters (0–4.7). High entropy may indicate DGA or tunneling. |
| `label_count` | integer | Yes | Number of labels in the query (e.g., `www.example.com` = 3). |
| `max_label_length` | integer | Yes | Length of the longest label. |
| `has_numeric_labels` | boolean | Yes | Whether any label is purely numeric. |
| `query_length` | integer | Yes | Total character count of the query name. |
| `unique_query_types` | integer | Yes | Number of distinct query types observed in the window. |
| `params.window_queries` | integer | Yes | Number of queries in the analysis window. |

**cert_fingerprint_v1 — Certificate identity**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `kind` | string | Yes | `"cert_fingerprint_v1"` |
| `hash` | string | Yes | SHA-256 fingerprint of the DER-encoded certificate. |
| `subject_cn` | string | Yes | Subject Common Name. |
| `issuer_cn` | string | Yes | Issuer Common Name. |
| `valid_days_remaining` | integer | Yes | Days until certificate expiration at time of capture. |
| `params.hash_algorithm` | string | Yes | `"sha256"`. |

### pulse.classification — What the system thinks this traffic is 🆕

> This entire block is new in v0.2.0. Mirrors `rf.classification` from RFVector.

| Field | Type | Required | New in v0.2.0 | Description |
|-------|------|----------|:---:|-------------|
| `traffic_type` | string | Yes | 🆕 | Classification label. Examples: `"web_browsing"`, `"streaming"`, `"voip"`, `"dns_tunnel"`, `"c2_beacon"`, `"scan"`, `"brute_force"`, `"unknown"`. |
| `confidence` | float (0–1) | Yes | 🆕 | Classification confidence. `0.0` = no idea, `1.0` = certain. |
| `model` | string | Yes | 🆕 | Identifier of the classifier that produced this result. `"none"` if no classifier is running. |

If no classifier is running, set `traffic_type` to `"unknown"` and `confidence` to `0.0`.

### pulse.entity_id — Who this traffic belongs to 🆕

| Field | Type | Required | New in v0.2.0 | Description |
|-------|------|----------|:---:|-------------|
| `entity_id` | string / null | No | 🆕 | Persistent identifier for a tracked entity, assigned by the LSM once correlation establishes identity. `null` until identity is established. |

This is the field that ties multiple observations across time and sensors to "the same thing." Once the LSM determines that a network flow matches an RF observation and a radar track, it assigns an `entity_id` that persists across all future observations of that entity.

### pulse.correlation — How this traffic connects to other sensor data 🆕

> This entire block is new in v0.2.0. Mirrors `rf.correlation` from RFVector.

| Field | Type | Required | New in v0.2.0 | Description |
|-------|------|----------|:---:|-------------|
| `source_refs` | array of strings | No | 🆕 | References to correlated observations from other domains. Format: `"domain:id"` (e.g., `"rf:det_1234"`, `"radar:trk_5678"`). |
| `method` | string / null | No | 🆕 | How correlation was established: `"fingerprint_match"`, `"spatiotemporal"`, `"multi_sensor_fusion"`, `"manual"`. |
| `confidence` | float (0–1) | No | 🆕 | Confidence that this observation belongs to the correlated entity. |
| `baseline_ref` | string / null | No | 🆕 | Reference to the stored baseline profile this observation was compared against. |
| `deviation_flags` | array of strings | No | 🆕 | What changed from baseline. Examples: `"new_cipher_suite"`, `"unusual_timing"`, `"new_destination"`, `"port_change"`, `"protocol_change"`, `"cert_rotation"`, `"traffic_volume_anomaly"`. |

The `correlation` block is `null` until the LSM establishes a cross-sensor link. The `deviation_flags` array tells the operator what is different about a known entity's behavior, not just that something was detected.

### pulse — Session and context 🆕

| Field | Type | Required | New in v0.2.0 | Description |
|-------|------|----------|:---:|-------------|
| `session_id` | string / null | No | 🆕 | Groups captures from a single collection run or mission. |
| `extensions` | object | No | 🆕 | Catch-all for domain-specific data not yet in the core schema. Consumers should handle absence gracefully. |

---

## Field Reference — `net_event_v1`

### pulse (root)

| Field | Type | Required | New in v0.2.0 | Description |
|-------|------|----------|:---:|-------------|
| `schema_version` | string | Yes | 🆕 | Schema version. Currently `"0.2.0"`. |
| `kind` | const | Yes | | Discriminator. Must be `"net_event_v1"`. |
| `event_type` | string | Yes | | Event category: `"firewall_drop"`, `"ids_alert"`, `"connection_reset"`, `"dns_nxdomain"`, `"tls_error"`, `"port_scan_detected"`, `"threshold_breach"`. |
| `occurred_us` | integer | Yes | | Microsecond Unix epoch when the event occurred. |
| `severity` | string | Yes | 🆕 | Severity level: `"info"`, `"low"`, `"medium"`, `"high"`, `"critical"`. |
| `attributes` | object | Yes | | Event-specific key-value pairs. Contents vary by `event_type`. Common keys: `src_ip`, `dst_ip`, `dst_port`, `proto`, `rule_id`, `action`, `reason`, `message`. |
| `fingerprints` | array | No | 🆕 | Fingerprints associated with this event (same schema as `flow_slice_v1`). |
| `classification` | object | No | 🆕 | Same as `flow_slice_v1.classification`. |
| `entity_id` | string / null | No | 🆕 | Same as `flow_slice_v1.entity_id`. |
| `correlation` | object / null | No | 🆕 | Same as `flow_slice_v1.correlation`. |
| `session_id` | string / null | No | 🆕 | Same as `flow_slice_v1.session_id`. |
| `extensions` | object | No | 🆕 | Same as `flow_slice_v1.extensions`. |

---

## DataFoundry Event Envelope

The PulseVector payload rides inside a DataFoundry event envelope. The envelope structure is identical to RFVector's — shared across all Vector schemas (RFVector, PulseVector, FlowVector, FinVector).

```json
{
  "event_id": "evt_pulse_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "event_type": "net.flow_slice",
  "timestamp": "2026-02-05T14:32:01.789Z",
  "schema_version": "1.1.0",

  "source": {
    "plugin_id": "net-transformer",
    "plugin_version": "0.1.0",
    "sensor_id": "network-sensor-01",
    "tenant_id": "vf-demo"
  },

  "content": {
    "pulse": { "...PulseVector payload goes here..." }
  },

  "divt": {
    "content_hash": "sha3-512:a1b2c3d4e5f6...",
    "signature": "ml-dsa-65:...",
    "signed_at": "2026-02-05T14:32:01.800Z",
    "key_id": "vf-signer-prod-01"
  }
}
```

**event_type values:**
- `"net.flow_slice"` — for `flow_slice_v1` payloads
- `"net.event"` — for `net_event_v1` payloads

Do not duplicate envelope fields (timestamp, event_id, source, DIVT) inside the PulseVector payload. They belong in the envelope.

---

## What Changed from v0.1.7

| Change | What's New | Why |
|--------|-----------|-----|
| **Added `schema_version`** | `"0.2.0"` at payload level | 🆕 Consumers can handle payloads from different schema versions. |
| **Added `timing` block** | `first_seen_us`, `last_seen_us`, `duration_us` | 🆕 Essential for flow analysis, correlation, and behavioral profiling. |
| **Added `ip_version` to tuple** | `ip_version`: `4` or `6` | 🆕 Enables IPv4/IPv6 discrimination without parsing IPs. |
| **Changed `proto` type** | `string` → `integer` | Protocol numbers (`6`, `17`, `1`) are more compact and standard than strings. |
| **Added TCP flag counts to stats** | `retransmits`, `rst_count`, `fin_count`, `syn_count` | 🆕 Essential for detecting connection anomalies, scans, and teardown patterns. |
| **Fully defined `tls` block** | 9 typed fields + `cert_chain[]` sub-schema | 📐 Was `"type": "object"` — now every field is defined with type, optionality, and semantics. |
| **Fully defined `dns` block** | 10 typed fields + `answers[]` sub-schema | 📐 Was `"type": "object"` — now every field is defined. |
| **Fully defined `http` block** | 10 typed fields | 📐 Was `"type": "object"` — now every field is defined. |
| **Added `fingerprints[]` array** | JA3, JA3S, JA4, flow_behavior, dns_pattern, cert_fingerprint | 🆕 Mirrors RFVector's fingerprints pattern. Enables signal identity matching across observations. |
| **Added `classification`** | `traffic_type`, `confidence`, `model` | 🆕 Preserves classifier output with the DIVT seal. Same pattern as RFVector. |
| **Added `entity_id`** | Persistent cross-session identity | 🆕 Links observations across time and sensors to the same tracked entity. |
| **Added `correlation`** | `source_refs`, `method`, `confidence`, `baseline_ref`, `deviation_flags` | 🆕 Multi-sensor fusion. Links network to RF, radar, ELINT. Flags behavioral deviations. |
| **Added `session_id`** | Groups captures from a single run | 🆕 Mission/session grouping. |
| **Added `extensions`** | Catch-all object | 🆕 Domain-specific data without cluttering the core schema. |
| **Added `severity` to `net_event_v1`** | `info`, `low`, `medium`, `high`, `critical` | 🆕 Event severity classification for alerting and prioritization. |
| **Made `tls`, `dns`, `http` nullable** | `null` when not applicable | Explicit nullability vs. field omission — consumers know the field was evaluated. |

---

## Cross-Schema Compatibility

PulseVector is designed to interoperate with the other Vector schemas in the DataFoundry ecosystem:

| Schema | Domain | Envelope Key | Event Type Prefix |
|--------|--------|:---:|:---:|
| **RFVector** v0.2.0 | RF/SDR signals | `content.rf` | `rf.*` |
| **PulseVector** v0.2.0 | Network traffic | `content.pulse` | `net.*` |
| **FlowVector** v0.1.7 | Content/documents | `content.flow` | `content.*` |
| **FinVector** (planned) | Financial transactions | `content.fin` | `fin.*` |

Shared fields across all schemas:
- `entity_id` — same entity ID space, enabling cross-domain correlation
- `correlation.source_refs` — references use `"domain:id"` format to link across schemas
- `session_id` — shared session grouping
- DataFoundry envelope — identical structure, DIVT sealing, and ingestion path

DataFoundry auto-detects the schema by inspecting the key inside `content` (`rf`, `pulse`, `flow`, `fin`).
