# Before the Next Metre

Remotion rough master for Healix 1, SIH 2026, PS 26121. It uses an actual 131-second dashboard recording at 1.3× playback in a 141-second captioned, originally scored composition. The opening/closing geology is original explanatory graphic; all screen states are recorded from the running prototype.

## 60-second cut (`NwisShort`)

Music-only short for upload: space cold open, seven zoomed chapters of the real recording (find, connect, trace, review, hand over, watch, alert), and an end card. The score is original and generated deterministically with the Python stdlib on a 96 BPM grid, so cuts land on bar lines.

```sh
python3 scripts/generate_score.py   # writes public/score-original.wav (ignored)
npm run render:short -- --browser-executable=/usr/bin/chromium   # out/stratasentry-nwis-60s.mp4
```

## Preview and render

```sh
npm ci
npm run studio
npm run still
npm run render:sample
npm run render
```

The Studio composition is `BeforeTheNextMetre` (1920×1080, 30 fps, 141 seconds). The captured 131.16-second workflow is played at 1.3×; recalculate the product segment duration if you change the capture. Remotion packages are pinned together at 4.0.537. To render where system Chromium is installed, append `--browser-executable=/usr/bin/chromium` to the Remotion command. To record dashboard interactions, follow [`demo/capture/README.md`](../../demo/capture/README.md).

## Reproduce rough-master inputs

From the repository root, after the dashboard and API are ready:

```sh
node demo/capture/record-workflow.mjs
cd apps/video
python3 scripts/generate_ambient.py
npx tsc --noEmit
npx remotion render src/index.ts BeforeTheNextMetre out/before-the-next-metre-rough.mp4 --browser-executable=/usr/bin/chromium
```

The capture runner records the verified browser workflow and PNG checkpoints. It writes a manifest with repository/core revision, dirty flags, capture URLs, API statuses, and SHA-256 hashes of the synthetic well, formation prognosis, telemetry scenario, reports, and generated PDF fixture. The take verifies radius filtering, source marker navigation, upload to the explicit offset well, physical-page extraction, review approval, watch eligibility, active-well handover persistence, and a replay through signal escalation. The Python standard-library script deterministically regenerates the original ambient WAV. The cut uses captions rather than synthesized speech; see `docs/media/voiceover-draft.md`, `docs/media/before-the-next-metre.srt`, and `docs/media/asset-credits.md` for script and asset status.

The scoped `.gitignore` keeps final exports in `out/`, raw WebM/MP4/WAV captures, generated ambient WAV, and scratch voice WAV out of ordinary Git history. PNG checkpoints, shot manifests, transcript/SRT, source scripts, and credits remain trackable.

## Production block

**Rough master:** render to `out/before-the-next-metre-rough.mp4`. It is not submission-ready: it has no spoken narration, the initial API state has no telemetry/risk frame until replay, and comprehension/domain/audio review gates remain outstanding. No copyrighted score or voice likeness is used. Review Remotion's separate [license](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md) for eligibility; it has no separate student-team exemption, and SIH evaluation is not a blanket commercial-use permission.
