# One Hour: a Heritage Short pipeline

A roughly 80-second AI short film ("One Hour") and the small Python studio that makes it.
One file, `storyboard.json`, is the contract between every stage. Change one shot, re-run, and only that shot is regenerated.

> Story: Daniel scrolls every night and promises to start "tomorrow". An old man roasting corn by the road tells him why that promise is expensive.
> Audience and intent: see [DESIGN.md](DESIGN.md).

## Run it (one command)

```bash
git clone <this repo> && cd heritage-short
python3 -m venv .venv && . .venv/bin/activate
make setup                    # pip install -r requirements.txt  (also needs ffmpeg on PATH)
cp .env.example .env          # fill in GEMINI_API_KEY, CF_ACCOUNT_ID, CF_API_TOKEN
make film                     # validate storyboard, then run the whole pipeline
```

Outputs: `outputs/film_9x16.mp4` and `outputs/film_16x9.mp4`. Every model call is appended to `runs.jsonl`.

No keys yet? `make offline` runs the *entire* pipeline with placeholder images, a placeholder voice and a procedural score, so you can see the structure work in about two minutes.

## Commands

| command | what it does |
|---|---|
| `make validate` | check `storyboard.json` against `schema/storyboard.schema.json` |
| `make smoke` | call each provider once and log latency (run this first) |
| `make radio` | narration-only cut over black, for user test 1 |
| `make film` | the whole pipeline; cached |
| `make shot SHOT=s03` | regenerate one shot only (this is the live demo) |
| `make costs` | per-stage latency, GPU minutes, list-price equivalent from `runs.jsonl` |
| `make showcase` | build `showcase/index.html`, a static page for the film |
| `make test` | unit tests plus an end-to-end test of the "only the changed shot regenerates" claim |

## What each stage does

| stage | reads | writes | model (free) |
|---|---|---|---|
| narration | `shots[].narration`, `voices` | `outputs/narration/*.wav` | Gemini TTS |
| keyframes | `style`, `characters`, `shots[].image_prompt` | `outputs/keyframes/*.png` | FLUX on Cloudflare Workers AI |
| music | `music.prompt`, `assets/music/score.*` | `outputs/music/score_*.wav` | ACE-Step 1.5 (Kaggle), procedural fallback |
| shots | keyframes, `motion`, durations | `outputs/shots/*.mp4` | FFmpeg Ken Burns; Wan 2.2 clips optional |
| assemble | all of the above | `outputs/film_*.mp4` | FFmpeg |

Details, contracts and failure handling: [ARCHITECTURE.md](ARCHITECTURE.md).

## Doing the GPU parts (optional but recommended)

- **Music:** run ACE-Step on Kaggle, pick the best of three candidates, save it as `assets/music/score.wav`. Then `make film`. See [notebooks/README.md](notebooks/README.md).
- **Wan 2.2 clips:** for any shot with `"motion": "wan"`, put the Kaggle output at `outputs/wan/<shot>.mp4`. Log the GPU time with `python -m pipeline log-manual --stage shots --model wan2.2-ti2v-5b --minutes 14 --shot s04`.

## Repository map

`DESIGN.md` (audience, intent, user tests) · `ARCHITECTURE.md` · `EXPERIMENTS.md` · `FAILURES.md` · `COSTS.md` · `ETHICS.md` · `schema/` · `pipeline/` · `tests/` · `runs.jsonl` · `outputs/` · `showcase/`

## Secrets

Keys live in `.env`, which is git-ignored. Only `.env.example` is committed.
