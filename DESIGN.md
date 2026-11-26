# Design

## Who it is for, and what they should feel

**Audience:** young Ethiopians, late teens to thirties, who scroll on their phones most evenings. They watch vertically, on TikTok, Instagram and WhatsApp status, often with sound on at low volume in a shared home. They will give a film 20 seconds before deciding.

**Intent:** they should recognise their own late-night scrolling in Daniel and finish the film with a gentle push to start one small thing today. Not guilt, not a lecture: recognition, then a quiet nudge.

**One-sentence test for every decision:** does this help a tired 24-year-old on a phone feel *seen* in the first ten seconds and *nudged* in the last ten?

## Design decisions and why

| decision | reason |
|---|---|
| Vertical 9:16 is the primary cut | that is where the audience watches; 16:9 is the second export |
| Cold blue (phone) -> warm amber (street, corn fire) -> golden morning | colour carries the story without words: the trap is blue, the answer is warm |
| Narrator opens, then two characters speak in their own voices | the promise ("Tomorrow, I'll start") must be heard from Daniel; the regret must come from the old man |
| Subtitles burned in | many viewers watch muted or at low volume |
| Eight shots of about 9 seconds | few enough for consistent characters, long enough for each line to land |
| Every shot has a `reason` field in `storyboard.json` | the schema rejects a shot with no stated purpose |
| Ethiopian setting (Addis Ababa roadside, corn on charcoal) | specific beats generic; the audience should recognise the street |

## Character consistency plan

FLUX schnell is text-only (no image conditioning), so consistency is engineered: one fixed description per character repeated word for word in every prompt, one shared style string, one fixed seed, and a reference sheet per character generated first (`outputs/keyframes/sheet_*.png`) that I review before accepting any shot. How well this works is Experiment E-03.

## User test 1: the radio cut (narration over black)

Generate with `make radio`, send `outputs/radio_cut.mp4` to at least three people from the audience.

Questions: What do you think the story is about? Which line stayed with you? Was any part unclear or too slow? Would you share it?

| tester (first name, age range) | what they said (verbatim where possible) | what I changed |
|---|---|---|
| TODO | TODO | TODO |
| TODO | TODO | TODO |
| TODO | TODO | TODO |

Resulting storyboard change (commit hash): TODO

## User test 2: the near-final cut

Same questions, plus: Do the pictures match the voice? Did the end card feel honest?

| tester | what they said | what I changed |
|---|---|---|
| TODO | TODO | TODO |
| TODO | TODO | TODO |
| TODO | TODO | TODO |

## What changed because of the tests

TODO: two or three concrete edits to `storyboard.json`, each with the git commit that made it.
