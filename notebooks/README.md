# GPU notebooks (Kaggle)

The pipeline runs without these. They upgrade the music and, optionally, a few shots.
Model APIs change quickly: **check each model's card before running**, and note what you actually did in `EXPERIMENTS.md` / `FAILURES.md`.

## Music with ACE-Step 1.5

1. New Kaggle notebook, GPU on, internet on (phone-verified account).
2. Follow the install and usage steps on the ACE-Step project page / model card.
3. Use the prompt in `storyboard.json` -> `music.prompt`, duration about 90 s, instrumental. Generate **three** candidates.
4. Listen, choose one, write why in `EXPERIMENTS.md` (E-09).
5. Download it as `assets/music/score.wav` in this repo, then `make film`.
6. Log the GPU time: `python -m pipeline log-manual --stage music --model ace-step-1.5 --minutes <n>`.

## Optional: Wan 2.2 image-to-video for 2 or 3 hero shots

1. Take the keyframe PNG from `outputs/keyframes/`, upload it to the notebook.
2. Run Wan 2.2 TI2V-5B image-to-video from its model card, 480p first, about 5 seconds.
3. Save as `outputs/wan/<shot>.mp4` (for example `outputs/wan/s06.mp4`).
4. In `storyboard.json` set that shot's `"motion": "wan"`, then `make shot SHOT=s06`.
5. Log it: `python -m pipeline log-manual --stage shots --model wan2.2-ti2v-5b --minutes <n> --shot s06`.

If the queue or memory defeats you, do nothing: the Ken Burns fallback is already the default. Record what happened in `FAILURES.md`.
