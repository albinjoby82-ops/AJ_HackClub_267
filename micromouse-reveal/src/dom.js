/** Small DOM builders shared by the overlay scenes. */

export function el(tag, className, html) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (html != null) node.innerHTML = html;
  return node;
}

/**
 * A framed photo layer.
 * `rect` is in stage pixels: { x, y, w, h }. No stretching — the image
 * always covers its frame and the frame is what animates.
 */
export function photo(src, rect, { plain = false, focal = '50% 50%' } = {}) {
  const wrap = el('div', `photo${plain ? ' -plain' : ''}`);
  Object.assign(wrap.style, {
    left: `${rect.x}px`,
    top: `${rect.y}px`,
    width: `${rect.w}px`,
    height: `${rect.h}px`,
  });
  const img = el('img');
  img.src = src;
  img.style.objectPosition = focal;
  img.draggable = false;
  wrap.append(img);
  return wrap;
}

/** A cut-out project shot, centred in its own full-frame layer. */
export function objectShot(src) {
  const wrap = el('div', 'object-shot');
  Object.assign(wrap.style, { left: '0', top: '0', width: '1080px', height: '1920px' });
  const img = el('img');
  img.src = src;
  img.draggable = false;
  wrap.append(img);
  return wrap;
}

/**
 * Impact word with a mask-reveal inner span.
 * Returns the wrapper; animate `.mask > span` with a y translate.
 */
export function impactWord(text, { size = '-lg', top = 820 } = {}) {
  const wrap = el('div', `impact ${size}`);
  wrap.style.top = `${top}px`;
  const mask = el('span', 'mask');
  const inner = el('span', null, text);
  mask.append(inner);
  wrap.append(mask);
  return wrap;
}

/**
 * Kinetic statistic: big number lands first, label follows.
 * `num` may contain <em> to pick out an accent glyph.
 */
export function statBlock(num, label, { top = 760 } = {}) {
  const wrap = el('div', 'stat');
  wrap.style.top = `${top}px`;
  wrap.append(el('span', 'num', num), el('span', 'label', label));
  return wrap;
}

export function projectLabel(text, { top = 1320 } = {}) {
  const node = el('div', 'project-label', text);
  node.style.top = `${top}px`;
  return node;
}

export function envType(text, { top = 900 } = {}) {
  const node = el('div', 'env-type', text);
  node.style.top = `${top}px`;
  return node;
}

/** Full-bleed solid colour layer, used for flashes and hard cuts. */
export function fill(color) {
  const node = el('div');
  Object.assign(node.style, {
    position: 'absolute',
    inset: '0',
    background: color,
  });
  return node;
}

/** Generates a tiny tiling noise texture as a data URI (deterministic). */
export function grainDataUri(size = 256, seed = 1337) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');
  const img = ctx.createImageData(size, size);
  let s = seed;
  const rand = () => {
    // xorshift32 — same texture on every run, including headless capture.
    s ^= s << 13;
    s ^= s >>> 17;
    s ^= s << 5;
    return ((s >>> 0) % 255) / 255;
  };
  for (let i = 0; i < img.data.length; i += 4) {
    const v = 110 + rand() * 90;
    img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
    img.data[i + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  return `url(${canvas.toDataURL('image/png')})`;
}
