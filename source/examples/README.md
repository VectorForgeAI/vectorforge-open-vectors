# Examples

This folder contains concrete, copy-pasteable examples.

- `profile-rf.default.95.json` and `profile-pulse.default.95.json`  
  Example Fidelity Profile manifests.

- `example-rfvector-record.jsonl`  
  A single RFVector record with a computed `divt.hash_b64` (signatures are placeholders).

- `example-manifest-record.jsonl`  
  A `manifest_v1` record that commits to the set of member records in a window (here, one record).

Note: Signature fields are placeholders in these examples because the package does not ship private keys. Use the DIVT service to create real signatures, or validate hashing behavior using `divt.hash_b64` plus the canonicalization reference code.
