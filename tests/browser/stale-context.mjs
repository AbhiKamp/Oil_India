// Browser regression check only: the deliberately delayed assistant responses below are mocks.
// Requires both local services and `npm ci` in apps/video (Playwright dependency).
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';

const require = createRequire(new URL('../../apps/video/package.json', import.meta.url));
const {chromium} = require('playwright');
const browser = await chromium.launch({executablePath: '/usr/bin/chromium', headless: true});
const page = await browser.newPage();
try {
  if (process.env.NWIS_TEST_API_URL) {
    const target = new URL(process.env.NWIS_TEST_API_URL);
    assert.ok(['localhost', '127.0.0.1', '[::1]'].includes(target.hostname));
    await page.route('**/api/v1/**', async route => {
      const source = new URL(route.request().url());
      const response = await route.fetch({url: new URL(source.pathname + source.search, target).href});
      await route.fulfill({response});
    });
  }
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  let calls = 0;
  await page.route('**/api/v1/assistant/chat', async route => {
    calls++;
    const first = calls === 1;
    if (first) await gate;
    await route.fulfill({status: 200, contentType: 'application/json', body: JSON.stringify({
      answer: first ? 'STALE RESPONSE MUST NOT APPEAR' : 'Current-context evidence summary.',
      citations: [], evidence_count: 0, engine: 'browser-regression-mock',
    })});
  });
  await page.goto(process.env.NWIS_DASHBOARD_URL || 'http://127.0.0.1:41987');
  await page.locator('.formation-track h3').first().filter({hasText: 'Naharkatiya 421'}).waitFor();
  await page.locator('.assistant-collapse > summary').click();
  await page.locator('#assistant-query').fill('What happened in Barail?');
  const requested = page.waitForRequest('**/api/v1/assistant/chat');
  await page.getByRole('button', {name: 'Search evidence', exact: true}).click();
  await requested;
  await page.getByLabel('Active well', {exact: true}).selectOption('NHK-412');
  await page.locator('.formation-track h3').first().filter({hasText: 'Naharkatiya 412'}).waitFor();
  await page.getByLabel('Active well', {exact: true}).selectOption('NHK-421');
  await page.locator('.formation-track h3').first().filter({hasText: 'Naharkatiya 421'}).waitFor();
  const response = page.waitForResponse('**/api/v1/assistant/chat');
  release();
  await response;
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  assert.equal(await page.getByText('STALE RESPONSE MUST NOT APPEAR', {exact: true}).count(), 0);
  await page.getByRole('button', {name: 'Search evidence', exact: true}).click();
  await page.getByText('Current-context evidence summary.', {exact: true}).waitFor();
  console.log('PASS: delayed response from a prior well context is discarded; current context remains usable.');
} finally {
  await browser.close();
}
