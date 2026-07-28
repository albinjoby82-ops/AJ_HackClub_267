/**
 * Keeps everything bulky off the system drive.
 *
 * C: is the Windows drive here and runs close to full; a frame-based render
 * needs ~1.8GB of scratch and Playwright caches ~700MB of browsers. Both live
 * on D: unless overridden.
 *
 * Import this module *before* importing playwright — PLAYWRIGHT_BROWSERS_PATH
 * is read when playwright is first loaded.
 */
import path from 'node:path';

/**
 * Root for all generated output. Defaults to the project directory, which is
 * already gitignored. Override with REVEAL_WORK_ROOT to render elsewhere —
 * useful if the checkout ever lives on a drive without room for the output.
 */
export const WORK_ROOT = process.env.REVEAL_WORK_ROOT ?? process.cwd();

export const OUT_DIR = path.join(WORK_ROOT, 'out');

if (!process.env.PLAYWRIGHT_BROWSERS_PATH) {
  process.env.PLAYWRIGHT_BROWSERS_PATH = 'D:\\dev\\ms-playwright';
}

export const BROWSERS_PATH = process.env.PLAYWRIGHT_BROWSERS_PATH;
