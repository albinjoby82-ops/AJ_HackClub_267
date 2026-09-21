// Browser smoke checks for the static event resources. No npm dependencies.
// node tools/check_debug_browser.mjs <directory-for-screenshots>
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.resolve(process.argv[2] || path.join(os.tmpdir(), 'micromouse-browser-check'));
fs.mkdirSync(out, { recursive: true });
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'micromouse-chrome-'));
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.zip': 'application/zip', '.ino': 'text/plain' };
const server = http.createServer((req, res) => {
  const rel = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  const filename = path.resolve(root, '.' + (rel.endsWith('/') ? rel + 'index.html' : rel));
  if (!filename.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  try {
    const data = fs.readFileSync(filename);
    res.writeHead(200, { 'Content-Type': (types[path.extname(filename)] || 'application/octet-stream') + '; charset=utf-8' });
    res.end(data);
  } catch { res.writeHead(404).end('Not found'); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}`;
const chrome = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank',
], { windowsHide: true, stdio: ['ignore', 'ignore', 'pipe'] });
let stderr = '';
chrome.stderr.on('data', data => { stderr += data; });
chrome.on('error', error => { stderr += error.message; });
let socket;
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
try {
  const portFile = path.join(profile, 'DevToolsActivePort');
  for (let i = 0; i < 100 && !fs.existsSync(portFile); i++) {
    if (chrome.exitCode !== null) throw new Error(`Chrome exited: ${stderr.slice(-2000)}`);
    await delay(100);
  }
  if (!fs.existsSync(portFile)) throw new Error(`Chrome did not start: ${stderr.slice(-2000)}`);
  const port = fs.readFileSync(portFile, 'utf8').split('\n')[0];
  const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  socket = new WebSocket(targets.find(target => target.type === 'page').webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  let nextId = 1;
  const pending = new Map();
  const exceptions = [];
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    if (message.method === 'Runtime.exceptionThrown') exceptions.push(message.params.exceptionDetails.text);
    if (!message.id) return;
    const job = pending.get(message.id);
    if (!job) return;
    pending.delete(message.id);
    clearTimeout(job.timer);
    if (message.error) job.reject(new Error(JSON.stringify(message.error))); else job.resolve(message.result);
  };
  function call(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = nextId++;
      const timer = setTimeout(() => { pending.delete(id); reject(new Error('CDP timeout: ' + method)); }, 20000);
      pending.set(id, { resolve, reject, timer });
      socket.send(JSON.stringify({ id, method, params }));
    });
  }
  async function evaluate(expression) {
    const result = await call('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true, userGesture: true });
    if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  }
  await call('Page.enable');
  await call('Runtime.enable');
  await call('Browser.grantPermissions', { origin: base, permissions: ['clipboardReadWrite', 'clipboardSanitizedWrite'] });
  async function navigate(url, selector) {
    await call('Page.navigate', { url });
    for (let i = 0; i < 100; i++) {
      if (await evaluate(`!!document.querySelector(${JSON.stringify(selector)})`)) return;
      await delay(100);
    }
    throw new Error(`Page did not render ${selector}: ${url}`);
  }
  async function screenshot(name, width, height) {
    await call('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
    await delay(350); // Allow the mobile sidebar's 250 ms transition to finish.
    const data = await call('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
    fs.writeFileSync(path.join(out, name + '.png'), Buffer.from(data.data, 'base64'));
    const dimensions = await evaluate('({viewport: innerWidth, document: document.documentElement.scrollWidth})');
    assert.ok(dimensions.document <= width + 1, `${name} overflows: ${JSON.stringify(dimensions)}`);
  }
  await navigate(base + '/micromouse-resources.html#debug', '.mm-cat[data-category="Debug"][aria-pressed="true"]');
  assert.equal(await evaluate('document.querySelectorAll(".mm-res[data-category=Debug]").length'), 14);
  assert.equal(await evaluate('document.querySelectorAll(".mm-res:not([hidden])").length'), 14);
  await screenshot('hub-desktop', 1440, 1000);
  await screenshot('hub-mobile', 390, 844);
  await screenshot('hub-small', 320, 800);

  for (const slug of ['esp32c6', 'dri0044', 'sen0142', 'vl53l0x', 'buck', 'motors', 'ai-agents']) {
    await navigate(base + '/micromouse/micromouse-' + slug + '.html', '.mm-panels');
    const invalid = await evaluate(`(async () => {
      const errors = [];
      for (const el of document.querySelectorAll('main a[href], main img[src]')) {
        const url = new URL(el.href || el.src);
        if (url.origin === location.origin && !(await fetch(url)).ok) errors.push(url.href);
      }
      return errors;
    })()`);
    assert.deepEqual(invalid, [], 'Native guide links: ' + slug);
    await screenshot('native-' + slug + '-mobile', 390, 844);
    if (slug === 'vl53l0x') await screenshot('native-wiring-desktop', 1440, 1000);
  }

  const sandbox = { window: {} };
  const { runInNewContext } = await import('node:vm');
  runInNewContext(fs.readFileSync(path.join(root, 'content/content.js'), 'utf8'), sandbox);
  const pagePaths = Object.keys(sandbox.window.SITE_CONTENT.pages).filter(p => /^docs\/Micromouse2026\/(Debug|Hardware)\//.test(p));
  let checkedLinks = 0;
  for (const pagePath of pagePaths) {
    await navigate(base + '/learn.html?scope=micromouse#/' + pagePath, '#content h1');
    assert.ok(await evaluate('typeof marked !== "undefined"'), 'Markdown renderer unavailable');
    const invalid = await evaluate(`(async () => {
      const elements = [...document.querySelectorAll('#content a[href], #content img[src]')];
      const failures = [];
      for (const el of elements) {
        const url = new URL(el.href || el.src);
        if (url.origin !== location.origin) continue;
        if (url.hash.startsWith('#/docs/')) {
          const p = url.hash.slice(2).split('#')[0];
          if (!window.SITE_CONTENT.pages[p]) failures.push(url.href);
        } else if (!(await fetch(url)).ok) failures.push(url.href);
      }
      return { failures, count: elements.length };
    })()`);
    assert.deepEqual(invalid.failures, [], pagePath);
    checkedLinks += invalid.count;
    if (pagePath.includes('/Debug/') && !pagePath.endsWith('/index.md')) {
      await evaluate('document.querySelector("#content details").open = true');
      const copied = await evaluate('(async () => { let captured; Object.defineProperty(navigator.clipboard, "writeText", { configurable: true, value: async text => { captured = text; } }); const p = document.querySelector("#content details pre"); p.querySelector("button").click(); await new Promise(r => setTimeout(r, 50)); return { code: p.querySelector("code").innerText, copied: captured }; })()');
      assert.equal(copied.copied, copied.code, 'Copy button: ' + pagePath);
    }
    if (pagePath.endsWith('/Debug/05_tof_3.md')) {
      await screenshot('step-desktop', 1440, 1000);
      await screenshot('step-mobile', 390, 844);
    }
    if (pagePath.endsWith('/Debug/index.md')) {
      await screenshot('debug-index-mobile', 390, 844);
    }
    if (pagePath.endsWith('/Hardware/VL53L0X.md')) {
      await screenshot('wiring-mobile', 390, 844);
      await evaluate('document.querySelector(".hardware-image").click()');
      assert.ok(await evaluate('document.querySelector(".hardware-viewer").open'));
      await screenshot('wiring-expanded', 1440, 1000);
    }
  }
  for (const name of ['micromouse-event-pin-map', 'micromouse-imu-wiring', 'VL53L0X-3-sensor-wiring', 'micromouse-motor-wiring', '2S-5V-buck-power-flow']) {
    await navigate(base + '/content/docs/assets/images/' + name + '.svg', 'svg');
    await screenshot(name, 1440, 1200);
  }
  await navigate(base + '/downloads/micromouse-debug-kit/imu_visualizer/', '#btnDemo');
  await evaluate('document.querySelector("#btnDemo").click()');
  await delay(300);
  await screenshot('imu-visualizer', 1440, 1000);
  assert.deepEqual(exceptions, []);
  console.log(`PASS: ${pagePaths.length} pages, ${checkedLinks} links/images, 13 copy buttons, diagram zoom, responsive layouts and visualizer demo. Screenshots: ${out}`);
} finally {
  if (socket?.readyState === WebSocket.OPEN) socket.close();
  chrome.kill();
  server.closeAllConnections();
  server.close();
}
