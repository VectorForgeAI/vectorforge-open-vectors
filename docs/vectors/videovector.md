# VideoVector

**Status: Spec-first**

VideoVector captures video activity: time-segmented summaries, keyframes, motion cues, object tracks, and events.

> **Note**: This vector is in early specification phase. The schema is skeletal and will be refined as reference producers are built.

## Use Cases

- Surveillance video analysis
- Media archive indexing
- Live stream monitoring
- Video search and retrieval
- Incident investigation

## Record Types

| Type | Description |
|------|-------------|
| `video_segment_v1` | Time-segmented video summary |
| `video_event_v1` | Discrete video event (motion, object detection) |
| `video_error_v1` | Error during video processing |
| `manifest_v1` | Continuity Level 2 window manifest |

## Payload Structure (Draft)

### video_segment_v1

```json
{
  "payload": {
    "video": {
      "kind": "video_segment_v1",
      "segment_id": "uuid",
      "source_uri": "rtsp://camera-01/stream",
      "time_bounds_us": [1738368000000000, 1738368010000000],
      "duration_ms": 10000,
      "resolution": {"width": 1920, "height": 1080},
      "fps_q8": 7680,
      "codec": "h264",
      "keyframes": [
        {
          "offset_ms": 0,
          "thumbnail_uri": "s3://bucket/keyframe-001.jpg",
          "embedding": []
        }
      ],
      "motion_summary": {
        "activity_score_q15": 15000,
        "regions": []
      },
      "tracks": [
        {
          "track_id": "track-001",
          "class": "person",
          "confidence_q15": 28000,
          "bbox_sequence": [
            {"offset_ms": 0, "x": 100, "y": 200, "w": 50, "h": 120}
          ]
        }
      ],
      "events": [],
      "extensions": {}
    }
  }
}
```

### video_event_v1

```json
{
  "payload": {
    "video": {
      "kind": "video_event_v1",
      "event_type": "person_entered",
      "occurred_us": 1738368005000000,
      "confidence_q15": 25000,
      "bbox": {"x": 100, "y": 200, "w": 50, "h": 120},
      "track_id": "track-001",
      "attributes": {
        "direction": "left_to_right",
        "zone": "entrance"
      },
      "extensions": {}
    }
  }
}
```

## Key Fields

### Segment Information
- **segment_id**: Unique segment identifier
- **source_uri**: Video source (RTSP, file, etc.)
- **time_bounds_us**: Segment time range in microseconds
- **resolution**: Frame dimensions
- **fps_q8**: Frames per second as Q8 fixed-point (divide by 256)

### Keyframes
Representative frames for the segment:
- **offset_ms**: Time offset within segment
- **thumbnail_uri**: Reference to extracted frame image
- **embedding**: Optional vector embedding for similarity search

### Motion Summary
Aggregate motion information:
- **activity_score_q15**: Overall motion level (0-32768)
- **regions**: Motion heatmap or active regions

### Tracks
Object tracking across the segment:
- **track_id**: Persistent track identifier
- **class**: Object classification (person, vehicle, etc.)
- **bbox_sequence**: Bounding boxes over time

### Events
Discrete detected events:
- **event_type**: What happened (person_entered, loitering, etc.)
- **confidence_q15**: Detection confidence

## Raw Artifact Reference

```json
{
  "artifacts": [
    {
      "artifact_id": "uuid",
      "kind": "video_segment",
      "uri": "s3://bucket/video/segment-001.mp4",
      "time": {"start_us": 1738368000000000, "end_us": 1738368010000000},
      "content_type": "video/mp4",
      "artifact_divt_id": "uuid-of-raw-divt",
      "locator": {"start_frame": 0, "end_frame": 300}
    }
  ]
}
```

## Context Basis Set (CBS)

Draft CBS for VideoVector (subject to change):

| Extractor | Description |
|-----------|-------------|
| `shot_boundary_v1` | Shot boundary detection parity |
| `keyframe_selection_v1` | Keyframe retrieval effectiveness |
| `tracklet_parity_v1` | Track continuity metrics (ID switches) |
| `event_parity_v1` | Event detection F1 |

## Fidelity Knobs

| Knob | Effect on Fidelity | Effect on Resources |
|------|-------------------|---------------------|
| segment_s ↓ | Finer temporal granularity | More records |
| keyframe_interval ↓ | Better frame coverage | More keyframes |
| detector_confidence ↓ | More detections | More noise |
| track_classes ↑ | More object types | More CPU |

## Schema

Full schema: `schemas/payloads/videovector.payload.schema.json`

## Contributing

This vector needs:
- Reference producer implementation
- CBS extractor implementations
- Benchmark datasets (synthetic or licensed video)

See [CONTRIBUTING.md](../../CONTRIBUTING.md) if you want to help.
