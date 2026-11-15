#!/usr/bin/env node
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { PNG } from 'pngjs';
import { startDistServer } from './serve-dist.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, '..');
const distDir = resolve(root, 'dist');
const artifactsDir = resolve(root, 'test-artifacts');
mkdirSync(artifactsDir, { recursive: true });

function assert(cond, msg) {
  if (!cond) throw new Error(`Player assertion failed: ${msg}`);
}

function decodeCanvasPng(buf) {
  return PNG.sync.read(buf);
}

function sampleTicGrid(png) {
  const { width, height, data } = png;
  const cols = new Set();
  const samples = [];
  for (let gx = 16; gx <= 224; gx += 26) {
    for (let gy = 10; gy <= 126; gy += 16) {
      const px = Math.min(width - 1, Math.max(0, Math.floor(((gx + 8.5) * width) / 256)));
      const py = Math.min(height - 1, Math.max(0, Math.floor(((gy + 4.5) * height) / 144)));
      const idx = (py * width + px) * 4;
      const key = `${data[idx]},${data[idx + 1]},${data[idx + 2]}`;
      cols.add(key);
      samples.push(key);
    }
  }
  return { uniqueColors: cols.size, samples };
}

function rectsOverlap(a, b) {
  return !(a.right <= b.left + 1 || a.left >= b.right - 1 || a.bottom <= b.top + 1 || a.top >= b.bottom - 1);
}

async function launchBrowser() {
  try {
    return await chromium.launch({
      channel: 'chrome',
      headless: true,
      args: ['--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
    });
  } catch (_) {
    return await chromium.launch({
      headless: true,
      args: ['--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
    });
  }
}

async function main() {
  const { server, url } = await startDistServer(distDir, 0, '127.0.0.1');
  const browser = await launchBrowser();
  const errors = [];

  try {
    // 1. Desktop (1280x860) verification
    const desktopCtx = await browser.newContext({ viewport: { width: 1280, height: 860 } });
    const page = await desktopCtx.newPage();
    page.on('pageerror', (e) => errors.push(`pageerror: ${e.message}`));
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(`console.error: ${msg.text()}`);
    });
    page.on('response', (res) => {
      if (res.status() >= 400) errors.push(`HTTP ${res.status()} ${res.url()}`);
    });

    await page.goto(url, { waitUntil: 'networkidle' });
    await page.waitForFunction(() => window.__sf2Shell && window.__sf2Shell.isBooted(), { timeout: 20000 });
    await page.waitForTimeout(1850);
    await page.screenshot({ path: resolve(artifactsDir, '10-desktop-intro.png') });
    await page.waitForTimeout(1750);

    const desktopTouchVisible = await page.evaluate(() => window.__sf2Shell.isTouchVisible());
    assert(desktopTouchVisible === false, 'Desktop mouse context should hide touch deck under TOUCH: AUTO');

    const canvasLoc = page.locator('#canvas');
    const titlePng = decodeCanvasPng(await canvasLoc.screenshot());
    const titleStats = sampleTicGrid(titlePng);
    assert(titleStats.uniqueColors >= 3, `Title screen canvas looks flat (${titleStats.uniqueColors} colors)`);
    await page.screenshot({ path: resolve(artifactsDir, '01-desktop-title.png') });

    // Navigate Title -> Select -> VS -> Fight via real keyboard events
    await page.click('#canvas');
    await page.keyboard.press('KeyZ'); // Title -> Select
    await page.waitForTimeout(350);
    await page.screenshot({ path: resolve(artifactsDir, '07-desktop-select.png') });
    await page.keyboard.press('KeyZ'); // Select -> VS (Ryu vs Ken)
    await page.waitForTimeout(450);
    await page.screenshot({ path: resolve(artifactsDir, '08-desktop-vs.png') });
    await page.keyboard.press('KeyZ'); // Skip VS -> Fight
    await page.waitForTimeout(1600); // Wait for ROUND 1 freeze to finish
    await page.keyboard.down('ArrowRight');
    await page.waitForTimeout(280);
    await page.keyboard.up('ArrowRight');
    await page.keyboard.press('KeyA');
    await page.waitForTimeout(120);

    const fightPng = decodeCanvasPng(await canvasLoc.screenshot());
    const fightStats = sampleTicGrid(fightPng);
    const diffCount = titleStats.samples.filter((s, idx) => s !== fightStats.samples[idx]).length;
    assert(diffCount >= 10, `Fight screen canvas did not change significantly from Title (${diffCount} diffs)`);
    await page.screenshot({ path: resolve(artifactsDir, '02-desktop-fight.png') });

    // Verify CRT & INT defaults, canvas 3x integer dimensions (720x408), and toggles
    const crtDefault = await page.evaluate(() => window.__sf2Shell.isCrtEnabled());
    const intDefault = await page.evaluate(() => window.__sf2Shell.isIntEnabled());
    assert(crtDefault === true, 'CRT scanlines should default to enabled');
    assert(intDefault === true, 'Integer scaling should default to enabled');

    const ticOpts = await page.evaluate(() => window.__sf2Shell.getTic80Options());
    assert(ticOpts.studioPtr > 0 && ticOpts.configPtr > 0, `TIC-80 studio/config pointers missing: ${JSON.stringify(ticOpts)}`);
    assert(ticOpts.wasmCrt === 1, `Expected TIC-80 WASM crt=1 by default, got ${JSON.stringify(ticOpts)}`);
    assert(ticOpts.wasmInt === 1, `Expected TIC-80 WASM integerScale=1 by default, got ${JSON.stringify(ticOpts)}`);
    assert(ticOpts.fsJson && ticOpts.fsJson.crt === true && ticOpts.fsJson.integerScale === true, `Expected options.json crt=true & integerScale=true, got ${JSON.stringify(ticOpts.fsJson)}`);

    const canvasBox = await canvasLoc.boundingBox();
    assert(canvasBox && Math.round(canvasBox.width) === 768 && Math.round(canvasBox.height) === 432, `Expected desktop #canvas 768x432 (3x 256x144), got ${JSON.stringify(canvasBox)}`);

    await page.click('#btn-crt');
    await page.waitForTimeout(60);
    const crtAfterOff = await page.evaluate(() => window.__sf2Shell.isCrtEnabled());
    assert(crtAfterOff === false, 'Clicking #btn-crt should toggle CRT off');
    await page.click('#btn-crt');
    await page.waitForTimeout(60);

    await page.click('#btn-int');
    await page.waitForTimeout(60);
    const intAfterOff = await page.evaluate(() => window.__sf2Shell.isIntEnabled());
    const optsAfterIntOff = await page.evaluate(() => window.__sf2Shell.getTic80Options());
    assert(intAfterOff === false && optsAfterIntOff.wasmInt === 0, `Clicking #btn-int should toggle INT off: ${JSON.stringify(optsAfterIntOff)}`);
    await page.click('#btn-int');
    await page.waitForTimeout(60);
    const intAfterOn = await page.evaluate(() => window.__sf2Shell.isIntEnabled());
    const optsAfterIntOn = await page.evaluate(() => window.__sf2Shell.getTic80Options());
    assert(intAfterOn === true && optsAfterIntOn.wasmInt === 1, `Clicking #btn-int again should restore INT on: ${JSON.stringify(optsAfterIntOn)}`);

    // 2. Virtual Touch Pad slide-to-motion test (2 -> 3 -> 6 + LP)
    await page.click('#btn-touch-mode');
    await page.waitForTimeout(120);
    const manualTouchVisible = await page.evaluate(() => window.__sf2Shell.isTouchVisible());
    assert(manualTouchVisible === true, 'Clicking TOUCH: AUTO should toggle TOUCH: ON');

    const dpadBox = await page.locator('#dpad-zone').boundingBox();
    assert(dpadBox && dpadBox.width >= 100, 'Missing #dpad-zone bounding box');
    const cx = dpadBox.x + dpadBox.width / 2;
    const cy = dpadBox.y + dpadBox.height / 2;
    const r = dpadBox.width * 0.32;

    await page.mouse.move(cx, cy + r); // 2 Down
    await page.mouse.down();
    await page.waitForTimeout(50);
    await page.mouse.move(cx + r * 0.72, cy + r * 0.72); // 3 Down-Right
    await page.waitForTimeout(50);
    await page.mouse.move(cx + r, cy); // 6 Right
    await page.waitForTimeout(50);
    await page.mouse.up();
    await page.click('.arc-lp');
    await page.waitForTimeout(100);

    const histText = await page.locator('#input-history').innerText();
    assert(histText.includes('↓') && histText.includes('↘') && histText.includes('→') && histText.includes('LP'), `Expected ↓ ↘ → LP in input history, got: ${histText}`);
    await page.screenshot({ path: resolve(artifactsDir, '03-touch-slide-motion.png') });

    // 3. HTML5 Gamepad Bridge test
    await page.evaluate(() => {
      const mockPad = {
        id: 'SF2 Arcade Stick Mock',
        index: 0,
        connected: true,
        mapping: 'standard',
        axes: [0.95, 0, 0, 0],
        buttons: Array.from({ length: 16 }, (_, i) => ({ pressed: i === 2, value: i === 2 ? 1 : 0 })),
      };
      navigator.getGamepads = () => [mockPad, null, null, null];
    });
    await page.waitForTimeout(120);
    const padLabel = await page.locator('#pad-status').innerText();
    const activeKeys = await page.evaluate(() => window.__sf2Shell.getActiveKeys());
    assert(padLabel === 'PAD: 1P', `Expected PAD: 1P, got ${padLabel}`);
    assert(activeKeys.includes('ArrowRight') && activeKeys.includes('KeyZ'), `Expected Gamepad bridge keys [ArrowRight, KeyZ], got ${activeKeys.join(',')}`);
    await page.screenshot({ path: resolve(artifactsDir, '04-gamepad-bridge.png') });

    // 3b. Car Bonus Stage visual capture (reboot -> ArrowDown x3 -> KeyZ -> walk right -> smash)
    await page.click('#btn-reset');
    await page.waitForFunction(() => window.__sf2Shell && window.__sf2Shell.isBooted(), { timeout: 20000 });
    await page.waitForTimeout(3600);
    await page.click('#canvas');
    await page.keyboard.press('ArrowDown', { delay: 65 });
    await page.waitForTimeout(80);
    await page.keyboard.press('ArrowDown', { delay: 65 });
    await page.waitForTimeout(80);
    await page.keyboard.press('ArrowDown', { delay: 65 });
    await page.waitForTimeout(80);
    await page.keyboard.press('KeyZ', { delay: 65 }); // Start Car Bonus
    await page.waitForTimeout(1100);
    await page.keyboard.down('ArrowRight');
    await page.waitForTimeout(500);
    await page.keyboard.up('ArrowRight');
    await page.keyboard.down('KeyA');
    await page.waitForTimeout(110);
    const bonusPath = resolve(artifactsDir, '09-desktop-bonus-car.png');
    await page.screenshot({ path: bonusPath });
    await page.keyboard.up('KeyA');

    // Verify Car Bonus actually entered the stage rather than staying on Title screen
    const fsMod = await import('node:fs');
    const titleB64 = fsMod.readFileSync(resolve(artifactsDir, '01-desktop-title.png')).toString('base64');
    const bonusB64 = fsMod.readFileSync(bonusPath).toString('base64');
    const bonusDiffs = await page.evaluate(async ([a, b]) => {
      const loadImg = (b64) => new Promise((res, rej) => {
        const img = new Image();
        img.onload = () => res(img);
        img.onerror = rej;
        img.src = 'data:image/png;base64,' + b64;
      });
      const [imgA, imgB] = await Promise.all([loadImg(a), loadImg(b)]);
      const w = imgA.width;
      const h = imgA.height;
      const cA = Object.assign(document.createElement('canvas'), { width: w, height: h });
      const cB = Object.assign(document.createElement('canvas'), { width: w, height: h });
      const ctxA = cA.getContext('2d');
      const ctxB = cB.getContext('2d');
      ctxA.drawImage(imgA, 0, 0);
      ctxB.drawImage(imgB, 0, 0);
      const dA = ctxA.getImageData(0, 0, w, h).data;
      const dB = ctxB.getImageData(0, 0, w, h).data;
      let diffs = 0;
      for (let gx = 0; gx < 16; gx++) {
        for (let gy = 0; gy < 12; gy++) {
          const px = Math.floor(w * (0.25 + (gx / 15) * 0.5));
          const py = Math.floor(h * (0.15 + (gy / 11) * 0.7));
          const i = (py * w + px) * 4;
          const delta = Math.abs(dA[i] - dB[i]) + Math.abs(dA[i + 1] - dB[i + 1]) + Math.abs(dA[i + 2] - dB[i + 2]);
          if (delta > 20) diffs++;
        }
      }
      return diffs;
    }, [titleB64, bonusB64]);
    if (bonusDiffs < 10) {
      throw new Error(`09-desktop-bonus-car.png matches Title screen too closely (sampled grid diffs=${bonusDiffs} < 10)`);
    }

    await desktopCtx.close();

    // 4. Mobile Portrait (390x844) Rotate-to-Landscape Guard test
    const portraitCtx = await browser.newContext({
      viewport: { width: 390, height: 844 },
      isMobile: true,
      hasTouch: true,
    });
    const pPage = await portraitCtx.newPage();
    pPage.on('pageerror', (e) => errors.push(`portrait pageerror: ${e.message}`));
    await pPage.goto(url, { waitUntil: 'networkidle' });
    await pPage.waitForFunction(() => window.__sf2Shell && window.__sf2Shell.isBooted(), { timeout: 20000 });
    await pPage.waitForTimeout(300);

    const blocked = await pPage.evaluate(() => window.__sf2Shell.isOrientationBlocked());
    assert(blocked === true, 'Mobile portrait must show #orientation-overlay');
    const overlayText = await pPage.locator('#orientation-overlay').innerText();
    assert(overlayText.includes('請將手機或平板旋轉為橫向') && overlayText.includes('ROTATE TO LANDSCAPE'), `Unexpected overlay copy: ${overlayText}`);
    await pPage.screenshot({ path: resolve(artifactsDir, '05-mobile-portrait-prompt.png') });

    await pPage.click('#btn-rotate-dismiss');
    await pPage.waitForTimeout(150);
    const blockedAfterDismiss = await pPage.evaluate(() => window.__sf2Shell.isOrientationBlocked());
    assert(blockedAfterDismiss === false, '#btn-rotate-dismiss failed to close orientation overlay');
    await portraitCtx.close();

    // 5. Mobile Landscape (844x390) Ergonomic Cockpit Layout test
    const landCtx = await browser.newContext({
      viewport: { width: 844, height: 390 },
      isMobile: true,
      hasTouch: true,
    });
    const lPage = await landCtx.newPage();
    lPage.on('pageerror', (e) => errors.push(`landscape pageerror: ${e.message}`));
    await lPage.goto(url, { waitUntil: 'networkidle' });
    await lPage.waitForFunction(() => window.__sf2Shell && window.__sf2Shell.isBooted(), { timeout: 20000 });
    await lPage.waitForTimeout(2400);

    const landState = await lPage.evaluate(() => ({
      blocked: window.__sf2Shell.isOrientationBlocked(),
      touchVisible: window.__sf2Shell.isTouchVisible(),
      scrollH: document.documentElement.scrollHeight,
      innerH: window.innerHeight,
      scrollW: document.documentElement.scrollWidth,
      innerW: window.innerWidth,
      leftDeck: document.querySelector('.touch-deck-left').getBoundingClientRect().toJSON(),
      rightDeck: document.querySelector('.touch-deck-right').getBoundingClientRect().toJSON(),
      bezel: document.querySelector('.crt-bezel').getBoundingClientRect().toJSON(),
      strip: document.querySelector('.telemetry-strip').getBoundingClientRect().toJSON(),
      canvas: document.getElementById('canvas').getBoundingClientRect().toJSON(),
    }));

    assert(landState.blocked === false, 'Mobile landscape should NOT show orientation overlay');
    assert(landState.touchVisible === true, 'Mobile landscape with hasTouch must auto-activate touch deck');
    assert(landState.scrollH <= landState.innerH + 2, `Landscape vertical overflow: ${landState.scrollH} > ${landState.innerH}`);
    assert(landState.scrollW <= landState.innerW + 2, `Landscape horizontal overflow: ${landState.scrollW} > ${landState.innerW}`);
    assert(!rectsOverlap(landState.leftDeck, landState.bezel), 'Left deck overlaps CRT bezel in landscape');
    assert(!rectsOverlap(landState.rightDeck, landState.bezel), 'Right deck overlaps CRT bezel in landscape');
    assert(!rectsOverlap(landState.bezel, landState.strip), 'CRT bezel overlaps telemetry strip in landscape');
    assert(landState.canvas.height >= 210, `CRT canvas height unexpectedly small (${landState.canvas.height}px)`);
    assert(Math.round(landState.canvas.width) === 512 && Math.round(landState.canvas.height) === 288, `Expected landscape #canvas 512x288 (2x 256x144), got ${JSON.stringify(landState.canvas)}`);
    await lPage.screenshot({ path: resolve(artifactsDir, '06-mobile-landscape-cockpit.png') });
    await landCtx.close();

    assert(errors.length === 0, `Runtime errors detected:\n${errors.join('\n')}`);
    console.log('[player] ALL 6 WEB PLAYER & MOBILE COCKPIT VERIFICATIONS PASSED!');
  } finally {
    await browser.close();
    server.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
