#!/usr/bin/env node
import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, '..');
const dist = resolve(root, 'dist');

execFileSync('python3', ['build_tic.py', '.'], { cwd: root, stdio: 'inherit' });
execFileSync('python3', ['scripts/gen_icons.py'], { cwd: root, stdio: 'inherit' });

rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });

for (const file of ['sf2_ce_80.tic', 'sf2_ce_80.lua']) {
  cpSync(resolve(root, file), resolve(dist, file));
}

for (const file of ['tic80.js', 'tic80lua.wasm']) {
  const src = resolve(root, 'vendor', 'tic80', file);
  if (!existsSync(src)) {
    throw new Error(`Missing vendor TIC-80 asset: ${src}`);
  }
  cpSync(src, resolve(dist, file));
}

for (const file of [
  'manifest.json',
  'sw.js',
  'icon.svg',
  'icon-192.png',
  'icon-512.png',
  'apple-touch-icon.png',
  'favicon.ico',
]) {
  cpSync(resolve(root, 'public', file), resolve(dist, file));
}

const pkg = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8'));
const template = readFileSync(resolve(root, 'web', 'template.html'), 'utf8');
const rendered = template.replace(/__APP_VERSION__/g, pkg.version);
writeFileSync(resolve(dist, 'index.html'), rendered, 'utf8');

// Package standalone distributable zip via Python zipfile (deterministic, zero external zip binary dependency)
const zipScript = `
import os, zipfile
dist_dir = os.path.abspath("dist")
zip_path = os.path.join(dist_dir, "sf2-ce-80-web.zip")
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for name in sorted(os.listdir(dist_dir)):
        if name.endswith(".zip"):
            continue
        full = os.path.join(dist_dir, name)
        if os.path.isfile(full):
            zf.write(full, arcname=name)
print(f"Packaged {zip_path} ({os.path.getsize(zip_path)} bytes)")
`;
execFileSync('python3', ['-c', zipScript], { cwd: root, stdio: 'inherit' });
console.log(`Built dist bundle v${pkg.version} at ${dist}`);
