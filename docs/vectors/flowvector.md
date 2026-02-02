# FlowVector

**Status: Spec-first**

FlowVector captures high-volume content streams: web scrapes, social feeds, API firehoses, and other content at scale.

> **Note**: This vector is in early specification phase. The schema is skeletal and will be refined as reference producers are built.

## Use Cases

- Web scraping pipelines
- Social media monitoring
- RSS/Atom feed aggregation
- Streaming API ingestion (Twitter, Reddit, etc.)

## Record Types

| Type | Description |
|------|-------------|
| `content_item_v1` | Single content item (article, post, page) |
| `content_error_v1` | Error during content processing |
| `manifest_v1` | Continuity Level 2 window manifest (optional) |

## Payload Structure (Draft)

```json
{
  "payload": {
    "flow": {
      "kind": "content_item_v1",
      "item_id": "unique-item-identifier",
      "uri": "https://example.com/article/123",
      "content_type": "text/html",
      "fetched_us": 1738368000000000,
      "published_us": 1738367000000000,
      "text": "Extracted article text...",
      "title": "Article Title",
      "author": "Author Name",
      "metadata": {
        "source": "example.com",
        "language": "en",
        "word_count": 500
      },
      "entities": [
        {"type": "person", "value": "John Doe", "span": [10, 18]}
      ],
      "embeddings": [],
      "links": ["https://example.com/related"],
      "dedup_hash": "sha256:...",
      "extensions": {}
    }
  }
}
```

## Key Fields

### Content Identification
- **item_id**: Unique identifier for this content item
- **uri**: Source URL
- **content_type**: MIME type of original content

### Timestamps
- **fetched_us**: When the content was retrieved
- **published_us**: When the content was originally published (if known)

### Extracted Content
- **text**: Extracted/cleaned text content
- **title**: Content title
- **author**: Author attribution
- **metadata**: Source-specific metadata

### Derived Features
- **entities**: Extracted named entities
- **embeddings**: Vector embeddings for similarity/search
- **links**: Outbound links
- **dedup_hash**: Hash for deduplication

## Context Basis Set (CBS)

Draft CBS for FlowVector (subject to change):

| Extractor | Description |
|-----------|-------------|
| `text_parity_v1` | Token overlap or embedding similarity |
| `metadata_parity_v1` | URL, timestamp, author field match |
| `entity_parity_v1` | Named entity extraction F1 |
| `dedup_parity_v1` | Same duplicates flagged |

## Schema

Full schema: `schemas/payloads/flowvector.payload.schema.json`

## Contributing

This vector needs:
- Reference producer implementation
- CBS extractor implementations
- Benchmark datasets

See [CONTRIBUTING.md](../../CONTRIBUTING.md) if you want to help.
