# ExchangeVector

**Status: Reference implementation available**

ExchangeVector captures financial and digital asset transactions: payments, settlements, ledger events, and transaction lifecycle states.

> **Note**: This vector has a reference implementation via the `exchangevector-plugin` in DataAnvil-Plugins.

## Use Cases

- Payment processing pipelines
- Cryptocurrency transaction monitoring
- Fraud detection systems
- Financial audit trails
- Cross-border payment tracking

## Record Types

| Type | Description |
|------|-------------|
| `transaction_event_v1` | Transaction lifecycle event |
| `transaction_error_v1` | Error during transaction processing |
| `manifest_v1` | Continuity Level 2 window manifest (optional) |

## Payload Structure (Draft)

```json
{
  "payload": {
    "exchange": {
      "kind": "transaction_event_v1",
      "transaction_id": "txn-uuid",
      "lifecycle_state": "captured",
      "event_type": "capture",
      "occurred_us": 1738368000000000,
      "amount": {
        "value": "1250.37",
        "currency": "USD",
        "precision": 2
      },
      "fees": {
        "value": "2.50",
        "currency": "USD",
        "precision": 2
      },
      "parties": {
        "payer": {"id": "account-123", "type": "bank_account"},
        "payee": {"id": "merchant-456", "type": "merchant"}
      },
      "instrument": {
        "type": "card",
        "network": "visa",
        "last_four": "4242"
      },
      "channel": "online",
      "metadata": {
        "merchant_category": "5411",
        "authorization_code": "ABC123"
      },
      "risk_signals": {},
      "extensions": {}
    }
  }
}
```

## Key Fields

### Transaction Identification
- **transaction_id**: Unique transaction identifier
- **lifecycle_state**: Current state (pending, authorized, captured, settled, refunded, etc.)
- **event_type**: What happened (authorize, capture, settle, refund, chargeback)

### Amounts

Currency amounts as decimal strings (not floats):

```json
{
  "amount": {
    "value": "1250.37",
    "currency": "USD",
    "precision": 2
  }
}
```

### Parties
- **payer**: Who is sending funds
- **payee**: Who is receiving funds

Each party has an `id` and `type` (bank_account, card, wallet, merchant, etc.)

### Instrument
Payment instrument details (card, ACH, wire, crypto, etc.)

### Lifecycle States

```
pending → authorized → captured → settled
                    ↘ voided
                    ↘ refunded → settled
                    ↘ chargeback → ...
```

## Context Basis Set (CBS)

Draft CBS for ExchangeVector (subject to change):

| Extractor | Description |
|-----------|-------------|
| `lifecycle_parity_v1` | State graph equivalence |
| `ledger_delta_v1` | Net changes match within rounding |
| `party_graph_v1` | Account/address linking accuracy |
| `risk_feature_v1` | Fraud/risk feature parity |

## Numeric Encoding

All currency amounts MUST be decimal strings, not floats:
- Correct: `"value": "1250.37"`
- Wrong: `"value": 1250.37`

This ensures deterministic canonicalization across platforms with different floating-point behavior.

## Schema

Full schema: `schemas/payloads/exchangevector.payload.schema.json`

## Contributing

This vector needs:
- CBS extractor implementations
- Benchmark datasets (synthetic transaction flows)

See [CONTRIBUTING.md](../../CONTRIBUTING.md) if you want to help.
