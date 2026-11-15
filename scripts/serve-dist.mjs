#!/usr/bin/env node
import { createServer } from 'node:http';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { extname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.wasm': 'application/wasm',
  '.tic': 'application/octet-stream',
  '.lua': 'text/plain; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
  '.zip': 'application/zip',
};

export function startDistServer(distDir, port = 0, host = '127.0.0.1') {
  return new Promise((resolvePromise, reject) => {
    const server = createServer((req, res) => {
      const rawPath = (req.url || '/').split('?')[0];
      let rel = decodeURIComponent(rawPath).replace(/^\/+/, '');
      if (!rel || rel === '/') rel = 'index.html';
      const target = resolve(distDir, rel);
      if (!target.startsWith(resolve(distDir))) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
      }
      if (!existsSync(target) || statSync(target).isDirectory()) {
        res.writeHead(404);
        res.end('Not found');
        return;
      }
      const ext = extname(target).toLowerCase();
      res.writeHead(200, {
        'Content-Type': MIME[ext] || 'application/octet-stream',
        'Cache-Control': 'no-cache',
      });
      res.end(readFileSync(target));
    });
    server.on('error', reject);
    server.listen(port, host, () => {
      const addr = server.address();
      resolvePromise({ server, port: addr.port, url: `http://${host}:${addr.port}/` });
    });
  });
}

if (resolve(process.argv[1] || '') === fileURLToPath(import.meta.url)) {
  const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
  const distDir = join(root, 'dist');
  const port = Number(process.env.PORT || 4173);
  startDistServer(distDir, port, '127.0.0.1').then(({ url }) => {
    console.log(`Serving SF2' CE 80 dist/ at ${url}`);
  });
}
