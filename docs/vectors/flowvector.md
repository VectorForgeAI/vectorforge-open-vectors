# FlowVector

**Status: Reference implementation available**

FlowVector captures high-volume content streams: web scrapes, social feeds, API firehoses, and other content at scale.

> **Note**: This vector has a reference implementation via the `flowvector-plugin` in DataAnvil-Plugins.

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

## Payload Structure (v0.2.0)

```json
{
  "payload": {
    "flow": {
      "kind": "content_item_v1",
      "item_id": "article-2025-0201-001",
      "uri": "https://example.com/article/123",
      "fetched_us": 1738368000000000,
      "published_us": 1738281600000000,
      "content": {
        "mime": "text/html",
        "text": "Extracted article text...",
        "title": "Article Title",
        "lang": "en",
        "byte_count": 24530,
        "word_count": 3200
      },
      "author": {
        "name": "Dr. Sarah Chen",
        "handle": "@schen",
        "url": "https://example.com/authors/sarah-chen",
        "platform": "web"
      },
      "source": {
        "domain": "example.com",
        "feed_url": "https://example.com/rss.xml",
        "platform": "wordpress",
        "collection_id": "tech-blogs-2025"
      },
      "entities": [
        {"type": "person", "value": "Dr. Sarah Chen", "span": [0, 14], "confidence_pct": 97}
      ],
      "embeddings": [
        {"model": "all-MiniLM-L6-v2", "dim": 384, "vector_b64": "base64..."}
      ],
      "dedup": {
        "hash": "a1b2c3...",
        "algo": "sha256",
        "is_duplicate": false,
        "canonical_id": "article-2025-0201-001"
      },
      "classification": {
        "category": "technology",
        "confidence_pct": 95,
        "model": "topic_classifier_v2",
        "tags": ["ai", "hardware"]
      },
      "sentiment": {
        "score_pct": 42,
        "model": "sentiment_v3"
      },
      "correlation": {
        "parent_item_id": "article-2025-0131-042",
        "thread_id": "ai-hardware-series",
        "reply_to": "comment-9281",
        "batch_id": "batch-20250201"
      },
      "links": ["https://example.com/related"],
      "metadata": {"http_status": 200},
      "extensions": {}
    }
  }
}
```

## Key Fields

### Content Identification
- **item_id**: Unique identifier for this content item (required)
- **uri**: Source URL (required)
- **kind**: Record type enum (`content_item_v1`, `content_error_v1`) (required)

### Timestamps
- **fetched_us**: When the content was retrieved (required, microseconds)
- **published_us**: When the content was originally published (optional, microseconds)

### Content Block (required)
- **mime**: MIME type of original content (required)
- **text**: Extracted/cleaned text content
- **title**: Content title
- **lang**: Language code
- **byte_count**: Size of original content in bytes
- **word_count**: Word count of extracted text
- **text_sha3_512_b64**: SHA3-512 hash of text content

### Author Block
- **name**: Author display name
- **handle**: Author handle/username
- **url**: Author profile URL
- **platform**: Platform identifier

### Source Block
- **domain**: Source domain
- **feed_url**: RSS/Atom feed URL
- **platform**: Platform identifier
- **collection_id**: Collection or campaign identifier

### Derived Features
- **entities**: Extracted named entities with type, value, span, and confidence_pct (0-100)
- **embeddings**: Vector embeddings with model, dim, and vector_b64
- **dedup**: Deduplication info with hash, algo, is_duplicate flag, canonical_id
- **classification**: Category, confidence_pct (0-100), model, tags
- **sentiment**: Sentiment score_pct (-100 to 100), model
- **correlation**: Parent/thread/reply/batch linking
- **links**: Outbound links
- **metadata**: Arbitrary key-value metadata

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
- CBS extractor implementations
- Benchmark datasets

See [CONTRIBUTING.md](../../CONTRIBUTING.md) if you want to help.
