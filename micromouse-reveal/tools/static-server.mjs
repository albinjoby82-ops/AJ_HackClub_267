/**
 * Minimal static file server for the render pipeline.
 *
 * The Vite dev server proved unreliable across a 1350-frame render — it died
 * mid-run more than once, and a dead server takes the whole render with it.
 * Rendering from a built `dist/` served by this removes HMR, the module graph
 * and the external process from the critical path.
 *
 * Range requests are supported because Chromium fetches the logo reveal mp4
 * with them; without Range the video never loads and the tail renders blank.
 */
import http from 'node:http';
import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import path from 'node:path';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.mp4': 'video/mp4',
  '.woff2': 'font/woff2',
};

export async function serve(root) {
  const server = http.createServer(async (req, res) => {
    try {
      const url = new URL(req.url, 'http://localhost');
      let filePath = path.join(root, decodeURIComponent(url.pathname));
      if (url.pathname === '/' || url.pathname === '') filePath = path.join(root, 'index.html');

      // Never serve outside the root.
      if (!filePath.startsWith(root)) {
        res.writeHead(403).end();
        return;
      }

      const info = await stat(filePath);
      const type = MIME[path.extname(filePath).toLowerCase()] ?? 'application/octet-stream';
      const range = req.headers.range;

      if (range) {
        const m = /bytes=(\d*)-(\d*)/.exec(range);
        const start = m[1] ? Number(m[1]) : 0;
        const end = m[2] ? Number(m[2]) : info.size - 1;
        res.writeHead(206, {
          'Content-Type': type,
          'Content-Range': `bytes ${start}-${end}/${info.size}`,
          'Accept-Ranges': 'bytes',
          'Content-Length': end - start + 1,
          'Cache-Control': 'no-store',
        });
        createReadStream(filePath, { start, end }).pipe(res);
        return;
      }

      res.writeHead(200, {
        'Content-Type': type,
        'Content-Length': info.size,
        'Accept-Ranges': 'bytes',
        'Cache-Control': 'no-store',
      });
      createReadStream(filePath).pipe(res);
    } catch {
      res.writeHead(404).end();
    }
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address();
  return { server, port, close: () => new Promise((r) => server.close(r)) };
}
