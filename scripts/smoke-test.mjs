#!/usr/bin/env node
import { existsSync, readFileSync, statSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, '..');
const dist = resolve(root, 'dist');

function assert(cond, msg) {
  if (!cond) throw new Error(`Smoke assertion failed: ${msg}`);
}

const REQUIRED = [
  'index.html',
  'sf2_ce_80.tic',
  'sf2_ce_80.lua',
  'tic80.js',
  'tic80lua.wasm',
  'manifest.json',
  'sw.js',
  'icon.svg',
  'icon-192.png',
  'icon-512.png',
  'apple-touch-icon.png',
  'favicon.ico',
  'sf2-ce-80-web.zip',
];

for (const name of REQUIRED) {
  const full = resolve(dist, name);
  assert(existsSync(full), `Missing dist file: ${name}`);
  assert(statSync(full).size > 0, `Empty dist file: ${name}`);
}

const html = readFileSync(resolve(dist, 'index.html'), 'utf8');
assert(!html.includes('__APP_VERSION__'), 'Unrendered __APP_VERSION__ token in dist/index.html');
assert(!/https?:\/\/(cdn\.|unpkg\.com|fonts\.googleapis|fonts\.gstatic)/i.test(html), 'External CDN dependency detected in dist/index.html');
assert(html.includes('id="orientation-overlay"'), 'Missing #orientation-overlay in dist/index.html');
assert(html.includes('id="dpad-zone"'), 'Missing #dpad-zone in dist/index.html');
assert(html.includes('id="canvas"'), 'Missing #canvas in dist/index.html');

console.log(`[smoke] Verified all ${REQUIRED.length} dist assets, zero CDN leaks, and valid HTML structure.`);
