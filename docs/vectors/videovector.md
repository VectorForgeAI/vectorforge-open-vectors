# VideoVector

**Status: Reference implementation available**

VideoVector captures video activity: time-segmented summaries, keyframes, motion cues, object tracks, and events.

> **Note**: This vector has a reference implementation via the `videovector-plugin` in DataAnvil-Plugins.

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

## Payload Structure

### video_segment_v1

```json
{
  "payload": {
    "video": {
      "kind": "video_segment_v1",
      "stream": {
        "codec": "h264",
        "width": 1920,
        "height": 1080,
        "fps_x1000": 29970,
        "bitrate_kbps": 5000,
        "duration_ms": 10000
      },
      "keyframes": [
        {
          "frame_index": 0,
          "pts_us": 1738368000000000,
          "phash_hex": "a1b2c3d4e5f6",
          "mean_brightness": 128
        }
      ],
      "motion": {
        "mean_magnitude_x1000": 1500,
        "max_magnitude_x1000": 8200,
        "scene_change_count": 0,
        "centroid_x_pct": 45,
        "centroid_y_pct": 60
      },
      "tracks": [
        {
          "track_id": "track-001",
          "object_class": "person",
          "confidence_pct": 85,
          "first_frame": 0,
          "last_frame": 299,
          "bbox_count": 300
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
      "stream": {
        "codec": "h264",
        "width": 1920,
        "height": 1080,
        "fps_x1000": 29970
      },
      "events": [
        {
          "event_type": "object_enter",
          "frame_index": 150,
          "pts_us": 1738368005000000,
          "confidence_pct": 76,
          "attributes": {
            "direction": "left_to_right",
            "zone": "entrance"
          }
        }
      ],
      "extensions": {}
    }
  }
}
```

## Key Fields

### Stream Information
- **stream.codec**: Video codec (h264, h265, vp9, etc.)
- **stream.width**: Frame width in pixels
- **stream.height**: Frame height in pixels
- **stream.fps_x1000**: Frames per second * 1000 (e.g. 29970 = 29.97 fps)
- **stream.duration_ms**: Segment duration in milliseconds

### Keyframes
Representative frames for the segment:
- **frame_index**: Frame number within the segment
- **pts_us**: Presentation timestamp in microseconds
- **phash_hex**: Perceptual hash as hex string
- **mean_brightness**: Average frame brightness (0-255)

### Motion
Aggregate motion information:
- **mean_magnitude_x1000**: Mean optical flow magnitude * 1000
- **max_magnitude_x1000**: Max optical flow magnitude * 1000
- **scene_change_count**: Number of scene changes detected
- **centroid_x_pct**: Motion centroid X as percentage of frame width
- **centroid_y_pct**: Motion centroid Y as percentage of frame height

### Tracks
Object tracking across the segment:
- **track_id**: Persistent track identifier
- **object_class**: Object classification (person, vehicle, etc.)
- **confidence_pct**: Detection confidence (0-100)
- **bbox_count**: Number of bounding box observations

### Events
Discrete detected events:
- **event_type**: What happened (scene_change, motion_spike, object_enter, etc.)
- **confidence_pct**: Detection confidence (0-100)

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
- CBS extractor implementations
- Benchmark datasets (synthetic or licensed video)

See [CONTRIBUTING.md](../../CONTRIBUTING.md) if you want to help.
