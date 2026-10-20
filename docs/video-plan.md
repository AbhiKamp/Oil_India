# Film plan — Before the Next Metre

Primary deliverable for StrataSentry NWIS, Healix 1, SIH 2026 PS 26121.
Companion: [prototype plan](prototype-plan.md) and [execution handoff](implementation-handoff.md).

Status: treatment and production specification. No footage or video application has been built.

## 1. Creative brief

**The viewer must understand the problem after 20 seconds and the solution after one viewing.**

Core sentence:

> Oil India has live drilling data. NWIS connects it to the experience buried in nearby-well reports, so engineers can see relevant risks and evidence before reaching the same geological conditions.

Working title: **Before the Next Metre**.
Closing line: **Every well leaves a lesson. The next well should not have to learn it again.**

Make a cinematic product explanation, not a science-fiction trailer and not a feature slideshow. The engineer is the protagonist. The old report is the missing knowledge. The approaching formation is the clock. The software makes the relationship visible.

### Interstellar-inspired direction

- Vast scale: a short surface-to-subsurface descent, then intimate detail on one report sentence.
- Time: a restrained pulse marks progress toward an interval; it never implies a known countdown to disaster.
- Memory: an old report's annotated depth line becomes a formation horizon in the present well.
- Visual contrast: quiet ivory evidence against deep graphite geology; amber only when attention is justified.
- Emotional payoff: the engineer gains context and records a decision. Do not manufacture a disaster/rescue montage.
- Music: original or properly licensed ambient score, low sustained organ-like texture, sparse piano, slow build, intelligible narration. Use original melody and arrangement; do not use the film's soundtrack or recognizable musical phrases.
- No film clips, character voices, logos, spaceship dashboards, black-hole intro, or copied title sequence.

## 2. Film architecture

Default master: **180 seconds, 16:9, 1920×1080, 30 fps**. Confirm competition limits before final timing. Capture larger than delivery where practical to allow readable punch-ins. At least 60% of runtime should show the actual application, not recreated UI.

Produce:

1. Three-minute narrated submission master.
2. Ninety-second cut using the same assets and proof sequence.
3. Captioned master, clean master, `.srt`, and full transcript.
4. Thumbnail and three stills for README/presentation.
5. Separate uncut functional walkthrough for technical verification.

Make the first rough film early, using a voice scratch track and annotated stills explicitly marked as storyboard material. Replace all product mockups with real footage before release. The film must not become the task that starts after everyone finishes coding.

## 3. Shot-by-shot master storyboard

Timing is a target. Narration should fit naturally at roughly 120–135 words/minute with breathing room; edit the words rather than racing through them.

| Time | Picture and action | Voiceover draft | Viewer takeaway / proof |
| --- | --- | --- | --- |
| 00–08 | Night-like silhouette of a drilling site; a restrained section line descends below the ground. A small caption says “Illustrative subsurface view.” | “The next drilling risk may already be written down. In the report of a well drilled years ago.” | This is a drilling knowledge problem, immediately. |
| 08–22 | Active telemetry on the left; a few legible historical report pages on the right. An event paragraph is visible but disconnected from the active depth. | “Oil India's eRTMAC shows what is happening now. But nearby wells' lessons are scattered across completion reports, daily records, and experience. Finding the right lesson takes time.” | The gap is historical context, not absence of telemetry. |
| 22–34 | Report depth line transforms into a geological horizon; cut to actual Operations screen. Small product title, then move on. | “StrataSentry NWIS connects those lessons to the active well—turning historical records into formation-aware, evidence-backed decision support.” | Clear solution in plain language. |
| 34–54 | Actual upload of one short synthetic report; extraction status; event fields; click source page and review one uncertain field. Hold on paragraph and matching fields. | “A report becomes a structured event: which well, which formation, what happened, what was tried, and what outcome was recorded. Every finding keeps its source, and uncertain fields are reviewed.” | Real ingestion and institutional memory, with provenance. |
| 54–73 | Map selects active well; radius changes; well list updates. Select relevant offset, then open comparison. | “The engineer selects nearby wells within a chosen radius. But surface distance is only the first filter. A close well may have drilled very different geology.” | Required map function and why more context matters. |
| 73–94 | Actual formation tracks toggle from absolute TVD to formation-relative alignment. Relevant event band aligns; unsuitable well dims with an explanation. | “NWIS compares formation intervals and survey data. Here, the same formation lies at different depths. Aligning the geology reveals the useful precedent that a simple depth search would miss.” | This is the central technical differentiator. |
| 94–116 | Replay advances. Historical approach watch appears while telemetry is normal. Zoom to distance, interval, sources, and method. | “Before the active well reaches the comparable interval, NWIS raises a historical-risk watch. It shows the interval ahead, the supporting wells, and the uncertainty—not just an unexplained score.” | Proactive warning from historical knowledge. |
| 116–136 | Replay pressure/torque/ROP tracks change; existing alert escalates with a separate live-signal explanation. No exaggerated alarm. | “As the replay develops adverse sensor trends, the warning adds live evidence. The engineer can distinguish the historical precedent from the current observations, and see why attention is needed.” | Historical plus real-time reasoning; no magical AI prediction claim. |
| 136–155 | Open cited report at actual page; show historical action/outcome; ask “Why this well?”; acknowledge and save decision note. | “One click opens the original report and the action recorded by that crew. The assistant explains the match with citations. The engineer reviews the evidence and records a decision for the next shift.” | Trust, human decision, and institutional memory loop. |
| 155–169 | Real local-mode status with measured readiness; short architecture overlay: eRTMAC read-only source → NWIS → engineer. If offline verification passed, show corresponding evidence. | “The prototype runs locally with a labeled synthetic replay. It is designed to sit beside eRTMAC, with read-only integration and engineering validation as the next deployment step.” | Honest feasibility and integration boundary. |
| 169–180 | Return to same geological interval; two wells connected by one evidence line. End card: product, team, PS, repo/QR. Hold at least four seconds. | “Every well leaves a lesson. The next well should not have to learn it again. StrataSentry NWIS. Before the next metre.” | Memorable value proposition and identity. |

### Required on-screen clarifications

- First application appearance: “Synthetic demonstration data.” Keep a small readable demo/replay badge in actual UI footage.
- First mention: “Offset well = a nearby or geologically relevant previously drilled well.”
- First comparison: “MD: distance along the borehole · TVD: vertical depth.”
- First event: “Pack-off: material restricts the space around the drillstring.”
- Historical watch: “Comparable interval ahead; not a predicted incident time.”
- Architecture: “eRTMAC integration proposed; replay source used in this prototype,” unless a real integration is verified later.
- Any trained model score: state whether it is experimental and synthetic-data evaluated.

Do not show all explanatory labels at once. Make each one appear when its concept first matters.

## 4. Signature visual moments

### A. The report becomes the ground

A source paragraph has the well, formation, event interval, and mitigation highlighted. Its interval line extends horizontally into the cross-section. The transition ends on the actual application's event band. This single moment communicates extraction, provenance, and relevance.

Use composited annotation over a real report. Label any explanatory geology animation as illustrative. It must not imply that a scanned paragraph alone reconstructs a measured 3D reservoir.

### B. The wells align

Three columns begin at their true depths. The formation-relative toggle aligns their named intervals. The active cursor now sits just above a historical event band. A nearby but unrelated candidate stays unselected, with a short reason.

This is more valuable than an elaborate rotating globe: the audience can see exactly why the platform's correlation helps.

### C. The alert earns its explanation

Build the alert visually in three readable steps:

1. **What is ahead:** comparable historical risk interval.
2. **Why this evidence:** formation and survey context.
3. **Where it comes from:** source page and historical outcome.

When live signals change, add a fourth layer rather than replacing the explanation with a red percentage.

### D. Memory closes the loop

The engineer's short decision note joins the evidence timeline. End on the idea of knowledge being retained across crews. Do not turn a click into an unverified “incident prevented” animation.

## 5. Typography, motion, and sound

### Frame readability

- One idea and one focal point per shot.
- At 1080p, aim for 48–72 px section titles and 28–36 px explanatory overlays; validate actual exported readability at 720p and on a phone.
- Do not shrink an entire dense dashboard to accommodate a decorative border. Crop into the exact control or evidence at the moment it is discussed.
- Maintain safe margins; subtitles never cover the selected evidence or replay controls.
- Show source paragraph and citation together for at least four seconds.
- Every displayed number, well name, depth, page, and event must match the frozen scenario.

### Motion vocabulary

- Slow deliberate descent for spatial context; short smooth push-ins for detail.
- Match cuts between map marker, survey path, formation band, and source highlight.
- UI cursor movement is deliberate; pause before and after clicks.
- Avoid constant zooms, glitch transitions, rapid word-by-word captions, excessive bloom, and decorative particles over data.
- Use camera presets for repeatable captures; user controls still work in the product.
- Reduced-motion product mode is independent from the film's editing.

### Audio treatment

- Record a scratch narration before animation; final human narration after wording is verified.
- Start with a quiet mechanical/ambient pulse, build gently through correlation, briefly reduce music when the source opens, resolve warmly at the end.
- Avoid alarm sounds suggesting a real emergency. One restrained notification cue is enough.
- Target approximately −16 LUFS integrated loudness and true peak no higher than −1 dBTP for the final mix; verify export rather than relying on mixer sliders.
- Dialogue remains intelligible on laptop speakers and a phone at low volume. Music ducks under speech.
- Record asset source, author, license, and required attribution. Verify Remotion's current licensing terms for the team's intended use as well as media licenses.

## 6. Production pipeline

### Tools and source layout

The official open-source Remotion agent skill is installed in `.agents/skills/remotion-best-practices/`. Restart OpenCode before expecting it in the skill list. It includes creation, markup, maps, captions, and render guidance. Use it during implementation; no Remotion app is created by this plan.

Proposed new workspace:

```text
apps/video/
  src/                 # scenes, typography, captions, composition
  public/              # selected licensed media and capture inputs
  package.json         # independent video dependencies and render scripts
demo/scenarios/        # canonical story and replay metadata
demo/capture/          # recording automation and shot manifest
docs/media/            # asset credits, transcript, shot review notes
```

Keep renderer dependencies outside the dashboard. Use real browser recordings for interactions and Remotion for editing, explanation overlays, transitions, audio, and captions. Do not rebuild a fake dashboard in the film workspace.

### Reproducible capture

1. Pin application revision and scenario version.
2. Reset the demo database/session from a known seed.
3. Preload fonts, maps, PDFs, and model assets.
4. Set viewport, browser version, locale, time zone, and reduced/non-reduced motion mode explicitly.
5. Capture named shots using deterministic replay pause/seek controls and stable test selectors.
6. Wait on application readiness and rendered data, not arbitrary sleeps.
7. Export a shot manifest containing revision, scenario, source capture, timestamps, and purpose.
8. Preserve uncut source footage; edited shots must not fabricate application behavior.

If OCR/model waits are shortened, mark the time compression. Do not use edits to imply instant processing or a function that was never executed.

### Rendering

Frame-driven animation, fixed seeds, and local media; no network fetches or wall-clock randomness during rendering. Use a single composition timeline and reusable scenes for the master and short cut. Preview small segments first, then approve the full cut before final rendering.

Final export: H.264 MP4, yuv420p, AAC audio, fast-start metadata, appropriate bitrate for text clarity. Preserve a high-quality master and produce a size-constrained submission copy only after the portal limits are known. Verify duration, resolution, frame rate, audio peaks, caption timing, first/last frames, and playback in an ordinary browser/player.

## 7. Quality gates

### Gate V0 — paper edit

Before polishing visuals, show the storyboard and scratch audio to someone unfamiliar with drilling. They should understand the present-versus-past knowledge gap without knowing any technology names.

### Gate V1 — rough proof cut

Working footage must show: upload → cited event → radius search → formation alignment → historical watch → live signal → source → decision. Fix a missing product proof instead of masking it with motion graphics.

### Gate V2 — one-view comprehension test

Show the rough film once to five people who have not built the application. Ask independently:

1. What problem does Oil India have despite already having live telemetry?
2. What information does NWIS extract from old reports?
3. Why does the nearest surface well not always provide the best comparison?
4. What makes an alert believable?
5. Who decides what action to take?

Target: at least four of five viewers answer all five substantially correctly. This is an internal communication gate, not a scientific user study. If they remember “AI dashboard” but not the evidence chain, rewrite the film.

### Gate V3 — domain and truth review

One reviewer traces every displayed event/page/depth against the scenario. A domain-informed reviewer checks terminology, geological assumptions, and historical-action wording. Remove unverified time savings, NPT reduction, predictive accuracy, and incident-prevention claims.

### Gate V4 — visual/audio review

Watch silently, on laptop speakers, on a phone, and at 720p. Check captions, contrast, label duration, music masking, typos, cursor visibility, and abrupt cuts. No tiny architecture diagram, watermark, accidental terminal secret, or unresolved placeholder.

### Gate V5 — submission verification

Open the uploaded video using a signed-out browser. Verify permissions, playback, QR code, repository URL, team identity, captions, and the exact file submitted. Keep local backups. A polished film that judges cannot open fails.

## 8. Ninety-second cut

- 00–12: problem and eRTMAC distinction.
- 12–25: report → structured, cited event.
- 25–43: map → formation alignment.
- 43–65: historical watch → live signal explanation.
- 65–80: source page → engineer decision.
- 80–90: local/synthetic scope and closing line.

Cut secondary features, not the causal chain. Do not double playback speed across the entire master.

## 9. Bragging rights, earned

After verification, strong lines include:

- “An old report, a matching formation, a warning before the interval.”
- “Click any showcased alert and inspect the original evidence.”
- “From nearby wells to the next drilling decision.”
- “Built for PS 26121: historical knowledge alongside live monitoring.”

Use measured demonstrations where available: a specific local retrieval latency, a reproducible replay warning lead time, or extraction results with denominators. Never replace evidence with “industry-leading,” “production-ready,” “zero hallucinations,” or invented savings.
