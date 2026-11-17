# Film assets and provenance

| Asset | Source / author | License / status | Use |
| --- | --- | --- | --- |
| Geological layer graphics, overlays, typography | Healix 1, generated in `apps/video/src/video.tsx` | Original project work | Explanatory visuals; explicitly labeled as schematic, not measured geology |
| Ambient score (`apps/video/public/ambient-original.wav`) | Deterministically synthesized by `apps/video/scripts/generate_ambient.py` using Python standard library sine waves and a fixed note sequence | Original generated audio; no samples or third-party music | Rough master only; no recognizable existing melody |
| Dashboard footage and PNG checkpoints | Local NWIS prototype at `127.0.0.1:41987`, captured with system Chromium and Playwright | Synthetic demo data; actual UI interaction recordings; 1.3× playback | Capture manifest records run details, API results, and workflow outcomes |
| Generated PDF training fixture | `demo/capture/generate_synthetic_pdf.py` | Original, generated demonstration material; not an OIL report; source code and SHA-256 in capture manifest | Demonstrates text extraction, physical PDF page provenance, explicit review, and offset-to-active handover |
| Narration text / captions | Healix 1, `docs/media/voiceover-draft.md` and `.srt` | Original script; captioned on-screen, no spoken recording in rough cut | Readable narration substitute |

## Voice synthesis decision

No voice track is used in the rough master. Piper TTS 1.8.0 was installed in a temporary `/tmp/opencode/film-tts` environment for evaluation only. The readily available `en_US-lessac-medium` voice traces to the Blizzard 2013 Lessac dataset, whose linked license is a research-only agreement. That voice is therefore not included in a public film deliverable. No human voice was cloned, imitated, or represented as recorded narration. The film uses readable captions and the original ambient bed instead.

References checked 20 October 2026:

- Piper voice model card: <https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/lessac/medium/MODEL_CARD>
- Underlying Lessac/Blizzard dataset license: <https://www.cstr.ed.ac.uk/projects/blizzard/2013/lessac_blizzard2013/license.html>
- Piper TTS source/package: <https://github.com/OHF-Voice/piper1-gpl>
- Remotion license: <https://github.com/remotion-dev/remotion/blob/main/LICENSE.md>. It grants free use to individuals, organizations with up to three employees, non-profits/not-for-profits, or evaluation before commercial use. There is no separate student-team exemption; eligibility should be rechecked before commercialization.

The prototype contains synthetic fictionalized demonstration records and report text. All application imagery must continue to disclose synthetic status and must not imply a verified physical PDF page when only a text marker is available.
