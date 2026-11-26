# Failures

Format: what broke -> what I tried -> what fixed it -> what I learned. Real entries only; add the Kaggle/quota/consistency ones as they happen.

## F-01: the film did not change after I changed how it was drawn

- **Broke:** I changed the subtitle style and re-ran. The pipeline said "done" in 0 seconds and the film looked identical.
- **Cause:** the assemble job's cache key contained the clips, narration and score, but not the render settings. The old film was served from the cache.
- **Fix:** subtitle size/margin and a `render_version` are now part of `inputs` in `stages/assemble.py`.
- **Lesson:** a cache key must contain *everything* that changes the output, including settings. This is the main risk of caching, and `tests/test_pipeline_offline.py` now checks the positive direction (edit one prompt -> exactly the right files regenerate).

## F-02: subtitles were enormous

- **Broke:** first burned-in subtitles covered a third of the vertical frame.
- **Tried:** `original_size=720x1280` in the `subtitles` filter; no visible change.
- **Cause:** libass sizes fonts against a 288-pixel-tall canvas for plain SRT files, so `FontSize=34` meant about 150 px on a 1280 px frame.
- **Fix:** small values on purpose (`FontSize=9` vertical, `12` horizontal), with a comment in the code. Verified by extracting a frame with `ffmpeg -ss`.

## F-03 onward (fill in while building)

Likely candidates, add the real story if they happen: Kaggle GPU queue or phone verification; Cloudflare daily image allowance; Gemini TTS rate limit or a model name that has changed; characters drifting between shots; ACE-Step running out of memory or mispronouncing lyrics; Wan clip taking longer than the quota allows.
