# Experiments

Format: hypothesis -> change -> result. Fill the result column from `runs.jsonl` and your own viewing/listening; add the log line `key` so a reader can find the evidence. Target: 10.

| id | hypothesis | change | how to measure | result |
|---|---|---|---|---|
| E-01 | Prefixing a delivery instruction ("Say slowly, warm and weary: ...") changes Gemini TTS pace and mood audibly | run the same old-man line with and without `delivery` | clip length in `runs.jsonl`, plus 3 listeners pick which fits | TODO |
| E-02 | The old man's voice choice matters more than the delivery text | try Algenib vs Charon vs Gacrux on one line | blind pick by 3 people | TODO |
| E-03 | Repeating the character description verbatim plus a fixed seed keeps Daniel recognisable across shots | render s01, s03, s05, s08; compare with and without the fixed seed | count of shots where 3 viewers say "same person" | TODO |
| E-04 | A character reference sheet prompt gives a better base face than the shot prompt alone | compare `sheet_daniel` with the s01 face | viewer preference | TODO |
| E-05 | Does the Workers AI FLUX endpoint honour `seed`? | same prompt twice, same seed vs different seed | pixel diff of the two PNGs | TODO |
| E-06 | `steps=4` is enough for schnell; more steps are wasted quota | steps 4 vs 8 on one shot | latency in `runs.jsonl`, viewer preference | TODO |
| E-07 | Wan 2.2 at 480p is good enough for a phone | one shot at 480p vs 720p on Kaggle | GPU minutes (`log-manual`), viewer preference | TODO |
| E-08 | A Wan clip beats Ken Burns on the emotional shot (s06) | swap `motion` to `wan` for s06 only | viewer preference, GPU minutes | TODO |
| E-09 | Of three ACE-Step candidates one clearly fits | generate 3 from the same prompt, choose one, write why | listeners rank them | TODO |
| E-10 | Music at -15 dB under the voice is audible but never competes | try ducking ratios 6 vs 10 | listen at phone speaker volume | TODO |

Extra ideas: subtitle size on a real phone; shot length 7s vs 9s (pace from test feedback).
