# Ethics, consent, licences, labelling

## Consent record

**No real person's face, voice or likeness appears in this film.**
- Daniel and the old man are fictional characters described only in text prompts; no photo of a real person was used as input.
- Voices are Gemini's prebuilt voices; no voice was cloned from a recording.
- The story is a parable, not about a named real person.

If this ever changes (for example a relative's voice), write their recorded, informed consent here *before* generating anything of them.

## Labelling plan

- The film ends with a 4-second card: "Made with AI. Story, images, voices and music generated with AI models."
- The public post will have the platform's AI-content label switched on.
- No watermark or provenance metadata is stripped; the pipeline does not remove any.

## Licences (verify each and fill the date you checked)

| component | licence / terms | checked |
|---|---|---|
| Gemini TTS | Google API terms; free-tier inputs may be used to improve models, so no private data is sent | TODO |
| FLUX.1 schnell via Cloudflare Workers AI | model licence and Cloudflare terms | TODO |
| Wan 2.2 (if used) | Apache 2.0 | TODO |
| ACE-Step 1.5 (if used) | outputs usable commercially | TODO |
| FFmpeg | LGPL/GPL depending on build; used as an external tool | TODO |
| Fonts (DejaVu / system) | free licences | TODO |
| Fallback score | generated procedurally by this repo's own code; original | n/a |

## Style and privacy

Prompts describe qualities ("warm hand-painted, film grain, teal shadows, amber highlights"), not living artists. No private family details are sent to any hosted model.
