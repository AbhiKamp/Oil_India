import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {readFile, mkdir, readdir, rename, stat, unlink, writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const require = createRequire(path.join(root, 'apps/video/package.json'));
const {chromium} = require('playwright');
const baseURL = process.env.DASHBOARD_URL || 'http://127.0.0.1:41987';
const apiURL = process.env.NWIS_API_URL || 'http://localhost:8000';
const output = path.resolve(process.env.CAPTURE_DIR || path.join(root, 'apps/video/public/captures'));
const browserPath = process.env.CHROMIUM_PATH || '/usr/bin/chromium';
const runId = new Date().toISOString().replace(/[:.]/g, '-');
const noteText = `Capture ${runId}: reviewed the cited synthetic source and formation context; carry the evidence into shift handover for engineering review.`;
const fixturePath = path.join(root, 'demo/capture/fixtures/synthetic_nhk412_demo.pdf');
const shots = [];
const apiResponses = new Map();
let failure;
let videoPath;
let initialRadius = 50;
let offsetCount = 0;
let uploadedEventId;
let uploadedDocumentName;

await mkdir(output, {recursive: true});
execFileSync('python3', ['demo/capture/generate_synthetic_pdf.py'], {cwd: root, stdio: 'ignore'});
const reset = await fetch(`${apiURL}/api/v1/demo/reset`, {method: 'POST'});
if (!reset.ok) throw new Error(`Could not reset isolated synthetic replay (${reset.status}). Start the API with a disposable NWIS_DATA_DIR.`);
const browser = await chromium.launch({headless: true, executablePath: browserPath, args: ['--no-sandbox']});
const browserVersion = browser.version();
const context = await browser.newContext({
  viewport: {width: 1600, height: 900},
  deviceScaleFactor: 1,
  locale: 'en-US',
  timezoneId: 'Asia/Kolkata',
  reducedMotion: 'reduce',
  recordVideo: {dir: output, size: {width: 1600, height: 900}},
});
const page = await context.newPage();
page.on('response', (response) => {
  if (response.url().includes(':8000/api/v1/')) apiResponses.set(`${response.url()} ${response.status()}`, {url: response.url(), status: response.status()});
});

const hold = async (name, purpose, seconds = 6) => {
  await page.screenshot({path: path.join(output, `${String(shots.length + 1).padStart(2, '0')}-${name}.png`)});
  shots.push({name, purpose, holdSeconds: seconds, at: new Date().toISOString(), url: page.url()});
  // This is an intentional editorial hold after the UI/API state is verified, not a readiness sleep.
  await page.waitForTimeout(seconds * 1000);
};
const waitForNearbyResponse = async (radiusKm, action) => {
  const responsePromise = page.waitForResponse((response) =>
    response.url().includes(`/nearby?radius_km=${radiusKm}`) && response.ok(), {timeout: 20000});
  await action();
  const response = await responsePromise;
  const data = await response.json();
  if (!Array.isArray(data)) throw new Error(`Nearby API did not return a list for ${radiusKm} km.`);
  return data;
};
const scrollTo = async (locator) => {
  await locator.waitFor({state: 'visible', timeout: 30000});
  await locator.scrollIntoViewIfNeeded();
};

try {
  await page.goto(baseURL, {waitUntil: 'domcontentloaded'});
  await page.getByRole('heading', {name: 'Nearby wells'}).waitFor({state: 'visible', timeout: 30000});
  const activeWell = page.getByRole('combobox', {name: 'Active well'});
  await activeWell.waitFor({state: 'visible'});
  await page.waitForFunction(() => document.querySelector('[aria-label="Active well"]')?.options.length > 1, null, {timeout: 30000});
  await page.getByTestId('operations-evidence').waitFor({state: 'visible'});
  const radius = page.getByRole('slider', {name: 'Search radius in kilometres'});
  initialRadius = Number(await radius.inputValue());
  const minRadius = await radius.getAttribute('min');
  if (minRadius !== '5') throw new Error(`Unexpected radius minimum: ${minRadius}`);

  const nearest = await waitForNearbyResponse(5, async () => {
    await radius.focus();
    await radius.press('Home');
  });
  if (nearest.length < 1) throw new Error('The 5 km nearby-well query returned no offset.');
  await page.getByRole('button', {name: /\d+(\.\d+)? km/}).first().waitFor({state: 'visible'});
  await hold('radius-nearby', 'Actual 5 km radius result after successful nearby API response');

  const offsets = await waitForNearbyResponse(50, async () => {
    await radius.focus();
    for (let i = 0; i < 9; i++) await radius.press('ArrowRight');
  });
  if (!offsets.length) throw new Error('The 50 km nearby-well query returned no offsets.');
  offsetCount = offsets.length;
  await page.getByRole('button', {name: /\d+(\.\d+)? km/}).first().waitFor({state: 'visible'});
  await hold('radius-offsets', `Actual 50 km offset results (${offsets.length}) after successful API response`);

  const comparison = page.getByRole('combobox', {name: 'Comparison well'});
  await comparison.waitFor({state: 'visible'});
  const activeWellId = await activeWell.inputValue();
  const offset = offsets.find((well) => well.well_id !== activeWellId);
  if (!offset) throw new Error('No offset returned to compare.');
  await comparison.selectOption(offset.well_id);
  const formationHeading = page.getByRole('heading', {name: 'Formation comparison'});
  await scrollTo(formationHeading);
  await page.getByText(/Shared formation names are comparison cues/).waitFor({state: 'visible'});
  await hold('formation-comparison', `Actual formation tracks for ${offset.well_id}; reported MD values and comparison caveat`);

  const watchHeading = page.getByRole('heading', {name: /Comparable intervals ahead/i});
  await scrollTo(watchHeading);
  const sourceButton = page.locator('.watch-card').filter({hasText: 'MECHANICAL HOLE PACK-OFF'}).getByRole('button', {name: /WCR_MOR_118/});
  await sourceButton.waitFor({state: 'visible', timeout: 20000});
  const watchCardText = await sourceButton.locator('xpath=ancestor::*[contains(@class,"watch-card")]').innerText().catch(() => 'Historical source watch shown in actual Operations UI');
  await hold('historical-watch', watchCardText);
  await sourceButton.click();
  const sourceDialog = page.getByRole('dialog', {name: /source/i});
  await sourceDialog.waitFor({state: 'visible'});
  await sourceDialog.getByText('Text marker 19 · cited evidence').waitFor({state: 'visible'});
  await page.waitForFunction(() => document.querySelector('.source-pages')?.scrollTop > 0);
  await hold('historical-source', 'Actual source viewer auto-scrolled to the cited synthetic text marker 19; not a physical PDF page');
  await sourceDialog.getByRole('button', {name: 'Close'}).click();
  await sourceDialog.waitFor({state: 'hidden'});

  await page.getByRole('tab', {name: 'Knowledge & review'}).click();
  await page.getByTestId('documents-workbench').waitFor({state: 'visible'});
  const uploadResponse = page.waitForResponse((response) => new URL(response.url()).pathname === '/api/v1/documents' && response.request().method() === 'POST');
  await page.getByLabel('Report well').selectOption('NHK-412');
  await page.getByLabel('Upload synthetic PDF').setInputFiles(fixturePath);
  const uploaded = await (await uploadResponse).json();
  uploadedDocumentName = uploaded.document_name;
  uploadedEventId = uploaded.events?.[0]?.event_id;
  if (!uploadedEventId || uploaded.events[0].page_reference_type !== 'physical_pdf_page') throw new Error('Uploaded demo PDF did not produce a physically paged source event.');
  await page.getByText('synthetic_nhk412_demo.pdf').waitFor({state: 'visible'});
  const reviewHeading = page.getByRole('heading', {name: 'Event review'});
  await scrollTo(reviewHeading);
  const uploadedReview = page.locator('.review-event').filter({hasText: 'SYNTHETIC DEMO - GAS KICK RESPONSE EXERCISE'});
  await uploadedReview.getByText('needs review').waitFor({state: 'visible'});
  await hold('knowledge-review', 'Real text-PDF extraction with original document name and needs-review state');
  await uploadedReview.getByRole('button', {name: 'Approve'}).click();
  await uploadedReview.getByText('approved').waitFor({state: 'visible'});
  await hold('approved-event', 'Engineer explicitly approved the extracted, cited training-only PDF event');
  await page.getByRole('tab', {name: 'Operations'}).click();
  const uploadedWatch = page.locator('.watch-card').filter({hasText: 'SYNTHETIC DEMO - GAS KICK RESPONSE EXERCISE'});
  await uploadedWatch.waitFor({state: 'visible', timeout: 20000});
  await hold('approved-watch', 'Approved PDF event became eligible for the historical watch, with physical page provenance');

  await page.getByRole('tab', {name: 'Handover'}).click();
  await page.getByTestId('handover-workbench').waitFor({state: 'visible'});
  const eventSelect = page.getByLabel('Historical source event');
  await eventSelect.waitFor({state: 'visible'});
  const options = await eventSelect.locator('option').allTextContents();
  if (options.length < 2) throw new Error('Handover has no selectable reviewed source event.');
  await eventSelect.selectOption(uploadedEventId);
  await page.getByLabel('Decision note').fill(noteText);
  await hold('handover-note', 'Actual engineer-entered note before save; not an operational recommendation');
  await page.getByRole('button', {name: 'Save acknowledged decision'}).click();
  const savedNote = page.getByText(noteText, {exact: true});
  await savedNote.waitFor({state: 'visible', timeout: 20000});
  await hold('handover-saved', 'Acknowledged decision returned in the Handover log');
  await page.reload({waitUntil: 'domcontentloaded'});
  await page.getByRole('heading', {name: /Context for the interval ahead/}).waitFor({state: 'visible'});
  await page.getByRole('tab', {name: 'Handover'}).click();
  const persistedNote = page.getByText(noteText, {exact: true});
  await persistedNote.waitFor({state: 'visible', timeout: 20000});
  await hold('handover-persisted', 'Same saved note reloaded from the API after page reload');

  await page.getByRole('tab', {name: 'Operations'}).click();
  const replayPanel = page.getByTestId('demo-replay');
  await scrollTo(replayPanel);
  await page.getByLabel('Replay scenario').selectOption('packoff');
  await page.getByRole('button', {name: 'Play'}).click();
  await page.getByText(/Synthetic replay · packoff · step (?:[5-9][0-9])\/80/i).waitFor({state: 'visible', timeout: 60000});
  const pause = page.getByRole('button', {name: 'Pause'});
  await pause.click();
  const riskText = await page.locator('.risk-card').innerText();
  await hold('synthetic-replay', `Actual pack-off synthetic replay, returned risk assessment: ${riskText}; not live telemetry`);
  await page.getByTestId('operations-evidence').scrollIntoViewIfNeeded();
  await hold('operations-close', 'Actual Operations view after replay, showing restored spatial/evidence/telemetry panels');

} catch (error) {
  failure = error instanceof Error ? error.message : String(error);
  throw error;
} finally {
  const pageVideo = page.video();
  const repositoryRevision = execFileSync('git', ['rev-parse', 'HEAD'], {cwd: root, encoding: 'utf8'}).trim();
  const dirtyPaths = execFileSync('git', ['status', '--porcelain'], {cwd: root, encoding: 'utf8'}).trim().split('\n').filter(Boolean);
  const coreDirtyPaths = execFileSync('git', ['status', '--porcelain', '--', '.', ':(exclude)apps/video', ':(exclude)demo/capture', ':(exclude)docs/media'], {cwd: root, encoding: 'utf8'}).trim().split('\n').filter(Boolean);
  const sourceFiles = [
    'data/synthetic/wells/wells.json',
    'data/synthetic/formation_prognosis_nhk421.json',
    'data/synthetic/telemetry/telemetry_packoff_incident.csv',
    'data/synthetic/reports/WCR_MOR_118.txt',
    'data/synthetic/reports/WCR_NHK_412.txt',
    'demo/capture/generate_synthetic_pdf.py',
    'demo/capture/fixtures/synthetic_nhk412_demo.pdf',
  ];
  const sourceHashes = Object.fromEntries(await Promise.all(sourceFiles.map(async (file) => [file, createHash('sha256').update(await readFile(path.join(root, file))).digest('hex')])));
  await context.close();
  await browser.close();
  const baseManifest = {
    capturedAt: new Date().toISOString(),
    baseURL,
    viewport: {width: 1600, height: 900},
    timezone: 'Asia/Kolkata',
    browser: `${browserPath} · Chromium ${browserVersion}`,
    repositoryRevision: execFileSync('git', ['rev-parse', 'HEAD'], {cwd: root, encoding: 'utf8'}).trim(),
    coreRevision: repositoryRevision,
    workingTreeDirty: dirtyPaths.length > 0,
    workingTreeDirtyPaths: dirtyPaths,
    coreTreeClean: coreDirtyPaths.length === 0,
    coreDirtyPaths,
    scenario: 'synthetic demo API; extracted and approved generated synthetic NHK-412 PDF; packoff replay progressed to signal escalation; no eRTMAC source',
    sourceHashesSha256: sourceHashes,
    initialRadiusKm: initialRadius,
    finalRadiusQueryKm: 50,
    offsetCount,
    noteText,
    uploadedDocumentName,
    uploadedEventId,
    captureDataDirectory: process.env.NWIS_DATA_DIR || 'API process default; must use disposable path for capture',
    notePersistenceVerified: !failure && shots.some((shot) => shot.name === 'handover-persisted'),
    status: failure ? 'incomplete' : 'complete',
    failure,
    shots,
    captureURLs: [...new Set([baseURL, ...[...apiResponses.values()].map(({url}) => url)])],
    apiResponses: [...apiResponses.values()],
  };
  try {
    const generatedVideo = videoPath || await pageVideo.path();
    if (!failure && shots.length >= 10) await rename(generatedVideo, path.join(output, 'workflow.webm'));
    else if (await stat(generatedVideo).then(() => true).catch(() => false)) await unlink(generatedVideo);
  } catch {}
  if (!shots.length) {
    for (const file of await readdir(output)) if (file.endsWith('.webm')) await unlink(path.join(output, file));
  }
  await writeFile(path.join(output, 'shot-manifest.json'), JSON.stringify(baseManifest, null, 2));
}
