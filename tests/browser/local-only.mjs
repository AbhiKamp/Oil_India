// Verify real application reads without any non-loopback browser requests.
// Optional NWIS_TEST_API_URL routes API traffic to a separate REAL local test process.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';

const require = createRequire(new URL('../../apps/video/package.json', import.meta.url));
const {chromium} = require('playwright');
const browser = await chromium.launch({executablePath: '/usr/bin/chromium', headless: true});
const page = await browser.newPage({viewport: {width: 1366, height: 900}});
const external = [];
const scriptErrors = [];
page.on('pageerror', error => scriptErrors.push(error.message));
try {
  if (process.env.NWIS_TEST_API_URL) {
    assert.ok(['localhost', '127.0.0.1', '[::1]'].includes(new URL(process.env.NWIS_TEST_API_URL).hostname));
  }
  await page.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (!['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname)) {
      external.push(url.origin);
      return route.abort();
    }
    if (process.env.NWIS_TEST_API_URL && url.pathname.startsWith('/api/v1/')) {
      const actual = new URL(url.pathname + url.search, process.env.NWIS_TEST_API_URL).href;
      const response = await route.fetch({url: actual});
      return route.fulfill({response});
    }
    return route.continue();
  });
  await page.goto(process.env.NWIS_DASHBOARD_URL || 'http://127.0.0.1:41987');
  await page.locator('.well-row').nth(2).waitFor();
  assert.equal(await page.locator('.well-row').count(), 3);
  const updated = page.waitForResponse(response => response.url().includes('/nearby?radius_km=5'));
  await page.getByLabel('Search radius in kilometres').focus();
  await page.getByLabel('Search radius in kilometres').press('Home');
  await updated;
  await page.waitForFunction(() => document.querySelectorAll('.well-row').length === 1);
  await page.getByRole('button', {name: /WCR_NHK_412.txt.*inspect source/}).click();
  await page.getByRole('dialog').waitFor();
  assert.match(await page.getByRole('dialog').innerText(), /18-barrel pit gain/);
  await page.getByRole('button', {name: 'Close', exact: true}).click();
  assert.deepEqual(external, []);
  assert.deepEqual(scriptErrors, []);
  console.log('PASS: coordinate filtering and source viewing used only loopback requests, with no page errors.');
} finally {
  await browser.close();
}
