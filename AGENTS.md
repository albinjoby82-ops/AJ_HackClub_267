# Repository Agent Instructions

These instructions apply to the entire repository.

## Site architecture

- This is a plain multi-page static HTML site. It is not a client-side SPA and does not use a JavaScript framework.
- There is no package installation or production compilation step.
- The production asset directory is the repository root (`.`).
- The root `index.html` is the homepage and must remain present in the deployed asset set.

## Cloudflare Workers deployment

- The Worker name is `hackclub267`.
- Keep `wrangler.jsonc` as the deployment source of truth.
- Keep `assets.directory` set to `"."`.
- Keep `assets.html_handling` set to `"auto-trailing-slash"` so `/` resolves to the root `index.html`.
- Do not set `assets.html_handling` to `"none"`; that causes the custom-domain root to return HTTP 404.
- Do not add `"not_found_handling": "single-page-application"` unless the site is intentionally converted to a client-side SPA and the user explicitly approves that architectural change.
- Preserve `.assetsignore`. In particular, never upload `.git`, development state, secrets, or local configuration as static assets.
- Do not remove, replace, or modify the custom domain `hackclub.ucdelecsoc.com`.

Use these Cloudflare dashboard build settings:

- Build command: leave blank.
- Deploy command: `npx wrangler deploy`.
- Root directory: leave blank (repository root).
- Production branch: `master`.

## Required deployment checks

Before committing any deployment configuration change:

1. Confirm `index.html` exists at the repository root and is not empty.
2. Run `npx wrangler deploy --dry-run` and require it to succeed.
3. Confirm `.env*`, `.dev.vars*`, and `config.js` are not tracked or included as assets.
4. After deployment, verify `https://hackclub.ucdelecsoc.com/` returns HTTP 200 and serves the expected homepage.

Make the smallest necessary change and do not introduce a framework, package manager, or build pipeline solely for deployment.
