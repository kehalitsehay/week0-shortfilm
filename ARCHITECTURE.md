# Architecture

## The one rule

Stages never call each other. Each stage reads `storyboard.json` (and files other stages already wrote to `outputs/`) and writes its own files. That is why one shot can change without redoing the rest.

```
storyboard.json --validate(schema)--> narration -> keyframes -> music -> shots -> assemble
                                          \_____________ every call -> runs.jsonl ___________/
```

## Three layers (each depends only on the one below)

| layer | path | job |
|---|---|---|
| stages | `pipeline/stages/` | decide *what* jobs exist for a storyboard (`plan(sb) -> [Job]`) |
| clients | `pipeline/clients/` | talk to the outside world (Gemini, Cloudflare, FFmpeg, offline placeholders) |
| core | `pipeline/core/` | schema validation, cache key, retry, run log, the job runner |

## The stage contract

A stage module exposes `plan(sb) -> list[Job]`. A `Job` holds:

- `inputs`: *everything* that influences the output (prompt, seed, model, upstream file names, render settings). It is hashed.
- `produce(path)`: writes the file, returns metadata (`model`, `params`, `seed`, `list_price_usd`).
- optional `fallback(path)`, `group` (the shot id used by `--only`), `global_job`.

`core/stage.execute()` runs jobs the same way for every stage.

## Caching

Output path = `outputs/<stage>/<shot>_<hash of inputs>.<ext>`. If the file exists, the job is a cache hit and is logged as one. Files are written to a `.part` name and renamed, so an interrupted run never leaves a corrupt cache entry.

Keys chain automatically: a clip's inputs contain its keyframe's *file name* (which contains the keyframe's hash), and the final film's inputs contain every clip, narration and score file name. Change one image prompt and exactly that keyframe, its two clips and the final edit are invalidated. `tests/test_pipeline_offline.py` proves this.

Lesson learned the hard way (FAILURES.md F-01): any render setting that changes the picture must be in `inputs`, or the cache will serve a stale film.

## Failure handling

```
produce() -> retry 3x with 1s, 2s backoff -> fallback() if the job has one -> else log and raise
```

| stage | on failure |
|---|---|
| narration | fail loudly (a placeholder voice in a real film is worse than a stop) |
| keyframes | fail loudly; cache means a re-run resumes where it stopped |
| shots | Wan clip missing -> Ken Burns pan/zoom (decided at plan time, logged) |
| music | no ACE-Step file -> original procedural score; logged in `params.note` |
| assemble | fail loudly with FFmpeg's stderr |

Because finished files are cached, quota exhaustion is a pause, not a loss: wait, then run `make film` again.

## Timing

`core/timing.py`: a shot lasts `max(storyboard duration, narration length + 0.5s lead + 0.8s tail)`, so the voice is never cut off. Subtitles use the real narration length.

## Audio chain (`assemble.audio_graph`)

Each narration WAV is delayed to its shot start and mixed. A copy of that mix feeds a sidechain compressor on the music (ducking). Voice plus ducked music are summed, loudness-normalised to -16 LUFS, padded and trimmed to the film length.

## Logging

`runs.jsonl`: one JSON object per call or cache hit: `ts, stage, shot, model, params, seed, latency_ms, cost_usd, list_price_usd, cache_hit, error, fallback_used, key, output`. GPU work done on Kaggle is added with `log-manual` (adds `gpu_minutes`). `make costs` aggregates it.

## Design choices worth defending

- **JSON Schema, validated before every run:** a typo fails in milliseconds, not after spending quota.
- **FFmpeg Ken Burns as the default motion:** GPU video is the least reliable, slowest part; a still sequence with narration, score and subtitles is still a film. Wan is an upgrade path, not a dependency.
- **Plain REST clients, no vendor SDKs:** short, readable, easy to mock.
- **Offline mode:** the whole pipeline runs without keys, which makes tests and CI possible.
