# Experiments

Format: hypothesis -> change -> result. Fill the result column from `runs.jsonl` and your own viewing/listening; add the log line `key` so a reader can find the evidence. Target: 10.

| id | hypothesis | status | evidence |
|---|---|---|---|---|
| E-01 | Prefixing a delivery instruction ("Say slowly, warm and weary: ...") changes Gemini TTS pace and mood audibly | run the same old-man line with and without `delivery` | clip length in `runs.jsonl`, plus 3 listeners pick which fits | 
| E-02 |Gemini TTS adds a noise burst at the end of each line | The model read the instruction aloud, so you turned it off (GEMINI_TTS_STYLE=off) | old and new narration files, and the style field in runs.jsonl |
| E-03 | Trimming that burst automatically removes the noise without cutting words | needs 10 minutes: render the film with and without the cleaner, ask 3 people which is cleaner | not done |
| E-04 | A character reference sheet prompt gives a better base face than the shot prompt alone | compare `sheet_daniel` with the s01 face | not done |
| E-05 | Does the Workers AI FLUX endpoint honour `seed`? | same prompt twice, same seed vs different seed | not done |
| E-06 | `steps=4` is enough for schnell; more steps are wasted quota | steps 4 vs 8 on one shot | not done |
| E-07 | Wan 2.2 at 480p is good enough for a phone | one shot at 480p vs 720p on Kaggle | not done |
| E-08 | A Wan clip beats Ken Burns on the emotional shot (s06) | swap `motion` to `wan` for s06 only | not done |
| E-09 | Of three ACE-Step candidates one clearly fits | generate 3 from the same prompt, choose one, write why | not done |
| E-10 | Music at -15 dB under the voice is audible but never competes | try ducking ratios 6 vs 10 | not done |

Extra ideas: subtitle size on a real phone; shot length 7s vs 9s (pace from test feedback).
