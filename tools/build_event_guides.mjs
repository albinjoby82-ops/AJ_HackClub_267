// Render corrected Markdown into the current static panel-page design.
// Pass a local copy of the site's pinned marked@12.0.2 renderer as argv[2].
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const context = {};
vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), context);
const { marked } = context;
const mapping = {
  'Hardware/ESP32C6.md': 'micromouse-esp32c6.html',
  'Hardware/DRI0044.md': 'micromouse-dri0044.html',
  'Hardware/SEN0142.md': 'micromouse-sen0142.html',
  'Hardware/VL53L0X.md': 'micromouse-vl53l0x.html',
  'Hardware/BuckConverter.md': 'micromouse-buck.html',
  'Hardware/GA12N20.md': 'micromouse-motors.html',
  'Software/C3_WorkingWithAIAgents.md': 'micromouse-ai-agents.html',
};
const escape = text => text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
for (const [source, target] of Object.entries(mapping)) {
  const sourcePath = 'content/docs/Micromouse2026/' + source;
  const markdown = fs.readFileSync(path.join(root, sourcePath), 'utf8').replace(/^---[\s\S]*?---\s*/, '');
  const title = markdown.match(/^# (.+)/)[1];
  let body = markdown.replace(/^# .+\s*/, '');
  const lead = body.split('\n\n')[0];
  body = body.slice(lead.length).trim();
  function render(text) {
    let html = marked.parse(text.replace(/^\{: \.\w+\}\s*$/gm, ''));
    html = html.replace(/href="#\/docs\/Micromouse2026\/([^"#]+)"/g, (_, doc) => `href="${mapping[doc] || '../learn.html?scope=micromouse#/docs/Micromouse2026/' + doc}"`);
    html = html.replace(/(src|href)="([^"#]+)"/g, (match, attr, url) => {
      if (/^(?:https?:|\/|\.\.\/learn|micromouse-)/.test(url)) return match;
      const resolved = path.posix.normalize(path.posix.join(path.posix.dirname(sourcePath), url));
      return `${attr}="../${resolved}"`;
    });
    return html.replaceAll('<table>', '<div class="mm-table-wrap"><table class="mm-table">').replaceAll('</table>', '</table></div>')
      .replaceAll('<ul>', '<ul class="mm-list">').replaceAll('<ol>', '<ol class="mm-list">')
      .replaceAll('<pre>', '<pre class="mm-code">').replaceAll('<blockquote>', '<blockquote class="mm-callout">')
      .replace(/<p>(<img[^>]+>)<\/p>/g, '<figure class="mm-figure">$1</figure>');
  }
  const sections = body.split(/^## /m);
  let panels = '';
  let count = 0;
  for (let i = 0; i < sections.length; i++) {
    if (!sections[i].trim()) continue;
    const newline = sections[i].indexOf('\n');
    const heading = i === 0 ? 'Wiring overview' : sections[i].slice(0, newline);
    const content = i === 0 ? sections[i] : sections[i].slice(newline + 1);
    panels += `<details class="mm-guide-panel" open>\n<summary><span class="mm-panel-num">${String(++count).padStart(2, '0')}</span><span class="mm-panel-name">${escape(heading)}</span><span class="mm-panel-toggle" aria-hidden="true"></span></summary>\n<div class="mm-panel-body">${render(content)}</div>\n</details>\n`;
  }
  const targetPath = path.join(root, 'micromouse', target);
  let page = fs.readFileSync(targetPath, 'utf8');
  page = page.replace(/<title>[\s\S]*?<\/title>/, `<title>${escape(title)} — Dublin Micromouse Open 2026</title>`);
  page = page.replace(/<meta name="description" content="[^"]*">/, `<meta name="description" content="${escape(lead.replace(/\*/g, ''))}">`);
  page = page.replace(/<h1 class="mm-guide-title">[\s\S]*?<\/h1>/, `<h1 class="mm-guide-title">${escape(title.replace(/^[HC]\d+ - /, ''))}</h1>`);
  page = page.replace(/<(?:p|div) class="mm-guide-lede">[\s\S]*?<\/(?:p|div)>/, `<p class="mm-guide-lede">${marked.parseInline(lead)}</p>`);
  const start = page.indexOf('<div class="mm-panels">');
  const end = page.indexOf('<nav class="mm-pager"', start);
  if (start < 0 || end < 0) throw new Error('Missing panel template: ' + target);
  page = page.slice(0, start) + `<div class="mm-panels">\n<p><a href="../learn.html?scope=micromouse#/docs/Micromouse2026/Debug/index.md">Open the debug checks and full sketches →</a></p>\n${panels}</div>\n\n        ` + page.slice(end);
  page = page.replaceAll('H3 SEN0142 IMU', 'H3 MPU-6050 IMU').replaceAll('H5 Buck converter', 'H5 Battery and power');
  fs.writeFileSync(targetPath, page);
}
for (const name of ['2S-5V-buck-power-flow.svg', 'VL53L0X-3-sensor-wiring.svg']) {
  fs.copyFileSync(path.join(root, 'content/docs/assets/images', name), path.join(root, 'assets/micromouse/diagrams', name));
}
for (const dir of ['content/docs/assets/images', 'assets/micromouse/diagrams']) {
  fs.copyFileSync(path.join(root, 'content/docs/assets/images/micromouse-motor-wiring.svg'), path.join(root, dir, 'GA12-N20-dual-encoder-wiring.svg'));
}
console.log('Updated 7 native guide pages and corrected legacy diagram URLs.');
